"""
Safety Oversight and Human-in-the-Loop System for HybridMind

This module implements comprehensive safety mechanisms including:
- Real-time monitoring of AI operations
- Risk assessment and intervention protocols
- Human oversight and approval workflows
- Safety constraint enforcement
- Ethical decision-making frameworks
"""

from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
import logging
import time
import threading
import queue
from collections import defaultdict, deque
import json
from pathlib import Path
import hashlib
from concurrent.futures import ThreadPoolExecutor
import warnings

logger = logging.getLogger(__name__)


class RiskLevel(Enum):
    """Risk levels for AI operations."""
    MINIMAL = "minimal"      # No intervention needed
    LOW = "low"             # Log and monitor
    MEDIUM = "medium"       # Request approval
    HIGH = "high"           # Block and alert
    CRITICAL = "critical"   # Emergency shutdown


class InterventionType(Enum):
    """Types of interventions that can be applied."""
    NONE = "none"
    LOG = "log"
    DELAY = "delay"
    REQUIRE_APPROVAL = "require_approval"
    MODIFY_OPERATION = "modify_operation"
    BLOCK = "block"
    EMERGENCY_STOP = "emergency_stop"


class EthicalPrinciple(Enum):
    """Ethical principles for decision making."""
    BENEFICENCE = "beneficence"           # Do good
    NON_MALEFICENCE = "non_maleficence"  # Do no harm
    AUTONOMY = "autonomy"                 # Respect human agency
    JUSTICE = "justice"                   # Fairness and equity
    TRANSPARENCY = "transparency"         # Explainable decisions
    ACCOUNTABILITY = "accountability"     # Responsibility for actions


@dataclass
class SafetyEvent:
    """Represents a safety-related event."""
    event_id: str
    timestamp: float
    risk_level: RiskLevel
    event_type: str
    description: str
    context: Dict[str, Any]
    intervention_applied: InterventionType
    human_involved: bool = False
    resolved: bool = False
    resolution_time: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SafetyRule:
    """Defines a safety rule or constraint."""
    rule_id: str
    name: str
    description: str
    risk_threshold: RiskLevel
    intervention: InterventionType
    condition: Callable[[Dict[str, Any]], bool]
    ethical_principles: List[EthicalPrinciple]
    active: bool = True
    priority: int = 0


@dataclass
class HumanApprovalRequest:
    """Request for human approval or intervention."""
    request_id: str
    timestamp: float
    operation_type: str
    description: str
    risk_assessment: Dict[str, Any]
    context: Dict[str, Any]
    timeout_seconds: float = 300.0  # 5 minutes default
    approved: Optional[bool] = None
    response_time: Optional[float] = None
    human_feedback: str = ""
    escalation_level: int = 0


class RiskAssessment:
    """Comprehensive risk assessment system."""
    
    def __init__(self):
        self.risk_factors = self._initialize_risk_factors()
        self.assessment_history = []
        
    def _initialize_risk_factors(self) -> Dict[str, Dict[str, Any]]:
        """Initialize risk assessment factors."""
        return {
            'code_modification': {
                'weight': 0.8,
                'indicators': [
                    'self_modifying_code',
                    'dynamic_imports', 
                    'eval_usage',
                    'exec_usage'
                ]
            },
            'data_access': {
                'weight': 0.7,
                'indicators': [
                    'file_system_access',
                    'network_access',
                    'database_access',
                    'sensitive_data'
                ]
            },
            'system_interaction': {
                'weight': 0.6,
                'indicators': [
                    'subprocess_calls',
                    'os_commands',
                    'hardware_access',
                    'process_control'
                ]
            },
            'decision_impact': {
                'weight': 0.9,
                'indicators': [
                    'human_welfare_impact',
                    'financial_impact',
                    'privacy_impact',
                    'autonomy_impact'
                ]
            },
            'uncertainty': {
                'weight': 0.5,
                'indicators': [
                    'confidence_level',
                    'model_uncertainty',
                    'data_quality',
                    'edge_case_handling'
                ]
            }
        }
    
    def assess_risk(self, operation: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive risk assessment."""
        assessment = {
            'overall_risk': RiskLevel.MINIMAL,
            'risk_score': 0.0,
            'factor_scores': {},
            'triggered_indicators': [],
            'recommendations': []
        }
        
        total_score = 0.0
        max_possible = 0.0
        
        for factor_name, factor_config in self.risk_factors.items():
            factor_score = self._assess_factor(operation, factor_name, factor_config)
            weight = factor_config['weight']
            
            assessment['factor_scores'][factor_name] = factor_score
            total_score += factor_score * weight
            max_possible += weight
            
            # Check for triggered indicators
            for indicator in factor_config['indicators']:
                if self._check_indicator(operation, indicator):
                    assessment['triggered_indicators'].append(indicator)
        
        # Normalize score
        if max_possible > 0:
            assessment['risk_score'] = total_score / max_possible
        
        # Determine risk level
        assessment['overall_risk'] = self._classify_risk_level(assessment['risk_score'])
        
        # Generate recommendations
        assessment['recommendations'] = self._generate_recommendations(assessment)
        
        # Store assessment
        self.assessment_history.append({
            'timestamp': time.time(),
            'operation': operation.get('type', 'unknown'),
            'assessment': assessment
        })
        
        return assessment
    
    def _assess_factor(self, operation: Dict[str, Any], factor_name: str, 
                      factor_config: Dict[str, Any]) -> float:
        """Assess a specific risk factor."""
        score = 0.0
        indicator_count = len(factor_config['indicators'])
        
        if indicator_count == 0:
            return 0.0
        
        for indicator in factor_config['indicators']:
            if self._check_indicator(operation, indicator):
                score += 1.0
        
        return score / indicator_count
    
    def _check_indicator(self, operation: Dict[str, Any], indicator: str) -> bool:
        """Check if a specific risk indicator is present."""
        checks = {
            'self_modifying_code': lambda op: 'code_generation' in op or 'self_extension' in op,
            'dynamic_imports': lambda op: 'import' in op.get('code', '') or 'importlib' in op.get('code', ''),
            'eval_usage': lambda op: 'eval(' in op.get('code', '') or 'exec(' in op.get('code', ''),
            'file_system_access': lambda op: any(fs in op.get('capabilities', []) for fs in ['file_read', 'file_write']),
            'network_access': lambda op: 'network' in op.get('capabilities', []),
            'database_access': lambda op: 'database' in op.get('capabilities', []),
            'sensitive_data': lambda op: op.get('data_classification') in ['confidential', 'restricted'],
            'subprocess_calls': lambda op: 'subprocess' in op.get('code', '') or 'process' in op.get('capabilities', []),
            'os_commands': lambda op: 'os.system' in op.get('code', '') or 'shell' in op.get('capabilities', []),
            'human_welfare_impact': lambda op: op.get('impact_scope') in ['human_welfare', 'safety_critical'],
            'financial_impact': lambda op: op.get('impact_scope') == 'financial',
            'privacy_impact': lambda op: op.get('data_type') in ['personal', 'private'],
            'autonomy_impact': lambda op: op.get('decision_type') in ['autonomous', 'independent'],
            'confidence_level': lambda op: op.get('confidence', 1.0) < 0.7,
            'model_uncertainty': lambda op: op.get('uncertainty_score', 0.0) > 0.3,
            'data_quality': lambda op: op.get('data_quality_score', 1.0) < 0.8,
            'edge_case_handling': lambda op: not op.get('edge_case_tested', False)
        }
        
        check_func = checks.get(indicator)
        if check_func:
            return check_func(operation)
        
        return False
    
    def _classify_risk_level(self, risk_score: float) -> RiskLevel:
        """Classify overall risk level based on score."""
        if risk_score < 0.2:
            return RiskLevel.MINIMAL
        elif risk_score < 0.4:
            return RiskLevel.LOW
        elif risk_score < 0.6:
            return RiskLevel.MEDIUM
        elif risk_score < 0.8:
            return RiskLevel.HIGH
        else:
            return RiskLevel.CRITICAL
    
    def _generate_recommendations(self, assessment: Dict[str, Any]) -> List[str]:
        """Generate safety recommendations based on assessment."""
        recommendations = []
        
        risk_level = assessment['overall_risk']
        triggered = assessment['triggered_indicators']
        
        if risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            recommendations.append("Require human oversight before execution")
            recommendations.append("Implement additional safety checks")
        
        if risk_level == RiskLevel.CRITICAL:
            recommendations.append("Consider blocking operation entirely")
        
        if 'self_modifying_code' in triggered:
            recommendations.append("Review code modification for safety implications")
        
        if 'eval_usage' in triggered or 'exec_usage' in triggered:
            recommendations.append("Eliminate dynamic code execution if possible")
        
        if 'human_welfare_impact' in triggered:
            recommendations.append("Conduct ethical impact assessment")
        
        if 'confidence_level' in triggered:
            recommendations.append("Improve model confidence before proceeding")
        
        return recommendations


class EthicalFramework:
    """Ethical decision-making framework."""
    
    def __init__(self):
        self.principles = self._initialize_principles()
        self.ethical_log = []
        
    def _initialize_principles(self) -> Dict[EthicalPrinciple, Dict[str, Any]]:
        """Initialize ethical principles with weights and rules."""
        return {
            EthicalPrinciple.BENEFICENCE: {
                'weight': 1.0,
                'description': 'Actions should benefit humans and society',
                'evaluation_criteria': [
                    'positive_outcomes',
                    'societal_benefit',
                    'human_wellbeing'
                ]
            },
            EthicalPrinciple.NON_MALEFICENCE: {
                'weight': 1.2,  # Higher weight as preventing harm is critical
                'description': 'Avoid causing harm to humans or society',
                'evaluation_criteria': [
                    'harm_potential',
                    'unintended_consequences',
                    'risk_mitigation'
                ]
            },
            EthicalPrinciple.AUTONOMY: {
                'weight': 0.8,
                'description': 'Respect human agency and decision-making',
                'evaluation_criteria': [
                    'human_control',
                    'informed_consent',
                    'freedom_preservation'
                ]
            },
            EthicalPrinciple.JUSTICE: {
                'weight': 0.9,
                'description': 'Ensure fairness and equitable treatment',
                'evaluation_criteria': [
                    'fair_distribution',
                    'equal_treatment',
                    'bias_prevention'
                ]
            },
            EthicalPrinciple.TRANSPARENCY: {
                'weight': 0.7,
                'description': 'Maintain explainability and openness',
                'evaluation_criteria': [
                    'explainability',
                    'process_clarity',
                    'decision_rationale'
                ]
            },
            EthicalPrinciple.ACCOUNTABILITY: {
                'weight': 0.8,
                'description': 'Ensure responsibility for AI actions',
                'evaluation_criteria': [
                    'responsibility_chain',
                    'audit_trail',
                    'error_handling'
                ]
            }
        }
    
    def evaluate_ethical_implications(self, operation: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate ethical implications of an operation."""
        evaluation = {
            'ethical_score': 0.0,
            'principle_scores': {},
            'ethical_concerns': [],
            'recommendations': [],
            'approval_required': False
        }
        
        total_weighted_score = 0.0
        total_weight = 0.0
        
        for principle, config in self.principles.items():
            score = self._evaluate_principle(operation, principle, config)
            weight = config['weight']
            
            evaluation['principle_scores'][principle.value] = score
            total_weighted_score += score * weight
            total_weight += weight
            
            # Check for ethical concerns
            if score < 0.5:  # Below threshold
                evaluation['ethical_concerns'].append({
                    'principle': principle.value,
                    'score': score,
                    'description': config['description']
                })
        
        # Calculate overall ethical score
        if total_weight > 0:
            evaluation['ethical_score'] = total_weighted_score / total_weight
        
        # Determine if approval required
        evaluation['approval_required'] = (
            evaluation['ethical_score'] < 0.6 or
            len(evaluation['ethical_concerns']) >= 2 or
            any(concern['score'] < 0.3 for concern in evaluation['ethical_concerns'])
        )
        
        # Generate recommendations
        evaluation['recommendations'] = self._generate_ethical_recommendations(evaluation)
        
        # Log evaluation
        self.ethical_log.append({
            'timestamp': time.time(),
            'operation': operation.get('type', 'unknown'),
            'evaluation': evaluation
        })
        
        return evaluation
    
    def _evaluate_principle(self, operation: Dict[str, Any], 
                          principle: EthicalPrinciple, config: Dict[str, Any]) -> float:
        """Evaluate a specific ethical principle."""
        criteria = config['evaluation_criteria']
        score = 0.0
        
        for criterion in criteria:
            criterion_score = self._evaluate_criterion(operation, principle, criterion)
            score += criterion_score
        
        return score / len(criteria) if criteria else 0.0
    
    def _evaluate_criterion(self, operation: Dict[str, Any], 
                          principle: EthicalPrinciple, criterion: str) -> float:
        """Evaluate a specific ethical criterion."""
        # This is a simplified evaluation system
        # In practice, this could be much more sophisticated
        
        evaluations = {
            'positive_outcomes': lambda op: op.get('expected_benefit', 0.5),
            'societal_benefit': lambda op: 1.0 if op.get('scope') == 'societal' else 0.5,
            'human_wellbeing': lambda op: 1.0 - op.get('harm_risk', 0.0),
            'harm_potential': lambda op: 1.0 - op.get('harm_risk', 0.0),
            'unintended_consequences': lambda op: op.get('consequence_analysis_score', 0.5),
            'risk_mitigation': lambda op: op.get('safety_measures_score', 0.5),
            'human_control': lambda op: op.get('human_oversight_level', 0.5),
            'informed_consent': lambda op: 1.0 if op.get('consent_obtained') else 0.0,
            'freedom_preservation': lambda op: 1.0 - op.get('autonomy_restriction', 0.0),
            'fair_distribution': lambda op: op.get('fairness_score', 0.5),
            'equal_treatment': lambda op: 1.0 - op.get('bias_score', 0.0),
            'bias_prevention': lambda op: op.get('bias_mitigation_score', 0.5),
            'explainability': lambda op: op.get('explainability_score', 0.5),
            'process_clarity': lambda op: op.get('transparency_score', 0.5),
            'decision_rationale': lambda op: 1.0 if op.get('rationale_provided') else 0.0,
            'responsibility_chain': lambda op: op.get('accountability_score', 0.5),
            'audit_trail': lambda op: 1.0 if op.get('audit_enabled') else 0.0,
            'error_handling': lambda op: op.get('error_recovery_score', 0.5)
        }
        
        eval_func = evaluations.get(criterion)
        if eval_func:
            return max(0.0, min(1.0, eval_func(operation)))  # Clamp to [0,1]
        
        return 0.5  # Default neutral score
    
    def _generate_ethical_recommendations(self, evaluation: Dict[str, Any]) -> List[str]:
        """Generate ethical recommendations."""
        recommendations = []
        
        if evaluation['ethical_score'] < 0.4:
            recommendations.append("Significant ethical concerns - recommend against proceeding")
        elif evaluation['ethical_score'] < 0.6:
            recommendations.append("Moderate ethical concerns - require additional safeguards")
        
        for concern in evaluation['ethical_concerns']:
            principle = concern['principle']
            if principle == 'non_maleficence':
                recommendations.append("Implement additional harm prevention measures")
            elif principle == 'autonomy':
                recommendations.append("Ensure human agency is preserved")
            elif principle == 'justice':
                recommendations.append("Address fairness and bias concerns")
            elif principle == 'transparency':
                recommendations.append("Improve explainability and documentation")
        
        if evaluation['approval_required']:
            recommendations.append("Require human ethical review before proceeding")
        
        return recommendations


class HumanInTheLoop:
    """Human-in-the-loop oversight system."""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or self._default_config()
        self.approval_queue = queue.Queue()
        self.active_requests = {}
        self.approval_history = []
        self.human_overrides = {}
        self.escalation_contacts = []
        
        # Start background processing thread
        self.processing_thread = threading.Thread(
            target=self._process_approval_requests, daemon=True
        )
        self.processing_thread.start()
        
    def _default_config(self) -> Dict[str, Any]:
        """Default configuration."""
        return {
            'default_timeout': 300.0,  # 5 minutes
            'escalation_timeout': 600.0,  # 10 minutes
            'max_escalation_level': 3,
            'auto_approve_low_risk': False,
            'require_double_approval_critical': True
        }
    
    def request_approval(self, operation: Dict[str, Any], 
                        risk_assessment: Dict[str, Any],
                        ethical_evaluation: Dict[str, Any] = None) -> HumanApprovalRequest:
        """Request human approval for an operation."""
        request = HumanApprovalRequest(
            request_id=self._generate_request_id(operation),
            timestamp=time.time(),
            operation_type=operation.get('type', 'unknown'),
            description=operation.get('description', 'No description provided'),
            risk_assessment=risk_assessment,
            context={
                'operation': operation,
                'ethical_evaluation': ethical_evaluation or {}
            },
            timeout_seconds=self._determine_timeout(risk_assessment)
        )
        
        # Add to queue and tracking
        self.approval_queue.put(request)
        self.active_requests[request.request_id] = request
        
        logger.info(f"Human approval requested: {request.request_id}")
        return request
    
    def provide_approval(self, request_id: str, approved: bool, 
                        feedback: str = "", override_reason: str = "") -> bool:
        """Provide approval decision for a request."""
        if request_id not in self.active_requests:
            logger.warning(f"Approval request not found: {request_id}")
            return False
        
        request = self.active_requests[request_id]
        request.approved = approved
        request.response_time = time.time()
        request.human_feedback = feedback
        
        # Record override if applicable
        if override_reason:
            self.human_overrides[request_id] = {
                'reason': override_reason,
                'timestamp': time.time(),
                'approver': 'human'  # Could be expanded to track specific users
            }
        
        # Move to history
        self.approval_history.append(request)
        del self.active_requests[request_id]
        
        logger.info(f"Approval decision received: {request_id} -> {'APPROVED' if approved else 'REJECTED'}")
        return True
    
    def check_approval_status(self, request_id: str) -> Optional[Dict[str, Any]]:
        """Check the status of an approval request."""
        if request_id in self.active_requests:
            request = self.active_requests[request_id]
            return {
                'status': 'pending',
                'elapsed_time': time.time() - request.timestamp,
                'timeout_remaining': request.timeout_seconds - (time.time() - request.timestamp),
                'escalation_level': request.escalation_level
            }
        
        # Check history
        for request in self.approval_history:
            if request.request_id == request_id:
                return {
                    'status': 'completed',
                    'approved': request.approved,
                    'response_time': request.response_time - request.timestamp,
                    'feedback': request.human_feedback
                }
        
        return None
    
    def escalate_request(self, request_id: str, reason: str = "") -> bool:
        """Escalate a request to higher authority."""
        if request_id not in self.active_requests:
            return False
        
        request = self.active_requests[request_id]
        if request.escalation_level >= self.config['max_escalation_level']:
            logger.warning(f"Request {request_id} already at maximum escalation level")
            return False
        
        request.escalation_level += 1
        request.timeout_seconds = self.config['escalation_timeout']
        
        logger.warning(f"Request escalated: {request_id} to level {request.escalation_level}")
        return True
    
    def get_pending_requests(self) -> List[HumanApprovalRequest]:
        """Get all pending approval requests."""
        return list(self.active_requests.values())
    
    def _process_approval_requests(self) -> None:
        """Background thread to process approval requests."""
        while True:
            try:
                # Check for timeouts
                current_time = time.time()
                timed_out_requests = []
                
                for request_id, request in self.active_requests.items():
                    elapsed = current_time - request.timestamp
                    
                    if elapsed > request.timeout_seconds:
                        timed_out_requests.append(request_id)
                
                # Handle timeouts
                for request_id in timed_out_requests:
                    request = self.active_requests[request_id]
                    
                    if request.escalation_level < self.config['max_escalation_level']:
                        self.escalate_request(request_id, "timeout")
                    else:
                        # Final timeout - default to rejection for safety
                        self.provide_approval(request_id, False, "Timed out after maximum escalation")
                
                time.sleep(5)  # Check every 5 seconds
                
            except Exception as e:
                logger.error(f"Error in approval processing thread: {e}")
                time.sleep(10)
    
    def _generate_request_id(self, operation: Dict[str, Any]) -> str:
        """Generate unique request ID."""
        content = f"{operation}{time.time()}"
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def _determine_timeout(self, risk_assessment: Dict[str, Any]) -> float:
        """Determine appropriate timeout based on risk level."""
        risk_level = risk_assessment.get('overall_risk', RiskLevel.MEDIUM)
        
        timeouts = {
            RiskLevel.MINIMAL: 60.0,   # 1 minute
            RiskLevel.LOW: 180.0,      # 3 minutes
            RiskLevel.MEDIUM: 300.0,   # 5 minutes
            RiskLevel.HIGH: 600.0,     # 10 minutes
            RiskLevel.CRITICAL: 1800.0 # 30 minutes
        }
        
        return timeouts.get(risk_level, self.config['default_timeout'])


class SafetyOversight:
    """Main safety oversight system that coordinates all safety mechanisms."""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or self._default_config()
        
        # Initialize subsystems
        self.risk_assessor = RiskAssessment()
        self.ethical_framework = EthicalFramework()
        self.human_loop = HumanInTheLoop()
        
        # Safety rules and monitoring
        self.safety_rules = []
        self.active_monitors = {}
        self.safety_log = deque(maxlen=10000)
        self.emergency_stop_active = False
        
        # Initialize default safety rules
        self._initialize_default_rules()
        
        logger.info("Safety Oversight System initialized")
    
    def _default_config(self) -> Dict[str, Any]:
        """Default configuration for safety system."""
        return {
            'monitoring_enabled': True,
            'real_time_intervention': True,
            'log_all_operations': True,
            'require_approval_threshold': RiskLevel.MEDIUM,
            'emergency_stop_threshold': RiskLevel.CRITICAL,
            'audit_trail_retention_days': 30
        }
    
    def _initialize_default_rules(self) -> None:
        """Initialize default safety rules."""
        # Rule 1: Block dangerous code patterns
        self.add_safety_rule(SafetyRule(
            rule_id="dangerous_code_block",
            name="Block Dangerous Code Patterns",
            description="Prevent execution of dangerous code patterns",
            risk_threshold=RiskLevel.HIGH,
            intervention=InterventionType.BLOCK,
            condition=lambda op: any(pattern in op.get('code', '') for pattern in ['exec(', 'eval(', '__import__']),
            ethical_principles=[EthicalPrinciple.NON_MALEFICENCE]
        ))
        
        # Rule 2: Require approval for self-modification
        self.add_safety_rule(SafetyRule(
            rule_id="self_mod_approval",
            name="Self-Modification Approval Required",
            description="Require human approval for self-modifying operations",
            risk_threshold=RiskLevel.MEDIUM,
            intervention=InterventionType.REQUIRE_APPROVAL,
            condition=lambda op: 'self_extension' in op or 'code_generation' in op,
            ethical_principles=[EthicalPrinciple.AUTONOMY, EthicalPrinciple.ACCOUNTABILITY]
        ))
        
        # Rule 3: Monitor high-impact decisions
        self.add_safety_rule(SafetyRule(
            rule_id="high_impact_monitor",
            name="High Impact Decision Monitoring",
            description="Monitor decisions with high human impact",
            risk_threshold=RiskLevel.LOW,
            intervention=InterventionType.LOG,
            condition=lambda op: op.get('impact_scope') in ['human_welfare', 'financial', 'safety_critical'],
            ethical_principles=[EthicalPrinciple.BENEFICENCE, EthicalPrinciple.NON_MALEFICENCE]
        ))
    
    def evaluate_operation(self, operation: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive safety evaluation of an operation."""
        evaluation_start = time.time()
        
        # Generate unique operation ID
        operation_id = self._generate_operation_id(operation)
        
        logger.info(f"Evaluating operation safety: {operation_id}")
        
        # 1. Risk assessment
        risk_assessment = self.risk_assessor.assess_risk(operation)
        
        # 2. Ethical evaluation
        ethical_evaluation = self.ethical_framework.evaluate_ethical_implications(operation)
        
        # 3. Apply safety rules
        rule_results = self._apply_safety_rules(operation)
        
        # 4. Determine overall safety decision
        safety_decision = self._make_safety_decision(
            operation, risk_assessment, ethical_evaluation, rule_results
        )
        
        # 5. Apply intervention if needed
        intervention_result = self._apply_intervention(
            operation, safety_decision, risk_assessment, ethical_evaluation
        )
        
        # Create comprehensive result
        evaluation_result = {
            'operation_id': operation_id,
            'timestamp': time.time(),
            'evaluation_time': time.time() - evaluation_start,
            'risk_assessment': risk_assessment,
            'ethical_evaluation': ethical_evaluation,
            'rule_results': rule_results,
            'safety_decision': safety_decision,
            'intervention_result': intervention_result,
            'approved': safety_decision.get('approved', False),
            'requires_human_approval': safety_decision.get('requires_human_approval', False)
        }
        
        # Log the evaluation
        self._log_safety_event(evaluation_result)
        
        return evaluation_result
    
    def add_safety_rule(self, rule: SafetyRule) -> None:
        """Add a new safety rule."""
        self.safety_rules.append(rule)
        self.safety_rules.sort(key=lambda r: r.priority, reverse=True)
        logger.info(f"Added safety rule: {rule.name}")
    
    def remove_safety_rule(self, rule_id: str) -> bool:
        """Remove a safety rule."""
        original_count = len(self.safety_rules)
        self.safety_rules = [r for r in self.safety_rules if r.rule_id != rule_id]
        
        removed = len(self.safety_rules) < original_count
        if removed:
            logger.info(f"Removed safety rule: {rule_id}")
        
        return removed
    
    def emergency_stop(self, reason: str) -> None:
        """Activate emergency stop protocol."""
        self.emergency_stop_active = True
        
        emergency_event = SafetyEvent(
            event_id=f"emergency_{int(time.time())}",
            timestamp=time.time(),
            risk_level=RiskLevel.CRITICAL,
            event_type="emergency_stop",
            description=f"Emergency stop activated: {reason}",
            context={'reason': reason},
            intervention_applied=InterventionType.EMERGENCY_STOP,
            human_involved=True
        )
        
        self.safety_log.append(emergency_event)
        logger.critical(f"EMERGENCY STOP ACTIVATED: {reason}")
    
    def reset_emergency_stop(self, authorization: str) -> bool:
        """Reset emergency stop (requires authorization)."""
        # In practice, this would have more sophisticated authorization
        if authorization == "authorized_reset":
            self.emergency_stop_active = False
            logger.warning("Emergency stop reset - system operational")
            return True
        
        logger.error("Unauthorized emergency stop reset attempt")
        return False
    
    def get_safety_status(self) -> Dict[str, Any]:
        """Get current safety system status."""
        return {
            'emergency_stop_active': self.emergency_stop_active,
            'active_rules_count': len([r for r in self.safety_rules if r.active]),
            'pending_approvals': len(self.human_loop.get_pending_requests()),
            'recent_events_count': len(self.safety_log),
            'risk_assessments_completed': len(self.risk_assessor.assessment_history),
            'ethical_evaluations_completed': len(self.ethical_framework.ethical_log),
            'system_health': 'operational' if not self.emergency_stop_active else 'emergency_stop'
        }
    
    def _apply_safety_rules(self, operation: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Apply all active safety rules to an operation."""
        results = []
        
        for rule in self.safety_rules:
            if not rule.active:
                continue
            
            try:
                triggered = rule.condition(operation)
                
                result = {
                    'rule_id': rule.rule_id,
                    'rule_name': rule.name,
                    'triggered': triggered,
                    'intervention': rule.intervention.value if triggered else InterventionType.NONE.value,
                    'risk_threshold': rule.risk_threshold.value,
                    'ethical_principles': [p.value for p in rule.ethical_principles]
                }
                
                results.append(result)
                
                if triggered:
                    logger.warning(f"Safety rule triggered: {rule.name}")
            
            except Exception as e:
                logger.error(f"Error evaluating safety rule {rule.rule_id}: {e}")
                results.append({
                    'rule_id': rule.rule_id,
                    'rule_name': rule.name,
                    'triggered': False,
                    'error': str(e)
                })
        
        return results
    
    def _make_safety_decision(self, operation: Dict[str, Any], 
                            risk_assessment: Dict[str, Any],
                            ethical_evaluation: Dict[str, Any],
                            rule_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Make overall safety decision."""
        decision = {
            'approved': True,
            'requires_human_approval': False,
            'intervention_type': InterventionType.NONE,
            'reasoning': [],
            'blocking_factors': []
        }
        
        # Check emergency stop
        if self.emergency_stop_active:
            decision.update({
                'approved': False,
                'intervention_type': InterventionType.EMERGENCY_STOP,
                'reasoning': ['Emergency stop is active'],
                'blocking_factors': ['emergency_stop']
            })
            return decision
        
        # Check risk level
        risk_level = RiskLevel(risk_assessment['overall_risk'])
        if risk_level == RiskLevel.CRITICAL:
            decision['approved'] = False
            decision['intervention_type'] = InterventionType.BLOCK
            decision['reasoning'].append(f"Critical risk level: {risk_level.value}")
            decision['blocking_factors'].append('critical_risk')
        
        elif risk_level in [RiskLevel.HIGH, RiskLevel.MEDIUM]:
            decision['requires_human_approval'] = True
            decision['intervention_type'] = InterventionType.REQUIRE_APPROVAL
            decision['reasoning'].append(f"Risk level requires approval: {risk_level.value}")
        
        # Check ethical concerns
        if ethical_evaluation.get('approval_required', False):
            decision['requires_human_approval'] = True
            if decision['intervention_type'] == InterventionType.NONE:
                decision['intervention_type'] = InterventionType.REQUIRE_APPROVAL
            decision['reasoning'].append("Ethical concerns require human review")
        
        # Check safety rules
        blocking_rules = [r for r in rule_results if r.get('triggered') and r.get('intervention') == InterventionType.BLOCK.value]
        approval_rules = [r for r in rule_results if r.get('triggered') and r.get('intervention') == InterventionType.REQUIRE_APPROVAL.value]
        
        if blocking_rules:
            decision['approved'] = False
            decision['intervention_type'] = InterventionType.BLOCK
            decision['reasoning'].extend([f"Blocking rule triggered: {r['rule_name']}" for r in blocking_rules])
            decision['blocking_factors'].extend([r['rule_id'] for r in blocking_rules])
        
        elif approval_rules:
            decision['requires_human_approval'] = True
            if decision['intervention_type'] == InterventionType.NONE:
                decision['intervention_type'] = InterventionType.REQUIRE_APPROVAL
            decision['reasoning'].extend([f"Approval rule triggered: {r['rule_name']}" for r in approval_rules])
        
        return decision
    
    def _apply_intervention(self, operation: Dict[str, Any], 
                          safety_decision: Dict[str, Any],
                          risk_assessment: Dict[str, Any],
                          ethical_evaluation: Dict[str, Any]) -> Dict[str, Any]:
        """Apply the determined safety intervention.""""