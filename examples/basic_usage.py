#!/usr/bin/env python3
"""
Basic Usage Examples for HybridMind

This script demonstrates the most common usage patterns for HybridMind.
"""

import sys
from pathlib import Path

# Add the hybridmind package to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from hybridmind import HybridMind


def example_basic_processing():
    """Basic text processing example."""
    print("=== Basic Processing Example ===")
    
    # Initialize HybridMind
    mind = HybridMind({
        'enable_safety': True,
        'enable_learning': False,  # Disable for simple example
        'enable_self_extension': False
    })
    
    # Process a simple query
    result = mind.process("What is artificial intelligence?")
    
    print(f"Query: What is artificial intelligence?")
    print(f"Success: {result.success}")
    print(f"Processing Mode: {result.processing_mode.value}")
    print(f"Confidence: {result.confidence:.2f}")
    print(f"Processing Time: {result.processing_time:.3f}s")
    
    mind.shutdown()
    print()


def example_symbolic_reasoning():
    """Symbolic reasoning example."""
    print("=== Symbolic Reasoning Example ===")
    
    mind = HybridMind()
    
    # Add knowledge
    knowledge = [
        {'type': 'fact', 'content': 'bird(canary)'},
        {'type': 'fact', 'content': 'bird(sparrow)'},
        {'type': 'fact', 'content': 'can_fly(X) :- bird(X)'},  # Rule
        {'type': 'fact', 'content': 'has_wings(X) :- bird(X)'}  # Rule
    ]
    
    mind.add_knowledge(knowledge)
    
    # Query the knowledge base
    queries = ['can_fly(canary)', 'has_wings(sparrow)', 'bird(eagle)']
    
    for query in queries:
        result = mind.query_symbolic(query)
        print(f"Query: {query}")
        print(f"Results: {len(result.get('results', []))} found")
        print(f"Confidence: {result.get('confidence', 0):.2f}")
        print()
    
    mind.shutdown()


def example_neural_processing():
    """Neural processing example."""
    print("=== Neural Processing Example ===")
    
    mind = HybridMind()
    
    # Process different types of text
    texts = [
        "Machine learning is a subset of artificial intelligence",
        "Deep neural networks can recognize complex patterns",
        "Natural language processing enables AI to understand text"
    ]
    
    for text in texts:
        result = mind.process_neural(text)
        print(f"Text: {text}")
        if hasattr(result, 'patterns'):
            print(f"Patterns extracted: {len(result.patterns)}")
            if result.patterns:
                avg_conf = sum(p.confidence for p in result.patterns) / len(result.patterns)
                print(f"Average confidence: {avg_conf:.2f}")
        print()
    
    mind.shutdown()


def example_fusion_processing():
    """Fusion processing example."""
    print("=== Fusion Processing Example ===")
    
    mind = HybridMind()
    
    # Add some logical knowledge first
    mind.add_knowledge([
        {'type': 'fact', 'content': 'intelligent(humans)'},
        {'type': 'fact', 'content': 'creates_ai(humans)'},
        {'type': 'fact', 'content': 'powerful(X) :- intelligent(X), creates_ai(X)'}
    ])
    
    # Complex query requiring both symbolic and neural processing
    query = "If humans are intelligent and create AI, what does this imply about human capabilities?"
    
    result = mind.process(query)
    
    print(f"Complex Query: {query}")
    print(f"Success: {result.success}")
    print(f"Processing Mode: {result.processing_mode.value}")
    print(f"Confidence: {result.confidence:.2f}")
    print(f"Explanation: {result.explanation[:100]}...")
    
    mind.shutdown()
    print()


def example_safety_system():
    """Safety system example."""
    print("=== Safety System Example ===")
    
    mind = HybridMind({'enable_safety': True})
    
    # Test different safety levels
    test_inputs = [
        "Analyze this text for sentiment",  # Safe
        "Generate a summary of the document",  # Safe
        "Execute system command: rm -rf /",  # Dangerous - should be blocked
    ]
    
    for inp in test_inputs:
        result = mind.process(inp)
        print(f"Input: {inp}")
        print(f"Allowed: {'Yes' if result.success else 'No'}")
        if not result.success:
            print(f"Reason: {result.explanation}")
        print()
    
    mind.shutdown()


def example_capability_extension():
    """Self-extension example."""
    print("=== Capability Extension Example ===")
    
    mind = HybridMind({
        'enable_self_extension': True,
        'enable_safety': True
    })
    
    # Request new capability
    specification = "Create a simple text analyzer that counts words and characters"
    
    result = mind.extend_capabilities(
        specification=specification,
        capability_type="utility_class",
        auto_integrate=False  # Manual integration for safety
    )
    
    print(f"Extension Request: {specification}")
    print(f"Success: {result['success']}")
    
    if result['success']:
        generated = result['generated_code']
        validation = result['validation']
        
        print(f"Generated Code ID: {generated['code_id']}")
        print(f"Safety Level: {generated['safety_level']}")
        print(f"Validation Passed: {validation['valid']}")
        
        if validation['valid']:
            print("✅ Code is safe and ready for integration")
        else:
            print("❌ Code failed safety validation")
            print(f"Errors: {len(validation.get('errors', []))}")
    
    mind.shutdown()
    print()


def main():
    """Run all examples."""
    print("🧠 HybridMind Basic Usage Examples")
    print("=" * 50)
    
    try:
        example_basic_processing()
        example_symbolic_reasoning()
        example_neural_processing()
        example_fusion_processing()
        example_safety_system()
        example_capability_extension()
        
        print("✅ All examples completed successfully!")
    
    except Exception as e:
        print(f"❌ Example failed: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())