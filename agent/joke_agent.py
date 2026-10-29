import os
from typing import typedDict
from dotenv import load_dotenv
from openai import OpenAI
load_dotenv()

key = os.getenv('env_key')
client = OpenAI(api_key = env_key)

calss JokeState(typedDict):
    topic:str
    joke:str
    rating:str
    
def joke_generator_node(state:JokeState):
    topic = state['topic']
    res = client.chat.completions.create(model ='gpt-4.1-mini',
                                         temperature = 0,
                                         messages=[{'role':'system','contenct':('your are comedian create joke ')},
                                                   {'role':'user','content':"""creta joke on {topic}"""}])
    joke = res.choices[0].message.content.strip()
    return {'joke':joke}

def joke_rater(state:JokeState):
    joke = state['joke']
    res = client.chat.completions.create(model = 'gpt-4.1-mini',
                                         temperature=0,
                                         messages=[{'role':'system','contenct':('your are evaluater  rate joke on 1 to  10 basis ')},
                                                                                            {'role':'user', "content": f"Rate this joke:\n{state['joke']}"}])
    
    rating = res.choices[0].message.content.strip()
    return {'rating':rating}

agent = StateGraph(JokeState):
agent.add_node('create':joke_generator_node)
agent.add_node('rate':joke_rater)

agent.add_edge(START,'create')
agent.add_edge('create','rate')
agent.add_edge('rate',END)


graph = agent.complie()
res = agent.invoke({'topic':'carickt',
                    'joke':'',
                    'rating':''}
                   
                   )
print(res)