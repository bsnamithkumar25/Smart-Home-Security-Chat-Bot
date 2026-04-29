"""
Configuration for AI Smart Home Security Assistant.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ── API & App Settings ──────────────────────────────────────
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = "gemini-2.0-flash"
SECRET_KEY = os.getenv("SECRET_KEY", "smart-home-security-secret-key-2026")

# ── System Prompt ───────────────────────────────────────────
SYSTEM_PROMPT = """You are an AI Smart Home Security Assistant designed to help users monitor, manage, and improve home security systems.

Your responsibilities include:
- Answering questions about home security (cameras, locks, alarms, sensors, lights)
- Providing safety recommendations and best practices
- Responding to security alerts with appropriate urgency
- Explaining security concepts in simple terms
- Helping troubleshoot security devices

Behavior rules:
1. Always prioritize user safety above everything else.
2. Give clear, step-by-step suggestions when needed.
3. Be concise but informative — avoid walls of text.
4. If a situation sounds dangerous, respond with urgency and recommend contacting authorities.
5. Do NOT answer unrelated questions — politely redirect to security topics.
6. Use simple language — the user may not be tech-savvy.
7. When reporting status, use emojis for clarity.
8. If the user seems anxious or scared, be reassuring while still giving practical advice.

You have access to a simulated smart home system. The current state of the home will be provided as context. Use this information to give accurate, state-aware responses.

When the user describes a threatening situation, treat it as a real emergency and provide immediate, actionable advice.

IMPORTANT: You are ONLY a smart home security assistant. If asked about unrelated topics, respond with:
"I'm specialized in home security. For that question, please consult an appropriate resource. Is there anything security-related I can help with?"
"""

# ── Default Smart Home State ────────────────────────────────
DEFAULT_HOME_STATE = {
    "door_lock": "locked",
    "alarm": "off",
    "camera": "active",
    "motion_sensor": "idle",
    "lights": "on",
    "event_log": []
}

# ── Intent Keywords ─────────────────────────────────────────
ALERT_KEYWORDS = [
    "break in", "breaking in", "intruder", "burglar", "thief",
    "glass breaking", "someone outside", "suspicious person",
    "emergency", "danger", "threat", "attack", "robbery",
    "stalker", "forced entry", "someone at the door",
    "stranger outside", "break the window"
]

COMMAND_KEYWORDS = [
    "lock", "unlock", "turn on", "turn off", "activate",
    "deactivate", "arm", "disarm", "enable", "disable",
    "open", "close", "switch on", "switch off"
]

TROUBLESHOOT_KEYWORDS = [
    "not working", "offline", "broken", "error", "malfunction",
    "won't connect", "can't see", "no signal", "battery low",
    "stopped working", "glitch", "problem with"
]

GREETING_KEYWORDS = [
    "hi", "hello", "hey", "good morning", "good evening",
    "good afternoon", "howdy", "greetings"
]

# ── Device Aliases ──────────────────────────────────────────
DEVICE_ALIASES = {
    "front door": "door_lock",
    "back door": "door_lock",
    "door lock": "door_lock",
    "door": "door_lock",
    "doors": "door_lock",
    "security alarm": "alarm",
    "alarm": "alarm",
    "siren": "alarm",
    "camera": "camera",
    "cameras": "camera",
    "cctv": "camera",
    "cam": "camera",
    "surveillance": "camera",
    "motion sensor": "motion_sensor",
    "motion detector": "motion_sensor",
    "sensor": "motion_sensor",
    "sensors": "motion_sensor",
    "detector": "motion_sensor",
    "light": "lights",
    "lights": "lights",
    "lamp": "lights",
    "bulb": "lights"
}
