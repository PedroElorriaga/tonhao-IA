from src.modules.agent.rag.vector_store import get_client, get_embedding_function
from src.modules.agent.state import State

CATEGORY_TO_COLLECTION = {
    "technical support": "tech",
    "account": "tech",
    "billing": "billing",
    "hr": "hr_support",
    "other": "general",
}


class RetrieverNode:
    def __init__(self):
        self._client = get_client()
        self._ef = get_embedding_function()

    def retrieve(self, state: State) -> State:
        category = (state["extract_ticket_data"] or {}
                    ).get("category", "other").lower()
        collection_name = CATEGORY_TO_COLLECTION.get(category, "general")

        query = state["messages"][-1].content

        try:
            collection = self._client.get_or_create_collection(
                name=collection_name,
                embedding_function=self._ef,
            )
            results = collection.query(query_texts=[query], n_results=3)
            documents = results.get("documents", [[]])[0]
            retrieved_context = "\n\n---\n\n".join(
                documents) if documents else ""
        except Exception:
            retrieved_context = ""

        return {"retrieved_context": retrieved_context}
