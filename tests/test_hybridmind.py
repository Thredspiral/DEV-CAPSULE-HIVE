#!/usr/bin/env python3
"""
Tests for HybridMind Core System
"""

import pytest
import sys
from pathlib import Path

# Add the hybridmind package to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from hybridmind import HybridMind
from hybridmind.core.hybridmind import ProcessingMode, SystemState


class TestHybridMind:
    """Test cases for HybridMind core functionality."""
    
    @pytest.fixture
    def mind(self):
        """Create a HybridMind instance for testing."""
        config = {
            'enable_safety': False,  # Disable for faster testing
            'enable_learning': False,
            'enable_self_extension': False,
            'neural_config': {'auto_initialize': False}
        }
        mind_instance = HybridMind(config)
        yield mind_instance
        mind_instance.shutdown()
    
    def test_initialization(self, mind):
        """Test HybridMind initialization."""
        assert mind.state == SystemState.READY
        assert mind.system_id is not None
        assert mind.symbolic_engine is not None
        assert mind.neural_engine is not None
        assert mind.fusion_system is not None
    
    def test_system_status(self, mind):
        """Test system status retrieval."""
        status = mind.get_system_status()
        
        assert 'system_id' in status
        assert 'state' in status
        assert 'components' in status
        assert 'statistics' in status
        
        # Check component availability
        components = status['components']
        assert components['symbolic_engine'] is True
        assert components['neural_engine'] is True
        assert components['fusion_system'] is True
    
    def test_basic_processing(self, mind):
        """Test basic text processing."""
        result = mind.process("Hello, world!")
        
        assert result.success is True
        assert result.request_id is not None
        assert result.processing_time > 0
        assert result.processing_mode in ProcessingMode
        assert 0 <= result.confidence <= 1
    
    def test_processing_modes(self, mind):
        """Test different processing modes."""
        test_text = "Artificial intelligence is fascinating"
        
        # Test each processing mode
        modes = [ProcessingMode.SYMBOLIC_ONLY, ProcessingMode.NEURAL_ONLY, ProcessingMode.FUSION]
        
        for mode in modes:
            result = mind.process(test_text, mode=mode)
            assert result.processing_mode == mode
            # Note: Some modes might fail without proper setup, but should not crash
    
    def test_add_knowledge(self, mind):
        """Test adding knowledge to the system."""
        knowledge = [
            {'type': 'fact', 'content': 'test_fact(example)'},
            {'type': 'rule', 'content': 'test_rule(X) :- test_fact(X)'}
        ]
        
        result = mind.add_knowledge(knowledge)
        
        assert result['success'] is True
        assert result['items_added'] > 0
        assert result['total_items'] == 2
    
    def test_symbolic_query(self, mind):
        """Test symbolic reasoning queries."""
        # Add a fact first
        mind.add_knowledge([{'type': 'fact', 'content': 'test(example)'}])
        
        # Query the fact
        result = mind.query_symbolic("test(example)")
        
        assert isinstance(result, dict)
        assert 'query' in result
        assert 'results' in result
    
    def test_neural_processing(self, mind):
        """Test neural processing."""
        result = mind.process_neural("Test text for neural processing")
        
        # Should return a result (even if minimal without full initialization)
        assert result is not None
    
    def test_capabilities_listing(self, mind):
        """Test listing system capabilities."""
        capabilities = mind.list_capabilities()
        
        assert 'core_capabilities' in capabilities
        assert 'learned_capabilities' in capabilities
        assert 'total_capabilities' in capabilities
        assert isinstance(capabilities['core_capabilities'], list)
    
    def test_statistics_tracking(self, mind):
        """Test that statistics are properly tracked."""
        initial_stats = mind.get_system_status()['statistics']
        initial_requests = initial_stats['total_requests']
        
        # Process something
        mind.process("Test request for statistics")
        
        updated_stats = mind.get_system_status()['statistics']
        assert updated_stats['total_requests'] == initial_requests + 1
    
    def test_error_handling(self, mind):
        """Test error handling in processing."""
        # This should not crash the system
        result = mind.process(None)  # Invalid input
        
        # Should return a result indicating failure
        assert result.success is False
        assert len(result.errors) > 0


class TestHybridMindWithSafety:
    """Test HybridMind with safety systems enabled."""
    
    @pytest.fixture
    def safe_mind(self):
        """Create a HybridMind instance with safety enabled."""
        config = {
            'enable_safety': True,
            'enable_learning': False,
            'enable_self_extension': False
        }
        mind_instance = HybridMind(config)
        yield mind_instance
        mind_instance.shutdown()
    
    def test_safety_initialization(self, safe_mind):
        """Test that safety system is properly initialized."""
        assert safe_mind.safety_oversight is not None
        
        status = safe_mind.get_system_status()
        assert 'safety_stats' in status
        
        safety_stats = status['safety_stats']
        assert 'system_health' in safety_stats
    
    def test_safe_processing(self, safe_mind):
        """Test processing with safety enabled."""
        result = safe_mind.process("Analyze this safe text")
        
        # Should be allowed
        assert result.success is True
    
    def test_dangerous_input_blocking(self, safe_mind):
        """Test that dangerous inputs are blocked."""
        dangerous_input = "exec('import os; os.system(\"rm -rf /\")')"
        
        result = safe_mind.process(dangerous_input)
        
        # Should be blocked by safety system
        assert result.success is False
        assert 'safety' in result.explanation.lower() or 'block' in result.explanation.lower()


class TestHybridMindExtension:
    """Test HybridMind self-extension capabilities."""
    
    @pytest.fixture
    def extensible_mind(self):
        """Create a HybridMind instance with self-extension enabled."""
        config = {
            'enable_safety': True,
            'enable_learning': False,
            'enable_self_extension': True
        }
        mind_instance = HybridMind(config)
        yield mind_instance
        mind_instance.shutdown()
    
    def test_extension_initialization(self, extensible_mind):
        """Test that extension components are initialized."""
        assert extensible_mind.code_generator is not None
        assert extensible_mind.safety_validator is not None
        assert extensible_mind.hot_loader is not None
    
    def test_capability_extension_request(self, extensible_mind):
        """Test requesting new capabilities."""
        specification = "Create a simple utility function that reverses a string"
        
        result = extensible_mind.extend_capabilities(
            specification=specification,
            capability_type="processing_function",
            auto_integrate=False
        )
        
        assert result['success'] is True
        assert 'generated_code' in result
        assert 'validation' in result
        
        generated = result['generated_code']
        assert 'code_id' in generated
        assert 'type' in generated
        assert 'safety_level' in generated


def test_module_imports():
    """Test that all HybridMind modules can be imported."""
    # These should not raise import errors
    from hybridmind import HybridMind
    from hybridmind.engines.symbolic_engine import SymbolicReasoningEngine
    from hybridmind.engines.neural_engine import NeuralProcessingEngine
    from hybridmind.fusion.symbolic_neural_fusion import SymbolicNeuralFusion
    from hybridmind.extensions.self_extension import LLMCodeGenerator
    from hybridmind.safety.oversight import SafetyOversight
    
    # Basic instantiation tests
    assert SymbolicReasoningEngine is not None
    assert NeuralProcessingEngine is not None
    assert LLMCodeGenerator is not None


if __name__ == "__main__":
    # Run tests if executed directly
    pytest.main([__file__, "-v"])