
import os
import sys
import json
import asyncio
from typing import TypedDict, List

from dotenv import load_dotenv
from pydantic import BaseModel, Field

from mcp.server.fastmcp import FastMCP
from langchain_mcp_adapters.client import MultiServerMCPClient

from langchain.agents import create_agent
from langchain.tools import tool
from langchain_openai import ChatOpenAI

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import interrupt, Command


# ==========================================================
# 1. CONFIGURATION AND DUMMY DATA
# ==========================================================

load_dotenv()

llm = ChatOpenAI(
    model="gpt-4.1-mini",
    temperature=0
)

TICKET = {
    "id": 101,
    "service": "payment-service",
    "description": "Payment API returning HTTP 500",
    "severity": "HIGH"
}

APPLICATION_LOGS = {
    "payment-service": [
        "INFO Payment service started",
        "INFO Request received",
        "ERROR HikariPool connection unavailable",
        "ERROR Database connection timeout",
        "ERROR HTTP 500 Internal Server Error"
    ]
}

HISTORICAL_TICKETS = [
    {
        "id": 11,
        "issue": "Payment API HTTP 500",
        "root_cause": "Database connection pool exhausted",
        "solution": "Check DB connections and restart service"
    },
    {
        "id": 12,
        "issue": "Payment API timeout",
        "root_cause": "Database connection timeout",
        "solution": "Check database connectivity"
    },
    {
        "id": 13,
        "issue": "Login service unavailable",
        "root_cause": "Authentication failure",
        "solution": "Check authentication service"
    }
]


# ==========================================================
# 2. OBSERVABILITY MCP SERVER
# ==========================================================

observability_server = FastMCP("observability-server")


@observability_server.tool()
def collect_logs(service: str) -> list:
    """Collect application logs for the requested service."""

    return APPLICATION_LOGS.get(service, [])


@observability_server.tool()
def filter_error_logs(logs: list) -> list:
    """Filter ERROR messages from application logs."""

    return [
        log for log in logs
        if "ERROR" in log
    ]


# ==========================================================
# 3. HISTORICAL TICKET MCP SERVER
# ==========================================================

historical_server = FastMCP("historical-ticket-server")


@historical_server.tool()
def search_historical_tickets(issue: str) -> list:
    """Search previous support tickets matching an issue."""

    words = [
        word.lower()
        for word in issue.split()
        if len(word) > 3
    ]

    matches = []

    for ticket in HISTORICAL_TICKETS:

        old_issue = ticket["issue"].lower()

        if any(word in old_issue for word in words):
            matches.append(ticket)

    return matches


# ==========================================================
# 4. MCP SERVER STARTUP MODES
# ==========================================================

if __name__ == "__main__":

    if "--observability-server" in sys.argv:

        observability_server.run(transport="stdio")
        sys.exit(0)

    if "--historical-server" in sys.argv:

        historical_server.run(transport="stdio")
        sys.exit(0)


# ==========================================================
# 5. ANALYSIS AGENT
# ==========================================================

class AnalysisResult(BaseModel):

    root_cause: str = Field(
        description="Identified technical root cause"
    )

    recommendation: str = Field(
        description="Recommended resolution"
    )

    script_required: bool = Field(
        description="Whether a remediation script is needed"
    )

    evidence: List[str] = Field(
        description="Evidence from current and historical data"
    )


analysis_agent = create_agent(

    model=llm,

    tools=[],

    response_format=AnalysisResult,

    system_prompt="""
    You are a Root Cause Analysis Agent.

    You receive current application errors and
    historical ticket resolutions.

    Your responsibilities:

    1. Compare current errors with historical tickets.
    2. Identify the most likely root cause.
    3. Recommend a solution.
    4. Decide whether a remediation script is required.

    Rules:
    - Do not invent evidence.
    - If evidence is insufficient, say so.
    - Never execute scripts.
    """
)


# ==========================================================
# 6. SCRIPT GENERATION AGENT
# ==========================================================

class ScriptResult(BaseModel):

    script: str = Field(
        description="Illustrative remediation script"
    )

    explanation: str = Field(
        description="Explanation of the script"
    )


@tool
def get_safe_script_template(action: str) -> str:
    """Return a harmless illustrative remediation template."""

    return """
# Demo remediation script
# No real infrastructure changes are performed

print("Checking payment service health")
print("Checking database connection pool")
print("Remediation requires operator review")
"""


script_agent = create_agent(

    model=llm,

    tools=[get_safe_script_template],

    response_format=ScriptResult,

    system_prompt="""
    You are a Script Generation Agent.

    Generate an illustrative remediation script
    based on the root cause and recommendation.

    Use the safe script template tool.

    Rules:
    - Never execute scripts.
    - Do not include destructive operations.
    - Do not include credentials or secrets.
    - Explain what the script does.
    - Script is for human review only.
    """
)


# ==========================================================
# 7. MAIN APPLICATION
# MCP CLIENT + SUBGRAPHS + REACT AGENTS
# ==========================================================

async def run_application():

    # ------------------------------------------------------
    # 7A. CONNECT TO BOTH MCP SERVERS
    # ------------------------------------------------------

    client = MultiServerMCPClient({

        "observability": {
            "transport": "stdio",
            "command": sys.executable,
            "args": [
                os.path.abspath(__file__),
                "--observability-server"
            ],
            "env": os.environ.copy()
        },

        "historical": {
            "transport": "stdio",
            "command": sys.executable,
            "args": [
                os.path.abspath(__file__),
                "--historical-server"
            ],
            "env": os.environ.copy()
        }

    })

    # Discover tools exposed by MCP servers
    mcp_tools = await client.get_tools()

    print("\nMCP TOOLS DISCOVERED:")

    for item in mcp_tools:
        print(item.name)

    # Map MCP tools by name
    mcp_tool_map = {
        item.name: item
        for item in mcp_tools
    }

    collect_logs_tool = mcp_tool_map["collect_logs"]

    filter_logs_tool = mcp_tool_map["filter_error_logs"]

    history_search_tool = mcp_tool_map[
        "search_historical_tickets"
    ]


    # ======================================================
    # 8. OBSERVABILITY LANGGRAPH SUBGRAPH
    # ======================================================

    class ObserveState(TypedDict):
        service: str
        logs: list
        errors: list

    async def collect_node(state: ObserveState):

        print("\n[Observability] Calling MCP collect_logs")

        result = await collect_logs_tool.ainvoke({
            "service": state["service"]
        })

        return {"logs": result}

    async def filter_node(state: ObserveState):

        print("[Observability] Calling MCP filter_error_logs")

        result = await filter_logs_tool.ainvoke({
            "logs": state["logs"]
        })

        return {"errors": result}

    obs_builder = StateGraph(ObserveState)

    obs_builder.add_node("collect", collect_node)
    obs_builder.add_node("filter", filter_node)

    obs_builder.add_edge(START, "collect")
    obs_builder.add_edge("collect", "filter")
    obs_builder.add_edge("filter", END)

    observability_graph = obs_builder.compile()


    # ======================================================
    # 9. HISTORICAL TICKET LANGGRAPH SUBGRAPH
    # ======================================================

    class HistoryState(TypedDict):
        issue: str
        matches: list

    async def history_node(state: HistoryState):

        print("\n[Historical] Calling MCP ticket search")

        result = await history_search_tool.ainvoke({
            "issue": state["issue"]
        })

        return {"matches": result}

    history_builder = StateGraph(HistoryState)

    history_builder.add_node("search", history_node)

    history_builder.add_edge(START, "search")
    history_builder.add_edge("search", END)

    historical_graph = history_builder.compile()


    # ======================================================
    # 10. TOOLS FOR MAIN REACT AGENT
    # These tools invoke the compiled subgraphs
    # ======================================================

    @tool
    async def investigate_logs(service: str) -> str:
        """Investigate current logs for a given application service."""

        result = await observability_graph.ainvoke({
            "service": service,
            "logs": [],
            "errors": []
        })

        return json.dumps({
            "service": service,
            "errors": result["errors"]
        })

    @tool
    async def investigate_history(issue: str) -> str:
        """Find historical support tickets and their resolutions."""

        result = await historical_graph.ainvoke({
            "issue": issue,
            "matches": []
        })

        return json.dumps(result["matches"])


    # ======================================================
    # 11. MAIN REACT AGENT
    # ======================================================

    main_agent = create_agent(

        model=llm,

        tools=[
            investigate_logs,
            investigate_history
        ],

        system_prompt="""
        You are the Main Support Ticket Investigation Agent.

        Your responsibilities:

        1. Understand the incoming ticket.
        2. Create an investigation plan.
        3. Call investigate_logs using the service name.
        4. Call investigate_history using the issue description.
        5. Collect both results.
        6. Return a structured evidence summary.

        Do not invent evidence.
        Do not generate or execute scripts.
        """

    )


    # ======================================================
    # 12. MAIN LANGGRAPH STATE
    # ======================================================

    class SupportState(TypedDict):

        ticket: dict
        investigation: str
        analysis: dict
        script: str
        approved: bool
        status: str


    # ======================================================
    # 13. MAIN REACT AGENT NODE
    # ======================================================

    async def investigation_node(state: SupportState):

        print("\nMAIN REACT AGENT")

        result = await main_agent.ainvoke({

            "messages": [
                {
                    "role": "user",
                    "content": (
                        "Investigate this support ticket. "
                        "Use both investigation tools.\n"
                        + json.dumps(state["ticket"])
                    )
                }
            ]

        })

        return {
            "investigation": str(
                result["messages"][-1].content
            )
        }


    # ======================================================
    # 14. ANALYSIS NODE
    # ======================================================

    async def analysis_node(state: SupportState):

        print("\nANALYSIS REACT AGENT")

        result = await analysis_agent.ainvoke({

            "messages": [
                {
                    "role": "user",
                    "content": (
                        "Analyse this investigation:\n"
                        + state["investigation"]
                    )
                }
            ]

        })

        analysis = result["structured_response"]

        print(analysis.model_dump_json(indent=2))

        return {
            "analysis": analysis.model_dump()
        }


    # ======================================================
    # 15. CONDITIONAL EDGE: SCRIPT REQUIRED?
    # ======================================================

    def script_router(state: SupportState):

        if state["analysis"]["script_required"]:
            print("\nScript required: YES")
            return "script"

        print("\nScript required: NO")
        return "finish"


    # ======================================================
    # 16. SCRIPT GENERATION NODE
    # ======================================================

    async def script_node(state: SupportState):

        # Called ONLY if script_required=True

        print("\nSCRIPT GENERATION REACT AGENT")

        result = await script_agent.ainvoke({

            "messages": [
                {
                    "role": "user",
                    "content": json.dumps(state["analysis"])
                }
            ]

        })

        script_result = result["structured_response"]

        return {
            "script": script_result.script,
            "status": "waiting_for_approval"
        }


    # ======================================================
    # 17. HUMAN APPROVAL
    # ======================================================

    def approval_node(state: SupportState):

        decision = interrupt({

            "ticket": state["ticket"],

            "recommendation": state["analysis"]["recommendation"],

            "script": state["script"],

            "message": "Review and approve remediation script"

        })

        return {
            "approved": decision == "approve"
        }


    def approval_router(state: SupportState):

        if state["approved"]:
            return "execute"

        return "reject"


    # ======================================================
    # 18. EXECUTION / REJECTION / FINISH
    # ======================================================

    def execute_node(state: SupportState):

        # Safe mock only: does not execute generated code.

        print("\nApproved remediation requested")
        print(state["script"])

        return {
            "status": "mock_execution_completed"
        }


    def reject_node(state: SupportState):

        return {
            "status": "manual_resolution_required"
        }


    def finish_node(state: SupportState):

        print("\nNo script required.")

        print(state["analysis"]["recommendation"])

        return {
            "status": "recommendation_ready"
        }


    # ======================================================
    # 19. BUILD MAIN LANGGRAPH
    # ======================================================

    builder = StateGraph(SupportState)

    builder.add_node("investigate", investigation_node)
    builder.add_node("analysis", analysis_node)
    builder.add_node("script", script_node)
    builder.add_node("approval", approval_node)
    builder.add_node("execute", execute_node)
    builder.add_node("reject", reject_node)
    builder.add_node("finish", finish_node)

    builder.add_edge(START, "investigate")

    builder.add_edge("investigate", "analysis")

    builder.add_conditional_edges(
        "analysis",
        script_router,
        {
            "script": "script",
            "finish": "finish"
        }
    )

    builder.add_edge("script", "approval")

    builder.add_conditional_edges(
        "approval",
        approval_router,
        {
            "execute": "execute",
            "reject": "reject"
        }
    )

    builder.add_edge("execute", END)
    builder.add_edge("reject", END)
    builder.add_edge("finish", END)

    checkpointer = InMemorySaver()

    support_graph = builder.compile(
        checkpointer=checkpointer
    )


    # ======================================================
    # 20. RUN THE COMPLETE WORKFLOW
    # ======================================================

    config = {
        "configurable": {
            "thread_id": "ticket-101"
        }
    }

    result = await support_graph.ainvoke({

        "ticket": TICKET,
        "investigation": "",
        "analysis": {},
        "script": "",
        "approved": False,
        "status": "started"

    }, config=config)

    # HITL interruption
    if "__interrupt__" in result:

        print("\nHUMAN APPROVAL REQUIRED")

        for item in result["__interrupt__"]:
            print(item.value)

        decision = input(
            "\nApprove script? (yes/no): "
        ).strip().lower()

        resume_value = (
            "approve" if decision == "yes"
            else "reject"
        )

        result = await support_graph.ainvoke(

            Command(resume=resume_value),

            config=config

        )

    print("\nFINAL STATUS:", result["status"])

    print("ANALYSIS:", result.get("analysis"))


# ==========================================================
# 21. APPLICATION ENTRY POINT
# ==========================================================

if __name__ == "__main__":

    asyncio.run(run_application())
