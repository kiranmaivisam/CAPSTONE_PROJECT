# API Example Transcripts

The following examples were tested locally with the default mock mode (`MOCK_LLM=1`).

## Example 1 — Policy Retrieval Question

### Request

```json
{
  "query": "What is the delivery fee for orders below INR 149?"
}

{
  "answer": "Based on the retrieved context: Zepto delivers grocery and household essentials to serviceable pin codes within 10 to 30 minutes of order confirmation, depending on the customer's delivery zone and current order volume. Standard del",
  "sources": [
    "doc_01",
    "doc_05",
    "doc_03"
  ],
  "confidence": 1
}

{
  "query": "Can you tell me a joke?"
}

