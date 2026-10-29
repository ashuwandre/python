
# from typing import TypedDict
# from langgraph.graph import StateGraph, END


# # ==================================================
# # 1. AGENT STATE
# # ==================================================

# class FAQState(TypedDict, total=False):
#     question: str
#     category: str
#     search_result: dict
#     response: str


# # ==================================================
# # 2. CLASSIFY USER QUESTION USING OPENAI
# # ==================================================

# def classify_question(state: dict) -> dict:
#     question = state["question"]

#     result = client.chat.completions.create(
#         model="gpt-4o-mini",
#         messages=[
#             {
#                 "role": "system",
#                 "content": (
#                     "Classify the question into exactly one category: "
#                     "billing, technical, or general. "
#                     "Return ONLY the category name."
#                 )
#             },
#             {
#                 "role": "user",
#                 "content": question
#             }
#         ],
#         temperature=0
#     )

#     category = (
#         result.choices[0].message.content or ""
#     ).strip().lower()

#     # Validate category
#     if category not in ["billing", "technical", "general"]:
#         category = "general"

#     return {"category": category}


# # ==================================================
# # 3. SEARCH KNOWLEDGE BASE
# # ==================================================

# def search_knowledge_base(state: dict) -> dict:
#     category = state["category"]
#     question = state["question"]

#     # Use the existing provided search function
#     result = search_kb(category, question)

#     return {"search_result": result}


# # ==================================================
# # 4. FORMAT FINAL RESPONSE USING OPENAI
# # ==================================================

# def format_response(state: dict) -> dict:
#     search_result = state["search_result"]

#     # If the answer is not found
#     if not search_result.get("found"):
#         return {
#             "response": (
#                 "Sorry, I couldn't find an answer to your question. "
#                 "Please contact our support team for assistance."
#             )
#         }

#     raw_answer = search_result.get("answer")

#     if not raw_answer:
#         return {
#             "response": (
#                 "Sorry, I couldn't find an answer to your question. "
#                 "Please contact our support team for assistance."
#             )
#         }

#     result = client.chat.completions.create(
#         model="gpt-4o-mini",
#         messages=[
#             {
#                 "role": "system",
#                 "content": (
#                     "Rewrite the FAQ answer in friendly, natural language. "
#                     "Preserve all specific details, numbers, URLs, and steps. "
#                     "Do not add information that is not in the original answer."
#                 )
#             },
#             {
#                 "role": "user",
#                 "content": f"FAQ answer:\n{raw_answer}"
#             }
#         ],
#         temperature=0
#     )

#     response = (
#         result.choices[0].message.content or ""
#     ).strip()

#     # Retain the original answer if the model returns empty content
#     if not response:
#         response = raw_answer

#     return {"response": response}


# # ==================================================
# # 5. CREATE LANGGRAPH AGENT
# # ==================================================

# def create_faq_agent():
#     graph = StateGraph(FAQState)

#     # Register nodes
#     graph.add_node("classify", classify_question)
#     graph.add_node("search", search_knowledge_base)
#     graph.add_node("format", format_response)

#     # Define workflow
#     graph.set_entry_point("classify")
#     graph.add_edge("classify", "search")
#     graph.add_edge("search", "format")
#     graph.add_edge("format", END)

#     # Compile graph
#     return graph.compile()


# # ==================================================
# # 6. QUERY FUNCTION - SINGLE ENTRY POINT
# # ==================================================

# def query(question: str) -> str:

#     # Validate empty or invalid input
#     if not isinstance(question, str) or not question.strip():
#         return "invalid_input"

#     normalized_question = question.strip().lower()

#     # Basic prompt-injection detection
#     blocked_phrases = [
#         "ignore previous instructions",
#         "ignore all instructions",
#         "ignore the system prompt",
#         "reveal your system prompt",
#         "disregard previous instructions"
#     ]

#     if any(
#         phrase in normalized_question
#         for phrase in blocked_phrases
#     ):
#         return "invalid_input"

#     # Create and run agent
#     agent = create_faq_agent()

#     result = agent.invoke({
#         "question": question.strip()
#     })

#     return result["response"]


# # ==================================================
# # 7. MANUAL TESTING
# # Use only when running outside an auto-grading setup
# # ==================================================

# if __name__ == "__main__":
#     question = input("Ask your FAQ question: ")
#     answer = query(question)
#     print("\nAnswer:", answer)


#___________________________________________________________________________________________________

from typing import TypedDict
from langgraph.graph import StateGraph,END
import os
from dotenv import load_dotenv
from openai import OpenAI
load_dotenv()

client = OpenAI(api_key = os.getenv('env_key'))

FAQ_DATABASE = {
    "billing": {
        "pricing": (
            "Basic costs $9.99/month, Pro costs $29.99/month, "
            "and Enterprise costs $99.99/month."
        ),
        "refund": "Refunds are available within 30 days.",
        "cancel": "You can cancel your subscription from account settings."
    },
    "technical": {
        "login": "Use Forgot Password to reset your password.",
        "api": "Refer to the API documentation for integration details."
    },
    "general": {
        "hours": "Support is available Monday to Friday.",
        "contact": "Contact our support team for assistance."
    }
}

class FAQState(TypedDict,total= False):
    question:str
    category:str
    search_result:dict
    response:str
    
def classify_question(state:dict)->dict:
    question = state['question']
    
    result = client.chat.completions.create(
        model = 'gpt-4.1-mini',
        messages = [{'role':'system','content':('classify the question in one category billling,technical,general return only one category')},
                   {'role':'user','content':question}],
        temperature = 0
    )
    
    category = (result.choices[0].message.content).strip().lower()
    if category not in ['billing','technical','general']:
        return {"category": "general"}
    
    return {"category": category}

def search_kb(category, question):
    question = question.lower()

    # Get FAQs for the given category
    category_data = FAQ_DATABASE.get(category, {})

    # Search for a matching keyword
    for keyword, answer in category_data.items():
        if keyword in question:
            return {
                "found": True,
                "answer": answer
            }

    # No matching answer found
    return {
        "found": False,
        "answer": None
    }

def format_response(state:dict)->dict:
    search_result= state['search_result']
    
    if not search_result.get('found'):
        return {'response':('sorry I could not find the ans')}
    raw_ans = search_result.get('answer')
    
    if not raw_ans:
        return {'response':('can not find ans')}
    res = client.chat.completions.create(
        model = 'gpt-4,1-mini',
        temperature =0,
        messages=[{'role':'system','content':("""rewirte FAQ ans in frinedly and naturela lag.do not add nay other info""")},{
            'role':'user','content':(raw_ans)}]
    )
    res = res.choices[0].message.content
    if not res:
        response = raw_ans
        
    return {'response':res}
       
def search_know_base(state:dict)->dict:
    category=state['category']
    question=state['question']
    
    result = search_kb(category,question)
    return {'search_result':result}

def create_faq_agent():
    graph = StateGraph(FAQState)
    
    graph.add_node('classify',classify_question)
    graph.add_node('search',search_know_base)
    graph.add_node('format',format_response)
    
    graph.set_entry_point('classify')
    graph.add_edge('classify','search')
    graph.add_edge('search','format')
    graph.add_edge('format',END)
    
    return graph.compile()

def query(question:str)->str:
    if not isinstance(question,str):
        return 'invalide input'
    normalised_question = question.strip().lower()
    blocked_phrase  =['ignore previoitun ntructions','revel sys prompt']
    if any(phrase in normalised_question for phrase in blocked_phrase):
        return ' invalid input'
    
    agent = create_faq_agent()
    result = agent.invoke({'question':question.strip()})
    return result['response']

if __name__ == '__main__':
    que = input('ask que    ')
    ans = query(que)
    print('ans',ans)
    



    
        
    