/* ═══════════════════════════════════════════════════════════
   AI Smart Home Security Assistant — Chat Logic
   ═══════════════════════════════════════════════════════════ */

// ── Session ────────────────────────────────────────────────
const SESSION_ID = 'session-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9);
let isProcessing = false;

// ── DOM Elements ───────────────────────────────────────────
const chatMessages = document.getElementById('chat-messages');
const chatInput = document.getElementById('chat-input');
const btnSend = document.getElementById('btn-send');
const btnReset = document.getElementById('btn-reset');
const btnToggleSidebar = document.getElementById('btn-toggle-sidebar');
const sidebar = document.getElementById('sidebar');
const typingIndicator = document.getElementById('typing-indicator');
const alertPanel = document.getElementById('alert-panel');

// ── Init ───────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', function() {
    showWelcomeMessage();

    btnSend.addEventListener('click', sendMessage);
    chatInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
    btnReset.addEventListener('click', resetSystem);
    btnToggleSidebar.addEventListener('click', toggleSidebar);

    // Quick action buttons (event delegation)
    document.getElementById('quick-actions').addEventListener('click', function(e) {
        var btn = e.target.closest('.quick-btn');
        if (btn) {
            chatInput.value = btn.getAttribute('data-message');
            sendMessage();
        }
    });

    chatInput.focus();
});

// ── Welcome Message ────────────────────────────────────────
function showWelcomeMessage() {
    chatMessages.innerHTML = '<div class="welcome-card">' +
        '<span class="welcome-icon">🛡️</span>' +
        '<h2>Smart Home Security Assistant</h2>' +
        '<p>I monitor, manage, and protect your home. Ask me anything about security or give me a command.</p>' +
        '<div class="welcome-features">' +
            '<span class="welcome-feature">🔒 Lock Doors</span>' +
            '<span class="welcome-feature">📷 Control Cameras</span>' +
            '<span class="welcome-feature">🚨 Emergency Help</span>' +
            '<span class="welcome-feature">🔧 Troubleshoot</span>' +
        '</div>' +
    '</div>';
}

// ── Send Message ───────────────────────────────────────────
function sendMessage() {
    var message = chatInput.value.trim();
    if (!message || isProcessing) return;

    isProcessing = true;
    btnSend.disabled = true;
    appendMessage('user', message);
    chatInput.value = '';
    showTyping();

    fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: message, session_id: SESSION_ID })
    })
    .then(function(response) {
        if (!response.ok) throw new Error('Server error: ' + response.status);
        return response.json();
    })
    .then(function(data) {
        hideTyping();

        var isAlert = data.intent && data.intent === 'Alert';
        appendMessage('bot', data.response, isAlert);

        if (data.state) updateDashboard(data.state);
        if (data.warning) addAlert('warning', data.warning);
        if (isAlert) addAlert('danger', 'Security alert triggered');
    })
    .catch(function(error) {
        hideTyping();
        appendMessage('bot', 'Connection error. Please check if the server is running and try again.');
        console.error('Chat error:', error);
    })
    .finally(function() {
        isProcessing = false;
        btnSend.disabled = false;
        chatInput.focus();
    });
}

// ── Append Message ─────────────────────────────────────────
function appendMessage(role, text, isAlertResponse) {
    var messageDiv = document.createElement('div');
    messageDiv.className = 'message ' + role;

    var avatar = role === 'bot' ? '🛡️' : '👤';
    var time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    var formattedText = formatMessage(text || '');
    var alertClass = isAlertResponse ? ' alert-response' : '';

    messageDiv.innerHTML =
        '<div class="message-avatar">' + avatar + '</div>' +
        '<div>' +
            '<div class="message-bubble' + alertClass + '">' + formattedText + '</div>' +
            '<div class="message-time">' + time + '</div>' +
        '</div>';

    chatMessages.appendChild(messageDiv);
    scrollToBottom();
}

// ── Format Message (simple & safe) ─────────────────────────
function formatMessage(text) {
    if (!text) return '';

    // Escape HTML
    var div = document.createElement('div');
    div.textContent = text;
    var escaped = div.innerHTML;

    // Bold: **text**
    escaped = escaped.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

    // Line breaks
    escaped = escaped.replace(/\n/g, '<br>');

    // Simple bullet points: lines starting with - or *
    escaped = escaped.replace(/(?:^|<br>)[-*]\s(.*?)(?=<br>|$)/g, function(match, content) {
        return '<br><span style="padding-left:16px">• ' + content + '</span>';
    });

    // Numbered lists: lines starting with digits
    escaped = escaped.replace(/(?:^|<br>)(\d+)\.\s(.*?)(?=<br>|$)/g, function(match, num, content) {
        return '<br><span style="padding-left:16px">' + num + '. ' + content + '</span>';
    });

    return escaped;
}

// ── Typing Indicator ───────────────────────────────────────
function showTyping() {
    typingIndicator.classList.remove('hidden');
    scrollToBottom();
}

function hideTyping() {
    typingIndicator.classList.add('hidden');
}

// ── Update Dashboard ───────────────────────────────────────
function updateDashboard(state) {
    var statusMap = {
        door_lock: { locked: 'Locked', unlocked: 'Unlocked' },
        alarm: { on: 'Armed', off: 'Disarmed' },
        camera: { active: 'Active', inactive: 'Inactive' },
        motion_sensor: { idle: 'Idle', triggered: 'Triggered' },
        lights: { on: 'On', off: 'Off' }
    };

    for (var device in state) {
        if (!state.hasOwnProperty(device) || !statusMap[device]) continue;

        var value = state[device];
        var statusEl = document.getElementById('status-' + device);
        var cardEl = document.getElementById('device-' + device);

        if (!statusEl) continue;

        var displayText = statusMap[device][value] || value;
        var oldText = statusEl.textContent;

        statusEl.textContent = displayText;
        statusEl.className = 'device-status ' + value;

        // Flash animation if value changed
        if (oldText !== displayText && cardEl) {
            cardEl.classList.remove('highlight-update');
            void cardEl.offsetWidth; // Force reflow
            cardEl.classList.add('highlight-update');

            var name = device.replace(/_/g, ' ').replace(/\b\w/g, function(l) { return l.toUpperCase(); });
            addAlert('success', name + ' → ' + displayText);
        }
    }
}

// ── Alert Panel ────────────────────────────────────────────
function addAlert(type, text) {
    var time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    var alertDiv = document.createElement('div');
    alertDiv.className = 'alert-item ' + type;
    alertDiv.innerHTML =
        '<span class="alert-time">' + time + '</span>' +
        '<span class="alert-text">' + text + '</span>';

    alertPanel.insertBefore(alertDiv, alertPanel.firstChild);

    // Keep max 8
    while (alertPanel.children.length > 8) {
        alertPanel.removeChild(alertPanel.lastChild);
    }
}

// ── Reset System ───────────────────────────────────────────
function resetSystem() {
    fetch('/reset', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: SESSION_ID })
    })
    .then(function(response) {
        if (!response.ok) return;

        updateDashboard({
            door_lock: 'locked', alarm: 'off', camera: 'active',
            motion_sensor: 'idle', lights: 'on'
        });

        alertPanel.innerHTML =
            '<div class="alert-item info">' +
                '<span class="alert-time">Now</span>' +
                '<span class="alert-text">System reset. All nominal.</span>' +
            '</div>';

        showWelcomeMessage();
    })
    .catch(function(error) {
        console.error('Reset error:', error);
    });
}

// ── Mobile Sidebar ─────────────────────────────────────────
function toggleSidebar() {
    sidebar.classList.toggle('open');

    var backdrop = document.querySelector('.sidebar-backdrop');
    if (!backdrop) {
        backdrop = document.createElement('div');
        backdrop.className = 'sidebar-backdrop';
        backdrop.addEventListener('click', function() {
            sidebar.classList.remove('open');
            backdrop.classList.remove('active');
        });
        document.body.appendChild(backdrop);
    }
    backdrop.classList.toggle('active');
}

// ── Auto-scroll ────────────────────────────────────────────
function scrollToBottom() {
    requestAnimationFrame(function() {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    });
}
