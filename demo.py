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
            result = self.mind.extend_capabilities(\n                specification=specification,\n                capability_type=\"reasoning_module\",\n                auto_integrate=False  # Don't auto-integrate for safety\n            )\n            \n            if result['success']:\n                generated = result['generated_code']\n                validation = result['validation']\n                \n                print(f\"\\n✅ Code Generation Successful:\")\n                print(f\"   Code ID: {generated['code_id']}\")\n                print(f\"   Type: {generated['type']}\")\n                print(f\"   Safety Level: {generated['safety_level']}\")\n                print(f\"   Description: {generated['description']}\")\n                \n                print(f\"\\n🔍 Validation Results:\")\n                print(f\"   Valid: {'✅' if validation['valid'] else '❌'}\")\n                print(f\"   Safety Level: {validation['safety_level']}\")\n                \n                if validation['errors']:\n                    print(f\"   Errors: {len(validation['errors'])}\")\n                    for error in validation['errors'][:2]:\n                        print(f\"     - {error}\")\n                \n                if validation['warnings']:\n                    print(f\"   Warnings: {len(validation['warnings'])}\")\n                    for warning in validation['warnings'][:2]:\n                        print(f\"     - {warning}\")\n                \n                if validation['test_results']:\n                    passed_tests = sum(1 for t in validation['test_results'] if t['passed'])\n                    total_tests = len(validation['test_results'])\n                    print(f\"   Tests: {passed_tests}/{total_tests} passed\")\n                \n                # Show integration capability\n                if validation['valid']:\n                    print(f\"\\n🔗 Integration Available:\")\n                    print(f\"   Code can be safely integrated into the system\")\n                    print(f\"   Would add new reasoning capabilities\")\n                else:\n                    print(f\"\\n⚠️  Integration Blocked:\")\n                    print(f\"   Code failed safety validation\")\n            \n            else:\n                print(f\"❌ Code generation failed: {result.get('error')}\")\n        \n        except Exception as e:\n            print(f\"❌ Self-extension error: {str(e)}\")\n        \n        # Show current capabilities\n        capabilities = self.mind.list_capabilities()\n        print(f\"\\n📊 Current System Capabilities:\")\n        print(f\"   Core: {len(capabilities['core_capabilities'])}\")\n        print(f\"   Learned: {len(capabilities['learned_capabilities'])}\")\n        print(f\"   Total: {capabilities['total_capabilities']}\")\n        \n        self.wait_for_user()\n    \n    def demo_safety_system(self):\n        \"\"\"Demonstrate safety oversight capabilities.\"\"\"\n        print(\"🛡️  SAFETY OVERSIGHT\")\n        print(\"-\" * 30)\n        \n        # Test safety system with various operations\n        test_operations = [\n            {\n                'name': 'Safe Text Processing',\n                'data': 'Analyze the sentiment of this text',\n                'expected': 'APPROVED'\n            },\n            {\n                'name': 'Potentially Risky Code',\n                'data': 'exec(\"import os; os.system(\\\"rm -rf /\\\")\")',\n                'expected': 'BLOCKED'\n            },\n            {\n                'name': 'Self-Modification Request',\n                'data': 'Generate code to modify the neural network weights',\n                'expected': 'REQUIRES_APPROVAL'\n            }\n        ]\n        \n        for test_op in test_operations:\n            print(f\"\\n🔍 Testing: {test_op['name']}\")\n            print(f\"   Input: {test_op['data'][:50]}{'...' if len(test_op['data']) > 50 else ''}\")\n            \n            try:\n                # Process through HybridMind (safety is automatically evaluated)\n                result = self.mind.process(\n                    test_op['data'],\n                    context={'safety_test': True}\n                )\n                \n                if result.success:\n                    print(f\"   ✅ APPROVED - Processing completed\")\n                    print(f\"   Confidence: {result.confidence:.2f}\")\n                else:\n                    print(f\"   🚫 BLOCKED - {result.explanation}\")\n                    if result.errors:\n                        print(f\"   Reason: {result.errors[0]}\")\n            \n            except Exception as e:\n                print(f\"   ❌ ERROR: {str(e)}\")\n        \n        # Show safety system status\n        if self.mind.safety_oversight:\n            safety_status = self.mind.safety_oversight.get_safety_status()\n            print(f\"\\n📊 Safety System Status:\")\n            print(f\"   Emergency Stop: {'🔴 ACTIVE' if safety_status['emergency_stop_active'] else '🟢 INACTIVE'}\")\n            print(f\"   Active Rules: {safety_status['active_rules_count']}\")\n            print(f\"   Recent Events: {safety_status['recent_events_count']}\")\n            print(f\"   System Health: {safety_status['system_health'].upper()}\")\n        \n        self.wait_for_user()\n    \n    def demo_integrated_processing(self):\n        \"\"\"Demonstrate integrated processing capabilities.\"\"\"\n        print(\"🎯 INTEGRATED PROCESSING\")\n        print(\"-\" * 30)\n        \n        # Complex queries that benefit from integrated processing\n        integrated_queries = [\n            {\n                'query': 'What are the logical implications of machine learning for human employment?',\n                'description': 'Complex reasoning requiring both logical analysis and pattern recognition'\n            },\n            {\n                'query': 'If artificial intelligence systems become more capable than humans, what safety measures should be in place?',\n                'description': 'Ethical and safety reasoning with future projections'\n            },\n            {\n                'query': 'How do symbolic reasoning and neural networks complement each other in AI systems?',\n                'description': 'Meta-reasoning about AI architectures'\n            }\n        ]\n        \n        for i, query_data in enumerate(integrated_queries, 1):\n            print(f\"\\n🎯 Query {i}: {query_data['description']}\")\n            print(f\"Question: {query_data['query']}\")\n            \n            try:\n                # Use automatic mode selection for optimal processing\n                result = self.mind.process(\n                    query_data['query'],\n                    context={'integrated_demo': True}\n                )\n                \n                print(f\"\\n   📊 Processing Results:\")\n                print(f\"   Success: {'✅' if result.success else '❌'}\")\n                print(f\"   Mode Used: {result.processing_mode.value}\")\n                print(f\"   Processing Time: {result.processing_time:.3f}s\")\n                print(f\"   Confidence: {result.confidence:.2f}\")\n                print(f\"   Explanation: {result.explanation[:100]}...\")\n                \n                if 'fusion_path' in result.metadata:\n                    print(f\"   Fusion Path: {' → '.join(result.metadata['fusion_path'])}\")\n            \n            except Exception as e:\n                print(f\"   ❌ Processing failed: {str(e)}\")\n            \n            if i < len(integrated_queries):\n                print(\"   \" + \"-\" * 40)\n        \n        self.wait_for_user()\n    \n    def demo_final_status(self):\n        \"\"\"Show final system status and statistics.\"\"\"\n        print(\"📈 FINAL SYSTEM STATUS\")\n        print(\"-\" * 30)\n        \n        status = self.mind.get_system_status()\n        stats = status['statistics']\n        \n        print(f\"📊 Processing Statistics:\")\n        print(f\"   Total Requests: {stats['total_requests']}\")\n        print(f\"   Successful: {stats['successful_requests']}\")\n        print(f\"   Failed: {stats['failed_requests']}\")\n        \n        if stats['total_requests'] > 0:\n            success_rate = stats['successful_requests'] / stats['total_requests'] * 100\n            print(f\"   Success Rate: {success_rate:.1f}%\")\n        \n        print(f\"   Average Processing Time: {stats['average_processing_time']:.3f}s\")\n        print(f\"   Capabilities Learned: {stats['capabilities_learned']}\")\n        print(f\"   Safety Interventions: {stats['safety_interventions']}\")\n        \n        uptime = time.time() - stats['uptime_start']\n        print(f\"   Total Uptime: {uptime:.2f}s\")\n        \n        # Component statistics\n        if 'symbolic_stats' in status:\n            symbolic_stats = status['symbolic_stats']\n            print(f\"\\n🧮 Symbolic Engine:\")\n            print(f\"   Facts: {symbolic_stats.get('facts_count', 0)}\")\n            print(f\"   Rules: {symbolic_stats.get('rules_count', 0)}\")\n            print(f\"   Graph Nodes: {symbolic_stats.get('graph_nodes', 0)}\")\n        \n        if 'neural_stats' in status:\n            neural_stats = status['neural_stats']\n            print(f\"\\n🧠 Neural Engine:\")\n            print(f\"   Learned Patterns: {neural_stats.get('learned_patterns', 0)}\")\n            print(f\"   Processing History: {neural_stats.get('processing_history', 0)}\")\n        \n        if 'fusion_stats' in status:\n            fusion_stats = status['fusion_stats']\n            print(f\"\\n🔄 Fusion System:\")\n            metrics = fusion_stats.get('metrics', {})\n            print(f\"   Total Fusions: {metrics.get('total_fusions', 0)}\")\n            print(f\"   Success Rate: {fusion_stats.get('success_rate', 0):.2f}\")\n            print(f\"   Most Used Mode: {fusion_stats.get('most_used_mode', 'none')}\")\n        \n        print(f\"\\n✨ HybridMind Demo Completed Successfully!\")\n        print(f\"   The system demonstrated:\")\n        print(f\"   ✅ Symbolic reasoning and logical inference\")\n        print(f\"   ✅ Neural pattern recognition and learning\")\n        print(f\"   ✅ Hybrid symbolic-neural fusion\")\n        print(f\"   ✅ Self-extension with code generation\")\n        print(f\"   ✅ Comprehensive safety oversight\")\n        print(f\"   ✅ Integrated multi-modal processing\")\n    \n    def wait_for_user(self):\n        \"\"\"Wait for user input to continue.\"\"\"\n        try:\n            input(\"\\n⏸️  Press Enter to continue...\")\n            print()\n        except KeyboardInterrupt:\n            raise\n        except:\n            time.sleep(2)  # Auto-continue if input fails\n\n\ndef main():\n    \"\"\"Main demo function.\"\"\"\n    try:\n        demo = HybridMindDemo()\n        demo.run_demo()\n    except Exception as e:\n        print(f\"\\n❌ Demo initialization failed: {e}\")\n        logger.exception(\"Demo failed to start\")\n        return 1\n    \n    return 0\n\n\nif __name__ == \"__main__\":\n    sys.exit(main())"