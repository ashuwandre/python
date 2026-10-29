from langchain.agents import create_agent
from langchain.tools import tool

@tool
def get_support_hours() -> str:
    """Get customer support working hours."""
    return "Monday to Friday, 9 AM to 5 PM."

agent = create_agent(
    model="openai:gpt-4.1-mini",
    tools=[get_support_hours],
    system_prompt="You are a helpful FAQ assistant."
)

result = agent.invoke({
    "messages": [
        {"role": "user", "content": "What are support hours?"}
    ]
})

print(result["messages"][-1].content)