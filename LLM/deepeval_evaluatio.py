
import json
import os

from openai import OpenAI

from deepeval.dataset import (
    Golden,
    EvaluationDataset,
    get_current_golden
)

from deepeval.tracing import (
    observe,
    update_current_span
)

from deepeval.test_case import ToolCall

from deepeval.metrics import (
    ToolCorrectnessMetric,
    ArgumentCorrectnessMetric,
    TaskCompletionMetric,
    StepEfficiencyMetric
)


# ==========================================
# 1. Initialize OpenAI
# ==========================================

client = OpenAI(
    api_key=os.environ["OPENAI_API_KEY"]
)

MODEL = "gpt-4o-mini"


# ==========================================
# 2. Define dummy historical ticket database
# ==========================================

TICKETS = [
    {
        "error_id": 101,
        "team": "CES",
        "error": "Database connection timeout",
        "root_cause": "Database server unavailable",
        "solution": "Check database connectivity and connection pool."
    },
    {
        "error_id": 102,
        "team": "CES",
        "error": "Authentication failed",
        "root_cause": "Invalid credentials",
        "solution": "Verify username and password."
    }
]


# ==========================================
# 3. Define tools
# ==========================================

@observe(type="tool")
def search_historical_tickets(query: str, team: str):

    """Search historical support tickets."""

    results = [
        ticket for ticket in TICKETS
        if team.lower() == ticket["team"].lower()
        and query.lower() in ticket["error"].lower()
    ]

    return results


@observe(type="tool")
def get_error_details(error_id: int):

    """Fetch complete details of a historical error."""

    for ticket in TICKETS:
        if ticket["error_id"] == error_id:
            return ticket

    return {"error": "Ticket not found"}


# ==========================================
# 4. Define tool schemas for OpenAI
# ==========================================

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_historical_tickets",
            "description": "Search historical tickets using error text and team.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string"
                    },
                    "team": {
                        "type": "string"
                    }
                },
                "required": ["query", "team"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_error_details",
            "description": "Get complete details of a ticket using error ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "error_id": {
                        "type": "integer"
                    }
                },
                "required": ["error_id"]
            }
        }
    }
]


# ==========================================
# 5. Tool mapping
# ==========================================

TOOL_FUNCTIONS = {
    "search_historical_tickets": search_historical_tickets,
    "get_error_details": get_error_details
}


# ==========================================
# 6. Define evaluation metrics
# ==========================================

tool_correctness = ToolCorrectnessMetric(
    threshold=0.7
)

argument_correctness = ArgumentCorrectnessMetric(
    threshold=0.7,
    model=MODEL
)

task_completion = TaskCompletionMetric(
    threshold=0.7,
    model=MODEL
)

step_efficiency = StepEfficiencyMetric(
    threshold=0.7,
    model=MODEL
)


# ==========================================
# 7. LLM tool-calling component
# ==========================================

@observe(
    type="llm",
    metrics=[
        tool_correctness,
        argument_correctness
    ]
)
def run_agent_llm(user_question):

    messages = [
        {
            "role": "system",
            "content": """
            You are a support automation assistant.

            Use historical ticket tools to investigate failures.

            First search historical tickets.
            If a relevant ticket is found, fetch its details.
            Then explain the root cause and solution.

            Do not invent ticket information.
            """
        },
        {
            "role": "user",
            "content": user_question
        }
    ]

    # Allow the model to call tools
    for _ in range(4):

        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto"
        )

        assistant_message = response.choices[0].message

        messages.append(
            assistant_message.model_dump(exclude_none=True)
        )

        # If no tool call, return final answer
        if not assistant_message.tool_calls:
            final_answer = assistant_message.content or ""

            # Provide expected tool list to DeepEval
            update_current_span(
                input=user_question,
                output=final_answer,
                expected_tools=get_current_golden().expected_tools
            )

            return final_answer

        # Execute selected tools
        for tool_call in assistant_message.tool_calls:

            tool_name = tool_call.function.name

            arguments = json.loads(
                tool_call.function.arguments
            )

            tool_function = TOOL_FUNCTIONS[tool_name]

            tool_result = tool_function(**arguments)

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(tool_result)
            })

    raise RuntimeError("Maximum tool-call iterations reached")


# ==========================================
# 8. Define main agent
# ==========================================

@observe(type="agent")
def support_agent(user_question):

    answer = run_agent_llm(user_question)

    return answer


# ==========================================
# 9. Create evaluation dataset
# ==========================================

dataset = EvaluationDataset(
    goldens=[
        Golden(
            input=(
                "Investigate the database connection timeout "
                "for CES and provide its root cause and solution."
            ),

            expected_tools=[
                ToolCall(
                    name="search_historical_tickets"
                ),
                ToolCall(
                    name="get_error_details"
                )
            ]
        )
    ]
)


# ==========================================
# 10. Run agent evaluation
# ==========================================

if __name__ == "__main__":

    for golden in dataset.evals_iterator(
        metrics=[
            task_completion,
            step_efficiency
        ]
    ):

        answer = support_agent(golden.input)

        print("\nAGENT ANSWER:")
        print(answer)

    print("\nAgent evaluation completed!")
