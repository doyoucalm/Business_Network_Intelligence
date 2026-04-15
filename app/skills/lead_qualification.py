from langchain_core.tools import tool

@tool
def qualify_lead(user_input: str, user_id: str):
    """
    Analyses the lead's input to determine if they are a high-value prospect.
    Extracts budget, authority, need, and timeline (BANT).
    """
    # In a real implementation, this would use an LLM or database lookup
    # to evaluate the lead's score and update the user's profile in the database.
    return {
        "score": 0.85, 
        "category": "High Intent", 
        "recommendation": "Handoff to human agent"
    }
