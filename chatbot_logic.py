"""
Chatbot Logic
Orchestrates intent detection, state management, and AI response generation.
"""

from google import genai
from config import GEMINI_API_KEY, GEMINI_MODEL, SYSTEM_PROMPT
from intent_detector import (
    detect_intent, extract_action, get_intent_label,
    INTENT_COMMAND, INTENT_ALERT, INTENT_TROUBLESHOOT, INTENT_GREETING
)
from state_manager import (
    get_state, update_state, get_state_summary, get_state_dict,
    add_to_history, get_history, log_event
)

# Lazy-initialized Gemini client
_client = None


def _get_client():
    """Initialize Gemini client on first use."""
    global _client
    if _client is None:
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is not set! Add it to your .env file.")
        _client = genai.Client(api_key=GEMINI_API_KEY)
    return _client


def process_message(session_id, user_message):
    """
    Main pipeline: receive message -> detect intent -> process -> respond.
    Returns dict with: response, intent, state, warning.
    """
    add_to_history(session_id, "user", user_message)

    intent = detect_intent(user_message)
    response = ""
    warning = None

    # Route based on intent
    if intent == INTENT_GREETING:
        response = _handle_greeting(session_id)

    elif intent == INTENT_COMMAND:
        result = _handle_command(session_id, user_message)
        response = result["message"]
        warning = result.get("warning")

    elif intent == INTENT_ALERT:
        response = _handle_alert(session_id, user_message)

    elif intent == INTENT_TROUBLESHOOT:
        response = _handle_troubleshoot(session_id, user_message)

    else:  # QUERY or anything else -> let AI handle it
        response = _handle_query(session_id, user_message)

    add_to_history(session_id, "assistant", response)

    return {
        "response": response,
        "intent": get_intent_label(intent),
        "state": get_state_dict(session_id),
        "warning": warning
    }


# ── Intent Handlers ─────────────────────────────────────────

def _handle_greeting(session_id):
    """Return a welcome message with current status."""
    state = get_state(session_id)
    door = "locked" if state["door_lock"] == "locked" else "unlocked"
    alarm = "armed" if state["alarm"] == "on" else "disarmed"
    camera = state["camera"]

    return (
        f"Hello! I'm your **AI Smart Home Security Assistant**.\n\n"
        f"Quick status:\n"
        f"- Door: **{door}**\n"
        f"- Alarm: **{alarm}**\n"
        f"- Camera: **{camera}**\n\n"
        f"I can help you:\n"
        f"- Control your security devices\n"
        f"- Get safety recommendations\n"
        f"- Respond to emergencies\n"
        f"- Troubleshoot device issues\n\n"
        f"How can I help secure your home today?"
    )


def _handle_command(session_id, message):
    """Parse command, update state, return confirmation."""
    action = extract_action(message)

    if action is None:
        return {
            "message": (
                "I understood you want to control a device, but I couldn't "
                "determine the exact action. Try commands like:\n"
                "- \"Lock the door\"\n"
                "- \"Turn on the alarm\"\n"
                "- \"Activate camera\"\n"
                "- \"Turn off lights\""
            ),
            "warning": None
        }

    device, value = action
    return update_state(session_id, device, value)


def _handle_alert(session_id, message):
    """Handle emergency situations with urgent AI response."""
    log_event(session_id, f"ALERT: {message}")

    return _call_ai(
        session_id, message,
        extra=(
            "URGENT SITUATION. The user may be in danger. "
            "Give immediate, actionable safety steps. Be direct. "
            "Suggest calling emergency services (100/112) if appropriate. "
            "Start with 'SECURITY ALERT' to convey urgency."
        )
    )


def _handle_troubleshoot(session_id, message):
    """Handle device issues with step-by-step AI help."""
    return _call_ai(
        session_id, message,
        extra=(
            "The user has a device issue. Provide a clear, numbered "
            "step-by-step troubleshooting guide. Start with easy fixes first."
        )
    )


def _handle_query(session_id, message):
    """Handle general security queries with AI."""
    return _call_ai(session_id, message)


# ── AI Layer ────────────────────────────────────────────────

def _call_ai(session_id, user_message, extra=None):
    """Build prompt and call Gemini API."""
    state_context = get_state_summary(session_id)
    history = get_history(session_id)

    # Build the prompt
    parts = [SYSTEM_PROMPT]

    if extra:
        parts.append(f"\n[SPECIAL INSTRUCTION]\n{extra}")

    parts.append(f"\n[HOME STATE]\n{state_context}")

    # Add recent conversation (last 6 messages)
    if history:
        recent = history[-6:]
        conv = "\n[RECENT CONVERSATION]\n"
        for msg in recent:
            role = "User" if msg["role"] == "user" else "Assistant"
            conv += f"{role}: {msg['message']}\n"
        parts.append(conv)

    parts.append(f"\n[USER MESSAGE]\nUser: {user_message}\n\nAssistant:")

    prompt = "\n".join(parts)

    # Call Gemini
    try:
        client = _get_client()
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt
        )
        return response.text.strip()
    except Exception as e:
        error_msg = str(e)
        if "API_KEY" in error_msg.upper() or "401" in error_msg:
            return "API key error. Please check your Gemini API key in the .env file."
        elif "429" in error_msg or "RATE" in error_msg.upper():
            return "Rate limit reached. Please wait a moment and try again."
        else:
            return f"Sorry, I encountered an error. Please try again. ({error_msg[:80]})"
