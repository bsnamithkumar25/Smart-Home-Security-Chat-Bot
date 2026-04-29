"""
Intent Detector
Classifies user messages into intent categories and extracts
device/action information for command processing.
"""

from config import (
    COMMAND_KEYWORDS, ALERT_KEYWORDS, TROUBLESHOOT_KEYWORDS,
    GREETING_KEYWORDS, DEVICE_ALIASES
)

# Intent Types
INTENT_COMMAND = "COMMAND"
INTENT_QUERY = "QUERY"
INTENT_ALERT = "ALERT"
INTENT_TROUBLESHOOT = "TROUBLESHOOT"
INTENT_GREETING = "GREETING"
INTENT_OUT_OF_SCOPE = "OUT_OF_SCOPE"


def detect_intent(message):
    """
    Classify the user's message into an intent category.
    Priority: ALERT > COMMAND > TROUBLESHOOT > GREETING > QUERY
    """
    msg = message.lower().strip()
    if not msg:
        return INTENT_OUT_OF_SCOPE

    # ALERT — highest priority (safety first)
    for keyword in ALERT_KEYWORDS:
        if keyword in msg:
            return INTENT_ALERT

    # COMMAND — must have both a command keyword AND a device
    for keyword in COMMAND_KEYWORDS:
        if keyword in msg:
            if extract_device(msg):
                return INTENT_COMMAND

    # TROUBLESHOOT
    for keyword in TROUBLESHOOT_KEYWORDS:
        if keyword in msg:
            return INTENT_TROUBLESHOOT

    # GREETING — only if message is short
    words = msg.split()
    if len(words) <= 4:
        for keyword in GREETING_KEYWORDS:
            if keyword in words or msg.startswith(keyword):
                return INTENT_GREETING

    # Default to QUERY — let AI handle it
    return INTENT_QUERY


def extract_device(message):
    """
    Extract which device the user is referring to.
    Checks longer aliases first to avoid partial matches.
    """
    msg = message.lower().strip()

    # Sort by length (longest first) so "motion sensor" matches before "sensor"
    for alias in sorted(DEVICE_ALIASES.keys(), key=len, reverse=True):
        if alias in msg:
            return DEVICE_ALIASES[alias]

    return None


def extract_action(message):
    """
    Extract the desired action from the user's message.
    Returns tuple (device_key, new_value) or None.
    """
    msg = message.lower().strip()
    device = extract_device(msg)
    if not device:
        return None

    # Define action phrases — check OFF before ON to avoid "turn off" matching "on"
    off_phrases = ["turn off", "switch off", "deactivate", "disable", "disarm"]
    on_phrases = ["turn on", "switch on", "activate", "enable", "arm"]

    is_off = any(p in msg for p in off_phrases)
    is_on = any(p in msg for p in on_phrases)

    # Special handling for lock/unlock (check unlock BEFORE lock)
    has_unlock = any(w in msg for w in ["unlock", "open"])
    has_lock = any(w in msg for w in ["lock", "close", "secure"])

    # Determine action based on device type
    if device == "door_lock":
        if has_unlock or is_off:
            return ("door_lock", "unlocked")
        if has_lock or is_on:
            return ("door_lock", "locked")

    elif device == "alarm":
        if is_off or has_unlock or "disarm" in msg:
            return ("alarm", "off")
        if is_on or has_lock or "arm" in msg:
            return ("alarm", "on")

    elif device == "camera":
        if is_off:
            return ("camera", "inactive")
        if is_on:
            return ("camera", "active")

    elif device == "motion_sensor":
        if is_off:
            return ("motion_sensor", "idle")
        if is_on:
            return ("motion_sensor", "triggered")

    elif device == "lights":
        if is_off:
            return ("lights", "off")
        if is_on:
            return ("lights", "on")

    return None


def get_intent_label(intent):
    """Get a user-friendly label for the intent."""
    labels = {
        INTENT_COMMAND: "Command",
        INTENT_QUERY: "Query",
        INTENT_ALERT: "Alert",
        INTENT_TROUBLESHOOT: "Troubleshoot",
        INTENT_GREETING: "Greeting",
        INTENT_OUT_OF_SCOPE: "Out of Scope"
    }
    return labels.get(intent, "Unknown")
