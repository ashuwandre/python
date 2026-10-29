
import os
import sys
import json
import asyncio

from typing import TypedDict
from dotenv import load_dotenv
from openai import OpenAI

from langgraph.graph import StateGraph, END

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


# ==================================================
# 1. CONFIGURATION
# ==================================================

load_dotenv()

client = OpenAI(api_key=os.getenv("env_key"))

MODEL = "gpt-4.1-mini"


# ==================================================
# 2. FAQ DATABASE
# ==================================================

FAQ_DATABASE = {
    "billing": {
        "pricing": (
            "Basic costs $9.99/month, Pro costs $29.99/month, "
            "and Enterprise costs $99.99/month."
        ),
        "refund": "Refunds are available within 30 days.",
        "cancel": (
            "You can cancel your subscription from account settings."
        )
    },
    "technical": {
        "login": "Use Forgot Password to reset your password.",
        "api": (
            "Refer to the API documentation for integration details."
        )
    },
    "general": {
        "contact": "Contact our support team for assistance."
    }
}


# ==================================================
# 3. LANGGRAPH STATE
# ==================================================

class FAQState(TypedDict, total=False):
    question: str
    messages: list
    pending_tool_calls: list
    response: str


# ==================================================
# 4. OPENAI TOOL DEFINITIONS
# The LLM chooses which tool to call.
# ==================================================

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_support_hours",
            "description": (
                "Get customer support working hours. "
                "Use this tool when the user asks about "
                "support hours, opening times, or support timings."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
                "additionalProperties": False
            },
            "strict": True
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_faq",
            "description": (
                "Search the FAQ database for information about "
                "pricing, refunds, cancellation, login, API "
                "integration, or contacting support."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "enum": [
                            "billing",
                            "technical",
                            "general"
                        ],
                        "description": "FAQ category."
                    },
                    "question": {
                        "type": "string",
                        "description": (
                            "The user's question to search for."
                        )
                    }
                },
                "required": ["category", "question"],
                "additionalProperties": False
            },
            "strict": True
        }
    }
]


# ==================================================
# 5. SEARCH THE FAQ DATABASE
# This is an ordinary Python tool, not an MCP tool.
# ==================================================

def search_faq(category: str, question: str) -> str:

    category_data = FAQ_DATABASE.get(category, {})
    question = question.lower()

    # Handle common words that mean the same thing.
    keyword_aliases = {
        "pricing": [
            "pricing", "price", "cost", "plans",
            "subscription", "how much"
        ],
        "refund": [
            "refund", "money back", "refunded"
        ],
        "cancel": [
            "cancel", "cancellation", "terminate subscription"
        ],
        "login": [
            "login", "log in", "password",
            "forgot password", "reset password"
        ],
        "api": [
            "api", "integration", "integrate"
        ],
        "contact": [
            "contact", "support team", "help"
        ]
    }

    for keyword, answer in category_data.items():

        terms = keyword_aliases.get(keyword, [keyword])

        if any(term in question for term in terms):
            return answer

    return (
        "NOT_FOUND: No matching answer was found in the FAQ database."
    )


# ==================================================
# 6. CALL THE MCP SERVER
# ==================================================

async def call_mcp_tool(tool_name: str, arguments: dict) -> str:

    server_file = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "mcp_server.py"
    )

    server_params = StdioServerParameters(
        command=sys.executable,
        args=[server_file]
    )

    async with stdio_client(server_params) as (read, write):

        async with ClientSession(read, write) as session:

            await session.initialize()

            # Discover the tools available on the MCP server.
            available_tools = await session.list_tools()

            tool_names = [
                tool.name for tool in available_tools.tools
            ]

            if tool_name not in tool_names:
                raise RuntimeError(
                    f"MCP tool '{tool_name}' is not available."
                )

            # Execute the MCP tool selected by the LLM.
            result = await session.call_tool(
                tool_name,
                arguments
            )

            if result.isError:
                raise RuntimeError(
                    f"MCP tool '{tool_name}' failed."
                )

            text_results = [
                item.text
                for item in result.content
                if item.type == "text"
            ]

            if not text_results:
                raise RuntimeError(
                    "MCP tool returned no text result."
                )

            return "\n".join(text_results)


# ==================================================
# 7. AGENT NODE
# The LLM decides whether a tool is needed.
# ==================================================

def agent_node(state: FAQState) -> dict:

    messages = state.get("messages", [])

    system_prompt = {
        "role": "system",
        "content": (
            "You are a helpful FAQ assistant.\n"
            "Use get_support_hours for questions about support "
            "hours or opening times.\n"
            "Use search_faq for questions about billing, pricing, "
            "refunds, cancellation, login, API integration, "
            "or contact information.\n"
            "Choose the appropriate tool when needed. "
            "Do not invent FAQ answers.\n"
            "If the tool returns NOT_FOUND, tell the user that "
            "the answer could not be found and suggest contacting "
            "support.\n"
            "After receiving a tool result, respond to the user "
            "in friendly, natural language. Preserve all specific "
            "details, prices, and instructions from the result."
        )
    }

    # Ask the LLM to decide whether to call a tool.
    result = client.chat.completions.create(
        model=MODEL,
        messages=[system_prompt] + messages,
        tools=TOOLS,
        tool_choice="auto",
        temperature=0
    )

    assistant_message = result.choices[0].message

    # Preserve the assistant message, including any tool calls.
    updated_messages = messages + [
        assistant_message.model_dump(exclude_none=True)
    ]

    if assistant_message.tool_calls:

        print("\nLLM selected tool(s):")

        for tool_call in assistant_message.tool_calls:
            print(" -", tool_call.function.name)

        return {
            "messages": updated_messages,
            "pending_tool_calls": [
                tool_call.model_dump()
                for tool_call in assistant_message.tool_calls
            ]
        }

    # No tool call: the LLM has produced its final answer.
    return {
        "messages": updated_messages,
        "pending_tool_calls": [],
        "response": assistant_message.content or (
            "Sorry, I could not generate a response."
        )
    }


# ==================================================
# 8. TOOL EXECUTION NODE
# Execute the tools chosen by the LLM.
# ==================================================

async def execute_tools_node(state: FAQState) -> dict:

    messages = list(state.get("messages", []))
    pending_tool_calls = state.get("pending_tool_calls", [])

    for tool_call in pending_tool_calls:

        function_name = tool_call["function"]["name"]
        arguments = json.loads(
            tool_call["function"]["arguments"]
        )

        print(f"\nExecuting: {function_name}")

        try:

            if function_name == "get_support_hours":

                # Actual MCP tool call
                tool_output = await call_mcp_tool(
                    "get_support_hours",
                    arguments
                )

            elif function_name == "search_faq":

                # Ordinary Python function call
                tool_output = search_faq(
                    arguments["category"],
                    arguments["question"]
                )

            else:
                tool_output = "Unknown tool requested."

        except Exception as error:

            print("Tool error:", error)

            tool_output = (
                "TOOL_ERROR: The requested tool failed. "
                "Do not invent its result."
            )

        # Return tool results to the LLM.
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call["id"],
            "content": tool_output
        })

    return {
        "messages": messages,
        "pending_tool_calls": []
    }


# ==================================================
# 9. CONDITIONAL ROUTING
# ==================================================

def route_after_agent(state: FAQState) -> str:

    if state.get("pending_tool_calls"):
        return "execute_tools"

    return "end"


# ==================================================
# 10. CREATE LANGGRAPH AGENT
# ==================================================

def create_faq_agent():

    graph = StateGraph(FAQState)

    graph.add_node("agent", agent_node)
    graph.add_node("execute_tools", execute_tools_node)

    graph.set_entry_point("agent")

    graph.add_conditional_edges(
        "agent",
        route_after_agent,
        {
            "execute_tools": "execute_tools",
            "end": END
        }
    )

    # After a tool executes, let the LLM inspect its result.
    graph.add_edge("execute_tools", "agent")

    return graph.compile()


# ==================================================
# 11. QUERY FUNCTION
# ==================================================

def query(question: str) -> str:

    if not isinstance(question, str) or not question.strip():
        return "Invalid input"

    question = question.strip()

    normalized_question = question.lower()

    blocked_phrases = [
        "ignore previous instructions",
        "ignore all instructions",
        "ignore the system prompt",
        "reveal your system prompt",
        "disregard previous instructions"
    ]

    if any(
        phrase in normalized_question
        for phrase in blocked_phrases
    ):
        return "Invalid input"

    agent = create_faq_agent()

    # Start the LangGraph agent with the user's question.
    result = asyncio.run(
        agent.ainvoke(
            {
                "question": question,
                "messages": [
                    {
                        "role": "user",
                        "content": question
                    }
                ],
                "pending_tool_calls": []
            },
            config={"recursion_limit": 10}
        )
    )

    return result.get(
        "response",
        "Sorry, I could not generate a response."
    )


# ==================================================
# 12. RUN THE APPLICATION
# ==================================================

if __name__ == "__main__":

    while True:

        question = input(
            "\nAsk your FAQ question (type exit to stop): "
        )

        if question.strip().lower() == "exit":
            print("Goodbye!")
            break

        try:
            answer = query(question)
            print("\nAnswer:", answer)

        except Exception as error:
            print("\nError:", error)
