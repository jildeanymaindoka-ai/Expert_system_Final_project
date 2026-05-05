// DOM Elements
const messageInput = document.getElementById('message-input');
const sendBtn = document.getElementById('send-btn');
const voiceBtn = document.getElementById('voice-btn');
const chatMessages = document.getElementById('chat-messages');
const typingIndicator = document.getElementById('typing-indicator');
const navItems = document.querySelectorAll('.nav-item');
const sections = document.querySelectorAll('.chat-section, .knowledge-section, .settings-section');
const darkModeToggle = document.getElementById('dark-mode-toggle');
const pdfOnlyToggle = document.getElementById('pdf-only-toggle');

// Init Modal Elements
const initModal = document.getElementById('init-modal');
const apiKeyInput = document.getElementById('api-key-input');
const initBtn = document.getElementById('init-btn');
const initStatus = document.getElementById('init-status');

// Global state
let isInitialized = false;

// Check initialization status on load
document.addEventListener('DOMContentLoaded', async () => {
    // Load dark mode preference
    const savedDarkMode = localStorage.getItem('darkMode');
    if (savedDarkMode === 'true' && darkModeToggle) {
        darkModeToggle.checked = true;
        document.body.classList.add('dark-mode');
    }
    
    await checkInitializationStatus();
    messageInput.focus();
    updateStatus('Ready', false);
});

// Check if system is initialized
async function checkInitializationStatus() {
    try {
        // For now, we'll assume it's not initialized and show the modal
        // In a real implementation, you'd check with the backend
        showInitModal();
    } catch (error) {
        console.error('Error checking init status:', error);
    }
}

// Show initialization modal
function showInitModal() {
    initModal.classList.add('show');
}

// Hide initialization modal
function hideInitModal() {
    initModal.classList.remove('show');
}

// Handle initialization
initBtn.addEventListener('click', async () => {
    const apiKey = apiKeyInput.value.trim();
    if (!apiKey) {
        showInitStatus('Please enter your API key', 'error');
        return;
    }

    showInitStatus('Initializing system...', 'processing');
    initBtn.disabled = true;
    initBtn.querySelector('.btn-text').textContent = 'Initializing...';
    initBtn.querySelector('.btn-spinner').style.display = 'block';

    try {
        const response = await fetch('/initialize', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ api_key: apiKey })
        });

        const data = await response.json();

        if (data.initialized) {
            showInitStatus(data.status, 'success');
            setTimeout(() => {
                hideInitModal();
                isInitialized = true;
                updateStatus('Ready', false);
            }, 2000);
        } else {
            showInitStatus(data.status, 'error');
        }
    } catch (error) {
        showInitStatus('Initialization failed. Please try again.', 'error');
        console.error('Init error:', error);
    } finally {
        initBtn.disabled = false;
        initBtn.querySelector('.btn-text').textContent = 'Initialize System';
        initBtn.querySelector('.btn-spinner').style.display = 'none';
    }
});

// Show initialization status
function showInitStatus(message, type) {
    initStatus.textContent = message;
    initStatus.className = `init-status ${type}`;
}

// Navigation
navItems.forEach(item => {
    item.addEventListener('click', (e) => {
        e.preventDefault();
        const targetSection = item.getAttribute('data-section');

        // Update active nav item
        navItems.forEach(nav => nav.classList.remove('active'));
        item.classList.add('active');

        // Show target section
        sections.forEach(section => {
            section.classList.remove('active');
        });
        document.getElementById(`${targetSection}-section`).classList.add('active');
    });
});

// Message Input Handling
messageInput.addEventListener('input', () => {
    sendBtn.disabled = messageInput.value.trim() === '' || !isInitialized;
});

messageInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

sendBtn.addEventListener('click', sendMessage);

// Voice Input (placeholder)
if (voiceBtn) {
    voiceBtn.addEventListener('click', () => {
        // Voice recognition would be implemented here
        alert('Voice input feature coming soon!');
    });
}

// Send Message Function
async function sendMessage() {
    if (!isInitialized) {
        showInitModal();
        return;
    }

    const message = messageInput.value.trim();
    if (!message) return;

    // Add user message
    addMessage(message, 'user');
    messageInput.value = '';
    sendBtn.disabled = true;

    // Show typing indicator
    showTypingIndicator();

    try {
        // Send message to backend
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                use_pdf_only: pdfOnlyToggle.checked
            })
        });

        const data = await response.json();

        // Hide typing indicator
        hideTypingIndicator();

        if (data.error) {
            addMessage(`Error: ${data.error}`, 'ai');
        } else {
            addMessage(data.response, 'ai');
        }
    } catch (error) {
        hideTypingIndicator();
        addMessage('Sorry, I encountered an error. Please try again.', 'ai');
        console.error('Chat error:', error);
    }
}

// Add Message to Chat
function addMessage(content, type) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}-message`;

    const avatar = type === 'user' ? '👤' : '🤖';
    const avatarClass = type === 'user' ? 'user-message' : 'ai-message';

    messageDiv.innerHTML = `
        <div class="message-avatar">${avatar}</div>
        <div class="message-content">
            <p>${content.replace(/\n/g, '</p><p>')}</p>
        </div>
    `;

    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Typing Indicator
function showTypingIndicator() {
    typingIndicator.style.display = 'flex';
    updateStatus('Processing', true);
}

function hideTypingIndicator() {
    typingIndicator.style.display = 'none';
    updateStatus('Ready', false);
}

// Status Indicator
function updateStatus(text, isProcessing) {
    const statusDot = document.querySelector('.status-dot');
    const statusText = document.querySelector('.status-text');

    if (statusDot && statusText) {
        statusText.textContent = text;
        statusDot.className = `status-dot ${isProcessing ? 'processing' : 'ready'}`;
    }
}

// Dark Mode Toggle
if (darkModeToggle) {
    darkModeToggle.addEventListener('change', () => {
        document.body.classList.toggle('dark-mode', darkModeToggle.checked);
        localStorage.setItem('darkMode', darkModeToggle.checked);
    });
}

// PDF Only Toggle
if (pdfOnlyToggle) {
    pdfOnlyToggle.addEventListener('change', () => {
        // This will be sent with the next message
        console.log('PDF only mode:', pdfOnlyToggle.checked);
    });
}

// Example chat history (would be loaded from backend)
const chatHistory = [
    { id: 1, title: 'University Policies', timestamp: '2024-01-15' },
    { id: 2, title: 'Course Registration', timestamp: '2024-01-14' },
    { id: 3, title: 'Campus Facilities', timestamp: '2024-01-13' }
];

function loadChatHistory() {
    const historyList = document.getElementById('chat-history-list');
    if (!historyList) return;

    historyList.innerHTML = '';

    chatHistory.forEach(chat => {
        const chatItem = document.createElement('div');
        chatItem.className = 'chat-history-item';
        chatItem.innerHTML = `
            <div class="chat-title">${chat.title}</div>
            <div class="chat-date">${chat.timestamp}</div>
        `;
        chatItem.addEventListener('click', () => loadChat(chat.id));
        historyList.appendChild(chatItem);
    });
}

function loadChat(chatId) {
    // Would load chat from backend
    console.log('Loading chat:', chatId);
}

// Load chat history on settings page
document.addEventListener('DOMContentLoaded', loadChatHistory);