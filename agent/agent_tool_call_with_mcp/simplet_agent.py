from langchain.agents import create_agent

def get_weather(city:str)->str:
    return f"""its sunny day in {city}"""
agent = create_agent(model = 'gpt-4.1-mini',
                     tools = [get_weather],
                     system_prompt =' you are helpful assistant')
result = agent.invoke(
    {"messages": [{"role": "user", "content": "What's the weather in San Francisco?"}]}
)
print(result["messages"][-1].content_blocks)


 