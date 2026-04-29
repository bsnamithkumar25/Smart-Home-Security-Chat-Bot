"""
Smart Home State Manager
Manages the simulated smart home state for each user session.
"""

import copy
from datetime import datetime
from config import DEFAULT_HOME_STATE

# In-memory storage keyed by session_id
_sessions = {}


def _get_session(session_id):
    """Get or create a session. Single init point to avoid duplication."""
    if session_id not in _sessions:
        _sessions[session_id] = {
            "state": copy.deepcopy(DEFAULT_HOME_STATE),
            "history": []
        }
    return _sessions[session_id]


def get_state(session_id):
    """Get the current home state for a session."""
    return _get_session(session_id)["state"]


def get_history(session_id):
    """Get the conversation history for a session."""
    return _get_session(session_id)["history"]


def add_to_history(session_id, role, message):
    """Add a message to conversation history (keeps last 20)."""
    history = get_history(session_id)
    history.append({
        "role": role,
        "message": message,
        "timestamp": datetime.now().strftime("%H:%M:%S")
    })
    # Trim to last 20 messages
    if len(history) > 20:
        _sessions[session_id]["history"] = history[-20:]


def update_state(session_id, device, value):
    """
    Update a device state.
    Returns dict with: success, message, warning.
    """
    state = get_state(session_id)

    if device not in state or device == "event_log":
        return {
            "success": False,
            "message": f"Unknown device: {device}.",
            "warning": None
        }

    old_value = state[device]
    friendly_name = device.replace("_", " ").title()

    # Already in desired state
    if old_value == value:
        return {
            "success": True,
            "message": f"{friendly_name} is already {value}.",
            "warning": None
        }

    # Update
    state[device] = value
    log_event(session_id, f"{friendly_name}: {old_value} -> {value}")

    # Check for warnings
    warnings = check_vulnerabilities(session_id)
    return {
        "success": True,
        "message": f"Done! {friendly_name} is now **{value}**.",
        "warning": " ".join(warnings) if warnings else None
    }


def log_event(session_id, event):
    """Add an event to the event log."""
    state = get_state(session_id)
    timestamp = datetime.now().strftime("%I:%M %p")
    state["event_log"].insert(0, {"time": timestamp, "event": event})
    state["event_log"] = state["event_log"][:10]  # Keep last 10


def check_vulnerabilities(session_id):
    """Check for risky state combinations."""
    state = get_state(session_id)
    warnings = []

    door_open = state["door_lock"] == "unlocked"
    alarm_off = state["alarm"] == "off"
    camera_off = state["camera"] == "inactive"
    lights_off = state["lights"] == "off"

    if door_open and alarm_off:
        warnings.append("HIGH RISK: Door is unlocked and alarm is off.")

    if camera_off and state["motion_sensor"] == "idle":
        warnings.append("BLIND SPOT: Camera is off and motion sensor is idle.")

    if door_open and alarm_off and camera_off and lights_off:
        warnings.append("CRITICAL: All security systems are disabled!")

    return warnings


def get_state_summary(session_id):
    """Get a human-readable summary for AI context."""
    state = get_state(session_id)

    labels = {
        "door_lock": {"locked": "Locked", "unlocked": "Unlocked"},
        "alarm": {"on": "Armed", "off": "Disarmed"},
        "camera": {"active": "Active", "inactive": "Inactive"},
        "motion_sensor": {"idle": "Idle", "triggered": "TRIGGERED"},
        "lights": {"on": "On", "off": "Off"}
    }

    lines = ["Current Smart Home Status:"]
    for device, statuses in labels.items():
        current = state.get(device, "unknown")
        display = statuses.get(current, current)
        lines.append(f"  {device.replace('_', ' ').title()}: {display}")

    warnings = check_vulnerabilities(session_id)
    if warnings:
        lines.append("\nSecurity Warnings:")
        for w in warnings:
            lines.append(f"  - {w}")
    else:
        lines.append("\nNo security vulnerabilities detected.")

    return "\n".join(lines)


def reset_state(session_id):
    """Reset home state to defaults."""
    _sessions.pop(session_id, None)
    return {"success": True, "message": "Smart home system has been reset."}


def get_state_dict(session_id):
    """Get state as a clean dict for JSON response."""
    state = get_state(session_id)
    return {k: v for k, v in state.items() if k != "event_log"}
