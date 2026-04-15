from langchain_core.tools import tool

@tool
def product_search(query: str):
    """
    Searches the official product knowledge base and FAQ to provide accurate specifications
    and prevent AI hallucinations.
    """
    # In a real implementation, this would use RAG or a vector database search.
    # For now, it returns a placeholder response.
    return {
        "result": f"Official information for: {query}",
        "source": "Mahardika Hub Catalog 2026"
    }
