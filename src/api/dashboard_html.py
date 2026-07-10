"""
Dashboard HTML template source for the browserAPI Gateway.
Presents a clean, GitHub Dark-themed interface.
Strips all neon/fancy effects. Strictly adheres to the no-emoji rule.
"""

DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>browserAPI Gateway Control Panel</title>
    <style>
        :root {
            --bg-color: #0d1117;
            --panel-bg: #161b22;
            --panel-header: #21262d;
            --border-color: #30363d;
            --text-color: #c9d1d9;
            --text-muted: #8b949e;
            --accent-blue: #58a6ff;
            --accent-blue-hover: #1f6feb;
            --btn-green: #238636;
            --btn-green-hover: #2ea44f;
            --btn-secondary: #21262d;
            --btn-secondary-hover: #30363d;
            --status-green: #3fb950;
            --status-red: #f85149;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            background-color: var(--bg-color);
            color: var(--text-color);
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
            padding: 40px 20px;
            line-height: 1.5;
        }

        .container {
            max-width: 1080px;
            margin: 0 auto;
        }

        /* Header Style */
        header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 16px;
            margin-bottom: 24px;
        }

        .logo-title {
            display: flex;
            flex-direction: column;
        }

        .logo-title h1 {
            font-size: 1.5rem;
            font-weight: 600;
            color: var(--text-color);
        }

        .logo-title span {
            font-size: 0.85rem;
            color: var(--text-muted);
            margin-top: 2px;
        }

        .health-status {
            display: flex;
            align-items: center;
            background-color: var(--panel-bg);
            border: 1px solid var(--border-color);
            border-radius: 6px;
            padding: 6px 12px;
            font-size: 0.85rem;
        }

        .status-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background-color: var(--status-green);
            margin-right: 8px;
        }

        .status-dot.unhealthy {
            background-color: var(--status-red);
        }

        /* Dashboard Grid Layout */
        .grid {
            display: grid;
            grid-template-columns: 1fr 2fr;
            gap: 20px;
        }

        @media (max-width: 768px) {
            .grid {
                grid-template-columns: 1fr;
            }
        }

        /* Card panels */
        .card {
            background-color: var(--panel-bg);
            border: 1px solid var(--border-color);
            border-radius: 6px;
            overflow: hidden;
            display: flex;
            flex-direction: column;
        }

        .card-header {
            background-color: var(--panel-header);
            border-bottom: 1px solid var(--border-color);
            padding: 12px 16px;
            font-weight: 600;
            color: var(--text-color);
            font-size: 0.9rem;
        }

        .card-body {
            padding: 16px;
            flex-grow: 1;
        }

        /* Info Item Rows */
        .info-group {
            margin-bottom: 12px;
            border-bottom: 1px solid rgba(240, 240, 240, 0.05);
            padding-bottom: 10px;
        }

        .info-group:last-child {
            margin-bottom: 0;
            border-bottom: none;
            padding-bottom: 0;
        }

        .info-label {
            font-size: 0.75rem;
            color: var(--text-muted);
            margin-bottom: 2px;
        }

        .info-value {
            font-size: 0.9rem;
            font-weight: 500;
        }

        .info-value.code {
            font-family: ui-monospace, SFMono-Regular, SF Mono, Menlo, Consolas, Liberation Mono, monospace;
            background-color: #1c2128;
            padding: 2px 6px;
            border-radius: 4px;
            border: 1px solid var(--border-color);
            display: inline-block;
            font-size: 0.8rem;
        }

        /* Button styles */
        .btn {
            color: #ffffff;
            font-weight: 500;
            border: 1px solid rgba(240, 240, 240, 0.1);
            padding: 8px 14px;
            border-radius: 6px;
            cursor: pointer;
            width: 100%;
            transition: background-color 0.15s ease;
            text-align: center;
            font-size: 0.85rem;
        }

        .btn-green {
            background-color: var(--btn-green);
            border-color: rgba(240, 240, 240, 0.1);
        }

        .btn-green:hover {
            background-color: var(--btn-green-hover);
        }

        .btn-secondary {
            background-color: var(--btn-secondary);
            border-color: var(--border-color);
            color: var(--text-color);
            margin-top: 8px;
        }

        .btn-secondary:hover {
            background-color: var(--btn-secondary-hover);
        }

        .btn:disabled {
            background-color: var(--btn-secondary);
            color: var(--text-muted);
            cursor: not-allowed;
            border-color: var(--border-color);
        }

        /* Playground Chat Panel */
        .chat-container {
            display: flex;
            flex-direction: column;
            height: 480px;
        }

        .chat-history {
            flex-grow: 1;
            overflow-y: auto;
            border: 1px solid var(--border-color);
            background-color: #0d1117;
            border-radius: 6px;
            padding: 16px;
            margin-bottom: 12px;
            font-family: ui-monospace, SFMono-Regular, SF Mono, Menlo, Consolas, Liberation Mono, monospace;
            font-size: 0.85rem;
        }

        .chat-msg {
            margin-bottom: 12px;
            word-wrap: break-word;
            white-space: pre-wrap;
        }

        .chat-msg.user {
            color: var(--accent-blue);
        }

        .chat-msg.assistant {
            color: var(--text-color);
            border-left: 2px solid #57606a;
            padding-left: 10px;
        }

        .chat-msg.system {
            color: var(--text-muted);
            font-style: italic;
        }

        .chat-input-row {
            display: grid;
            grid-template-columns: 140px 1fr 80px;
            gap: 8px;
        }

        select, input[type="text"] {
            background-color: #0d1117;
            border: 1px solid var(--border-color);
            color: var(--text-color);
            padding: 8px 12px;
            border-radius: 6px;
            outline: none;
            font-size: 0.85rem;
        }

        select:focus, input[type="text"]:focus {
            border-color: var(--accent-blue);
        }

        .btn-blue {
            background-color: var(--accent-blue-hover);
            border-color: rgba(240, 240, 240, 0.1);
        }

        .btn-blue:hover {
            background-color: var(--accent-blue);
        }

        /* Footer links */
        footer {
            margin-top: 40px;
            text-align: center;
            font-size: 0.8rem;
            color: var(--text-muted);
            border-top: 1px solid var(--border-color);
            padding-top: 20px;
        }

        footer a {
            color: var(--accent-blue);
            text-decoration: none;
            font-weight: 500;
        }

        footer a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div class="logo-title">
                <h1>browserAPI Control Panel</h1>
                <span>Unofficial Google Gemini Local API Gateway dashboard</span>
            </div>
            <div class="health-status">
                <div id="statusDot" class="status-dot"></div>
                <span id="statusText">Verifying Session...</span>
            </div>
        </header>

        <div class="grid">
            <!-- Left Panel: Status & Actions -->
            <div class="card">
                <div class="card-header">Gateway Status</div>
                <div class="card-body">
                    <div class="info-group">
                        <div class="info-label">Active Browser</div>
                        <div id="cfgBrowser" class="info-value">Loading...</div>
                    </div>
                    <div class="info-group">
                        <div class="info-label">API Base Host</div>
                        <div id="cfgHost" class="info-value code">Loading...</div>
                    </div>
                    <div class="info-group">
                        <div class="info-label">Default Model</div>
                        <div id="cfgDefaultModel" class="info-value code">Loading...</div>
                    </div>
                    <div class="info-group">
                        <div class="info-label">Strong Model</div>
                        <div id="cfgStrongModel" class="info-value code">Loading...</div>
                    </div>
                    <div class="info-group">
                        <div class="info-label">Weak Model</div>
                        <div id="cfgWeakModel" class="info-value code">Loading...</div>
                    </div>
                    <div class="info-group" style="margin-bottom: 20px;">
                        <div class="info-label">Sync Interval</div>
                        <div id="cfgSync" class="info-value">Loading...</div>
                    </div>

                    <button id="btnSync" class="btn btn-green">Force Sync Cookies</button>
                    <button id="btnTest" class="btn btn-secondary">Verify Session Health</button>
                </div>
            </div>

            <!-- Right Panel: Interactive Playground -->
            <div class="card">
                <div class="card-header">API Chat Playground</div>
                <div class="card-body">
                    <div class="chat-container">
                        <div id="chatHistory" class="chat-history">
                            <div class="chat-msg system">[System] Connection established. Chat Playground is ready.</div>
                        </div>
                        <div class="chat-input-row">
                            <select id="chatModel">
                                <option value="gemini-2.0-flash-lite">Weak (Lite)</option>
                                <option value="gemini-2.0-flash">Default (Flash)</option>
                                <option value="gemini-1.5-pro">Strong (Pro)</option>
                            </select>
                            <input type="text" id="chatInput" placeholder="Type a message to Gemini..." autocomplete="off">
                            <button id="btnSend" class="btn btn-blue">Send</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <footer>
            <span>For educational purposes only. Built by <a href="https://github.com/muhammetozmen" target="_blank">Muhammet OZMEN</a>.</span>
        </footer>
    </div>

    <script>
        // DOM Elements
        const statusDot = document.getElementById('statusDot');
        const statusText = document.getElementById('statusText');
        const cfgBrowser = document.getElementById('cfgBrowser');
        const cfgHost = document.getElementById('cfgHost');
        const cfgDefaultModel = document.getElementById('cfgDefaultModel');
        const cfgStrongModel = document.getElementById('cfgStrongModel');
        const cfgWeakModel = document.getElementById('cfgWeakModel');
        const cfgSync = document.getElementById('cfgSync');
        const btnSync = document.getElementById('btnSync');
        const btnTest = document.getElementById('btnTest');

        const chatHistory = document.getElementById('chatHistory');
        const chatInput = document.getElementById('chatInput');
        const chatModel = document.getElementById('chatModel');
        const btnSend = document.getElementById('btnSend');

        // Append log helper
        function addLog(sender, message, isUser = false, isSystem = false) {
            const msgDiv = document.createElement('div');
            msgDiv.classList.add('chat-msg');
            if (isUser) {
                msgDiv.classList.add('user');
                msgDiv.textContent = `[User] ${message}`;
            } else if (isSystem) {
                msgDiv.classList.add('system');
                msgDiv.textContent = `[System] ${message}`;
            } else {
                msgDiv.classList.add('assistant');
                msgDiv.textContent = `[Gemini] ${message}`;
            }
            chatHistory.appendChild(msgDiv);
            chatHistory.scrollTop = chatHistory.scrollHeight;
        }

        // Fetch Server configurations
        async function loadConfig() {
            try {
                const response = await fetch('/api/status');
                if (!response.ok) throw new Error('Failed to load status');
                const data = await response.json();

                cfgBrowser.textContent = data.default_browser ? data.default_browser.toUpperCase() : 'Not Set';
                cfgHost.textContent = `http://${data.host}:${data.port}`;
                cfgDefaultModel.textContent = data.default_model;
                cfgStrongModel.textContent = data.strong_model;
                cfgWeakModel.textContent = data.weak_model;
                cfgSync.textContent = `${data.cookie_update} seconds`;
            } catch (err) {
                console.error('Error fetching config:', err);
            }
        }

        // Health check status
        async function runHealthCheck() {
            try {
                const response = await fetch('/health');
                const data = await response.json();
                if (data.status === 'healthy') {
                    statusDot.className = 'status-dot';
                    statusText.textContent = 'Session Healthy';
                } else {
                    statusDot.className = 'status-dot unhealthy';
                    statusText.textContent = 'Session Disconnected';
                }
            } catch (err) {
                statusDot.className = 'status-dot unhealthy';
                statusText.textContent = 'Server Offline';
            }
        }

        // Actions
        btnTest.addEventListener('click', async () => {
            btnTest.disabled = true;
            addLog(null, 'Verifying active browser session health...', false, true);
            await runHealthCheck();
            addLog(null, `Session health verification check: ${statusText.textContent}`, false, true);
            btnTest.disabled = false;
        });

        btnSync.addEventListener('click', async () => {
            btnSync.disabled = true;
            addLog(null, 'Triggering manual browser cookie synchronization...', false, true);
            try {
                const response = await fetch('/api/sync', { method: 'POST' });
                const data = await response.json();
                if (data.status === 'success' && data.session_healthy) {
                    addLog(null, 'Manual synchronization succeeded. Session is healthy.', false, true);
                } else {
                    addLog(null, 'Manual synchronization completed. Warning: session verification failed.', false, true);
                }
                await runHealthCheck();
            } catch (err) {
                addLog(null, `Sync failed: ${err.message}`, false, true);
            }
            btnSync.disabled = false;
        });

        // Chat playground query execution
        async function sendPlaygroundPrompt() {
            const prompt = chatInput.value.trim();
            if (!prompt) return;

            const model = chatModel.value;
            chatInput.value = '';
            chatInput.disabled = true;
            btnSend.disabled = true;

            addLog('User', prompt, true);

            try {
                const response = await fetch('/v1/chat/completions', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        model: model,
                        messages: [{ role: 'user', content: prompt }]
                    })
                });

                if (!response.ok) {
                    const errData = await response.json();
                    throw new Error(errData.detail || 'Query failure');
                }

                const data = await response.json();
                const reply = data.choices[0].message.content;
                addLog('Gemini', reply, false);
            } catch (err) {
                addLog(null, `Error generating completion: ${err.message}`, false, true);
            } finally {
                chatInput.disabled = false;
                btnSend.disabled = false;
                chatInput.focus();
            }
        }

        btnSend.addEventListener('click', sendPlaygroundPrompt);
        chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') sendPlaygroundPrompt();
        });

        // Init
        loadConfig();
        runHealthCheck();
    </script>
</body>
</html>
"""
