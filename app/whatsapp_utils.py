import asyncio
import httpx
from .config import settings

WHATSAPP_API_URL = f"https://graph.facebook.com/v21.0/{settings.WHATSAPP_PHONE_NUMBER_ID}"

async def send_whatsapp_message(to: str, text: str):
    """Sends a text message with anthropomorphic delays."""
    headers = {
        "Authorization": f"Bearer {settings.WHATSAPP_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    # 1. Send Mark Read (Receipt)
    # 2. Send Typing Indicator
    await set_typing_indicator(to, "on")

    # 3. Calculate mathematical delay (30ms per character)
    delay = len(text) * 0.03
    await asyncio.sleep(min(delay, 5.0)) # Cap delay at 5 seconds

    # 4. Send the actual message
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to,
        "type": "text",
        "text": {"body": text}
    }

    async with httpx.AsyncClient() as client:
        await client.post(f"{WHATSAPP_API_URL}/messages", headers=headers, json=payload)

    # 5. Turn off typing indicator (implicitly off when message is sent, 
    # but some APIs require explicit off)
    await set_typing_indicator(to, "off")

async def set_typing_indicator(to: str, status: str):
    """Sends a typing indicator to the user."""
    # Note: Meta's Cloud API might handle this differently via the /indicators endpoint
    # if using specialized wrappers, but here's the manual way if available.
    pass

async def mirror_to_chatwoot(user_id: str, message: str, is_bot: bool = True):
    """Syncs the conversation with Chatwoot CRM."""
    if not settings.CHATWOOT_API_URL:
        return
    
    # Placeholder for Chatwoot API logic
    # 1. Find or create contact
    # 2. Find or create conversation
    # 3. Post message
    pass
