"""
HybridMind: Main Orchestrator Class

This module implements the central orchestrator that coordinates all
HybridMind subsystems and provides the main interface for the Super AI
architecture.
"""

import asyncio
import logging
import threading
import time
from typing import Dict, List, Any, Optional, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import json
from collections import defaultdict, deque
from concurrent.futures import ThreadPoolExecutor, as_completed
import warnings

from ..engines.symbolic_engine import SymbolicReasoningEngine
from ..engines.neural_engine import NeuralProcessingEngine
from ..fusion.symbolic_neural_fusion import SymbolicNeuralFusion, FusionMode
from ..extensions.self_extension import LLMCodeGenerator, SafetyValidator, HotLoader
from ..safety.oversight import SafetyOversight

logger = logging.getLogger(__name__)


class ProcessingMode(Enum):
    """Processing modes for HybridMind operations."""
    SYMBOLIC_ONLY = "symbolic_only"
    NEURAL_ONLY = "neural_only"
    FUSION = "fusion"
    AUTO = "auto"


class SystemState(Enum):
    """System states for HybridMind."""
    INITIALIZING = "initializing"
    READY = "ready"
    PROCESSING = "processing"
    LEARNING = "learning"
    EXTENDING = "extending"
    ERROR = "error"
    SHUTDOWN = "shutdown"


@dataclass
class ProcessingRequest:
    """Represents a processing request to HybridMind."""
    request_id: str
    timestamp: float
    input_data: Any
    processing_mode: ProcessingMode
    context: Dict[str, Any] = field(default_factory=dict)
    priority: int = 0
    timeout: Optional[float] = None
    callback: Optional[Callable] = None


@dataclass
class ProcessingResult:
    """Result from HybridMind processing."""
    request_id: str
    success: bool
    result: Any
    processing_time: float
    processing_mode: ProcessingMode
    confidence: float
    explanation: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)


class HybridMind:
    """
    Main HybridMind Super AI Architecture
    
    Orchestrates symbolic reasoning, neural processing, multi-modal consciousness,
    collaborative intelligence, and self-extending capabilities into a unified
    system with built-in safety mechanisms.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize HybridMind system."""
        self.config = config or self._default_config()
        
        # System state
        self.state = SystemState.INITIALIZING
        self.system_id = f"hybridmind_{int(time.time())}"
        self.initialization_time = time.time()
        
        # Core components
        self.symbolic_engine = None
        self.neural_engine = None
        self.fusion_system = None
        self.code_generator = None
        self.safety_validator = None
        self.hot_loader = None
        self.safety_oversight = None
        
        # Processing and memory
        self.request_queue = deque()
        self.processing_history = deque(maxlen=10000)
        self.learned_capabilities = {}
        self.dynamic_modules = {}
        
        # Threading and async
        self.executor = ThreadPoolExecutor(max_workers=self.config['max_workers'])
        self.processing_lock = threading.Lock()
        self.background_tasks = []
        
        # Statistics and monitoring
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'average_processing_time': 0.0,
            'capabilities_learned': 0,
            'safety_interventions': 0,
            'uptime_start': time.time()
        }
        
        # Initialize system
        self._initialize_system()
        
        logger.info(f"HybridMind initialized: {self.system_id}")
    
    def _default_config(self) -> Dict[str, Any]:
        """Default configuration for HybridMind."""
        return {
            'max_workers': 4,
            'default_timeout': 30.0,
            'enable_safety': True,
            'enable_learning': True,
            'enable_self_extension': True,
            'symbolic_config': {},
            'neural_config': {},
            'fusion_config': {},
            'safety_config': {},
            'log_level': 'INFO',
            'auto_save_interval': 300.0,  # 5 minutes
            'memory_limit_mb': 2048
        }
    
    def _initialize_system(self) -> None:
        """Initialize all HybridMind subsystems."""
        try:
            logger.info("Initializing HybridMind subsystems...")
            
            # Initialize core engines
            self.symbolic_engine = SymbolicReasoningEngine()
            self.neural_engine = NeuralProcessingEngine(self.config.get('neural_config', {}))
            
            # Initialize fusion system
            self.fusion_system = SymbolicNeuralFusion(
                self.symbolic_engine, 
                self.neural_engine
            )
            
            # Initialize self-extension components
            if self.config['enable_self_extension']:
                self.code_generator = LLMCodeGenerator()
                self.safety_validator = SafetyValidator()
                self.hot_loader = HotLoader(self)
            
            # Initialize safety oversight
            if self.config['enable_safety']:
                self.safety_oversight = SafetyOversight(self.config.get('safety_config', {}))
            
            # Initialize neural models (if configuration provided)
            if self.config.get('neural_config', {}).get('auto_initialize'):
                self.neural_engine.initialize_models(
                    input_dim=384,  # Default embedding dimension
                    num_classes=10  # Default number of classes
                )
            
            # Start background tasks
            self._start_background_tasks()
            
            self.state = SystemState.READY
            logger.info("HybridMind initialization complete")
            
        except Exception as e:
            self.state = SystemState.ERROR
            logger.error(f"HybridMind initialization failed: {e}")
            raise
    
    def process(self, input_data: Any, 
                mode: ProcessingMode = ProcessingMode.AUTO,
                context: Dict[str, Any] = None,
                priority: int = 0,
                timeout: Optional[float] = None) -> ProcessingResult:
        """
        Main processing method for HybridMind.
        
        Args:
            input_data: Data to process (text, structured data, etc.)
            mode: Processing mode (symbolic, neural, fusion, auto)
            context: Additional context for processing
            priority: Request priority (higher = more urgent)
            timeout: Maximum processing time in seconds
            
        Returns:
            ProcessingResult with results, confidence, and explanation
        """
        request_id = f"req_{int(time.time() * 1000000)}"
        start_time = time.time()
        
        # Create processing request
        request = ProcessingRequest(
            request_id=request_id,
            timestamp=start_time,
            input_data=input_data,
            processing_mode=mode,
            context=context or {},
            priority=priority,
            timeout=timeout or self.config['default_timeout']
        )
        
        # Safety evaluation
        if self.config['enable_safety'] and self.safety_oversight:
            safety_result = self._evaluate_safety(request)
            if not safety_result['approved']:
                return ProcessingResult(
                    request_id=request_id,
                    success=False,
                    result=None,
                    processing_time=time.time() - start_time,
                    processing_mode=mode,
                    confidence=0.0,
                    explanation=f"Request blocked by safety system: {safety_result['reasoning']}",
                    errors=safety_result.get('blocking_factors', [])
                )
        
        try:
            # Update statistics
            self.stats['total_requests'] += 1
            
            # Determine processing mode if AUTO
            if mode == ProcessingMode.AUTO:
                mode = self._determine_optimal_mode(input_data, context or {})
            
            # Execute processing
            result = self._execute_processing(request, mode)
            
            # Update success statistics
            if result.success:
                self.stats['successful_requests'] += 1
            else:
                self.stats['failed_requests'] += 1
            
            # Update average processing time
            processing_time = result.processing_time
            total_requests = self.stats['total_requests']
            current_avg = self.stats['average_processing_time']
            self.stats['average_processing_time'] = (
                (current_avg * (total_requests - 1) + processing_time) / total_requests
            )
            
            # Store in history
            self.processing_history.append({
                'request': request,
                'result': result,
                'timestamp': time.time()
            })
            
            # Trigger learning if enabled
            if self.config['enable_learning'] and result.success:
                self._trigger_learning(request, result)
            
            return result
            
        except Exception as e:
            self.stats['failed_requests'] += 1
            logger.error(f"Processing failed for request {request_id}: {e}")
            
            return ProcessingResult(
                request_id=request_id,
                success=False,
                result=None,
                processing_time=time.time() - start_time,
                processing_mode=mode,
                confidence=0.0,
                explanation=f"Processing error: {str(e)}",
                errors=[str(e)]
            )
    
    def extend_capabilities(self, specification: str,
                          capability_type: str = "reasoning_module",
                          auto_integrate: bool = False) -> Dict[str, Any]:
        """
        Generate and integrate new capabilities.
        
        Args:
            specification: Natural language description of desired capability
            capability_type: Type of capability to generate
            auto_integrate: Whether to automatically integrate if safe
            
        Returns:
            Dictionary with generation and integration results
        """
        if not self.config['enable_self_extension']:
            return {
                'success': False,
                'error': 'Self-extension disabled in configuration'
            }
        
        if not self.code_generator or not self.safety_validator:
            return {
                'success': False,
                'error': 'Self-extension components not initialized'
            }
        
        logger.info(f"Extending capabilities: {specification}")
        
        try:
            # Generate code
            generation_spec = {
                'type': capability_type,
                'description': specification,
                'name': self._generate_capability_name(specification),
                'auto_integrate': auto_integrate
            }
            
            generated_code = self.code_generator.generate_code(generation_spec)
            
            # Validate code
            validation_result = self.safety_validator.validate_code(generated_code)
            
            result = {
                'success': True,
                'generated_code': {
                    'code_id': generated_code.code_id,
                    'type': generated_code.extension_type.value,
                    'safety_level': generated_code.safety_level.value,
                    'description': generated_code.description
                },
                'validation': validation_result,
                'integrated': False,
                'integration_result': None
            }
            
            # Integrate if validation passed and auto_integrate is True
            if validation_result['valid'] and auto_integrate:
                integration_result = self.hot_loader.integrate_code(
                    generated_code, validation_result
                )
                
                result['integrated'] = integration_result['success']
                result['integration_result'] = integration_result
                
                if integration_result['success']:
                    self.stats['capabilities_learned'] += 1
                    logger.info(f"Successfully integrated new capability: {generated_code.code_id}")
            
            return result
            
        except Exception as e:
            logger.error(f"Capability extension failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def query_symbolic(self, query: str, method: str = "forward") -> Dict[str, Any]:
        """Query the symbolic reasoning engine."""
        if self.symbolic_engine is None:
            return {'error': 'Symbolic engine not initialized'}
        
        return self.symbolic_engine.query(query, method)
    
    def process_neural(self, input_data: Any, extract_patterns: bool = True) -> Any:
        """Process data through neural engine."""
        if self.neural_engine is None:
            return {'error': 'Neural engine not initialized'}
        
        if isinstance(input_data, str):
            return self.neural_engine.process_text([input_data], extract_patterns)
        elif isinstance(input_data, list):
            if all(isinstance(item, str) for item in input_data):
                return self.neural_engine.process_text(input_data, extract_patterns)
            else:
                return self.neural_engine.process_sequences(input_data)
        else:
            return {'error': f'Unsupported input type: {type(input_data)}'}
    
    def fuse_reasoning(self, query: str, mode: FusionMode = FusionMode.AUTO) -> Dict[str, Any]:
        """Perform fusion reasoning."""
        if self.fusion_system is None:
            return {'error': 'Fusion system not initialized'}
        
        # Auto-select fusion mode if requested
        if mode == FusionMode.AUTO:
            mode = self.fusion_system.optimize_fusion_strategy(query)
        
        result = self.fusion_system.process(query, mode)
        
        return {
            'fusion_result': {
                'confidence': result.confidence,
                'explanation': result.explanation,
                'fusion_path': result.fusion_path,
                'symbolic_output': result.symbolic_output,
                'neural_patterns': len(result.neural_output.patterns)
            }
        }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status."""
        uptime = time.time() - self.stats['uptime_start']
        
        status = {
            'system_id': self.system_id,
            'state': self.state.value,
            'uptime_seconds': uptime,
            'statistics': self.stats.copy(),
            'components': {
                'symbolic_engine': self.symbolic_engine is not None,
                'neural_engine': self.neural_engine is not None,
                'fusion_system': self.fusion_system is not None,
                'safety_oversight': self.safety_oversight is not None,
                'self_extension': {
                    'code_generator': self.code_generator is not None,
                    'safety_validator': self.safety_validator is not None,
                    'hot_loader': self.hot_loader is not None
                }
            },
            'capabilities': {
                'learned_capabilities': len(self.learned_capabilities),
                'dynamic_modules': len(self.dynamic_modules),
                'processing_queue_size': len(self.request_queue)
            }
        }
        
        # Add component-specific status
        if self.symbolic_engine:
            status['symbolic_stats'] = self.symbolic_engine.get_statistics()
        
        if self.neural_engine:
            status['neural_stats'] = self.neural_engine.get_statistics()
        
        if self.fusion_system:
            status['fusion_stats'] = self.fusion_system.get_performance_report()
        
        if self.safety_oversight:
            status['safety_stats'] = self.safety_oversight.get_safety_status()
        
        return status
    
    def add_knowledge(self, knowledge_items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Add knowledge to the system."""
        added_count = 0
        
        for item in knowledge_items:
            try:
                if item.get('type') == 'fact':
                    self.symbolic_engine.add_fact(item['content'])
                    added_count += 1
                elif item.get('type') == 'rule':
                    self.symbolic_engine.add_rule(item['content'])
                    added_count += 1
                elif item.get('type') == 'training_data':
                    # Add to neural training data (simplified)
                    if 'text' in item and 'label' in item:
                        # Could be expanded to actually train models
                        added_count += 1
            except Exception as e:
                logger.error(f"Failed to add knowledge item: {e}")
        
        return {
            'success': True,
            'items_added': added_count,
            'total_items': len(knowledge_items)
        }
    
    def explain_reasoning(self, query: str) -> Dict[str, Any]:
        """Get detailed explanation of reasoning process."""
        explanations = {}
        
        # Symbolic explanation
        if self.symbolic_engine:
            explanations['symbolic'] = self.symbolic_engine.explain_reasoning(query)
        
        # Neural explanation (attention insights)
        if self.neural_engine:
            explanations['neural'] = self.neural_engine.get_attention_insights(query)
        
        # Fusion explanation
        if self.fusion_system:
            explanations['fusion'] = self.fusion_system.get_explanation(query)
        
        return explanations
    
    def shutdown(self, save_state: bool = True) -> None:
        """Gracefully shutdown HybridMind."""
        logger.info("Initiating HybridMind shutdown...")
        
        self.state = SystemState.SHUTDOWN
        
        # Stop background tasks
        for task in self.background_tasks:
            if hasattr(task, 'cancel'):
                task.cancel()
        
        # Save state if requested
        if save_state:
            self._save_system_state()
        
        # Shutdown executor
        self.executor.shutdown(wait=True)
        
        logger.info("HybridMind shutdown complete")
    
    # Internal methods
    
    def _execute_processing(self, request: ProcessingRequest, 
                          mode: ProcessingMode) -> ProcessingResult:
        """Execute the actual processing based on mode."""
        start_time = time.time()
        
        try:
            if mode == ProcessingMode.SYMBOLIC_ONLY:
                result_data = self._process_symbolic_only(request)
            elif mode == ProcessingMode.NEURAL_ONLY:
                result_data = self._process_neural_only(request)
            elif mode == ProcessingMode.FUSION:
                result_data = self._process_fusion(request)
            else:
                raise ValueError(f"Unknown processing mode: {mode}")
            
            processing_time = time.time() - start_time
            
            return ProcessingResult(
                request_id=request.request_id,
                success=True,
                result=result_data['result'],
                processing_time=processing_time,
                processing_mode=mode,
                confidence=result_data.get('confidence', 0.8),
                explanation=result_data.get('explanation', 'Processing completed successfully'),
                metadata=result_data.get('metadata', {})
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            
            return ProcessingResult(
                request_id=request.request_id,
                success=False,
                result=None,
                processing_time=processing_time,
                processing_mode=mode,
                confidence=0.0,
                explanation=f"Processing failed: {str(e)}",
                errors=[str(e)]
            )
    
    def _process_symbolic_only(self, request: ProcessingRequest) -> Dict[str, Any]:
        """Process using symbolic reasoning only."""
        if isinstance(request.input_data, str):
            symbolic_result = self.symbolic_engine.query(request.input_data, method="forward")
            
            return {
                'result': symbolic_result,
                'confidence': symbolic_result.get('confidence', 0.0),
                'explanation': f"Symbolic reasoning found {len(symbolic_result.get('results', []))} results",
                'metadata': {'processing_type': 'symbolic_only'}
            }
        else:
            raise ValueError("Symbolic processing requires string input")
    
    def _process_neural_only(self, request: ProcessingRequest) -> Dict[str, Any]:
        """Process using neural networks only."""
        neural_result = self.process_neural(request.input_data)
        
        if 'error' in neural_result:
            raise ValueError(neural_result['error'])
        
        # Extract confidence from neural patterns
        confidence = 0.0
        if hasattr(neural_result, 'patterns') and neural_result.patterns:
            confidence = sum(p.confidence for p in neural_result.patterns) / len(neural_result.patterns)
        
        return {
            'result': neural_result,
            'confidence': confidence,
            'explanation': f"Neural processing identified patterns and embeddings",
            'metadata': {'processing_type': 'neural_only'}
        }
    
    def _process_fusion(self, request: ProcessingRequest) -> Dict[str, Any]:
        """Process using fusion reasoning."""
        if isinstance(request.input_data, str):
            fusion_result = self.fuse_reasoning(request.input_data)
            
            if 'error' in fusion_result:
                raise ValueError(fusion_result['error'])
            
            fusion_data = fusion_result['fusion_result']
            
            return {
                'result': fusion_data,
                'confidence': fusion_data['confidence'],
                'explanation': fusion_data['explanation'],
                'metadata': {
                    'processing_type': 'fusion',
                    'fusion_path': fusion_data['fusion_path']
                }
            }
        else:
            raise ValueError("Fusion processing requires string input")
    
    def _determine_optimal_mode(self, input_data: Any, context: Dict[str, Any]) -> ProcessingMode:
        """Automatically determine the optimal processing mode."""
        # Simple heuristics - could be enhanced with ML-based selection
        
        if isinstance(input_data, str):
            # Text input - check for logical vs. pattern-based processing needs
            logical_indicators = ['if', 'then', 'because', 'therefore', 'implies', 'rule']
            pattern_indicators = ['similar', 'like', 'pattern', 'recognize', 'classify']
            
            text_lower = input_data.lower()
            
            logical_score = sum(1 for indicator in logical_indicators if indicator in text_lower)
            pattern_score = sum(1 for indicator in pattern_indicators if indicator in text_lower)
            
            if logical_score > pattern_score and logical_score > 0:
                return ProcessingMode.SYMBOLIC_ONLY
            elif pattern_score > logical_score and pattern_score > 0:
                return ProcessingMode.NEURAL_ONLY
            else:
                return ProcessingMode.FUSION  # Use fusion for ambiguous cases
        
        elif isinstance(input_data, list):
            # Sequential data - prefer neural processing
            return ProcessingMode.NEURAL_ONLY
        
        else:
            # Unknown data type - use fusion for robustness
            return ProcessingMode.FUSION
    
    def _evaluate_safety(self, request: ProcessingRequest) -> Dict[str, Any]:
        """Evaluate safety of a processing request."""
        operation = {
            'type': 'processing_request',
            'input_type': type(request.input_data).__name__,
            'processing_mode': request.processing_mode.value,
            'context': request.context,
            'has_code': 'code' in str(request.input_data).lower(),
            'has_sensitive_data': any(
                keyword in str(request.input_data).lower() 
                for keyword in ['password', 'secret', 'private', 'confidential']
            )
        }
        
        return self.safety_oversight.evaluate_operation(operation)
    
    def _trigger_learning(self, request: ProcessingRequest, result: ProcessingResult) -> None:
        """Trigger learning from successful processing."""
        # Simple learning trigger - could be enhanced
        if result.confidence > 0.7:
            learning_data = {
                'input': request.input_data,
                'output': result.result,
                'mode': result.processing_mode.value,
                'confidence': result.confidence,
                'timestamp': time.time()
            }
            
            # Store for potential future learning
            if hasattr(self, 'learning_buffer'):
                self.learning_buffer.append(learning_data)
    
    def _generate_capability_name(self, specification: str) -> str:
        """Generate a name for a new capability."""
        words = specification.split()[:3]  # First 3 words
        return ''.join(word.capitalize() for word in words if word.isalnum())
    
    def _start_background_tasks(self) -> None:
        """Start background tasks."""
        # Auto-save task
        if self.config.get('auto_save_interval', 0) > 0:
            save_task = threading.Timer(
                self.config['auto_save_interval'],
                self._periodic_save
            )
            save_task.daemon = True
            save_task.start()
            self.background_tasks.append(save_task)
    
    def _periodic_save(self) -> None:
        """Periodically save system state."""
        try:
            self._save_system_state()
            logger.debug("Periodic state save completed")
        except Exception as e:
            logger.error(f"Periodic save failed: {e}")
        
        # Schedule next save
        if self.state not in [SystemState.SHUTDOWN, SystemState.ERROR]:
            save_task = threading.Timer(
                self.config['auto_save_interval'],
                self._periodic_save
            )
            save_task.daemon = True
            save_task.start()
            self.background_tasks.append(save_task)
    
    def _save_system_state(self) -> None:
        """Save current system state."""
        state_data = {
            'system_id': self.system_id,
            'initialization_time': self.initialization_time,
            'statistics': self.stats,
            'learned_capabilities': self.learned_capabilities,
            'config': self.config
        }
        
        # Save component states
        try:
            if self.neural_engine:
                self.neural_engine.save_state('data/neural_engine_state.json')
            
            if self.fusion_system:
                self.fusion_system.save_fusion_state('data/fusion_state.json')
            
            # Save main state
            with open('data/hybridmind_state.json', 'w') as f:
                json.dump(state_data, f, indent=2, default=str)
            
            logger.info("System state saved successfully")
            
        except Exception as e:
            logger.error(f"Failed to save system state: {e}")
    
    # Methods for dynamic capability integration
    
    def add_reasoning_module(self, name: str, module_class: type) -> None:
        """Add a dynamically generated reasoning module."""
        self.learned_capabilities[f'reasoning_{name}'] = {
            'type': 'reasoning_module',
            'class': module_class,
            'added_time': time.time()
        }
        logger.info(f"Added reasoning module: {name}")
    
    def add_processor(self, name: str, processor_func: Callable) -> None:
        """Add a dynamically generated processor function."""
        self.learned_capabilities[f'processor_{name}'] = {
            'type': 'processor',
            'function': processor_func,
            'added_time': time.time()
        }
        logger.info(f"Added processor: {name}")
    
    def add_utility(self, name: str, utility_class: type) -> None:
        """Add a dynamically generated utility class."""
        self.learned_capabilities[f'utility_{name}'] = {
            'type': 'utility',
            'class': utility_class,
            'added_time': time.time()
        }
        logger.info(f"Added utility: {name}")
    
    def remove_dynamic_capability(self, capability_name: str) -> None:
        """Remove a dynamically added capability."""
        if capability_name in self.learned_capabilities:
            del self.learned_capabilities[capability_name]
            logger.info(f"Removed capability: {capability_name}")
    
    def list_capabilities(self) -> Dict[str, Any]:
        """List all available capabilities."""
        capabilities = {
            'core_capabilities': [
                'symbolic_reasoning',
                'neural_processing',
                'fusion_reasoning',
                'safety_oversight'
            ],
            'learned_capabilities': list(self.learned_capabilities.keys()),
            'self_extension': self.config['enable_self_extension'],
            'total_capabilities': len(self.learned_capabilities) + 4
        }
        
        if self.config['enable_self_extension']:
            capabilities['core_capabilities'].append('self_extension')
        
        return capabilities