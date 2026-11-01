# # pip install -U deepagents langchain-openai python-dotenv


import os
import json
from typing import TypedDict, List
from dotenv import load_dotenv
from pydantic import BaseModel, Field

from deepagents import create_deep_agent

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import interrupt, Command

from langchain_openai import ChatOpenAI


# =====================================================
# 1. CONFIGURATION
# =====================================================

load_dotenv()

llm = ChatOpenAI(
    model="gpt-4.1-mini",
    temperature=0
)


# =====================================================
# 2. DUMMY DATA
# =====================================================

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
        "ERROR HikariPool - Connection is not available",
        "ERROR Database connection timeout",
        "ERROR HTTP 500 Internal Server Error"
    ]
}


HISTORICAL_TICKETS = [
    {
        "id": 11,
        "issue": "Payment API returning HTTP 500",
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
        "root_cause": "Authentication service failure",
        "solution": "Check authentication service"
    }
]


# =====================================================
# 3. OBSERVABILITY SUBGRAPH
# =====================================================

class ObserveState(TypedDict):
    ticket: dict
    logs: list
    errors: list
    summary: str


def collect_logs(state: ObserveState):

    service = state["ticket"]["service"]

    logs = APPLICATION_LOGS.get(service, [])

    print("\n[Observability] Collecting logs")

    return {"logs": logs}


def filter_errors(state: ObserveState):

    errors = [
        log for log in state["logs"]
        if "ERROR" in log
    ]

    print("[Observability] Filtering errors")

    return {"errors": errors}


def summarize_logs(state: ObserveState):

    summary = "\n".join(state["errors"])

    print("[Observability] Log collection completed")

    return {"summary": summary}


observe_builder = StateGraph(ObserveState)

observe_builder.add_node("collect", collect_logs)
observe_builder.add_node("filter", filter_errors)
observe_builder.add_node("summarize", summarize_logs)

observe_builder.add_edge(START, "collect")
observe_builder.add_edge("collect", "filter")
observe_builder.add_edge("filter", "summarize")
observe_builder.add_edge("summarize", END)

observability_graph = observe_builder.compile()


# =====================================================
# 4. HISTORICAL TICKET SUBGRAPH
# =====================================================

class HistoryState(TypedDict):
    ticket: dict
    similar_tickets: list
    summary: str


def search_history(state: HistoryState):

    issue = state["ticket"]["description"].lower()

    matches = []

    # Simple dummy keyword matching
    if "payment" in issue:

        matches = [
            ticket for ticket in HISTORICAL_TICKETS
            if "payment" in ticket["issue"].lower()
        ]

    print("\n[Historical Agent] Searching old tickets")

    return {"similar_tickets": matches}


def summarize_history(state: HistoryState):

    summary = json.dumps(
        state["similar_tickets"],
        indent=2
    )

    print("[Historical Agent] Historical search completed")

    return {"summary": summary}


history_builder = StateGraph(HistoryState)

history_builder.add_node("search", search_history)
history_builder.add_node("summarize", summarize_history)

history_builder.add_edge(START, "search")
history_builder.add_edge("search", "summarize")
history_builder.add_edge("summarize", END)

historical_graph = history_builder.compile()


# =====================================================
# 5. ANALYSIS AGENT
# =====================================================

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
        description="Evidence from current logs and historical tickets"
    )


analysis_agent = create_deep_agent(

    model=llm,

    system_prompt="""
    You are an IT Root Cause Analysis Agent.

    You receive:
    1. Current application logs.
    2. Historical tickets and their resolutions.

    Your responsibilities:

    - Compare current logs with historical tickets.
    - Identify the most likely root cause.
    - Recommend a resolution.
    - Decide whether a remediation script is required.

    Rules:

    - Do not invent evidence.
    - If there is not enough evidence, clearly say so.
    - A script is required only when a technical
      remediation action needs automation.
    - Never execute any script.

    Return structured analysis.
    """,

    response_format=AnalysisResult
)


# =====================================================
# 6. SCRIPT GENERATION AGENT
# =====================================================

class ScriptResult(BaseModel):

    script: str = Field(
        description="Generated illustrative remediation script"
    )

    explanation: str = Field(
        description="What the script is intended to do"
    )


script_agent = create_deep_agent(

    model=llm,

    system_prompt="""
    You are a Script Generation Agent.

    Generate a remediation script based on the
    root cause and approved recommendation.

    Rules:

    - Generate code only for the requested remediation.
    - Never execute the script.
    - Never include destructive operations.
    - Never include real credentials or secrets.
    - Return a safe illustrative script for review.
    - Explain what the script does.

    Return structured output.
    """,

    response_format=ScriptResult
)


# =====================================================
# 7. MAIN DEEP AGENT - PLANNER
# =====================================================

main_deep_agent = create_deep_agent(

    model=llm,

    system_prompt="""
    You are the Main Support Deep Agent and Planner.

    Your job is to create a plan for investigating
    incoming support tickets.

    Plan these activities:

    1. Collect current application logs.
    2. Search historical support tickets.
    3. Analyse current and historical evidence.
    4. Recommend a solution.
    5. Determine whether script generation is needed.
    6. Require human approval before execution.

    Do not execute scripts.

    Return a clear numbered investigation plan.
    """
)


# =====================================================
# 8. MAIN LANGGRAPH STATE
# =====================================================

class SupportState(TypedDict):

    ticket: dict

    plan: str

    logs: list

    errors: list

    log_summary: str

    historical_tickets: list

    historical_summary: str

    analysis: dict

    script: str

    script_explanation: str

    approved: bool

    status: str


# =====================================================
# 9. PLANNER NODE
# =====================================================

def planner_node(state: SupportState):

    result = main_deep_agent.invoke({

        "messages": [
            {
                "role": "user",
                "content": f"""
                Create an investigation plan for this ticket:

                {state['ticket']}
                """
            }
        ]

    })

    plan = result["messages"][-1].content

    print("\n[Main Deep Agent] Investigation plan:")
    print(plan)

    return {"plan": plan}


# =====================================================
# 10. OBSERVABILITY NODE
# =====================================================

def observability_node(state: SupportState):

    result = observability_graph.invoke({

        "ticket": state["ticket"],
        "logs": [],
        "errors": [],
        "summary": ""

    })

    return {

        "logs": result["logs"],
        "errors": result["errors"],
        "log_summary": result["summary"]

    }


# =====================================================
# 11. HISTORICAL NODE
# =====================================================

def historical_node(state: SupportState):

    result = historical_graph.invoke({

        "ticket": state["ticket"],
        "similar_tickets": [],
        "summary": ""

    })

    return {

        "historical_tickets": result["similar_tickets"],
        "historical_summary": result["summary"]

    }


# =====================================================
# 12. ANALYSIS NODE
# =====================================================

def analysis_node(state: SupportState):

    print("\n[Analysis Agent] Analysing evidence")

    result = analysis_agent.invoke({

        "messages": [
            {
                "role": "user",
                "content": f"""
                Analyse this support ticket.

                TICKET:
                {state['ticket']}

                CURRENT LOGS:
                {state['log_summary']}

                HISTORICAL TICKETS:
                {state['historical_summary']}

                Identify root cause and recommendation.
                Decide if a script is required.
                """
            }
        ]

    })

    analysis = result["structured_response"]

    print("\nAnalysis Result:")
    print(analysis.model_dump_json(indent=2))

    return {
        "analysis": analysis.model_dump()
    }


# =====================================================
# 13. CONDITIONAL EDGE
# =====================================================

def check_script_required(state: SupportState):

    if state["analysis"]["script_required"]:

        print("\n[Router] Script required: YES")

        return "generate_script"

    print("\n[Router] Script required: NO")

    return "finish"


# =====================================================
# 14. SCRIPT GENERATION NODE
# =====================================================

def script_generation_node(state: SupportState):

    # This node is called ONLY when script_required=True

    print("\n[Script Agent] Generating remediation script")

    result = script_agent.invoke({

        "messages": [
            {
                "role": "user",
                "content": f"""
                Generate a remediation script.

                Root cause:
                {state['analysis']['root_cause']}

                Recommendation:
                {state['analysis']['recommendation']}

                The script is for human review only.
                Do not execute it.
                """
            }
        ]

    })

    script_result = result["structured_response"]

    return {

        "script": script_result.script,

        "script_explanation": script_result.explanation,

        "status": "waiting_for_approval"

    }


# =====================================================
# 15. HUMAN APPROVAL NODE
# =====================================================

def human_approval_node(state: SupportState):

    decision = interrupt({

        "message": "Human approval required before execution",

        "ticket": state["ticket"],

        "root_cause": state["analysis"]["root_cause"],

        "recommendation": state["analysis"]["recommendation"],

        "script": state["script"],

        "explanation": state["script_explanation"]

    })

    return {

        "approved": decision == "approve"

    }


# =====================================================
# 16. APPROVAL CONDITIONAL EDGE
# =====================================================

def check_approval(state: SupportState):

    if state["approved"]:

        print("\n[HITL] Script approved")

        return "execute"

    print("\n[HITL] Script rejected")

    return "reject"


# =====================================================
# 17. MOCK EXECUTION TOOL
# =====================================================

def execute_remediation(state: SupportState):

    # IMPORTANT:
    # This is only a mock execution.
    # It does not execute generated Python or shell code.

    print("\n[Execution Tool] Approved remediation requested")

    print(state["script"])

    print("Mock service remediation completed")

    return {

        "status": "completed"

    }


# =====================================================
# 18. REJECTION NODE
# =====================================================

def reject_remediation(state: SupportState):

    print("\n[Execution] Rejected by human")

    return {

        "status": "manual_resolution_required"

    }


# =====================================================
# 19. NO SCRIPT REQUIRED NODE
# =====================================================

def finish_without_script(state: SupportState):

    print("\nNo script required.")

    return {

        "status": "recommendation_ready"

    }


# =====================================================
# 20. BUILD MAIN LANGGRAPH
# =====================================================

builder = StateGraph(SupportState)

builder.add_node("planner", planner_node)

builder.add_node("observability", observability_node)

builder.add_node("historical", historical_node)

builder.add_node("analysis", analysis_node)

builder.add_node("generate_script", script_generation_node)

builder.add_node("approval", human_approval_node)

builder.add_node("execute", execute_remediation)

builder.add_node("reject", reject_remediation)

builder.add_node("finish", finish_without_script)


# Main workflow
builder.add_edge(START, "planner")

builder.add_edge("planner", "observability")

builder.add_edge("observability", "historical")

builder.add_edge("historical", "analysis")


# Conditional edge: Script required?
builder.add_conditional_edges(

    "analysis",

    check_script_required,

    {
        "generate_script": "generate_script",
        "finish": "finish"
    }

)


# Script -> Human approval
builder.add_edge("generate_script", "approval")


# Conditional edge: Human approval?
builder.add_conditional_edges(

    "approval",

    check_approval,

    {
        "execute": "execute",
        "reject": "reject"
    }

)


# Final edges
builder.add_edge("execute", END)

builder.add_edge("reject", END)

builder.add_edge("finish", END)


# Compile with checkpointing
checkpointer = InMemorySaver()

support_graph = builder.compile(
    checkpointer=checkpointer
)


# =====================================================
# 21. RUN THE PROJECT
# =====================================================

if __name__ == "__main__":

    config = {
        "configurable": {
            "thread_id": "ticket-101"
        }
    }

    initial_state = {

        "ticket": TICKET,

        "plan": "",

        "logs": [],

        "errors": [],

        "log_summary": "",

        "historical_tickets": [],

        "historical_summary": "",

        "analysis": {},

        "script": "",

        "script_explanation": "",

        "approved": False,

        "status": "started"

    }

    # First execution
    result = support_graph.invoke(
        initial_state,
        config=config
    )

    # Check whether LangGraph is paused
    if "__interrupt__" in result:

        print("\n========== HUMAN REVIEW ==========")

        for item in result["__interrupt__"]:
            print(item.value)

        decision = input(
            "\nApprove script? (yes/no): "
        ).strip().lower()

        human_decision = (
            "approve" if decision == "yes" else "reject"
        )

        # Resume using SAME thread_id
        final_result = support_graph.invoke(

            Command(resume=human_decision),

            config=config

        )

        print("\nFinal status:")
        print(final_result["status"])  

    else:

        print("\nFinal recommendation:")

        print(result["analysis"])

        print("Status:", result["status"])
