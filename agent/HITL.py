
from langgraph.graph import StateGraph, START, END
from langgraph.types import interrupt, Command
from typing import TypedDict

# 1. Define state
class State(TypedDict):
    message: str

# 2. Agent node
def agent(state: State):

    print("Agent: Preparing email...")

    # Pause and ask human for approval
    decision = interrupt("Do you approve sending this email?")

    if decision == "yes":
        print("Human approved!")
        print("Email sent:", state["message"])
    else:
        print("Human rejected the email!")

    return state

# 3. Create graph
builder = StateGraph(State)

builder.add_node("agent", agent)

builder.add_edge(START, "agent")
builder.add_edge("agent", END)

# 4. Compile with checkpointer
from langgraph.checkpoint.memory import InMemorySaver

graph = builder.compile(checkpointer=InMemorySaver())

# 5. Run agent
config = {"configurable": {"thread_id": "1"}}

result = graph.invoke(
    {"message": "Hello, your order is confirmed!"},
    config=config
)

print("Agent paused. Waiting for human approval.")

# 6. Human gives approval and resumes execution
result = graph.invoke(
    Command(resume="yes"),
    config=config
)
