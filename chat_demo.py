#!/usr/bin/env python3
"""
HybridMind Chat Interface

A conversational chat interface that provides intelligent responses
using a simplified version of the HybridMind architecture.
"""

import sys
import logging
import json
import time
import random
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from fastapi import FastAPI, WebSocket, WebSocketDisconnect
    from fastapi.responses import HTMLResponse
    from fastapi.staticfiles import StaticFiles
    import uvicorn
    FASTAPI_AVAILABLE = True
except ImportError:
    print("Installing required packages...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "fastapi", "uvicorn", "websockets"])
    from fastapi import FastAPI, WebSocket, WebSocketDisconnect
    from fastapi.responses import HTMLResponse
    from fastapi.staticfiles import StaticFiles
    import uvicorn
    FASTAPI_AVAILABLE = True

class ChatBot:
    """Intelligent chatbot powered by HybridMind concepts."""
    
    def __init__(self):
        self.conversation_history = []
        self.knowledge_base = {
            # Programming and AI
            "python": "Python is a versatile programming language excellent for AI development, with rich libraries like PyTorch, TensorFlow, and scikit-learn.",
            "ai": "Artificial Intelligence encompasses machine learning, natural language processing, computer vision, and reasoning systems that can perform tasks requiring human-like intelligence.",
            "machine learning": "Machine learning enables computers to learn and improve from data without being explicitly programmed for every scenario.",
            "neural networks": "Neural networks are computational models inspired by biological neurons, capable of learning complex patterns in data through interconnected layers.",
            
            # HybridMind specific
            "hybridmind": "HybridMind is a revolutionary Super AI architecture combining symbolic reasoning, neural processing, and self-extension capabilities with comprehensive safety mechanisms.",
            "symbolic reasoning": "Symbolic reasoning uses logical rules and knowledge representations to make inferences, providing interpretable and explainable AI decisions.",
            "fusion": "In HybridMind, fusion combines symbolic logic with neural pattern recognition, leveraging the strengths of both approaches for superior intelligence.",
            
            # Philosophy and ethics
            "consciousness": "Consciousness involves self-awareness, subjective experience, and the ability to reflect on one's own mental states and existence.",
            "ethics": "AI ethics involves ensuring artificial intelligence systems are beneficial, fair, transparent, accountable, and aligned with human values.",
            "philosophy": "Philosophy explores fundamental questions about existence, knowledge, values, reason, mind, and language through critical thinking and logical analysis.",
            
            # Science and technology
            "quantum": "Quantum computing leverages quantum mechanical phenomena like superposition and entanglement to process information in fundamentally different ways.",
            "future": "The future of AI likely involves more sophisticated reasoning, better human-AI collaboration, and careful attention to safety and alignment with human values.",
            "technology": "Technology advancement continues to accelerate, with AI, quantum computing, biotechnology, and renewable energy driving major societal changes."
        }
        
        self.patterns = {
            "greeting": ["hello", "hi", "hey", "good morning", "good afternoon", "good evening"],
            "question": ["what", "how", "why", "when", "where", "who", "which"],
            "emotional": ["feel", "emotion", "happy", "sad", "excited", "worried", "confused"],
            "capability": ["can you", "are you able", "do you know", "help me"],
            "complex": ["explain", "analyze", "compare", "evaluate", "discuss", "elaborate"]
        }
        
        self.responses = {
            "greeting": [
                "Hello! I'm HybridMind, your AI assistant. I can help with questions about AI, programming, philosophy, and much more. What would you like to explore?",
                "Hi there! Welcome to HybridMind. I combine symbolic reasoning with neural processing to provide thoughtful responses. How can I assist you?",
                "Greetings! I'm an advanced AI system designed to engage in meaningful conversations. What's on your mind today?"
            ],
            "unknown": [
                "That's an interesting question! While I don't have specific information about that topic, I can help you think through it logically.",
                "I'm not entirely sure about that specific topic, but let me try to provide a thoughtful response based on related concepts I understand.",
                "That's outside my current knowledge base, but I'd be happy to explore the topic with you from first principles."
            ],
            "capability": [
                "I can help with a wide range of topics including AI, programming, philosophy, science, and logical reasoning. What specifically interests you?",
                "My capabilities span symbolic reasoning, pattern analysis, and thoughtful conversation. I'm designed to provide helpful, accurate, and engaging responses.",
                "I'm built on HybridMind architecture, combining different AI approaches. I can discuss complex topics, answer questions, and help with problem-solving."
            ]
        }
    
    def process_message(self, message: str) -> str:
        """Process a user message and generate an intelligent response."""
        message_lower = message.lower().strip()
        
        # Add to conversation history
        self.conversation_history.append({
            "user": message,
            "timestamp": datetime.now().isoformat()
        })
        
        # Simulate thinking time
        time.sleep(0.5)
        
        # Determine response type and generate response
        response = self._generate_response(message_lower)
        
        # Add response to history
        self.conversation_history.append({
            "assistant": response,
            "timestamp": datetime.now().isoformat()
        })
        
        return response
    
    def _generate_response(self, message: str) -> str:
        """Generate an appropriate response based on message analysis."""
        
        # Check for greetings
        if any(greeting in message for greeting in self.patterns["greeting"]):
            return random.choice(self.responses["greeting"])
        
        # Check for capability questions
        if any(cap in message for cap in self.patterns["capability"]):
            return random.choice(self.responses["capability"])
        
        # Check knowledge base for relevant topics
        for topic, info in self.knowledge_base.items():
            if topic in message or any(word in message for word in topic.split()):
                return self._elaborate_response(info, message)
        
        # Handle specific question patterns
        if any(q in message for q in self.patterns["question"]):
            return self._answer_question(message)
        
        # Handle emotional expressions
        if any(emotion in message for emotion in self.patterns["emotional"]):
            return self._respond_emotionally(message)
        
        # Handle complex requests
        if any(complex_word in message for complex_word in self.patterns["complex"]):
            return self._provide_complex_response(message)
        
        # Handle specific topics
        if "love" in message or "relationship" in message:
            return "Love and relationships are complex human experiences involving deep emotional connections, mutual care, and often a desire for companionship and understanding. They're fundamental to human wellbeing and social structure."
        
        if "meaning" in message and "life" in message:
            return "The meaning of life is one of philosophy's most profound questions. Some find meaning through relationships, others through achievement, creativity, spiritual beliefs, or contributing to something greater than themselves. It's deeply personal and varies for each individual."
        
        if "time" in message or "universe" in message:
            return "Time and the universe are fascinating subjects. Our current understanding suggests the universe is about 13.8 billion years old, with time being a fundamental dimension that may be relative rather than absolute, as Einstein showed us."
        
        if "creativity" in message or "art" in message:
            return "Creativity and art are uniquely human expressions that combine imagination, skill, and emotion. They allow us to communicate experiences, ideas, and feelings in ways that transcend ordinary language."
        
        # Default thoughtful response
        return self._generate_thoughtful_default(message)
    
    def _elaborate_response(self, base_info: str, message: str) -> str:
        """Elaborate on knowledge base information contextually."""
        elaborations = [
            f"{base_info} Is there a particular aspect of this topic you'd like to explore further?",
            f"{base_info} This connects to many interesting areas - what specifically would you like to know more about?",
            f"{base_info} I find this fascinating because it demonstrates how different fields of knowledge interconnect."
        ]
        return random.choice(elaborations)
    
    def _answer_question(self, message: str) -> str:
        """Provide thoughtful answers to questions."""
        if "what" in message:
            if "ai" in message or "artificial intelligence" in message:
                return "AI is the simulation of human intelligence in machines. It includes machine learning, natural language processing, computer vision, and reasoning. Modern AI combines statistical methods with symbolic approaches for more robust intelligence."
            elif "consciousness" in message:
                return "Consciousness is one of the deepest mysteries in science and philosophy. It involves self-awareness, subjective experience, and the integration of sensory information into a unified sense of self and reality."
        
        elif "how" in message:
            if "work" in message:
                return "That depends on what system you're asking about! Generally, complex systems work through the interaction of simpler components following specific rules or patterns. Could you be more specific?"
            elif "learn" in message:
                return "Learning involves acquiring new information, skills, or understanding through experience, study, or instruction. In AI, learning typically involves adjusting parameters based on data patterns."
        
        elif "why" in message:
            return "That's a profound question that could have multiple layers of explanation. Why questions often involve understanding purposes, causes, or motivations. What specific aspect interests you most?"
        
        return "That's a great question! I'd need a bit more context to provide the most helpful answer. Could you elaborate on what you're most curious about?"
    
    def _respond_emotionally(self, message: str) -> str:
        """Respond to emotional content with empathy."""
        if "happy" in message or "excited" in message or "great" in message:
            return "That's wonderful to hear! Positive emotions like happiness and excitement can be contagious and help us see possibilities more clearly. What's bringing you joy today?"
        
        elif "sad" in message or "worried" in message or "confused" in message:
            return "I understand those feelings can be challenging. It's natural to experience a full range of emotions. Sometimes talking through what we're feeling can help clarify our thoughts. Would you like to share more?"
        
        return "Emotions are such an important part of the human experience. They provide valuable information about our needs, values, and relationships with the world around us."
    
    def _provide_complex_response(self, message: str) -> str:
        """Handle requests for explanation or analysis."""
        topics = []
        
        # Extract potential topics from the message
        words = message.split()
        for word in words:
            if len(word) > 4 and word not in ["explain", "analyze", "compare", "evaluate", "discuss"]:
                topics.append(word)
        
        if topics:
            main_topic = topics[0]
            return f"To properly {message.split()[0]} {main_topic}, I'd need to consider multiple perspectives and dimensions. This is the kind of complex topic that benefits from systematic analysis. What particular aspect would you like me to focus on first?"
        
        return "I'd be happy to provide a detailed analysis! Complex topics often involve multiple interconnected factors. Could you specify what particular elements you'd like me to focus on?"
    
    def _generate_thoughtful_default(self, message: str) -> str:
        """Generate a thoughtful default response."""
        defaults = [
            f"That's an intriguing point. I notice there could be several ways to approach this topic. What perspective interests you most?",
            f"Your question touches on some deep concepts. While I may not have all the answers, I'm curious about your thoughts on this. What led you to think about this?",
            f"That's the kind of question that could lead to a fascinating discussion. I'd love to explore this with you further - what aspect would you like to dive into first?",
            f"Interesting! This topic connects to many different fields of knowledge. I'm designed to think through complex problems - shall we break this down together?"
        ]
        return random.choice(defaults)

# FastAPI app
app = FastAPI(title="HybridMind Chat Interface")
chatbot = ChatBot()

@app.get("/", response_class=HTMLResponse)
async def chat_interface():
    """Serve the chat interface."""
    
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>HybridMind Chat</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
            }
            
            .chat-container {
                width: 90%;
                max-width: 800px;
                height: 90vh;
                background: white;
                border-radius: 20px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.2);
                display: flex;
                flex-direction: column;
                overflow: hidden;
            }
            
            .chat-header {
                background: linear-gradient(45deg, #667eea, #764ba2);
                color: white;
                padding: 20px;
                text-align: center;
                position: relative;
            }
            
            .chat-header h1 {
                font-size: 2em;
                margin-bottom: 5px;
            }
            
            .chat-header p {
                opacity: 0.9;
                font-size: 0.9em;
            }
            
            .chat-messages {
                flex: 1;
                overflow-y: auto;
                padding: 20px;
                background: #f8f9fa;
            }
            
            .message {
                margin-bottom: 15px;
                display: flex;
                animation: fadeIn 0.3s ease-in;
            }
            
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(10px); }
                to { opacity: 1; transform: translateY(0); }
            }
            
            .message.user {
                justify-content: flex-end;
            }
            
            .message.assistant {
                justify-content: flex-start;
            }
            
            .message-bubble {
                max-width: 70%;
                padding: 15px 20px;
                border-radius: 20px;
                word-wrap: break-word;
                line-height: 1.4;
            }
            
            .message.user .message-bubble {
                background: linear-gradient(45deg, #667eea, #764ba2);
                color: white;
                border-bottom-right-radius: 5px;
            }
            
            .message.assistant .message-bubble {
                background: white;
                color: #333;
                border: 1px solid #e1e5e9;
                border-bottom-left-radius: 5px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }
            
            .chat-input-container {
                padding: 20px;
                background: white;
                border-top: 1px solid #e1e5e9;
                display: flex;
                gap: 10px;
            }
            
            .chat-input {
                flex: 1;
                padding: 15px 20px;
                border: 2px solid #e1e5e9;
                border-radius: 25px;
                font-size: 16px;
                outline: none;
                transition: border-color 0.3s;
            }
            
            .chat-input:focus {
                border-color: #667eea;
            }
            
            .send-button {
                padding: 15px 25px;
                background: linear-gradient(45deg, #667eea, #764ba2);
                color: white;
                border: none;
                border-radius: 25px;
                cursor: pointer;
                font-size: 16px;
                font-weight: bold;
                transition: transform 0.2s, box-shadow 0.2s;
            }
            
            .send-button:hover {
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(0,0,0,0.2);
            }
            
            .send-button:disabled {
                background: #ccc;
                cursor: not-allowed;
                transform: none;
                box-shadow: none;
            }
            
            .typing-indicator {
                display: none;
                padding: 15px 20px;
                color: #666;
                font-style: italic;
            }
            
            .typing-indicator.show {
                display: block;
            }
            
            .suggestions {
                padding: 0 20px 10px;
                display: flex;
                gap: 10px;
                flex-wrap: wrap;
            }
            
            .suggestion-chip {
                background: #e9ecef;
                color: #495057;
                padding: 8px 15px;
                border-radius: 20px;
                font-size: 14px;
                cursor: pointer;
                transition: all 0.2s;
                border: none;
            }
            
            .suggestion-chip:hover {
                background: #667eea;
                color: white;
                transform: translateY(-1px);
            }
            
            .status-indicator {
                position: absolute;
                top: 10px;
                right: 10px;
                width: 10px;
                height: 10px;
                background: #28a745;
                border-radius: 50%;
                animation: pulse 2s infinite;
            }
            
            @keyframes pulse {
                0% { opacity: 1; }
                50% { opacity: 0.5; }
                100% { opacity: 1; }
            }
            
            @media (max-width: 600px) {
                .chat-container {
                    width: 95%;
                    height: 95vh;
                    border-radius: 10px;
                }
                
                .message-bubble {
                    max-width: 85%;
                }
                
                .chat-header h1 {
                    font-size: 1.5em;
                }
                
                .suggestions {
                    flex-direction: column;
                }
            }
        </style>
    </head>
    <body>
        <div class="chat-container">
            <div class="chat-header">
                <div class="status-indicator"></div>
                <h1>🧠 HybridMind Chat</h1>
                <p>Intelligent conversation with Super AI architecture</p>
            </div>
            
            <div class="suggestions">
                <button class="suggestion-chip" onclick="sendMessage('Hello! What can you help me with?')">👋 Say Hello</button>
                <button class="suggestion-chip" onclick="sendMessage('What is artificial intelligence?')">🤖 Ask about AI</button>
                <button class="suggestion-chip" onclick="sendMessage('Explain consciousness to me')">🧠 Explore consciousness</button>
                <button class="suggestion-chip" onclick="sendMessage('What is the meaning of life?')">🤔 Philosophy</button>
            </div>
            
            <div class="chat-messages" id="messages">
                <div class="message assistant">
                    <div class="message-bubble">
                        🌟 Welcome to HybridMind! I'm an advanced AI assistant that combines symbolic reasoning with neural processing. I can discuss AI, philosophy, science, programming, and much more. What would you like to explore today?
                    </div>
                </div>
            </div>
            
            <div class="typing-indicator" id="typing">
                🤖 HybridMind is thinking...
            </div>
            
            <div class="chat-input-container">
                <input type="text" class="chat-input" id="messageInput" placeholder="Type your message here..." onkeypress="handleKeyPress(event)">
                <button class="send-button" id="sendButton" onclick="sendUserMessage()">Send</button>
            </div>
        </div>

        <script>
            let ws = null;
            let isConnected = false;

            function connectWebSocket() {
                const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
                ws = new WebSocket(`${protocol}//${window.location.host}/ws`);
                
                ws.onopen = function() {
                    console.log('Connected to HybridMind');
                    isConnected = true;
                };
                
                ws.onmessage = function(event) {
                    const data = JSON.parse(event.data);
                    if (data.type === 'response') {
                        hideTyping();
                        addMessage(data.message, 'assistant');
                    }
                };
                
                ws.onclose = function() {
                    console.log('Disconnected from HybridMind');
                    isConnected = false;
                    // Try to reconnect after 3 seconds
                    setTimeout(connectWebSocket, 3000);
                };
                
                ws.onerror = function(error) {
                    console.error('WebSocket error:', error);
                };
            }

            function sendMessage(message) {
                document.getElementById('messageInput').value = message;
                sendUserMessage();
            }

            function sendUserMessage() {
                const input = document.getElementById('messageInput');
                const message = input.value.trim();
                
                if (!message) return;
                
                addMessage(message, 'user');
                input.value = '';
                
                showTyping();
                
                if (isConnected) {
                    ws.send(JSON.stringify({
                        type: 'message',
                        message: message
                    }));
                } else {
                    // Fallback if WebSocket isn't connected
                    setTimeout(() => {
                        hideTyping();
                        addMessage("I'm having trouble connecting right now. Please refresh the page and try again.", 'assistant');
                    }, 1000);
                }
            }

            function addMessage(text, sender) {
                const messagesContainer = document.getElementById('messages');
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${sender}`;
                
                const bubble = document.createElement('div');
                bubble.className = 'message-bubble';
                bubble.textContent = text;
                
                messageDiv.appendChild(bubble);
                messagesContainer.appendChild(messageDiv);
                
                messagesContainer.scrollTop = messagesContainer.scrollHeight;
            }

            function showTyping() {
                document.getElementById('typing').classList.add('show');
                document.getElementById('sendButton').disabled = true;
            }

            function hideTyping() {
                document.getElementById('typing').classList.remove('show');
                document.getElementById('sendButton').disabled = false;
            }

            function handleKeyPress(event) {
                if (event.key === 'Enter') {
                    sendUserMessage();
                }
            }

            // Initialize WebSocket connection
            connectWebSocket();
        </script>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time chat."""
    await websocket.accept()
    
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            if message_data["type"] == "message":
                user_message = message_data["message"]
                
                # Process message through chatbot
                response = chatbot.process_message(user_message)
                
                # Send response back
                await websocket.send_text(json.dumps({
                    "type": "response",
                    "message": response
                }))
                
    except WebSocketDisconnect:
        pass

def main():
    """Run the chat interface."""
    print("🧠 Starting HybridMind Chat Interface")
    print("=" * 50)
    
    config = uvicorn.Config(
        app=app,
        host="0.0.0.0",
        port=8081,  # Changed port to 8081
        log_level="info"
    )
    
    server = uvicorn.Server(config)
    
    print("💬 Chat interface starting...")
    print("🌍 Access your chat at: http://localhost:8081")
    print("🛑 Press Ctrl+C to stop\n")
    
    try:
        server.run()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down chat interface...")
        print("✅ Chat stopped")

if __name__ == "__main__":
    main()