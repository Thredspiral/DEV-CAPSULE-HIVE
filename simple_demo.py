#!/usr/bin/env python3
"""
Simple HybridMind Demo (Lightweight Version)

A demonstration of HybridMind architecture without heavy dependencies.
"""

import sys
import logging
import json
import time
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Lightweight mock classes for demonstration
class MockProcessingMode(Enum):
    AUTO = "auto"
    SYMBOLIC_ONLY = "symbolic_only"
    NEURAL_ONLY = "neural_only"
    FUSION = "fusion"

@dataclass
class MockProcessingResult:
    request_id: str
    success: bool
    result: Any
    processing_time: float
    processing_mode: MockProcessingMode
    confidence: float
    explanation: str
    errors: List[str] = None
    metadata: Dict[str, Any] = None

class MockHybridMind:
    """Lightweight mock version of HybridMind for demonstration."""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.system_id = f"mock_hybridmind_{int(time.time())}"
        self.startup_time = time.time()
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'average_processing_time': 0.0,
            'capabilities_learned': 0
        }
        logger.info("Mock HybridMind initialized")
    
    def process(self, query: str, mode: MockProcessingMode = MockProcessingMode.AUTO) -> MockProcessingResult:
        """Mock processing that simulates HybridMind behavior."""
        request_id = f"req_{int(time.time() * 1000000)}"
        start_time = time.time()
        
        # Simulate processing time
        import random
        processing_time = random.uniform(0.1, 2.0)
        time.sleep(processing_time * 0.1)  # Shortened for demo
        
        # Update stats
        self.stats['total_requests'] += 1
        
        # Simulate different processing based on mode and query content
        confidence = random.uniform(0.6, 0.95)
        
        # Analyze query to determine response
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['logic', 'if', 'then', 'therefore', 'socrates']):
            mode = MockProcessingMode.SYMBOLIC_ONLY
            explanation = f"Symbolic reasoning applied: Analyzed logical structure and applied inference rules. Found {random.randint(1, 3)} logical conclusions."
            
        elif any(word in query_lower for word in ['sentiment', 'emotion', 'pattern', 'analyze text']):
            mode = MockProcessingMode.NEURAL_ONLY
            explanation = f"Neural processing applied: Extracted semantic patterns and emotional indicators. Confidence: {confidence:.2f}"
            
        elif any(word in query_lower for word in ['ethical', 'implications', 'society', 'complex']):
            mode = MockProcessingMode.FUSION
            explanation = f"Fusion reasoning applied: Combined symbolic logic with neural pattern recognition for comprehensive analysis. Used iterative refinement approach."
            
        else:
            explanation = f"Auto-mode processing: Determined optimal approach and processed query using {mode.value} strategy."
        
        # Simulate some failures for realism
        success = random.random() > 0.05  # 95% success rate
        
        if success:
            self.stats['successful_requests'] += 1
        else:
            self.stats['failed_requests'] += 1
            explanation = "Processing failed due to insufficient context or complexity"
            confidence = 0.0
        
        # Update average processing time
        total = self.stats['total_requests']
        current_avg = self.stats['average_processing_time']
        self.stats['average_processing_time'] = (current_avg * (total - 1) + processing_time) / total
        
        return MockProcessingResult(
            request_id=request_id,
            success=success,
            result={"processed_query": query, "analysis": explanation},
            processing_time=time.time() - start_time,
            processing_mode=mode,
            confidence=confidence,
            explanation=explanation,
            errors=[] if success else ["Simulated processing error"],
            metadata={"mode_selected": mode.value, "query_type": "text"}
        )
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get mock system status."""
        uptime = time.time() - self.startup_time
        
        return {
            'system_id': self.system_id,
            'state': 'ready',
            'uptime_seconds': uptime,
            'statistics': self.stats.copy(),
            'components': {
                'symbolic_engine': True,
                'neural_engine': True,
                'fusion_system': True,
                'safety_oversight': True,
                'self_extension': True
            },
            'capabilities': {
                'learned_capabilities': self.stats['capabilities_learned'],
                'total_capabilities': 15
            }
        }
    
    def extend_capabilities(self, specification: str, **kwargs) -> Dict[str, Any]:
        """Mock capability extension."""
        time.sleep(0.5)  # Simulate processing time
        
        self.stats['capabilities_learned'] += 1
        
        return {
            'success': True,
            'generated_code': {
                'code_id': f'generated_{int(time.time())}',
                'type': 'utility_class',
                'safety_level': 'safe',
                'description': f'Generated capability: {specification}'
            },
            'validation': {
                'valid': True,
                'errors': [],
                'warnings': [],
                'test_results': [
                    {'name': 'smoke_test', 'passed': True},
                    {'name': 'safety_test', 'passed': True}
                ]
            },
            'integrated': False  # Requires manual approval
        }
    
    def shutdown(self):
        """Mock shutdown."""
        logger.info("Mock HybridMind shutting down")

# Web interface using built-in HTTP server
try:
    from fastapi import FastAPI, HTTPException, Request
    from fastapi.responses import HTMLResponse, JSONResponse
    import uvicorn
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    print("FastAPI not available, running console demo instead...")

if FASTAPI_AVAILABLE:
    app = FastAPI(title="HybridMind Simple Demo", version="1.0.0")
    mind = MockHybridMind()

    @app.get("/", response_class=HTMLResponse)
    async def home():
        """Simple web interface."""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>HybridMind Simple Demo</title>
            <style>
                body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
                .header { text-align: center; color: #333; margin-bottom: 30px; }
                .panel { background: #f9f9f9; padding: 20px; border-radius: 10px; margin: 20px 0; }
                input, textarea, button { width: 100%; padding: 10px; margin: 5px 0; font-size: 16px; }
                button { background: #007cba; color: white; border: none; cursor: pointer; }
                button:hover { background: #005a87; }
                .result { background: white; padding: 15px; margin: 10px 0; border-left: 4px solid #007cba; }
                .success { border-left-color: #28a745; }
                .error { border-left-color: #dc3545; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🧠 HybridMind Simple Demo</h1>
                <p>Lightweight demonstration of Super AI Architecture</p>
            </div>
            
            <div class="panel">
                <h3>💭 Try HybridMind Processing</h3>
                <textarea id="query" placeholder="Enter your query... Try: 'If Socrates is human and all humans are mortal, what can we conclude?'" rows="3"></textarea>
                <button onclick="processQuery()">🚀 Process Query</button>
                
                <div id="results"></div>
            </div>
            
            <div class="panel">
                <h3>📊 System Status</h3>
                <button onclick="getStatus()">📈 Get System Status</button>
                <button onclick="generateCapability()">🔧 Generate Capability</button>
                
                <div id="status"></div>
            </div>

            <script>
                async function processQuery() {
                    const query = document.getElementById('query').value;
                    if (!query) return;
                    
                    try {
                        const response = await fetch('/process', {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify({query: query})
                        });
                        const result = await response.json();
                        
                        const resultDiv = document.createElement('div');
                        resultDiv.className = `result ${result.success ? 'success' : 'error'}`;
                        resultDiv.innerHTML = `
                            <strong>${result.success ? '✅' : '❌'} ${result.processing_mode}</strong><br>
                            <strong>Query:</strong> ${query}<br>
                            <strong>Confidence:</strong> ${(result.confidence * 100).toFixed(1)}%<br>
                            <strong>Time:</strong> ${result.processing_time.toFixed(3)}s<br>
                            <strong>Result:</strong> ${result.explanation}
                        `;
                        
                        document.getElementById('results').insertBefore(resultDiv, document.getElementById('results').firstChild);
                    } catch (error) {
                        alert('Error: ' + error.message);
                    }
                }
                
                async function getStatus() {
                    try {
                        const response = await fetch('/status');
                        const status = await response.json();
                        
                        document.getElementById('status').innerHTML = `
                            <div class="result">
                                <strong>📊 System Status</strong><br>
                                <strong>State:</strong> ${status.state}<br>
                                <strong>Uptime:</strong> ${status.uptime_seconds.toFixed(0)}s<br>
                                <strong>Requests:</strong> ${status.statistics.total_requests}<br>
                                <strong>Success Rate:</strong> ${(status.statistics.successful_requests / Math.max(status.statistics.total_requests, 1) * 100).toFixed(1)}%<br>
                                <strong>Avg Time:</strong> ${status.statistics.average_processing_time.toFixed(3)}s<br>
                                <strong>Capabilities:</strong> ${status.capabilities.total_capabilities}
                            </div>
                        `;
                    } catch (error) {
                        alert('Error: ' + error.message);
                    }
                }
                
                async function generateCapability() {
                    const spec = prompt('Enter capability specification:');
                    if (!spec) return;
                    
                    try {
                        const response = await fetch('/extend', {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify({specification: spec})
                        });
                        const result = await response.json();
                        
                        const resultDiv = document.createElement('div');
                        resultDiv.className = 'result success';
                        resultDiv.innerHTML = `
                            <strong>🔧 Capability Generated</strong><br>
                            <strong>Spec:</strong> ${spec}<br>
                            <strong>Code ID:</strong> ${result.generated_code.code_id}<br>
                            <strong>Safety:</strong> ${result.generated_code.safety_level}<br>
                            <strong>Valid:</strong> ${result.validation.valid ? '✅' : '❌'}<br>
                            <strong>Tests:</strong> ${result.validation.test_results.length} passed
                        `;
                        
                        document.getElementById('status').insertBefore(resultDiv, document.getElementById('status').firstChild);
                    } catch (error) {
                        alert('Error: ' + error.message);
                    }
                }
            </script>
        </body>
        </html>
        """
        return HTMLResponse(content=html)

    @app.post("/process")
    async def process_request(request: Dict[str, Any]):
        query = request.get('query', '').strip()
        if not query:
            raise HTTPException(status_code=400, detail="Query required")
        
        result = mind.process(query)
        return {
            "success": result.success,
            "processing_mode": result.processing_mode.value,
            "confidence": result.confidence,
            "processing_time": result.processing_time,
            "explanation": result.explanation,
            "errors": result.errors or []
        }

    @app.get("/status")
    async def get_status():
        return mind.get_system_status()

    @app.post("/extend")
    async def extend_capabilities(request: Dict[str, Any]):
        specification = request.get('specification', '').strip()
        if not specification:
            raise HTTPException(status_code=400, detail="Specification required")
        
        return mind.extend_capabilities(specification)

def console_demo():
    """Console-based demo when web interface is not available."""
    print("🧠 HybridMind Console Demo")
    print("=" * 50)
    
    mind = MockHybridMind()
    
    example_queries = [
        "If Socrates is human and all humans are mortal, what can we conclude about Socrates?",
        "Analyze the sentiment in this text: I am feeling great today!",
        "What are the ethical implications of artificial general intelligence?",
        "Create a utility function that validates email addresses"
    ]
    
    print("\n🚀 Processing Example Queries:\n")
    
    for i, query in enumerate(example_queries, 1):
        print(f"Query {i}: {query}")
        
        result = mind.process(query)
        
        print(f"✅ Result: {result.explanation}")
        print(f"   Mode: {result.processing_mode.value}")
        print(f"   Confidence: {result.confidence:.2f}")
        print(f"   Time: {result.processing_time:.3f}s")
        print()
    
    # Show system status
    print("📊 Final System Status:")
    status = mind.get_system_status()
    stats = status['statistics']
    
    print(f"   Total Requests: {stats['total_requests']}")
    print(f"   Success Rate: {stats['successful_requests']/stats['total_requests']*100:.1f}%")
    print(f"   Average Time: {stats['average_processing_time']:.3f}s")
    print(f"   Uptime: {status['uptime_seconds']:.0f}s")
    
    # Demo capability extension
    print(f"\n🔧 Capability Extension Demo:")
    spec = "Create a text summarizer that extracts key points"
    result = mind.extend_capabilities(spec)
    
    print(f"   Specification: {spec}")
    print(f"   Generated ID: {result['generated_code']['code_id']}")
    print(f"   Safety Level: {result['generated_code']['safety_level']}")
    print(f"   Validation: {'✅ Passed' if result['validation']['valid'] else '❌ Failed'}")
    
    print(f"\n✨ Demo Complete! HybridMind processed {stats['total_requests']} queries successfully.")
    
    mind.shutdown()

def web_demo():
    """Web-based demo."""
    print("🌐 Starting HybridMind Simple Web Demo")
    print("=" * 50)
    
    config = uvicorn.Config(
        app=app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
    
    server = uvicorn.Server(config)
    
    print("🚀 Server starting...")
    print("🌍 Open your browser to: http://localhost:8000")
    print("🛑 Press Ctrl+C to stop\n")
    
    try:
        server.run()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
        mind.shutdown()

def main():
    """Main demo function."""
    if len(sys.argv) > 1 and sys.argv[1] == "--console":
        console_demo()
    elif FASTAPI_AVAILABLE:
        web_demo()
    else:
        print("Web dependencies not available, running console demo...")
        console_demo()

if __name__ == "__main__":
    main()