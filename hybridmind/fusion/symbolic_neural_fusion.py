"""
Symbolic-Neural Fusion Layer for HybridMind

This module implements the fusion layer that bridges symbolic reasoning
and neural processing, enabling hybrid AI capabilities that combine
the interpretability of symbolic logic with the pattern recognition
power of neural networks.
"""

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, List, Tuple, Any, Optional, Union
from dataclasses import dataclass, field
import logging
from enum import Enum
import json
from collections import defaultdict

from ..engines.symbolic_engine import SymbolicReasoningEngine, Fact, Rule, RuleType
from ..engines.neural_engine import NeuralProcessingEngine, NeuralPattern, ProcessingResult

logger = logging.getLogger(__name__)


class FusionMode(Enum):
    """Modes of symbolic-neural fusion."""
    SEQUENTIAL = "sequential"  # Neural then symbolic or vice versa
    PARALLEL = "parallel"     # Both process simultaneously  
    ITERATIVE = "iterative"   # Back-and-forth refinement
    GUIDED = "guided"         # One guides the other
    ENSEMBLE = "ensemble"     # Combine outputs


@dataclass
class FusionResult:
    """Result from symbolic-neural fusion processing."""
    symbolic_output: Dict[str, Any]
    neural_output: ProcessingResult
    fused_reasoning: Dict[str, Any]
    confidence: float
    fusion_path: List[str]
    explanation: str


@dataclass
class HybridConcept:
    """Represents a concept that bridges symbolic and neural representations."""
    concept_id: str
    symbolic_form: List[str]  # Symbolic predicates/rules
    neural_embedding: np.ndarray
    confidence: float
    evidence: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)


class ConceptTranslator:
    """Translates between symbolic and neural representations."""
    
    def __init__(self):
        self.concept_mappings = {}
        self.embedding_to_symbol = {}
        self.symbol_to_embedding = {}
        self.translation_cache = {}
        
    def add_concept_mapping(self, concept: HybridConcept) -> None:
        """Add a mapping between symbolic and neural forms."""
        self.concept_mappings[concept.concept_id] = concept
        
        # Create bidirectional mappings
        for symbol in concept.symbolic_form:
            self.symbol_to_embedding[symbol] = concept.neural_embedding
        
        # Use a hash of the embedding for reverse lookup
        embedding_key = hash(tuple(concept.neural_embedding.flatten()))
        self.embedding_to_symbol[embedding_key] = concept.symbolic_form
    
    def neural_to_symbolic(self, neural_pattern: NeuralPattern, 
                          threshold: float = 0.8) -> List[str]:
        """Convert neural pattern to symbolic representation."""
        cache_key = f"n2s_{neural_pattern.pattern_id}"
        if cache_key in self.translation_cache:
            return self.translation_cache[cache_key]
        
        symbolic_forms = []
        
        # Find matching concepts by embedding similarity
        for concept in self.concept_mappings.values():
            similarity = np.dot(neural_pattern.embedding, concept.neural_embedding) / (
                np.linalg.norm(neural_pattern.embedding) * np.linalg.norm(concept.neural_embedding)
            )
            
            if similarity > threshold:
                symbolic_forms.extend(concept.symbolic_form)
        
        # If no direct mapping, generate symbolic form from pattern metadata
        if not symbolic_forms and neural_pattern.metadata:
            symbolic_forms = self._generate_symbolic_from_metadata(neural_pattern.metadata)
        
        self.translation_cache[cache_key] = symbolic_forms
        return symbolic_forms
    
    def symbolic_to_neural(self, symbolic_fact: Fact) -> Optional[np.ndarray]:
        """Convert symbolic fact to neural embedding."""
        fact_str = str(symbolic_fact)
        
        if fact_str in self.symbol_to_embedding:
            return self.symbol_to_embedding[fact_str]
        
        # Generate embedding based on predicate and arguments
        # This is a simplified approach - could use more sophisticated methods
        predicate_embedding = self._get_predicate_embedding(symbolic_fact.predicate)
        
        if symbolic_fact.arguments:
            arg_embeddings = [self._get_argument_embedding(arg) for arg in symbolic_fact.arguments]
            combined_embedding = np.concatenate([predicate_embedding] + arg_embeddings)
        else:
            combined_embedding = predicate_embedding
        
        # Normalize to standard size
        if len(combined_embedding) < 384:  # Standard embedding size
            padding = np.zeros(384 - len(combined_embedding))
            combined_embedding = np.concatenate([combined_embedding, padding])
        elif len(combined_embedding) > 384:
            combined_embedding = combined_embedding[:384]
        
        return combined_embedding
    
    def _generate_symbolic_from_metadata(self, metadata: Dict[str, Any]) -> List[str]:
        """Generate symbolic forms from neural pattern metadata."""
        symbolic_forms = []
        
        if 'text' in metadata:
            # Extract predicates from text (simplified)
            text = metadata['text'].lower()
            if 'is' in text:
                parts = text.split(' is ')
                if len(parts) == 2:
                    symbolic_forms.append(f"is({parts[0].strip()}, {parts[1].strip()})")
            
            if 'has' in text:
                parts = text.split(' has ')
                if len(parts) == 2:
                    symbolic_forms.append(f"has({parts[0].strip()}, {parts[1].strip()})")
        
        if 'category' in metadata:
            symbolic_forms.append(f"category({metadata.get('entity', 'X')}, {metadata['category']})")
        
        return symbolic_forms
    
    def _get_predicate_embedding(self, predicate: str) -> np.ndarray:
        """Get embedding for a predicate."""
        # Simple hash-based embedding - could use learned embeddings
        hash_val = hash(predicate) % 1000000
        np.random.seed(hash_val)
        return np.random.normal(0, 0.1, 128)
    
    def _get_argument_embedding(self, argument: str) -> np.ndarray:
        """Get embedding for an argument."""
        # Simple hash-based embedding
        hash_val = hash(argument) % 1000000
        np.random.seed(hash_val)
        return np.random.normal(0, 0.1, 64)


class FusionController:
    """Controls the fusion process between symbolic and neural engines."""
    
    def __init__(self, symbolic_engine: SymbolicReasoningEngine,
                 neural_engine: NeuralProcessingEngine):
        self.symbolic_engine = symbolic_engine
        self.neural_engine = neural_engine
        self.translator = ConceptTranslator()
        self.fusion_history = []
        
    def fuse_reasoning(self, query: str, mode: FusionMode = FusionMode.ITERATIVE,
                      max_iterations: int = 3) -> FusionResult:
        """Main fusion reasoning method."""
        logger.info(f"Starting fusion reasoning with mode: {mode}")
        
        if mode == FusionMode.SEQUENTIAL:
            return self._sequential_fusion(query)
        elif mode == FusionMode.PARALLEL:
            return self._parallel_fusion(query)
        elif mode == FusionMode.ITERATIVE:
            return self._iterative_fusion(query, max_iterations)
        elif mode == FusionMode.GUIDED:
            return self._guided_fusion(query)
        elif mode == FusionMode.ENSEMBLE:
            return self._ensemble_fusion(query)
        else:
            raise ValueError(f"Unknown fusion mode: {mode}")
    
    def _sequential_fusion(self, query: str) -> FusionResult:
        """Neural processing followed by symbolic reasoning."""
        fusion_path = ["neural_first", "symbolic_second"]
        
        # Step 1: Neural processing
        neural_result = self.neural_engine.process_text([query])
        
        # Step 2: Convert neural patterns to symbolic facts
        symbolic_facts = []
        for pattern in neural_result.patterns:
            symbolic_forms = self.translator.neural_to_symbolic(pattern)
            for form in symbolic_forms:
                symbolic_facts.append(form)
        
        # Step 3: Symbolic reasoning
        symbolic_output = {}
        if symbolic_facts:
            # Add derived facts to symbolic engine temporarily
            for fact_str in symbolic_facts:
                self.symbolic_engine.add_fact(fact_str)
            
            symbolic_output = self.symbolic_engine.query(query, method="forward")
        
        # Combine results
        fused_reasoning = self._combine_outputs(symbolic_output, neural_result)
        
        return FusionResult(
            symbolic_output=symbolic_output,
            neural_output=neural_result,
            fused_reasoning=fused_reasoning,
            confidence=self._calculate_fusion_confidence(symbolic_output, neural_result),
            fusion_path=fusion_path,
            explanation=self._generate_explanation(fusion_path, symbolic_output, neural_result)
        )
    
    def _parallel_fusion(self, query: str) -> FusionResult:
        """Simultaneous symbolic and neural processing."""
        fusion_path = ["parallel_processing"]
        
        # Process simultaneously
        neural_result = self.neural_engine.process_text([query])
        symbolic_output = self.symbolic_engine.query(query, method="forward")
        
        # Cross-validate results
        fused_reasoning = self._cross_validate_outputs(symbolic_output, neural_result)
        
        return FusionResult(
            symbolic_output=symbolic_output,
            neural_output=neural_result,
            fused_reasoning=fused_reasoning,
            confidence=self._calculate_fusion_confidence(symbolic_output, neural_result),
            fusion_path=fusion_path,
            explanation=self._generate_explanation(fusion_path, symbolic_output, neural_result)
        )
    
    def _iterative_fusion(self, query: str, max_iterations: int) -> FusionResult:
        """Iterative refinement between symbolic and neural."""
        fusion_path = ["iterative_start"]
        
        current_query = query
        symbolic_output = {}
        neural_result = None
        
        for iteration in range(max_iterations):
            fusion_path.append(f"iteration_{iteration}")
            
            # Neural processing
            neural_result = self.neural_engine.process_text([current_query])
            fusion_path.append(f"neural_iter_{iteration}")
            
            # Convert to symbolic and reason
            symbolic_facts = []
            for pattern in neural_result.patterns:
                symbolic_forms = self.translator.neural_to_symbolic(pattern)
                symbolic_facts.extend(symbolic_forms)
            
            if symbolic_facts:
                # Update knowledge base
                for fact_str in symbolic_facts:
                    self.symbolic_engine.add_fact(fact_str)
                
                symbolic_output = self.symbolic_engine.query(current_query, method="forward")
                fusion_path.append(f"symbolic_iter_{iteration}")
                
                # Generate refined query for next iteration
                current_query = self._refine_query(current_query, symbolic_output, neural_result)
                fusion_path.append(f"refine_iter_{iteration}")
            
            # Check convergence
            if iteration > 0 and self._has_converged(symbolic_output):
                fusion_path.append("converged")
                break
        
        fused_reasoning = self._iterative_combine(symbolic_output, neural_result)
        
        return FusionResult(
            symbolic_output=symbolic_output,
            neural_output=neural_result or ProcessingResult([], np.array([])),
            fused_reasoning=fused_reasoning,
            confidence=self._calculate_fusion_confidence(symbolic_output, neural_result),
            fusion_path=fusion_path,
            explanation=self._generate_explanation(fusion_path, symbolic_output, neural_result)
        )
    
    def _guided_fusion(self, query: str, guide: str = "symbolic") -> FusionResult:
        """One engine guides the other."""
        fusion_path = [f"{guide}_guided"]
        
        if guide == "symbolic":
            # Symbolic reasoning guides neural processing
            symbolic_output = self.symbolic_engine.query(query, method="forward")
            fusion_path.append("symbolic_guide")
            
            # Use symbolic results to focus neural processing
            focused_inputs = self._extract_neural_targets(symbolic_output)
            neural_result = self.neural_engine.process_text(focused_inputs)
            fusion_path.append("neural_focused")
            
        else:  # neural guided
            # Neural processing guides symbolic reasoning
            neural_result = self.neural_engine.process_text([query])
            fusion_path.append("neural_guide")
            
            # Convert patterns to symbolic facts
            guided_facts = []
            for pattern in neural_result.patterns:
                symbolic_forms = self.translator.neural_to_symbolic(pattern)
                guided_facts.extend(symbolic_forms)
            
            # Add to knowledge base and reason
            for fact_str in guided_facts:
                self.symbolic_engine.add_fact(fact_str)
            
            symbolic_output = self.symbolic_engine.query(query, method="backward")
            fusion_path.append("symbolic_guided")
        
        fused_reasoning = self._guided_combine(symbolic_output, neural_result, guide)
        
        return FusionResult(
            symbolic_output=symbolic_output,
            neural_output=neural_result,
            fused_reasoning=fused_reasoning,
            confidence=self._calculate_fusion_confidence(symbolic_output, neural_result),
            fusion_path=fusion_path,
            explanation=self._generate_explanation(fusion_path, symbolic_output, neural_result)
        )
    
    def _ensemble_fusion(self, query: str) -> FusionResult:
        """Ensemble approach combining multiple fusion strategies."""
        fusion_path = ["ensemble_start"]
        
        # Run multiple fusion strategies
        sequential_result = self._sequential_fusion(query)
        parallel_result = self._parallel_fusion(query)
        
        fusion_path.extend(["sequential_done", "parallel_done"])
        
        # Combine ensemble results
        ensemble_symbolic = self._combine_symbolic_outputs([
            sequential_result.symbolic_output,
            parallel_result.symbolic_output
        ])
        
        ensemble_neural = self._combine_neural_outputs([
            sequential_result.neural_output,
            parallel_result.neural_output
        ])
        
        fused_reasoning = {
            'ensemble_agreement': self._measure_agreement([
                sequential_result.fused_reasoning,
                parallel_result.fused_reasoning
            ]),
            'weighted_combination': self._weighted_combine([
                (sequential_result, 0.6),
                (parallel_result, 0.4)
            ])
        }
        
        fusion_path.append("ensemble_combined")
        
        return FusionResult(
            symbolic_output=ensemble_symbolic,
            neural_output=ensemble_neural,
            fused_reasoning=fused_reasoning,
            confidence=self._calculate_ensemble_confidence([sequential_result, parallel_result]),
            fusion_path=fusion_path,
            explanation=self._generate_ensemble_explanation([sequential_result, parallel_result])
        )
    
    def learn_concept_mapping(self, text_examples: List[str], 
                            symbolic_examples: List[str]) -> None:
        """Learn mappings between neural patterns and symbolic concepts."""
        if len(text_examples) != len(symbolic_examples):
            raise ValueError("Text and symbolic examples must have same length")
        
        for text, symbolic in zip(text_examples, symbolic_examples):
            # Process text to get neural pattern
            neural_result = self.neural_engine.process_text([text])
            
            if neural_result.patterns:
                pattern = neural_result.patterns[0]
                
                # Create hybrid concept
                concept = HybridConcept(
                    concept_id=f"learned_{len(self.translator.concept_mappings)}",
                    symbolic_form=[symbolic],
                    neural_embedding=pattern.embedding,
                    confidence=0.8,
                    evidence=[text]
                )
                
                self.translator.add_concept_mapping(concept)
                logger.info(f"Learned concept mapping: {text} -> {symbolic}")
    
    def explain_fusion_decision(self, result: FusionResult) -> Dict[str, Any]:
        """Provide detailed explanation of fusion decision process."""
        return {
            'fusion_path': result.fusion_path,
            'reasoning_steps': {
                'symbolic_reasoning': result.symbolic_output.get('reasoning_path', []),
                'neural_patterns': [p.metadata for p in result.neural_output.patterns],
                'translation_steps': self._get_translation_steps(result)
            },
            'confidence_breakdown': self._analyze_confidence(result),
            'alternative_paths': self._suggest_alternatives(result),
            'validation': self._validate_fusion_result(result)
        }
    
    # Helper methods for fusion operations
    
    def _combine_outputs(self, symbolic_output: Dict, neural_result: ProcessingResult) -> Dict[str, Any]:
        """Combine symbolic and neural outputs."""
        return {
            'symbolic_facts': symbolic_output.get('results', []),
            'neural_patterns': [p.pattern_id for p in neural_result.patterns],
            'cross_validation': self._cross_validate_simple(symbolic_output, neural_result),
            'unified_confidence': np.mean([
                symbolic_output.get('confidence', 0),
                np.mean([p.confidence for p in neural_result.patterns]) if neural_result.patterns else 0
            ])
        }
    
    def _cross_validate_outputs(self, symbolic_output: Dict, neural_result: ProcessingResult) -> Dict[str, Any]:
        """Cross-validate symbolic and neural outputs."""
        validation_score = 0.0
        agreements = []
        
        # Check if neural patterns support symbolic conclusions
        symbolic_facts = symbolic_output.get('results', [])
        
        for fact in symbolic_facts:
            # Find supporting neural patterns
            supporting_patterns = []
            for pattern in neural_result.patterns:
                if self._pattern_supports_fact(pattern, fact):
                    supporting_patterns.append(pattern)
            
            if supporting_patterns:
                agreements.append({
                    'fact': fact,
                    'supporting_patterns': len(supporting_patterns),
                    'support_confidence': np.mean([p.confidence for p in supporting_patterns])
                })
                validation_score += 1.0
        
        if symbolic_facts:
            validation_score /= len(symbolic_facts)
        
        return {
            'validation_score': validation_score,
            'agreements': agreements,
            'total_facts': len(symbolic_facts),
            'supported_facts': len(agreements)
        }
    
    def _pattern_supports_fact(self, pattern: NeuralPattern, fact: Dict) -> bool:
        """Check if neural pattern supports symbolic fact."""
        # Simplified support check - could be more sophisticated
        if 'fact' in fact:
            fact_text = fact['fact'].lower()
            if 'text' in pattern.metadata:
                pattern_text = pattern.metadata['text'].lower()
                # Simple keyword overlap check
                fact_words = set(fact_text.split())
                pattern_words = set(pattern_text.split())
                overlap = len(fact_words.intersection(pattern_words))
                return overlap > 0
        return False
    
    def _calculate_fusion_confidence(self, symbolic_output: Dict, neural_result: ProcessingResult) -> float:
        """Calculate overall confidence in fusion result."""
        symbolic_conf = symbolic_output.get('confidence', 0.0)
        
        if neural_result.patterns:
            neural_conf = np.mean([p.confidence for p in neural_result.patterns])
        else:
            neural_conf = 0.0
        
        # Weighted combination with agreement bonus
        base_confidence = 0.6 * symbolic_conf + 0.4 * neural_conf
        
        # Agreement bonus
        if symbolic_output.get('results') and neural_result.patterns:
            cross_val = self._cross_validate_simple(symbolic_output, neural_result)
            agreement_bonus = cross_val.get('validation_score', 0) * 0.2
            return min(1.0, base_confidence + agreement_bonus)
        
        return base_confidence
    
    def _cross_validate_simple(self, symbolic_output: Dict, neural_result: ProcessingResult) -> Dict:
        """Simplified cross-validation."""
        return {'validation_score': 0.5}  # Placeholder
    
    def _generate_explanation(self, fusion_path: List[str], 
                            symbolic_output: Dict, neural_result: ProcessingResult) -> str:
        """Generate human-readable explanation of fusion process."""
        explanation = f"Fusion process followed path: {' -> '.join(fusion_path)}\n"
        
        if symbolic_output.get('results'):
            explanation += f"Symbolic reasoning found {len(symbolic_output['results'])} relevant facts.\n"
        
        if neural_result.patterns:
            explanation += f"Neural processing identified {len(neural_result.patterns)} patterns.\n"
        
        explanation += f"Combined confidence: {self._calculate_fusion_confidence(symbolic_output, neural_result):.2f}"
        
        return explanation
    
    def _refine_query(self, query: str, symbolic_output: Dict, neural_result: ProcessingResult) -> str:
        """Refine query based on current results."""
        # Simple refinement - could be more sophisticated
        if symbolic_output.get('results'):
            # Add context from symbolic results
            return f"{query} given that " + "; ".join([
                str(r.get('fact', '')) for r in symbolic_output['results'][:2]
            ])
        return query
    
    def _has_converged(self, symbolic_output: Dict) -> bool:
        """Check if iterative process has converged."""
        # Simple convergence check
        return symbolic_output.get('confidence', 0) > 0.8
    
    def _iterative_combine(self, symbolic_output: Dict, neural_result: ProcessingResult) -> Dict[str, Any]:
        """Combine results from iterative fusion."""
        return {
            'final_symbolic': symbolic_output,
            'final_neural': len(neural_result.patterns) if neural_result else 0,
            'iterative_convergence': self._has_converged(symbolic_output)
        }
    
    def _extract_neural_targets(self, symbolic_output: Dict) -> List[str]:
        """Extract focused targets for neural processing from symbolic results."""
        targets = []
        for result in symbolic_output.get('results', []):
            if 'fact' in result:
                targets.append(result['fact'])
        return targets or ["general query"]
    
    def _guided_combine(self, symbolic_output: Dict, neural_result: ProcessingResult, guide: str) -> Dict[str, Any]:
        """Combine results from guided fusion."""
        return {
            'guide_engine': guide,
            'guided_results': symbolic_output if guide == 'neural' else neural_result.patterns,
            'guide_confidence': symbolic_output.get('confidence', 0) if guide == 'symbolic' else np.mean([p.confidence for p in neural_result.patterns]) if neural_result.patterns else 0
        }
    
    def _combine_symbolic_outputs(self, outputs: List[Dict]) -> Dict:
        """Combine multiple symbolic outputs."""
        combined = {'results': []}
        for output in outputs:
            combined['results'].extend(output.get('results', []))
        combined['confidence'] = np.mean([o.get('confidence', 0) for o in outputs])
        return combined
    
    def _combine_neural_outputs(self, outputs: List[ProcessingResult]) -> ProcessingResult:
        """Combine multiple neural outputs."""
        all_patterns = []
        all_embeddings = []
        
        for output in outputs:
            all_patterns.extend(output.patterns)
            if len(output.embeddings) > 0:
                all_embeddings.append(output.embeddings)
        
        combined_embeddings = np.concatenate(all_embeddings) if all_embeddings else np.array([])
        
        return ProcessingResult(
            patterns=all_patterns,
            embeddings=combined_embeddings
        )
    
    def _measure_agreement(self, results: List[Dict]) -> float:
        """Measure agreement between fusion results."""
        # Simplified agreement measure
        if len(results) < 2:
            return 1.0
        
        # Compare result counts as a proxy for agreement
        counts = [len(r.get('symbolic_facts', [])) for r in results]
        if max(counts) == 0:
            return 1.0
        
        agreement = 1.0 - (max(counts) - min(counts)) / max(counts)
        return max(0.0, agreement)
    
    def _weighted_combine(self, weighted_results: List[Tuple[FusionResult, float]]) -> Dict[str, Any]:
        """Combine results with weights."""
        combined = {
            'weighted_confidence': sum(r.confidence * w for r, w in weighted_results),
            'component_results': len(weighted_results)
        }
        return combined
    
    def _calculate_ensemble_confidence(self, results: List[FusionResult]) -> float:
        """Calculate confidence for ensemble results."""
        individual_confidences = [r.confidence for r in results]
        agreement = self._measure_agreement([r.fused_reasoning for r in results])
        
        # Higher confidence with agreement
        base_confidence = np.mean(individual_confidences)
        return min(1.0, base_confidence + agreement * 0.1)
    
    def _generate_ensemble_explanation(self, results: List[FusionResult]) -> str:
        """Generate explanation for ensemble results."""
        return f"Ensemble of {len(results)} fusion strategies with average confidence {np.mean([r.confidence for r in results]):.2f}"
    
    def _get_translation_steps(self, result: FusionResult) -> List[Dict]:
        """Get translation steps performed during fusion."""
        return []  # Placeholder for translation logging
    
    def _analyze_confidence(self, result: FusionResult) -> Dict[str, float]:
        """Analyze confidence breakdown."""
        return {
            'symbolic_confidence': result.symbolic_output.get('confidence', 0),
            'neural_confidence': np.mean([p.confidence for p in result.neural_output.patterns]) if result.neural_output.patterns else 0,
            'fusion_confidence': result.confidence
        }
    
    def _suggest_alternatives(self, result: FusionResult) -> List[str]:
        """Suggest alternative fusion approaches."""
        alternatives = []
        
        if result.confidence < 0.7:
            alternatives.append("Try iterative fusion for refinement")
            alternatives.append("Consider ensemble approach")
        
        if not result.neural_output.patterns:
            alternatives.append("Enhance neural processing with more context")
        
        if not result.symbolic_output.get('results'):
            alternatives.append("Add more symbolic rules or facts")
        
        return alternatives
    
    def _validate_fusion_result(self, result: FusionResult) -> Dict[str, Any]:
        """Validate fusion result quality."""
        return {
            'has_symbolic_results': bool(result.symbolic_output.get('results')),
            'has_neural_patterns': bool(result.neural_output.patterns),
            'confidence_threshold_met': result.confidence > 0.6,
            'explanation_available': bool(result.explanation)
        }


class SymbolicNeuralFusion:
    """Main fusion system that orchestrates symbolic-neural integration."""
    
    def __init__(self, symbolic_engine: SymbolicReasoningEngine = None,
                 neural_engine: NeuralProcessingEngine = None):
        
        self.symbolic_engine = symbolic_engine or SymbolicReasoningEngine()
        self.neural_engine = neural_engine or NeuralProcessingEngine()
        self.controller = FusionController(self.symbolic_engine, self.neural_engine)
        
        # Fusion configuration
        self.default_mode = FusionMode.ITERATIVE
        self.fusion_cache = {}
        self.performance_metrics = {
            'total_fusions': 0,
            'successful_fusions': 0,
            'average_confidence': 0.0,
            'mode_usage': defaultdict(int)
        }
        
        logger.info("Symbolic-Neural Fusion system initialized")
    
    def process(self, query: str, mode: FusionMode = None, 
                cache_result: bool = True) -> FusionResult:
        """Main processing method for fusion reasoning."""
        mode = mode or self.default_mode
        
        # Check cache
        cache_key = f"{query}_{mode.value}"
        if cache_result and cache_key in self.fusion_cache:
            logger.debug(f"Returning cached fusion result for: {query}")
            return self.fusion_cache[cache_key]
        
        # Perform fusion
        result = self.controller.fuse_reasoning(query, mode)
        
        # Update metrics
        self.performance_metrics['total_fusions'] += 1
        self.performance_metrics['mode_usage'][mode.value] += 1
        
        if result.confidence > 0.6:
            self.performance_metrics['successful_fusions'] += 1
        
        # Update average confidence
        total = self.performance_metrics['total_fusions']
        current_avg = self.performance_metrics['average_confidence']
        self.performance_metrics['average_confidence'] = (
            (current_avg * (total - 1) + result.confidence) / total
        )
        
        # Cache result
        if cache_result:
            self.fusion_cache[cache_key] = result
        
        logger.info(f"Fusion completed with confidence: {result.confidence:.2f}")
        return result
    
    def train_fusion_mappings(self, training_data: List[Dict]) -> None:
        """Train the fusion system with example mappings."""
        text_examples = []
        symbolic_examples = []
        
        for example in training_data:
            if 'text' in example and 'symbolic' in example:
                text_examples.append(example['text'])
                symbolic_examples.append(example['symbolic'])
        
        if text_examples:
            self.controller.learn_concept_mapping(text_examples, symbolic_examples)
            logger.info(f"Trained fusion with {len(text_examples)} examples")
    
    def get_explanation(self, query: str, mode: FusionMode = None) -> Dict[str, Any]:
        """Get detailed explanation of fusion reasoning."""
        result = self.process(query, mode)
        return self.controller.explain_fusion_decision(result)
    
    def optimize_fusion_strategy(self, query: str) -> FusionMode:
        """Automatically select optimal fusion strategy for query."""
        # Simple heuristics - could be ML-based
        
        # Check symbolic knowledge relevance
        symbolic_result = self.symbolic_engine.query(query, method="forward")
        has_symbolic_knowledge = bool(symbolic_result.get('results'))
        
        # Check neural pattern complexity
        neural_result = self.neural_engine.process_text([query])
        has_complex_patterns = len(neural_result.patterns) > 2
        
        if has_symbolic_knowledge and has_complex_patterns:
            return FusionMode.ITERATIVE
        elif has_symbolic_knowledge:
            return FusionMode.GUIDED  # symbolic guided
        elif has_complex_patterns:
            return FusionMode.SEQUENTIAL
        else:
            return FusionMode.PARALLEL
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Get performance metrics and analysis."""
        return {
            'metrics': self.performance_metrics.copy(),
            'cache_size': len(self.fusion_cache),
            'success_rate': (
                self.performance_metrics['successful_fusions'] / 
                max(1, self.performance_metrics['total_fusions'])
            ),
            'most_used_mode': max(
                self.performance_metrics['mode_usage'].items(),
                key=lambda x: x[1],
                default=("none", 0)
            )[0]
        }
    
    def clear_cache(self) -> None:
        """Clear fusion cache."""
        self.fusion_cache.clear()
        logger.info("Fusion cache cleared")
    
    def save_fusion_state(self, path: str) -> None:
        """Save fusion system state."""
        state = {
            'performance_metrics': dict(self.performance_metrics),
            'default_mode': self.default_mode.value,
            'concept_mappings': {
                concept_id: {
                    'symbolic_form': concept.symbolic_form,
                    'neural_embedding': concept.neural_embedding.tolist(),
                    'confidence': concept.confidence,
                    'evidence': concept.evidence,
                    'metadata': concept.metadata
                }
                for concept_id, concept in self.controller.translator.concept_mappings.items()
            }
        }
        
        with open(path, 'w') as f:
            json.dump(state, f, indent=2)
        
        logger.info(f"Fusion state saved to {path}")
    
    def load_fusion_state(self, path: str) -> None:
        """Load fusion system state."""
        with open(path, 'r') as f:
            state = json.load(f)
        
        # Restore metrics
        self.performance_metrics.update(state['performance_metrics'])
        self.default_mode = FusionMode(state['default_mode'])
        
        # Restore concept mappings
        for concept_id, concept_data in state['concept_mappings'].items():
            concept = HybridConcept(
                concept_id=concept_id,
                symbolic_form=concept_data['symbolic_form'],
                neural_embedding=np.array(concept_data['neural_embedding']),
                confidence=concept_data['confidence'],
                evidence=concept_data['evidence'],
                metadata=concept_data['metadata']
            )
            self.controller.translator.add_concept_mapping(concept)
        
        logger.info(f"Fusion state loaded from {path}")