#!/usr/bin/env python3
"""
HybridMind Demo Application

This demo showcases the key capabilities of the HybridMind Super AI architecture:
- Symbolic reasoning and logical inference
- Neural pattern recognition and learning
- Symbolic-neural fusion for hybrid intelligence
- Self-extension with code generation
- Safety oversight and human-in-the-loop
"""

import sys
import logging
import time
from typing import Dict, Any
import json
from pathlib import Path

# Add the hybridmind package to the path
sys.path.insert(0, str(Path(__file__).parent))

from hybridmind import HybridMind
from hybridmind.engines.symbolic_engine import Fact, Rule, RuleType
from hybridmind.fusion.symbolic_neural_fusion import FusionMode
from hybridmind.extensions.self_extension import ExtensionType

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class HybridMindDemo:
    """Comprehensive demo of HybridMind capabilities."""
    
    def __init__(self):
        """Initialize the demo."""
        print("🧠 HybridMind Super AI Architecture Demo")
        print("=" * 50)
        
        # Initialize HybridMind with demo configuration
        config = {
            'enable_safety': True,
            'enable_learning': True,
            'enable_self_extension': True,
            'neural_config': {
                'auto_initialize': False  # We'll manually initialize for demo
            },
            'log_level': 'INFO'
        }
        
        print("Initializing HybridMind system...")
        self.mind = HybridMind(config)
        print("✅ HybridMind initialized successfully!\n")
    
    def run_demo(self):
        """Run the complete demo."""
        try:
            print("🚀 Starting HybridMind Demo\n")
            
            # 1. System Status
            self.demo_system_status()
            
            # 2. Symbolic Reasoning
            self.demo_symbolic_reasoning()
            
            # 3. Neural Processing
            self.demo_neural_processing()
            
            # 4. Fusion Reasoning
            self.demo_fusion_reasoning()
            
            # 5. Self-Extension
            self.demo_self_extension()
            
            # 6. Safety System
            self.demo_safety_system()
            
            # 7. Integrated Processing
            self.demo_integrated_processing()
            
            # 8. Final Status
            self.demo_final_status()
            
        except KeyboardInterrupt:
            print("\n❌ Demo interrupted by user")
        except Exception as e:
            print(f"\n❌ Demo failed with error: {e}")
            logger.exception("Demo failed")
        finally:
            print("\n🔄 Shutting down HybridMind...")
            self.mind.shutdown()
            print("✅ Demo complete!")
    
    def demo_system_status(self):
        """Demonstrate system status and capabilities."""
        print("📊 SYSTEM STATUS")
        print("-" * 30)
        
        status = self.mind.get_system_status()
        
        print(f"System ID: {status['system_id']}")
        print(f"State: {status['state']}")
        print(f"Uptime: {status['uptime_seconds']:.2f} seconds")
        
        print("\nCore Components:")
        components = status['components']
        for component, available in components.items():
            if isinstance(available, dict):
                print(f"  {component}:")
                for sub_comp, sub_available in available.items():
                    status_icon = "✅" if sub_available else "❌"
                    print(f"    {status_icon} {sub_comp}")
            else:
                status_icon = "✅" if available else "❌"
                print(f"  {status_icon} {component}")
        
        capabilities = self.mind.list_capabilities()
        print(f"\nTotal Capabilities: {capabilities['total_capabilities']}")
        print(f"Self-Extension Enabled: {'✅' if capabilities['self_extension'] else '❌'}")
        
        self.wait_for_user()
    
    def demo_symbolic_reasoning(self):
        """Demonstrate symbolic reasoning capabilities."""
        print("🧮 SYMBOLIC REASONING")
        print("-" * 30)
        
        # Add some facts to the knowledge base
        print("Adding facts to knowledge base:")
        facts = [
            "human(socrates)",
            "human(plato)",
            "mortal(X) :- human(X)",  # Rule: all humans are mortal
            "philosopher(socrates)",
            "philosopher(plato)",
            "teacher(plato, aristotle)",
            "student(aristotle, plato)"
        ]
        
        for fact in facts:
            print(f"  + {fact}")
            self.mind.add_knowledge([{'type': 'fact', 'content': fact}])
        
        print("\n🔍 Querying symbolic knowledge:")
        
        # Test queries
        queries = [
            "mortal(socrates)",
            "human(plato)",
            "philosopher(socrates)",
            "teacher(plato, X)"
        ]
        
        for query in queries:
            print(f"\nQuery: {query}")
            result = self.mind.query_symbolic(query)
            
            if result.get('results'):
                print(f"✅ Found {len(result['results'])} results")
                print(f"   Confidence: {result.get('confidence', 0):.2f}")
                for i, res in enumerate(result['results'][:2]):  # Show first 2 results
                    print(f"   Result {i+1}: {res}")
            else:
                print("❌ No results found")
        
        # Demonstrate reasoning explanation
        print(f"\n🔍 Reasoning explanation for 'mortal(socrates)':")
        explanation = self.mind.explain_reasoning("mortal(socrates)")
        if 'symbolic' in explanation:
            symbolic_exp = explanation['symbolic']
            print(f"   Applied rules: {len(symbolic_exp.get('applied_rules', []))}")
            print(f"   Reasoning steps: {len(symbolic_exp.get('reasoning_steps', []))}")
        
        self.wait_for_user()
    
    def demo_neural_processing(self):
        """Demonstrate neural processing capabilities."""
        print("🧠 NEURAL PROCESSING")
        print("-" * 30)
        
        # Process text through neural engine
        print("Processing text through neural networks:")
        
        test_texts = [
            "Artificial intelligence is transforming the world",
            "Machine learning enables pattern recognition",
            "Deep learning neural networks process complex data",
            "Natural language processing understands human communication"
        ]
        
        for text in test_texts:
            print(f"\nProcessing: '{text}'")
            
            result = self.mind.process_neural(text)
            
            if hasattr(result, 'patterns') and result.patterns:
                print(f"✅ Extracted {len(result.patterns)} patterns")
                for i, pattern in enumerate(result.patterns[:2]):  # Show first 2
                    print(f"   Pattern {i+1}: {pattern.pattern_type} (confidence: {pattern.confidence:.2f})")
            else:
                print("❌ No patterns extracted")
            
            # Show embedding information
            if hasattr(result, 'embeddings') and len(result.embeddings) > 0:
                print(f"   Generated embeddings: shape {result.embeddings.shape}")
        
        # Demonstrate pattern similarity
        print(f"\n🔍 Finding similar patterns:")
        similar_patterns = self.mind.neural_engine.find_similar_patterns(
            "artificial intelligence and machine learning", top_k=3
        )
        
        if similar_patterns:
            print(f"✅ Found {len(similar_patterns)} similar patterns")
            for pattern, similarity in similar_patterns:
                print(f"   Similarity: {similarity:.2f} - {pattern.pattern_id}")
        else:
            print("❌ No similar patterns found")
        
        self.wait_for_user()
    
    def demo_fusion_reasoning(self):
        """Demonstrate symbolic-neural fusion capabilities."""
        print("🔄 FUSION REASONING")
        print("-" * 30)
        
        # Test different fusion modes
        test_query = "If Socrates is human and all humans are mortal, what can we conclude about Socrates?"
        
        fusion_modes = [
            (FusionMode.SEQUENTIAL, "Sequential (Neural → Symbolic)"),
            (FusionMode.PARALLEL, "Parallel Processing"),
            (FusionMode.ITERATIVE, "Iterative Refinement")
        ]
        
        print(f"Query: {test_query}\n")
        
        for mode, description in fusion_modes:
            print(f"🔄 {description}")
            
            try:
                result = self.mind.fuse_reasoning(test_query, mode)
                
                if 'fusion_result' in result:
                    fusion_data = result['fusion_result']
                    print(f"   ✅ Confidence: {fusion_data['confidence']:.2f}")
                    print(f"   📋 Path: {' → '.join(fusion_data['fusion_path'])}")
                    print(f"   💭 Explanation: {fusion_data['explanation'][:100]}...")
                else:
                    print(f"   ❌ Fusion failed: {result.get('error', 'Unknown error')}")
            
            except Exception as e:
                print(f"   ❌ Error: {str(e)}")
            
            print()
        
        # Demonstrate automatic mode selection
        print("🤖 Automatic Fusion Mode Selection:")
        auto_result = self.mind.fuse_reasoning(test_query, FusionMode.AUTO)
        if 'fusion_result' in auto_result:
            fusion_data = auto_result['fusion_result']
            print(f"   Selected optimal fusion approach")
            print(f"   Confidence: {fusion_data['confidence']:.2f}")
        
        self.wait_for_user()
    
    def demo_self_extension(self):
        """Demonstrate self-extension capabilities."""
        print("🔧 SELF-EXTENSION")
        print("-" * 30)
        
        # Generate a new reasoning capability
        specification = "Create a mathematical reasoning module that can solve basic arithmetic and algebraic equations"
        
        print(f"Generating new capability:")
        print(f"Specification: {specification}")
        
        try:
            result = self.mind.extend_capabilities(
                specification=specification,
                capability_type="reasoning_module",
                auto_integrate=False  # Don't auto-integrate for safety
            )

            if result['success']:
                generated = result['generated_code']
                validation = result['validation']

                print(f"\n✅ Code Generation Successful:")
                print(f"   Code ID: {generated['code_id']}")
                print(f"   Type: {generated['type']}")
                print(f"   Safety Level: {generated['safety_level']}")
                print(f"   Description: {generated['description']}")

                print(f"\n🔍 Validation Results:")
                print(f"   Valid: {'✅' if validation['valid'] else '❌'}")
                print(f"   Safety Level: {validation['safety_level']}")

                if validation['errors']:
                    print(f"   Errors: {len(validation['errors'])}")
                    for error in validation['errors'][:2]:
                        print(f"     - {error}")

                if validation['warnings']:
                    print(f"   Warnings: {len(validation['warnings'])}")
                    for warning in validation['warnings'][:2]:
                        print(f"     - {warning}")

                if validation['test_results']:
                    passed_tests = sum(1 for t in validation['test_results'] if t['passed'])
                    total_tests = len(validation['test_results'])
                    print(f"   Tests: {passed_tests}/{total_tests} passed")

                # Show integration capability
                if validation['valid']:
                    print(f"\n🔗 Integration Available:")
                    print(f"   Code can be safely integrated into the system")
                    print(f"   Would add new reasoning capabilities")
                else:
                    print(f"\n⚠️  Integration Blocked:")
                    print(f"   Code failed safety validation")

            else:
                print(f"❌ Code generation failed: {result.get('error')}")

        except Exception as e:
            print(f"❌ Self-extension error: {str(e)}")

        # Show current capabilities
        capabilities = self.mind.list_capabilities()
        print(f"\n📊 Current System Capabilities:")
        print(f"   Core: {len(capabilities['core_capabilities'])}")
        print(f"   Learned: {len(capabilities['learned_capabilities'])}")
        print(f"   Total: {capabilities['total_capabilities']}")

        self.wait_for_user()