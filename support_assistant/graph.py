import os
from typing import TypedDict, List

import chromadb
from sentence_transformers import SentenceTransformer
from langgraph.graph import StateGraph, START, END

from models import AskResponse
from prompt import PROMPT_TEMPLATE

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHROMA_DIR = os.path.join(BASE_DIR, "chroma_db")

COLLECTION_NAME = "zepto_policies"

MOCK_LLM = os.getenv("MOCK_LLM", "1") != "0"
client = chromadb.PersistentClient(path=CHROMA_DIR)

collection = client.get_collection(
    name=COLLECTION_NAME
)

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

class GraphState(TypedDict, total=False):
    query: str
    intent: str
    context: str
    sources: List[str]
    answer: str
    confidence: float


def classify_intent(state: GraphState):
    query = state["query"].lower()

    policy_keywords = [
        "delivery",
        "return",
        "refund",
        "membership",
        "tracking",
        "track",
        "cancel",
        "cancellation",
        "gift card",
        "support hours",
        "customer support",
    ]

    if any(keyword in query for keyword in policy_keywords):
        intent = "policy_question"
    else:
        intent = "general_question"

    return {
        "intent": intent
    }


def retrieve_and_answer(state: GraphState):
    query = state["query"]

    query_embedding = embedding_model.encode(
        [query]
    ).tolist()[0]

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=3
    )

    documents = results["documents"][0]
    ids = results["ids"][0]

    context = "\n\n".join(documents)

    if MOCK_LLM:

        top_chunk_snippet = documents[0][:200]

        answer = (
            f"Based on the retrieved context: "
            f"{top_chunk_snippet}"
        )

        return {
            "context": context,
            "sources": ids,
            "answer": answer,
            "confidence": 1.0
        }

    prompt = PROMPT_TEMPLATE.format(
        context=context,
        question=query
    )

    response = generate_real_llm_response(prompt)

    return {
        "context": context,
        "sources": response.sources,
        "answer": response.answer,
        "confidence": response.confidence
    }


def direct_answer(state: GraphState):

    if MOCK_LLM:
        answer = (
            "I can only answer questions about "
            "Zepto policies right now."
        )

        return {
            "answer": answer,
            "sources": [],
            "confidence": 1.0
        }
    
    return {
        "answer": (
            "I can only answer questions about "
            "Zepto policies right now."
        ),
        "sources": [],
        "confidence": 1.0
    }


def generate_real_llm_response(prompt: str) -> AskResponse:
    """
    Optional real LLM mode.

    Uses Groq's OpenAI-compatible API.
    MOCK_LLM=1 remains the default graded mode.
    """

    from openai import OpenAI

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY is required when MOCK_LLM=0."
        )

    client_llm = OpenAI(
        api_key=api_key,
        base_url="https://api.groq.com/openai/v1"
    )

    model_name = os.getenv(
        "GROQ_MODEL",
        "llama-3.1-8b-instant"
    )

    last_error = None

    # Initial attempt + 2 retries
    for attempt in range(3):

        current_prompt = prompt

        if attempt > 0:
            current_prompt += """

CORRECTION:
Your previous response failed schema validation.

Return ONLY valid JSON with exactly:
{
  "answer": "string",
  "sources": ["document_id"],
  "confidence": 0.0
}

Do not include markdown or extra text.
"""

        try:
            completion = client_llm.chat.completions.create(
                model=model_name,
                messages=[
                    {
                        "role": "user",
                        "content": current_prompt
                    }
                ],
                temperature=0
            )

            raw_output = completion.choices[0].message.content

            import json

            parsed = json.loads(raw_output)

            validated = AskResponse.model_validate(parsed)

            return validated

        except Exception as error:
            last_error = error

    raise ValueError(
        f"LLM response validation failed after 3 attempts: "
        f"{last_error}"
    )


def route_after_classification(state: GraphState):

    if state["intent"] == "policy_question":
        return "retrieve_and_answer"

    return "direct_answer"


builder = StateGraph(GraphState)

builder.add_node(
    "classify_intent",
    classify_intent
)

builder.add_node(
    "retrieve_and_answer",
    retrieve_and_answer
)

builder.add_node(
    "direct_answer",
    direct_answer
)

builder.add_edge(
    START,
    "classify_intent"
)

builder.add_conditional_edges(
    "classify_intent",
    route_after_classification,
    {
        "retrieve_and_answer": "retrieve_and_answer",
        "direct_answer": "direct_answer"
    }
)

builder.add_edge(
    "retrieve_and_answer",
    END
)

builder.add_edge(
    "direct_answer",
    END
)

graph = builder.compile()


def run_query(query: str) -> AskResponse:

    result = graph.invoke(
        {
            "query": query
        }
    )

    return AskResponse(
        answer=result["answer"],
        sources=result.get("sources", []),
        confidence=result.get("confidence", 1.0)
    )


if __name__ == "__main__":

    test_query = (
        "What is the delivery fee for an order "
        "below INR 149?"
    )

    response = run_query(test_query)

    print("\nResponse:")
    print(response.model_dump_json(indent=2))