"""
HybridMind: A Self-Extending Super AI Architecture

This package provides a revolutionary AI system that combines symbolic reasoning,
neural networks, multi-modal consciousness integration, collaborative intelligence,
and self-modifying capabilities into a unified Super AI architecture.
"""

from .core.hybridmind import HybridMind
from .engines.symbolic_engine import SymbolicReasoningEngine
from .engines.neural_engine import NeuralProcessingEngine
from .fusion.symbolic_neural_fusion import SymbolicNeuralFusion

__version__ = "1.0.0"
__author__ = "HybridMind Development Team"

__all__ = [
    "HybridMind",
    "SymbolicReasoningEngine", 
    "NeuralProcessingEngine",
    "SymbolicNeuralFusion"
]