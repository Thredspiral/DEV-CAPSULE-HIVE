#!/usr/bin/env python3
"""
HybridMind Web Demo Interface

A simple web interface to demonstrate HybridMind capabilities through a browser.
"""

import sys
import logging
import json
import time
from pathlib import Path
from typing import Dict, Any
import asyncio
from datetime import datetime

# Add the hybridmind package to the path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
    from fastapi.responses import HTMLResponse, JSONResponse
    from fastapi.staticfiles import StaticFiles
    from fastapi.templating import Jinja2Templates
    import uvicorn
except ImportError:
    print("FastAPI not available. Installing required packages...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "fastapi", "uvicorn", "jinja2", "python-multipart"])
    from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
    from fastapi.responses import HTMLResponse, JSONResponse
    from fastapi.staticfiles import StaticFiles
    from fastapi.templating import Jinja2Templates
    import uvicorn

from hybridmind import HybridMind
from hybridmind.fusion.symbolic_neural_fusion import FusionMode

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="HybridMind Web Demo",
    description="Interactive web interface for HybridMind Super AI Architecture",
    version="1.0.0"
)

# Initialize HybridMind
try:
    mind_config = {
        'enable_safety': True,
        'enable_learning': False,
        'enable_self_extension': True,
        'neural_config': {'auto_initialize': False},
        'log_level': 'INFO'
    }
    mind = HybridMind(mind_config)
    logger.info("HybridMind initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize HybridMind: {e}")
    mind = None

# Store active WebSocket connections
active_connections: list = []

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                # Remove broken connections
                self.active_connections.remove(connection)

manager = ConnectionManager()

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home page with HybridMind interface."""
    
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>HybridMind Super AI Demo</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 0;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: #333;
                min-height: 100vh;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
            }
            .header {
                text-align: center;
                color: white;
                margin-bottom: 30px;
            }
            .header h1 {
                font-size: 3em;
                margin: 0;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            }
            .header p {
                font-size: 1.2em;
                margin: 10px 0;
                opacity: 0.9;
            }
            .main-panel {
                background: white;
                border-radius: 15px;
                padding: 30px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                margin-bottom: 20px;
            }
            .input-section {
                margin-bottom: 20px;
            }
            .input-group {
                margin-bottom: 15px;
            }
            label {
                display: block;
                font-weight: bold;
                margin-bottom: 5px;
                color: #555;
            }
            input, textarea, select {
                width: 100%;
                padding: 12px;
                border: 2px solid #ddd;
                border-radius: 8px;
                font-size: 16px;
                transition: border-color 0.3s;
            }
            input:focus, textarea:focus, select:focus {
                outline: none;
                border-color: #667eea;
            }
            textarea {
                height: 120px;
                resize: vertical;
            }
            .button-group {
                display: flex;
                gap: 10px;
                flex-wrap: wrap;
                margin-bottom: 20px;
            }
            button {
                padding: 12px 20px;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                cursor: pointer;
                transition: all 0.3s;
                flex: 1;
                min-width: 120px;
            }
            .btn-primary {
                background: linear-gradient(45deg, #667eea, #764ba2);
                color: white;
            }
            .btn-primary:hover {
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(0,0,0,0.2);
            }
            .btn-secondary {
                background: #f8f9fa;
                color: #333;
                border: 2px solid #ddd;
            }
            .btn-secondary:hover {
                background: #e9ecef;
            }
            .result-panel {
                background: #f8f9fa;
                border-radius: 10px;
                padding: 20px;
                margin-top: 20px;
                border-left: 5px solid #667eea;
            }
            .result-header {
                font-weight: bold;
                color: #667eea;
                margin-bottom: 10px;
                font-size: 18px;
            }
            .status-indicator {
                display: inline-block;
                padding: 4px 8px;
                border-radius: 12px;
                font-size: 12px;
                font-weight: bold;
                margin-right: 10px;
            }
            .status-success {
                background: #d4edda;
                color: #155724;
            }
            .status-error {
                background: #f8d7da;
                color: #721c24;
            }
            .status-warning {
                background: #fff3cd;
                color: #856404;
            }
            .loading {
                display: none;
                text-align: center;
                color: #667eea;
                margin: 20px 0;
            }
            .loading.show {
                display: block;
            }
            .spinner {
                display: inline-block;
                width: 20px;
                height: 20px;
                border: 3px solid #f3f3f3;
                border-top: 3px solid #667eea;
                border-radius: 50%;
                animation: spin 1s linear infinite;
                margin-right: 10px;
            }
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            .stats-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
                margin-bottom: 20px;
            }
            .stat-card {
                background: white;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                text-align: center;
                border-top: 4px solid #667eea;
            }
            .stat-value {
                font-size: 2em;
                font-weight: bold;
                color: #667eea;
                margin-bottom: 5px;
            }
            .stat-label {
                color: #666;
                font-size: 0.9em;
            }
            .examples {
                background: white;
                border-radius: 15px;
                padding: 20px;
                margin-top: 20px;
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            }
            .example-item {
                padding: 10px;
                margin: 5px 0;
                background: #f8f9fa;
                border-radius: 5px;
                cursor: pointer;
                transition: background-color 0.3s;
            }
            .example-item:hover {
                background: #e9ecef;
            }
            @media (max-width: 768px) {
                .container {
                    padding: 10px;
                }
                .header h1 {
                    font-size: 2em;
                }
                .button-group {
                    flex-direction: column;
                }
                button {
                    flex: none;
                }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🧠 HybridMind</h1>
                <p>Super AI Architecture Demo</p>
                <p>Symbolic Reasoning • Neural Processing • Fusion Intelligence • Self-Extension • Safety Oversight</p>
            </div>

            <div class="main-panel">
                <div class="input-section">
                    <div class="input-group">
                        <label for="query">Enter your query or request:</label>
                        <textarea id="query" placeholder="Ask me anything! Try: 'What are the implications of AI for society?' or 'Generate a function to calculate fibonacci numbers'"></textarea>
                    </div>
                    
                    <div class="input-group">
                        <label for="processing-mode">Processing Mode:</label>
                        <select id="processing-mode">
                            <option value="AUTO">🤖 Auto (Recommended)</option>
                            <option value="SYMBOLIC_ONLY">🧮 Symbolic Reasoning</option>
                            <option value="NEURAL_ONLY">🧠 Neural Processing</option>
                            <option value="FUSION">🔄 Fusion Mode</option>
                        </select>
                    </div>
                </div>

                <div class="button-group">
                    <button class="btn-primary" onclick="processQuery()">🚀 Process Query</button>
                    <button class="btn-secondary" onclick="getSystemStatus()">📊 System Status</button>
                    <button class="btn-secondary" onclick="generateCapability()">🔧 Self-Extension</button>
                    <button class="btn-secondary" onclick="clearResults()">🗑️ Clear</button>
                </div>

                <div class="loading" id="loading">
                    <div class="spinner"></div>
                    Processing your request...
                </div>

                <div id="results"></div>
            </div>

            <div class="examples">
                <h3>💡 Try These Examples:</h3>
                <div class="example-item" onclick="setQuery('If Socrates is human and all humans are mortal, what can we conclude?')">
                    🧮 Logic: "If Socrates is human and all humans are mortal, what can we conclude?"
                </div>
                <div class="example-item" onclick="setQuery('Analyze the sentiment and emotions in this text: I am feeling great today!')">
                    🧠 Neural: "Analyze the sentiment and emotions in this text: I am feeling great today!"
                </div>
                <div class="example-item" onclick="setQuery('What are the ethical implications of artificial general intelligence?')">
                    🔄 Fusion: "What are the ethical implications of artificial general intelligence?"
                </div>
                <div class="example-item" onclick="setQuery('Create a utility function that validates email addresses')">
                    🔧 Extension: "Create a utility function that validates email addresses"
                </div>
            </div>
        </div>

        <script>
            function setQuery(text) {
                document.getElementById('query').value = text;
            }

            function showLoading(show = true) {
                const loading = document.getElementById('loading');
                if (show) {
                    loading.classList.add('show');
                } else {
                    loading.classList.remove('show');
                }
            }

            function displayResult(title, content, status = 'success') {
                const results = document.getElementById('results');
                const statusClass = `status-${status}`;
                const statusText = status.charAt(0).toUpperCase() + status.slice(1);
                
                const resultHTML = `
                    <div class="result-panel">
                        <div class="result-header">
                            <span class="status-indicator ${statusClass}">${statusText}</span>
                            ${title}
                        </div>
                        <div>${content}</div>
                    </div>
                `;
                
                results.innerHTML = resultHTML + results.innerHTML;
            }

            async function processQuery() {
                const query = document.getElementById('query').value.trim();
                const mode = document.getElementById('processing-mode').value;
                
                if (!query) {
                    alert('Please enter a query');
                    return;
                }

                showLoading(true);
                
                try {
                    const response = await fetch('/process', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            query: query,
                            mode: mode
                        })
                    });

                    const result = await response.json();
                    
                    if (result.success) {
                        const content = `
                            <p><strong>Query:</strong> ${query}</p>
                            <p><strong>Mode:</strong> ${result.processing_mode}</p>
                            <p><strong>Confidence:</strong> ${(result.confidence * 100).toFixed(1)}%</p>
                            <p><strong>Processing Time:</strong> ${result.processing_time.toFixed(3)}s</p>
                            <p><strong>Result:</strong> ${result.explanation}</p>
                        `;
                        displayResult('✅ Processing Complete', content, 'success');
                    } else {
                        const content = `
                            <p><strong>Query:</strong> ${query}</p>
                            <p><strong>Error:</strong> ${result.explanation}</p>
                            ${result.errors ? `<p><strong>Details:</strong> ${result.errors.join(', ')}</p>` : ''}
                        `;
                        displayResult('❌ Processing Failed', content, 'error');
                    }
                } catch (error) {
                    displayResult('❌ Request Failed', `Error: ${error.message}`, 'error');
                } finally {
                    showLoading(false);
                }
            }

            async function getSystemStatus() {
                showLoading(true);
                
                try {
                    const response = await fetch('/status');
                    const status = await response.json();
                    
                    const stats = status.statistics;
                    const components = status.components;
                    
                    const content = `
                        <div class="stats-grid">
                            <div class="stat-card">
                                <div class="stat-value">${stats.total_requests}</div>
                                <div class="stat-label">Total Requests</div>
                            </div>
                            <div class="stat-card">
                                <div class="stat-value">${(stats.successful_requests / Math.max(stats.total_requests, 1) * 100).toFixed(1)}%</div>
                                <div class="stat-label">Success Rate</div>
                            </div>
                            <div class="stat-card">
                                <div class="stat-value">${stats.average_processing_time.toFixed(3)}s</div>
                                <div class="stat-label">Avg Processing Time</div>
                            </div>
                            <div class="stat-card">
                                <div class="stat-value">${stats.capabilities_learned}</div>
                                <div class="stat-label">Capabilities Learned</div>
                            </div>
                        </div>
                        <p><strong>System State:</strong> ${status.state}</p>
                        <p><strong>Uptime:</strong> ${status.uptime_seconds.toFixed(0)} seconds</p>
                        <p><strong>Components:</strong></p>
                        <ul>
                            <li>Symbolic Engine: ${components.symbolic_engine ? '✅' : '❌'}</li>
                            <li>Neural Engine: ${components.neural_engine ? '✅' : '❌'}</li>
                            <li>Fusion System: ${components.fusion_system ? '✅' : '❌'}</li>
                            <li>Safety Oversight: ${components.safety_oversight ? '✅' : '❌'}</li>
                        </ul>
                    `;
                    
                    displayResult('📊 System Status', content, 'success');
                } catch (error) {
                    displayResult('❌ Status Request Failed', `Error: ${error.message}`, 'error');
                } finally {
                    showLoading(false);
                }
            }

            async function generateCapability() {
                const specification = prompt('Enter capability specification (e.g., "Create a text summarizer"):');
                if (!specification) return;

                showLoading(true);
                
                try {
                    const response = await fetch('/extend', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            specification: specification
                        })
                    });

                    const result = await response.json();
                    
                    if (result.success) {
                        const generated = result.generated_code;
                        const validation = result.validation;
                        
                        const content = `
                            <p><strong>Specification:</strong> ${specification}</p>
                            <p><strong>Generated Code ID:</strong> ${generated.code_id}</p>
                            <p><strong>Type:</strong> ${generated.type}</p>
                            <p><strong>Safety Level:</strong> ${generated.safety_level}</p>
                            <p><strong>Validation:</strong> ${validation.valid ? '✅ Passed' : '❌ Failed'}</p>
                            ${validation.errors?.length ? `<p><strong>Errors:</strong> ${validation.errors.join(', ')}</p>` : ''}
                            ${validation.warnings?.length ? `<p><strong>Warnings:</strong> ${validation.warnings.join(', ')}</p>` : ''}
                            <p><strong>Integration:</strong> ${result.integrated ? '✅ Integrated' : '⏸️ Manual approval required'}</p>
                        `;
                        
                        displayResult('🔧 Capability Generation', content, validation.valid ? 'success' : 'warning');
                    } else {
                        displayResult('❌ Generation Failed', `Error: ${result.error}`, 'error');
                    }
                } catch (error) {
                    displayResult('❌ Extension Request Failed', `Error: ${error.message}`, 'error');
                } finally {
                    showLoading(false);
                }
            }

            function clearResults() {
                document.getElementById('results').innerHTML = '';
            }

            // Auto-refresh system status periodically
            setInterval(async () => {
                try {
                    const response = await fetch('/health');
                    const health = await response.json();
                    // Could update a status indicator here
                } catch (error) {
                    console.log('Health check failed:', error);
                }
            }, 30000); // Every 30 seconds
        </script>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)

@app.post("/process")
async def process_request(request: Dict[str, Any]):
    """Process a user query through HybridMind."""
    if not mind:
        raise HTTPException(status_code=503, detail="HybridMind not available")
    
    query = request.get('query', '').strip()
    mode = request.get('mode', 'AUTO')
    
    if not query:
        raise HTTPException(status_code=400, detail="Query is required")
    
    try:
        # Convert mode string to ProcessingMode enum
        from hybridmind.core.hybridmind import ProcessingMode
        processing_mode = ProcessingMode[mode] if mode != 'AUTO' else ProcessingMode.AUTO
        
        # Process the query
        result = mind.process(query, mode=processing_mode)
        
        return {
            "success": result.success,
            "request_id": result.request_id,
            "processing_mode": result.processing_mode.value,
            "confidence": result.confidence,
            "processing_time": result.processing_time,
            "explanation": result.explanation,
            "errors": result.errors,
            "metadata": result.metadata
        }
        
    except Exception as e:
        logger.error(f"Processing error: {e}")
        return {
            "success": False,
            "explanation": f"Processing failed: {str(e)}",
            "errors": [str(e)]
        }

@app.get("/status")
async def get_status():
    """Get system status."""
    if not mind:
        return {"error": "HybridMind not available"}
    
    try:
        status = mind.get_system_status()
        return status
    except Exception as e:
        logger.error(f"Status error: {e}")
        return {"error": str(e)}

@app.post("/extend")
async def extend_capabilities(request: Dict[str, Any]):
    """Generate new capabilities."""
    if not mind:
        raise HTTPException(status_code=503, detail="HybridMind not available")
    
    specification = request.get('specification', '').strip()
    
    if not specification:
        raise HTTPException(status_code=400, detail="Specification is required")
    
    try:
        result = mind.extend_capabilities(
            specification=specification,
            capability_type="utility_class",
            auto_integrate=False  # Require manual approval for safety
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Extension error: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy" if mind else "unhealthy",
        "timestamp": datetime.now().isoformat(),
        "system_available": mind is not None
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time communication."""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Echo back for now - could implement real-time processing
            await manager.send_personal_message(f"Echo: {data}", websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

def main():
    """Run the web demo server."""
    print("🌐 Starting HybridMind Web Demo")
    print("=" * 50)
    
    if not mind:
        print("❌ HybridMind failed to initialize")
        return 1
    
    print("✅ HybridMind initialized successfully")
    print("🚀 Starting web server...")
    
    # Configure server
    config = uvicorn.Config(
        app=app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
        access_log=True
    )
    
    server = uvicorn.Server(config)
    
    print(f"🌍 Server will be available at:")
    print(f"   Local: http://localhost:8000")
    print(f"   Network: http://0.0.0.0:8000")
    print(f"\n💡 Open your browser and navigate to the URL above")
    print(f"🛑 Press Ctrl+C to stop the server\n")
    
    try:
        server.run()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down web server...")
        if mind:
            mind.shutdown()
        print("✅ Server stopped")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())