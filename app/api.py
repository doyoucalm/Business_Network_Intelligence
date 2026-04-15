import hmac
import hashlib
from fastapi import APIRouter, Request, HTTPException, Header, Depends
from typing import Optional
from .config import settings
from .ai import chat_with_ai
from .whatsapp_utils import send_whatsapp_message, mirror_to_chatwoot

router = APIRouter()

# 1. SHA256 Signature Verification Utility
def verify_whatsapp_signature(payload: bytes, signature: str):
    """Verifies that the webhook payload is signed by Meta's App Secret."""
    if not settings.WHATSAPP_APP_SECRET:
        return True # Dev mode or secret not set
    
    expected_signature = hmac.new(
        settings.WHATSAPP_APP_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    # Meta signature is "sha256=<hash>"
    actual_hash = signature.replace("sha256=", "")
    return hmac.compare_digest(expected_signature, actual_hash)

# 2. Webhook Token Verification (GET)
@router.get("/webhook")
async def verify_webhook(request: Request):
    """Meta's handshake to verify the webhook URL."""
    params = request.query_params
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    if mode == "subscribe" and token == settings.WHATSAPP_VERIFY_TOKEN:
        print("WEBHOOK_VERIFIED")
        return int(challenge)
    
    raise HTTPException(status_code=403, detail="Verification failed")

# 3. Webhook Message Handling (POST)
@router.post("/webhook")
async def handle_whatsapp_event(
    request: Request,
    x_hub_signature_256: Optional[str] = Header(None)
):
    """Handles incoming WhatsApp messages from the Cloud API."""
    body = await request.body()
    
    # Security: Verify SHA256 signature
    if x_hub_signature_256 and not verify_whatsapp_signature(body, x_hub_signature_256):
        raise HTTPException(status_code=401, detail="Invalid signature")

    data = await request.json()
    
    # Extract message details (Note: Meta payload is deeply nested)
    try:
        entry = data.get("entry", [])[0]
        changes = entry.get("changes", [])[0]
        value = changes.get("value", {})
        messages = value.get("messages", [])
        
        if messages:
            message = messages[0]
            from_number = message.get("from")
            text_body = message.get("text", {}).get("body", "")
            
            # Sync with Chatwoot CRM
            await mirror_to_chatwoot(from_number, text_body, is_bot=False)

            # Trigger AI Orchestration (LangGraph)
            reply = await chat_with_ai([{"role": "user", "content": text_body}])
            
            # Send WhatsApp Response with anthropomorphic delay
            await send_whatsapp_message(from_number, reply)
            
            # Sync AI response with Chatwoot CRM
            await mirror_to_chatwoot(from_number, reply, is_bot=True)

    except Exception as e:
        print(f"Error processing webhook: {e}")
    
    return {"status": "ok"}

@router.get("/health")
def health_check():
    return {"status": "ok"}
