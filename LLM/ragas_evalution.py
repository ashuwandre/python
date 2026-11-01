
import os
import asyncio
import pandas as pd

from openai import AsyncOpenAI

from langchain_openai import (
    ChatOpenAI,
    OpenAIEmbeddings
)

from langchain_chroma import Chroma

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# RAGAS imports (modern collections API)
from ragas.llms import llm_factory
from ragas.embeddings.base import embedding_factory

from ragas.metrics.collections import (
    Faithfulness,
    AnswerRelevancy,
    ContextPrecision,
    ContextRecall
)


# --------------------------------------------------
# 1. Initialize ChromaDB
# --------------------------------------------------

embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small"
)

vectorstore = Chroma(
    collection_name="support_tickets",
    persist_directory="./chroma_db",
    embedding_function=embeddings
)

retriever = vectorstore.as_retriever(
    search_kwargs={"k": 4}
)


# --------------------------------------------------
# 2. Initialize generation LLM
# --------------------------------------------------

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0
)


# --------------------------------------------------
# 3. Create RAG prompt and chain
# --------------------------------------------------

prompt = ChatPromptTemplate.from_template("""
You are a support engineer.

Analyze the historical error logs and identify
the root cause of the issue.

Use only the provided context.

Context:
{context}

Question:
{question}

Provide a clear answer.
""")

rag_chain = (
    prompt
    | llm
    | StrOutputParser()
)


# --------------------------------------------------
# 4. Define RAG execution function
# --------------------------------------------------

def run_rag(question):

    # Retrieve historical tickets
    documents = retriever.invoke(question)

    # Extract document text
    contexts = [
        doc.page_content
        for doc in documents
    ]

    # Combine retrieved documents
    context_text = "\n\n".join(contexts)

    # Generate answer
    answer = rag_chain.invoke({
        "context": context_text,
        "question": question
    })

    return answer, contexts


# --------------------------------------------------
# 5. Prepare evaluation dataset
# --------------------------------------------------

test_data = [

    {
        "question": "Why did the database automation fail?",

        "reference": (
            "The automation failed because the "
            "database connection timed out."
        )
    },

    {
        "question": "Why did the login automation fail?",

        "reference": (
            "The login failed because authentication "
            "credentials were invalid."
        )
    },

    {
        "question": "Why did the API request fail?",

        "reference": (
            "The API request failed because the "
            "server returned an HTTP 500 error."
        )
    }

]


# --------------------------------------------------
# 6. Initialize RAGAS evaluator
# --------------------------------------------------

eval_client = AsyncOpenAI(
    api_key=os.environ["OPENAI_API_KEY"]
)

evaluator_llm = llm_factory(
    "gpt-4o-mini",
    client=eval_client
)

evaluator_embeddings = embedding_factory(
    "openai",
    model="text-embedding-3-small",
    client=eval_client
)


# --------------------------------------------------
# 7. Define evaluation metrics
# --------------------------------------------------

faithfulness = Faithfulness(
    llm=evaluator_llm
)

answer_relevancy = AnswerRelevancy(
    llm=evaluator_llm,
    embeddings=evaluator_embeddings
)

context_precision = ContextPrecision(
    llm=evaluator_llm
)

context_recall = ContextRecall(
    llm=evaluator_llm
)


# --------------------------------------------------
# 8. Execute RAG and evaluate each question
# --------------------------------------------------

async def evaluate_rag():

    results = []

    for item in test_data:

        question = item["question"]
        reference = item["reference"]

        # Run actual RAG application
        answer, contexts = run_rag(question)

        # Evaluate faithfulness
        faith_score = await faithfulness.ascore(
            user_input=question,
            response=answer,
            retrieved_contexts=contexts
        )

        # Evaluate answer relevancy
        relevancy_score = await answer_relevancy.ascore(
            user_input=question,
            response=answer
        )

        # Evaluate context precision
        precision_score = await context_precision.ascore(
            user_input=question,
            retrieved_contexts=contexts,
            reference=reference
        )

        # Evaluate context recall
        recall_score = await context_recall.ascore(
            user_input=question,
            retrieved_contexts=contexts,
            reference=reference
        )

        # Store evaluation results
        results.append({

            "question": question,

            "generated_answer": answer,

            "faithfulness": faith_score.value,

            "answer_relevancy": relevancy_score.value,

            "context_precision": precision_score.value,

            "context_recall": recall_score.value

        })

    return results


# --------------------------------------------------
# 9. Run evaluation
# --------------------------------------------------

if __name__ == "__main__":

    results = asyncio.run(evaluate_rag())

    df = pd.DataFrame(results)

    print("\nRAGAS EVALUATION RESULTS")

    print(df.to_string(index=False))

    # Save results
    df.to_csv(
        "ragas_evaluation_results.csv",
        index=False
    )

    print("\nEvaluation completed!")
