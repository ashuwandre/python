from typing import Any

from pydantic import BaseModel
from typing_extensions import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import START, StateGraph
from langgraph.types import Command, interrupt


class Decision(BaseModel):
    approved: bool
    note: str | None = None


class State(TypedDict):
    answer: Any


def node(state: State) -> State:
    answer = interrupt({"question": "approve?"}, response_schema=Decision)
    return {"answer": answer}


graph = (
    StateGraph(State)
    .add_node("node", node)
    .add_edge(START, "node")
    .compile(checkpointer=InMemorySaver())
)
config = {"configurable": {"thread_id": "1"}}

result = graph.invoke({"answer": None}, config)
pending = result["__interrupt__"][0]
assert pending.response_schema == Decision.model_json_schema()

result = graph.invoke(Command(resume={"approved": True}), config)
assert result["answer"] == Decision(approved=True)