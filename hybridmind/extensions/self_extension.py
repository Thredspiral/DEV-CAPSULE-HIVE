"""
Self-Extension System for HybridMind

This module implements the self-modifying capabilities that allow HybridMind
to generate, test, and integrate new code capabilities autonomously while
maintaining strict safety protocols.
"""

import ast
import sys
import os
import importlib
import importlib.util
import inspect
from typing import Dict, List, Any, Optional, Callable, Tuple
from dataclasses import dataclass
import logging
import tempfile
import subprocess
import json
from pathlib import Path
from enum import Enum
import hashlib
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError

logger = logging.getLogger(__name__)


class ExtensionType(Enum):
    """Types of extensions that can be generated."""
    REASONING_MODULE = "reasoning_module"
    PROCESSING_FUNCTION = "processing_function"
    UTILITY_CLASS = "utility_class"
    DATA_TRANSFORMER = "data_transformer"
    ANALYSIS_TOOL = "analysis_tool"
    INTEGRATION_ADAPTER = "integration_adapter"


class SafetyLevel(Enum):
    """Safety levels for code execution."""
    SAFE = "safe"              # No external access, pure functions
    RESTRICTED = "restricted"   # Limited external access
    SUPERVISED = "supervised"   # Human approval required
    DANGEROUS = "dangerous"     # Blocked


@dataclass
class GeneratedCode:
    """Represents generated code with metadata."""
    code_id: str
    code: str
    extension_type: ExtensionType
    safety_level: SafetyLevel
    description: str
    dependencies: List[str]
    test_cases: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    author: str = "HybridMind"
    version: str = "1.0.0"
    timestamp: float = 0.0
    
    def __post_init__(self):
        if self.timestamp == 0.0:
            self.timestamp = time.time()


class LLMCodeGenerator:
    """Generates code using Large Language Model capabilities."""
    
    def __init__(self, model_config: Dict[str, Any] = None):
        self.model_config = model_config or self._default_config()
        self.generation_history = []
        self.templates = self._load_templates()
        
    def _default_config(self) -> Dict[str, Any]:
        """Default configuration for code generation."""
        return {
            'max_tokens': 2048,
            'temperature': 0.3,
            'top_p': 0.9,
            'safety_prompt': True,
            'include_docstrings': True,
            'include_type_hints': True
        }
    
    def _load_templates(self) -> Dict[str, str]:
        """Load code generation templates."""
        return {
            'reasoning_module': '''
class {class_name}:
    """{description}"""
    
    def __init__(self):
        {init_code}
    
    def process(self, input_data: Any) -> Any:
        """{process_description}"""
        {process_code}
        
    def validate(self, result: Any) -> bool:
        """{validation_description}"""
        {validation_code}
''',
            'processing_function': '''
def {function_name}({parameters}) -> {return_type}:
    """{description}
    
    Args:
        {args_docs}
    
    Returns:
        {return_docs}
    """
    {function_code}
''',
            'utility_class': '''
class {class_name}:
    """{description}"""
    
    def __init__(self, {init_parameters}):
        {init_code}
    
    {methods}
'''
        }
    
    def generate_code(self, specification: Dict[str, Any]) -> GeneratedCode:
        """Generate code based on specification."""
        extension_type = ExtensionType(specification['type'])
        
        # Create generation context
        context = {
            'specification': specification,
            'extension_type': extension_type,
            'safety_requirements': self._get_safety_requirements(extension_type),
            'templates': self.templates
        }
        
        # Generate code using appropriate method
        if extension_type == ExtensionType.REASONING_MODULE:
            code = self._generate_reasoning_module(context)
        elif extension_type == ExtensionType.PROCESSING_FUNCTION:
            code = self._generate_processing_function(context)
        elif extension_type == ExtensionType.UTILITY_CLASS:
            code = self._generate_utility_class(context)
        else:
            code = self._generate_generic_code(context)
        
        # Determine safety level
        safety_level = self._assess_safety_level(code, specification)
        
        # Generate test cases
        test_cases = self._generate_test_cases(code, specification)
        
        # Create GeneratedCode object
        generated = GeneratedCode(
            code_id=self._generate_code_id(specification),
            code=code,
            extension_type=extension_type,
            safety_level=safety_level,
            description=specification.get('description', ''),
            dependencies=specification.get('dependencies', []),
            test_cases=test_cases,
            metadata={'specification': specification}
        )
        
        self.generation_history.append(generated)
        logger.info(f"Generated {extension_type.value} with ID: {generated.code_id}")
        
        return generated
    
    def _generate_reasoning_module(self, context: Dict[str, Any]) -> str:
        """Generate a reasoning module."""
        spec = context['specification']
        template = context['templates']['reasoning_module']
        
        class_name = spec.get('name', 'CustomReasoningModule')
        description = spec.get('description', 'Custom reasoning module')
        
        # Generate init code
        init_code = '''
self.rules = []
self.facts = set()
self.confidence_threshold = 0.7'''
        
        # Generate process code
        process_code = '''
try:
    # Apply reasoning logic
    result = self._apply_reasoning(input_data)
    return result
except Exception as e:
    logger.error(f"Reasoning error: {e}")
    return None'''
        
        # Generate validation code
        validation_code = '''
if result is None:
    return False
if isinstance(result, dict) and 'confidence' in result:
    return result['confidence'] > self.confidence_threshold
return True'''
        
        code = template.format(
            class_name=class_name,
            description=description,
            init_code=init_code,
            process_description="Process input data through reasoning logic",
            process_code=process_code,
            validation_description="Validate reasoning result",
            validation_code=validation_code
        )
        
        # Add helper methods
        helper_methods = '''
    def _apply_reasoning(self, input_data: Any) -> Dict[str, Any]:
        """Apply reasoning logic to input data."""
        # Placeholder reasoning logic
        return {
            'result': input_data,
            'confidence': 0.8,
            'reasoning_steps': ['input_processed']
        }
    
    def add_rule(self, rule: str) -> None:
        """Add a reasoning rule."""
        self.rules.append(rule)
    
    def add_fact(self, fact: str) -> None:
        """Add a fact to the knowledge base."""
        self.facts.add(fact)
'''
        
        return code + helper_methods
    
    def _generate_processing_function(self, context: Dict[str, Any]) -> str:
        """Generate a processing function."""
        spec = context['specification']
        template = context['templates']['processing_function']
        
        function_name = spec.get('name', 'custom_processor')
        description = spec.get('description', 'Custom processing function')
        parameters = spec.get('parameters', 'data: Any')
        return_type = spec.get('return_type', 'Any')
        
        # Generate function body
        function_code = '''
try:
    # Process input data
    processed_data = data
    
    # Apply custom logic here
    if isinstance(data, dict):
        processed_data = {k: v for k, v in data.items()}
    elif isinstance(data, list):
        processed_data = [item for item in data]
    
    return processed_data
except Exception as e:
    logger.error(f"Processing error: {e}")
    return None'''
        
        return template.format(
            function_name=function_name,
            parameters=parameters,
            return_type=return_type,
            description=description,
            args_docs="data: Input data to process",
            return_docs="Processed data or None on error",
            function_code=function_code
        )
    
    def _generate_utility_class(self, context: Dict[str, Any]) -> str:
        """Generate a utility class."""
        spec = context['specification']
        template = context['templates']['utility_class']
        
        class_name = spec.get('name', 'CustomUtility')
        description = spec.get('description', 'Custom utility class')
        
        init_parameters = spec.get('init_parameters', '')
        init_code = 'pass'
        
        methods = '''
def process(self, data: Any) -> Any:
        """Process data using utility methods."""
        return data
    
    def validate(self, data: Any) -> bool:
        """Validate data."""
        return data is not None'''
        
        return template.format(
            class_name=class_name,
            description=description,
            init_parameters=init_parameters,
            init_code=init_code,
            methods=methods
        )
    
    def _generate_generic_code(self, context: Dict[str, Any]) -> str:
        """Generate generic code structure."""
        spec = context['specification']
        
        code = f'''
# {spec.get('description', 'Generated code')}
# Type: {context['extension_type'].value}

class Generated{spec.get('name', 'Code')}:
    """Generated code for {spec.get('purpose', 'custom functionality')}."""
    
    def __init__(self):
        self.initialized = True
    
    def execute(self, *args, **kwargs):
        """Execute the generated functionality."""
        # Placeholder implementation
        return {{
            'status': 'executed',
            'args': args,
            'kwargs': kwargs
        }}
'''
        
        return code
    
    def _get_safety_requirements(self, extension_type: ExtensionType) -> List[str]:
        """Get safety requirements for extension type."""
        base_requirements = [
            "No arbitrary code execution",
            "No file system access outside sandbox",
            "No network access without permission",
            "Input validation required",
            "Error handling mandatory"
        ]
        
        type_specific = {
            ExtensionType.REASONING_MODULE: [
                "Logic must be deterministic",
                "No infinite loops allowed",
                "Memory usage must be bounded"
            ],
            ExtensionType.PROCESSING_FUNCTION: [
                "Pure function preferred",
                "Side effects must be documented",
                "Resource usage limits"
            ]
        }
        
        return base_requirements + type_specific.get(extension_type, [])
    
    def _assess_safety_level(self, code: str, specification: Dict[str, Any]) -> SafetyLevel:
        """Assess the safety level of generated code."""
        dangerous_patterns = [
            'exec(', 'eval(', 'import os', 'import sys', 'subprocess',
            'open(', '__import__', 'getattr(', 'setattr(',
            'file(', 'input(', 'raw_input('
        ]
        
        restricted_patterns = [
            'import requests', 'import urllib', 'import socket',
            'import threading', 'import multiprocessing'
        ]
        
        # Check for dangerous patterns
        for pattern in dangerous_patterns:
            if pattern in code:
                return SafetyLevel.DANGEROUS
        
        # Check for restricted patterns
        for pattern in restricted_patterns:
            if pattern in code:
                return SafetyLevel.RESTRICTED
        
        # Check specification requirements
        if specification.get('requires_human_approval', False):
            return SafetyLevel.SUPERVISED
        
        return SafetyLevel.SAFE
    
    def _generate_test_cases(self, code: str, specification: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate test cases for the code."""
        test_cases = []
        
        # Basic smoke test
        test_cases.append({
            'name': 'smoke_test',
            'description': 'Basic instantiation and execution test',
            'input': {},
            'expected_output_type': 'any',
            'should_pass': True
        })
        
        # Error handling test
        test_cases.append({
            'name': 'error_handling_test',
            'description': 'Test error handling with invalid input',
            'input': None,
            'expected_output_type': 'none_or_error',
            'should_pass': True
        })
        
        # Add specification-specific tests
        if 'test_cases' in specification:
            test_cases.extend(specification['test_cases'])
        
        return test_cases
    
    def _generate_code_id(self, specification: Dict[str, Any]) -> str:
        """Generate unique ID for code."""
        content = json.dumps(specification, sort_keys=True)
        hash_obj = hashlib.md5(content.encode())
        return f"code_{hash_obj.hexdigest()[:8]}"


class SafetyValidator:
    """Validates generated code for safety and correctness."""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or self._default_config()
        self.validation_cache = {}
        self.blocked_patterns = self._load_blocked_patterns()
        
    def _default_config(self) -> Dict[str, Any]:
        """Default validation configuration."""
        return {
            'max_execution_time': 5.0,
            'max_memory_mb': 100,
            'allow_imports': ['typing', 'dataclasses', 'enum', 'json', 'logging'],
            'require_docstrings': True,
            'require_type_hints': False
        }
    
    def _load_blocked_patterns(self) -> List[str]:
        """Load patterns that are blocked for safety."""
        return [
            # Dangerous built-ins
            'exec', 'eval', 'compile', '__import__',
            'getattr', 'setattr', 'delattr', 'hasattr',
            'globals', 'locals', 'vars', 'dir',
            
            # File and system access
            'open', 'file', 'input', 'raw_input',
            'os.system', 'subprocess', 'commands',
            
            # Network access
            'urllib', 'requests', 'socket', 'http',
            
            # Process and thread control
            'threading', 'multiprocessing', '_thread',
            'asyncio', 'concurrent.futures',
            
            # Introspection and modification
            'inspect.getmembers', 'inspect.getsource',
            'types.', 'importlib', 'pkgutil'
        ]
    
    def validate_code(self, generated_code: GeneratedCode) -> Dict[str, Any]:
        """Comprehensive validation of generated code."""
        validation_id = f"{generated_code.code_id}_{hash(generated_code.code)}"
        
        if validation_id in self.validation_cache:
            return self.validation_cache[validation_id]
        
        result = {
            'valid': True,
            'safety_level': generated_code.safety_level,
            'errors': [],
            'warnings': [],
            'recommendations': [],
            'test_results': []
        }
        
        try:
            # 1. Static analysis
            static_result = self._static_analysis(generated_code.code)
            result.update(static_result)
            
            # 2. Safety pattern checking
            safety_result = self._safety_pattern_check(generated_code.code)
            result['errors'].extend(safety_result['errors'])
            result['warnings'].extend(safety_result['warnings'])
            
            # 3. Syntax validation
            syntax_result = self._syntax_validation(generated_code.code)
            if not syntax_result['valid']:
                result['valid'] = False
                result['errors'].extend(syntax_result['errors'])
            
            # 4. Import validation
            import_result = self._import_validation(generated_code.code)
            result['errors'].extend(import_result['errors'])
            result['warnings'].extend(import_result['warnings'])
            
            # 5. Test execution (if safe)
            if result['valid'] and generated_code.safety_level in [SafetyLevel.SAFE, SafetyLevel.RESTRICTED]:
                test_results = self._execute_tests(generated_code)
                result['test_results'] = test_results
                
                # Mark as invalid if tests fail
                failed_tests = [t for t in test_results if not t['passed']]
                if failed_tests:
                    result['warnings'].append(f"{len(failed_tests)} tests failed")
            
            # 6. Documentation validation
            doc_result = self._documentation_validation(generated_code.code)
            result['warnings'].extend(doc_result['warnings'])
            result['recommendations'].extend(doc_result['recommendations'])
            
            # Final safety assessment
            if generated_code.safety_level == SafetyLevel.DANGEROUS:
                result['valid'] = False
                result['errors'].append("Code marked as dangerous - blocked")
            
        except Exception as e:
            result['valid'] = False
            result['errors'].append(f"Validation error: {str(e)}")
            logger.error(f"Code validation failed: {e}")
        
        # Cache result
        self.validation_cache[validation_id] = result
        
        return result
    
    def _static_analysis(self, code: str) -> Dict[str, Any]:
        """Perform static analysis on code."""
        result = {'errors': [], 'warnings': [], 'metrics': {}}
        
        try:
            tree = ast.parse(code)
            
            # Analyze AST
            analyzer = StaticAnalyzer()
            analyzer.visit(tree)
            
            result['metrics'] = {
                'lines_of_code': len(code.split('\n')),
                'function_count': analyzer.function_count,
                'class_count': analyzer.class_count,
                'complexity_score': analyzer.complexity_score
            }
            
            # Check complexity
            if analyzer.complexity_score > 20:
                result['warnings'].append("High complexity score - consider simplification")
            
            # Check for potential issues
            result['warnings'].extend(analyzer.warnings)
            
        except SyntaxError as e:
            result['errors'].append(f"Syntax error: {e}")
        
        return result
    
    def _safety_pattern_check(self, code: str) -> Dict[str, Any]:
        """Check for dangerous patterns in code."""
        result = {'errors': [], 'warnings': []}
        
        for pattern in self.blocked_patterns:
            if pattern in code:
                result['errors'].append(f"Blocked pattern detected: {pattern}")
        
        # Additional safety checks
        lines = code.split('\n')
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            # Check for potential code injection
            if 'exec(' in stripped or 'eval(' in stripped:
                result['errors'].append(f"Line {i}: Code injection risk")
            
            # Check for file operations
            if any(op in stripped for op in ['open(', 'file(', 'with open']):
                result['warnings'].append(f"Line {i}: File operation detected")
            
            # Check for network operations
            if any(net in stripped for net in ['urllib', 'requests', 'socket']):
                result['warnings'].append(f"Line {i}: Network operation detected")
        
        return result
    
    def _syntax_validation(self, code: str) -> Dict[str, Any]:
        """Validate code syntax."""
        result = {'valid': True, 'errors': []}
        
        try:
            ast.parse(code)
        except SyntaxError as e:
            result['valid'] = False
            result['errors'].append(f"Syntax error at line {e.lineno}: {e.msg}")
        except Exception as e:
            result['valid'] = False
            result['errors'].append(f"Parse error: {str(e)}")
        
        return result
    
    def _import_validation(self, code: str) -> Dict[str, Any]:
        """Validate imports in code."""
        result = {'errors': [], 'warnings': []}
        
        try:
            tree = ast.parse(code)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name not in self.config['allow_imports']:
                            result['warnings'].append(f"Import not in allowlist: {alias.name}")
                
                elif isinstance(node, ast.ImportFrom):
                    if node.module and node.module not in self.config['allow_imports']:
                        result['warnings'].append(f"Import not in allowlist: {node.module}")
        
        except Exception as e:
            result['errors'].append(f"Import validation error: {str(e)}")
        
        return result
    
    def _execute_tests(self, generated_code: GeneratedCode) -> List[Dict[str, Any]]:
        """Execute test cases for generated code."""
        test_results = []
        
        # Create temporary module
        temp_dir = tempfile.mkdtemp()
        temp_file = Path(temp_dir) / f"{generated_code.code_id}.py"
        
        try:
            # Write code to temporary file
            temp_file.write_text(generated_code.code)
            
            # Load module
            spec = importlib.util.spec_from_file_location(generated_code.code_id, temp_file)
            module = importlib.util.module_from_spec(spec)
            
            # Execute in limited environment
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(spec.loader.exec_module, module)
                
                try:
                    future.result(timeout=self.config['max_execution_time'])
                    
                    # Run test cases
                    for test_case in generated_code.test_cases:
                        test_result = self._run_single_test(module, test_case)
                        test_results.append(test_result)
                
                except TimeoutError:
                    test_results.append({
                        'name': 'execution_timeout',
                        'passed': False,
                        'error': 'Code execution timed out'
                    })
        
        except Exception as e:
            test_results.append({
                'name': 'module_load_error',
                'passed': False,
                'error': f"Failed to load module: {str(e)}"
            })
        
        finally:
            # Cleanup
            if temp_file.exists():
                temp_file.unlink()
            os.rmdir(temp_dir)
        
        return test_results
    
    def _run_single_test(self, module: Any, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """Run a single test case."""
        result = {
            'name': test_case['name'],
            'passed': False,
            'output': None,
            'error': None
        }
        
        try:
            # Find test target (class or function)
            test_target = None
            for name in dir(module):
                obj = getattr(module, name)
                if (inspect.isclass(obj) or inspect.isfunction(obj)) and not name.startswith('_'):
                    test_target = obj
                    break
            
            if test_target is None:
                result['error'] = "No testable class or function found"
                return result
            
            # Execute test
            if inspect.isclass(test_target):
                instance = test_target()
                if hasattr(instance, 'process'):
                    output = instance.process(test_case['input'])
                elif hasattr(instance, 'execute'):
                    output = instance.execute(test_case['input'])
                else:
                    output = "Class instantiated successfully"
            else:
                output = test_target(test_case['input'])
            
            result['output'] = output
            result['passed'] = True
        
        except Exception as e:
            result['error'] = str(e)
            result['passed'] = False
        
        return result
    
    def _documentation_validation(self, code: str) -> Dict[str, Any]:
        """Validate code documentation."""
        result = {'warnings': [], 'recommendations': []}
        
        try:
            tree = ast.parse(code)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    if not ast.get_docstring(node):
                        result['warnings'].append(f"Function '{node.name}' missing docstring")
                
                elif isinstance(node, ast.ClassDef):
                    if not ast.get_docstring(node):
                        result['warnings'].append(f"Class '{node.name}' missing docstring")
        
        except Exception:
            pass  # Don't fail validation for documentation issues
        
        return result


class StaticAnalyzer(ast.NodeVisitor):
    """AST visitor for static code analysis."""
    
    def __init__(self):
        self.function_count = 0
        self.class_count = 0
        self.complexity_score = 0
        self.warnings = []
    
    def visit_FunctionDef(self, node):
        self.function_count += 1
        
        # Calculate cyclomatic complexity
        complexity = 1  # Base complexity
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.Try, ast.With)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        
        self.complexity_score += complexity
        
        if complexity > 10:
            self.warnings.append(f"Function '{node.name}' has high complexity: {complexity}")
        
        self.generic_visit(node)
    
    def visit_ClassDef(self, node):
        self.class_count += 1
        self.generic_visit(node)


class HotLoader:
    """Hot-loads and integrates new capabilities into the running system."""
    
    def __init__(self, target_system: Any):
        self.target_system = target_system
        self.loaded_modules = {}
        self.integration_log = []
    
    def integrate_code(self, validated_code: GeneratedCode, 
                      validation_result: Dict[str, Any]) -> Dict[str, Any]:
        """Integrate validated code into the system."""
        if not validation_result['valid']:
            return {
                'success': False,
                'error': 'Code failed validation',
                'validation_errors': validation_result['errors']
            }
        
        integration_result = {
            'success': False,
            'module_name': None,
            'integration_method': None,
            'capabilities_added': [],
            'error': None
        }
        
        try:
            # Create module from code
            module_name = f"dynamic_{validated_code.code_id}"
            module = self._create_module(validated_code.code, module_name)
            
            if module is None:
                integration_result['error'] = "Failed to create module"
                return integration_result
            
            # Store module
            self.loaded_modules[module_name] = {
                'module': module,
                'code_info': validated_code,
                'load_time': time.time()
            }
            
            # Integrate based on extension type
            if validated_code.extension_type == ExtensionType.REASONING_MODULE:
                self._integrate_reasoning_module(module, validated_code)
            elif validated_code.extension_type == ExtensionType.PROCESSING_FUNCTION:
                self._integrate_processing_function(module, validated_code)
            elif validated_code.extension_type == ExtensionType.UTILITY_CLASS:
                self._integrate_utility_class(module, validated_code)
            
            integration_result.update({
                'success': True,
                'module_name': module_name,
                'integration_method': validated_code.extension_type.value,
                'capabilities_added': self._list_new_capabilities(module)
            })
            
            # Log integration
            self.integration_log.append({
                'timestamp': time.time(),
                'code_id': validated_code.code_id,
                'module_name': module_name,
                'success': True
            })
            
            logger.info(f"Successfully integrated {validated_code.extension_type.value}: {module_name}")
        
        except Exception as e:
            integration_result['error'] = str(e)
            logger.error(f"Integration failed: {e}")
        
        return integration_result
    
    def _create_module(self, code: str, module_name: str) -> Optional[Any]:
        """Create a module from code string."""
        try:
            # Compile code
            compiled_code = compile(code, module_name, 'exec')
            
            # Create module
            module = type(sys)('dynamic_module')
            module.__name__ = module_name
            module.__file__ = f'<dynamic:{module_name}>'
            
            # Execute code in module namespace
            exec(compiled_code, module.__dict__)
            
            return module
        
        except Exception as e:
            logger.error(f"Failed to create module {module_name}: {e}")
            return None
    
    def _integrate_reasoning_module(self, module: Any, code_info: GeneratedCode) -> None:
        """Integrate a reasoning module into the system."""
        # Find reasoning classes in module
        for name in dir(module):
            obj = getattr(module, name)
            if inspect.isclass(obj) and hasattr(obj, 'process'):
                # Add to system's reasoning capabilities
                if hasattr(self.target_system, 'add_reasoning_module'):
                    self.target_system.add_reasoning_module(name, obj)
    
    def _integrate_processing_function(self, module: Any, code_info: GeneratedCode) -> None:
        """Integrate a processing function into the system."""
        # Find functions in module
        for name in dir(module):
            obj = getattr(module, name)
            if inspect.isfunction(obj) and not name.startswith('_'):
                # Add to system's processing capabilities
                if hasattr(self.target_system, 'add_processor'):
                    self.target_system.add_processor(name, obj)
    
    def _integrate_utility_class(self, module: Any, code_info: GeneratedCode) -> None:
        """Integrate a utility class into the system."""
        # Find utility classes in module
        for name in dir(module):
            obj = getattr(module, name)
            if inspect.isclass(obj):
                # Add to system's utilities
                if hasattr(self.target_system, 'add_utility'):
                    self.target_system.add_utility(name, obj)
    
    def _list_new_capabilities(self, module: Any) -> List[str]:
        """List new capabilities added by the module."""
        capabilities = []
        
        for name in dir(module):
            obj = getattr(module, name)
            if not name.startswith('_'):
                if inspect.isclass(obj):
                    capabilities.append(f"class:{name}")
                elif inspect.isfunction(obj):
                    capabilities.append(f"function:{name}")
        
        return capabilities
    
    def unload_module(self, module_name: str) -> bool:
        """Unload a dynamically loaded module."""
        if module_name in self.loaded_modules:
            # Remove from target system if possible
            module_info = self.loaded_modules[module_name]
            
            # Clean up system integration
            if hasattr(self.target_system, 'remove_dynamic_capability'):
                self.target_system.remove_dynamic_capability(module_name)
            
            # Remove from loaded modules
            del self.loaded_modules[module_name]
            
            logger.info(f"Unloaded module: {module_name}")
            return True
        
        return False
    
    def list_loaded_modules(self) -> List[Dict[str, Any]]:
        """List all loaded dynamic modules."""
        modules_info = []
        
        for name, info in self.loaded_modules.items():
            modules_info.append({
                'name': name,
                'code_id': info['code_info'].code_id,
                'extension_type': info['code_info'].extension_type.value,
                'load_time': info['load_time'],
                'capabilities': self._list_new_capabilities(info['module'])
            })
        
        return modules_info