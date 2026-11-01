# pip install langchain langchain-openai langchain-neo4j langchain-experimental neo4j python-dotenv

# main.py
# Project: Employee-Company Knowledge Graph using LangChain and Neo4j

import os
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_neo4j import Neo4jGraph
from langchain_core.documents import Document
from langchain_experimental.graph_transformers import LLMGraphTransformer


# --------------------------------------------------
# STEP 1: Load environment variables
# --------------------------------------------------

load_dotenv()

# --------------------------------------------------
# STEP 2: Initialize LLM
# LLM will extract entities and relationships
# from our text documents.
# --------------------------------------------------

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0
)


# --------------------------------------------------
# STEP 3: Connect to Neo4j database
# Neo4j will store our graph nodes and relationships.
# --------------------------------------------------

graph = Neo4jGraph(
    url=os.getenv("NEO4J_URI"),
    username=os.getenv("NEO4J_USERNAME"),
    password=os.getenv("NEO4J_PASSWORD")
)


# --------------------------------------------------
# STEP 4: Create dummy text documents
# These are normal text documents, not graph data.
# --------------------------------------------------

documents = [

    Document(
        page_content="Rahul works at Google as a Java Developer."
    ),

    Document(
        page_content="Priya works at Microsoft as a Python Developer."
    ),

    Document(
        page_content="Amit works at Google as a Python Developer."
    ),

    Document(
        page_content="Sneha works at Amazon as a Java Developer."
    )
]


# --------------------------------------------------
# STEP 5: Initialize LLMGraphTransformer
#
# LLMGraphTransformer uses the LLM to extract:
# - Entities (Person, Company, Technology)
# - Relationships (WORKS_AT, HAS_SKILL)
#
# We are not manually defining nodes or edges.
# --------------------------------------------------

llm_transformer = LLMGraphTransformer(
    llm=llm
)


# --------------------------------------------------
# STEP 6: Convert text documents into GraphDocuments
#
# LLM reads the documents and extracts graph data.
# Output contains nodes and relationships.
# --------------------------------------------------

graph_documents = llm_transformer.convert_to_graph_documents(
    documents
)


# --------------------------------------------------
# STEP 7: Print extracted nodes and relationships
# --------------------------------------------------

for doc in graph_documents:

    print("\nExtracted Nodes:")

    for node in doc.nodes:
        print(node)

    print("\nExtracted Relationships:")

    for relationship in doc.relationships:
        print(relationship)


# --------------------------------------------------
# STEP 8: Store graph documents in Neo4j
#
# Creates nodes and relationships in Neo4j.
# include_source=True also stores source document
# information in the graph.
# --------------------------------------------------

graph.add_graph_documents(
    graph_documents,
    include_source=True
)


# Refresh schema after inserting graph data.
# This allows LangChain to see the updated graph schema.

graph.refresh_schema()


# --------------------------------------------------
# STEP 9: Display graph schema
# --------------------------------------------------

print("\nNeo4j Graph Schema:")

print(graph.schema)


# --------------------------------------------------
# STEP 10: Verify stored graph data
# --------------------------------------------------

result = graph.query("""
    MATCH (a)-[r]->(b)
    RETURN a, type(r) AS relationship, b
""")

print("\nStored Graph Data:")

for record in result:
    print(record)


print("\nKnowledge Graph Created Successfully!")


from langchain_neo4j import GraphCypherQAChain
from langchain_core.prompts import PromptTemplate

cypher_prompt = PromptTemplate(
    input_variables=["schema", "question"],

    template="""
    You are an expert Neo4j developer.

    Graph Schema:
    {schema}

    Convert the user's question into a valid Cypher query.

    Instructions:
    1. Use only labels, relationships and properties
       available in the schema.
    2. Generate read-only Cypher queries.
    3. Do not create, update or delete data.
    4. Return only the Cypher query.

    User Question:
    {question}

    Cypher Query:
    """
)

qa_chain = GraphCypherQAChain.from_llm(
    llm=llm,
    graph=graph,
    cypher_prompt=cypher_prompt,
    verbose=True,
    allow_dangerous_requests=True,
    return_intermediate_steps=True
)

# Question 1
response = qa_chain.invoke({
    "query": "Which employees work at Google?"
})

print("\nQuestion:")
print("Which employees work at Google?")

print("\nAnswer:")
print(response["result"])

print("\nGenerated Cypher and Retrieved Data:")
print(response["intermediate_steps"])


# Question 2
response = qa_chain.invoke({
    "query": "Which technologies does Rahul know?"
})

print("\nAnswer:")
print(response["result"])


# Question 3
response = qa_chain.invoke({
    "query": "Which employees know Python?"
})

print("\nAnswer:")
print(response["result"])