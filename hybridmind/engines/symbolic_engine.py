"""
Symbolic Reasoning Engine for HybridMind

This module implements a powerful symbolic reasoning system that combines:
- First-order logic inference
- Rule-based reasoning
- Knowledge graph operations
- Constraint satisfaction
- Causal reasoning
"""

from typing import Dict, List, Set, Tuple, Any, Optional, Union
from dataclasses import dataclass, field
from enum import Enum
import logging
from collections import defaultdict, deque
import sympy
from sympy.logic.boolalg import Boolean
from sympy.logic import satisfiable
import networkx as nx
import json
import re

logger = logging.getLogger(__name__)


class RuleType(Enum):
    """Types of reasoning rules supported."""
    IMPLICATION = "implication"
    EQUIVALENCE = "equivalence" 
    CONSTRAINT = "constraint"
    CAUSAL = "causal"
    TEMPORAL = "temporal"


@dataclass
class Fact:
    """Represents a symbolic fact in the knowledge base."""
    predicate: str
    arguments: List[str]
    confidence: float = 1.0
    source: str = "user"
    timestamp: Optional[float] = None
    
    def __str__(self) -> str:
        args_str = ", ".join(self.arguments)
        return f"{self.predicate}({args_str})"
    
    def __hash__(self) -> int:
        return hash((self.predicate, tuple(self.arguments)))


@dataclass 
class Rule:
    """Represents a symbolic reasoning rule."""
    name: str
    rule_type: RuleType
    premises: List[str]  # Symbolic expressions
    conclusions: List[str]  # Symbolic expressions
    confidence: float = 1.0
    priority: int = 0
    conditions: List[str] = field(default_factory=list)
    
    def __str__(self) -> str:
        premises_str = " ∧ ".join(self.premises)
        conclusions_str = " ∧ ".join(self.conclusions)
        return f"{self.name}: {premises_str} → {conclusions_str}"


class KnowledgeGraph:
    """Knowledge graph for storing and querying symbolic knowledge."""
    
    def __init__(self):
        self.graph = nx.MultiDiGraph()
        self.entity_types = {}
        self.relations = set()
        
    def add_fact(self, fact: Fact) -> None:
        """Add a fact to the knowledge graph."""
        if len(fact.arguments) >= 2:
            # Binary relation
            subject, obj = fact.arguments[0], fact.arguments[1]
            self.graph.add_edge(
                subject, obj, 
                relation=fact.predicate,
                confidence=fact.confidence,
                source=fact.source
            )
            self.relations.add(fact.predicate)
        else:
            # Unary predicate (property)
            entity = fact.arguments[0] if fact.arguments else fact.predicate
            self.graph.add_node(
                entity,
                property=fact.predicate,
                confidence=fact.confidence,
                source=fact.source
            )
    
    def query_relations(self, subject: str, relation: str = None) -> List[Tuple[str, str, Dict]]:
        """Query relations from a subject."""
        results = []
        if subject in self.graph:
            for target in self.graph.neighbors(subject):
                for edge_data in self.graph[subject][target].values():
                    if relation is None or edge_data.get('relation') == relation:
                        results.append((subject, target, edge_data))
        return results
    
    def find_path(self, start: str, end: str, max_length: int = 5) -> List[List[str]]:
        """Find reasoning paths between entities."""
        try:
            paths = list(nx.all_simple_paths(self.graph, start, end, cutoff=max_length))
            return paths
        except nx.NetworkXNoPath:
            return []


class InferenceEngine:
    """Forward and backward chaining inference engine."""
    
    def __init__(self):
        self.working_memory = set()
        self.inference_log = []
        
    def forward_chain(self, facts: Set[Fact], rules: List[Rule], max_iterations: int = 100) -> Set[Fact]:
        """Forward chaining inference."""
        derived_facts = set(facts)
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            new_facts = set()
            
            for rule in sorted(rules, key=lambda r: r.priority, reverse=True):
                # Check if rule premises are satisfied
                if self._check_premises(rule, derived_facts):
                    # Generate new facts from conclusions
                    for conclusion in rule.conclusions:
                        new_fact = self._parse_conclusion(conclusion, rule)
                        if new_fact and new_fact not in derived_facts:
                            new_facts.add(new_fact)
                            self.inference_log.append({
                                'rule': rule.name,
                                'derived': str(new_fact),
                                'iteration': iteration
                            })
            
            if not new_facts:
                break  # No new inferences possible
                
            derived_facts.update(new_facts)
            
        return derived_facts
    
    def backward_chain(self, goal: Fact, facts: Set[Fact], rules: List[Rule]) -> bool:
        """Backward chaining to prove a goal."""
        if goal in facts:
            return True
            
        # Find rules that could conclude the goal
        applicable_rules = [r for r in rules if self._rule_concludes(r, goal)]
        
        for rule in applicable_rules:
            # Try to prove all premises
            premises_satisfied = True
            for premise in rule.premises:
                premise_fact = self._parse_premise(premise)
                if premise_fact and not self.backward_chain(premise_fact, facts, rules):
                    premises_satisfied = False
                    break
            
            if premises_satisfied:
                return True
                
        return False
    
    def _check_premises(self, rule: Rule, facts: Set[Fact]) -> bool:
        """Check if rule premises are satisfied by current facts."""
        for premise in rule.premises:
            if not self._premise_satisfied(premise, facts):
                return False
        return True
    
    def _premise_satisfied(self, premise: str, facts: Set[Fact]) -> bool:
        """Check if a single premise is satisfied."""
        # Parse premise and check against facts
        # This is a simplified implementation
        for fact in facts:
            if premise.strip() == str(fact).strip():
                return True
        return False
    
    def _rule_concludes(self, rule: Rule, goal: Fact) -> bool:
        """Check if rule can conclude the goal."""
        for conclusion in rule.conclusions:
            if conclusion.strip() == str(goal).strip():
                return True
        return False
    
    def _parse_conclusion(self, conclusion: str, rule: Rule) -> Optional[Fact]:
        """Parse a conclusion string into a Fact."""
        # Simplified parsing - in practice would be more sophisticated
        match = re.match(r'(\w+)\((.*)\)', conclusion.strip())
        if match:
            predicate = match.group(1)
            args_str = match.group(2)
            args = [arg.strip() for arg in args_str.split(',') if arg.strip()]
            return Fact(predicate, args, confidence=rule.confidence, source=f"rule:{rule.name}")
        return None
    
    def _parse_premise(self, premise: str) -> Optional[Fact]:
        """Parse a premise string into a Fact."""
        return self._parse_conclusion(premise, Rule("temp", RuleType.IMPLICATION, [], []))


class ConstraintSolver:
    """Constraint satisfaction problem solver."""
    
    def __init__(self):
        self.variables = {}
        self.constraints = []
        
    def add_variable(self, name: str, domain: List[Any]) -> None:
        """Add a variable with its domain."""
        self.variables[name] = domain
        
    def add_constraint(self, constraint_func, variables: List[str]) -> None:
        """Add a constraint function."""
        self.constraints.append((constraint_func, variables))
        
    def solve(self) -> List[Dict[str, Any]]:
        """Solve the constraint satisfaction problem."""
        solutions = []
        
        def backtrack(assignment: Dict[str, Any]) -> None:
            if len(assignment) == len(self.variables):
                # Check all constraints
                if self._check_constraints(assignment):
                    solutions.append(assignment.copy())
                return
            
            # Choose next variable
            var = next(v for v in self.variables if v not in assignment)
            
            # Try each value in domain
            for value in self.variables[var]:
                assignment[var] = value
                if self._is_consistent(assignment):
                    backtrack(assignment)
                del assignment[var]
        
        backtrack({})
        return solutions
    
    def _check_constraints(self, assignment: Dict[str, Any]) -> bool:
        """Check if assignment satisfies all constraints."""
        for constraint_func, variables in self.constraints:
            values = [assignment[var] for var in variables]
            if not constraint_func(*values):
                return False
        return True
    
    def _is_consistent(self, partial_assignment: Dict[str, Any]) -> bool:
        """Check if partial assignment is consistent."""
        for constraint_func, variables in self.constraints:
            # Only check constraints where all variables are assigned
            if all(var in partial_assignment for var in variables):
                values = [partial_assignment[var] for var in variables]
                if not constraint_func(*values):
                    return False
        return True


class CausalReasoner:
    """Causal reasoning and inference system."""
    
    def __init__(self):
        self.causal_graph = nx.DiGraph()
        self.interventions = {}
        
    def add_causal_relation(self, cause: str, effect: str, strength: float = 1.0) -> None:
        """Add a causal relation."""
        self.causal_graph.add_edge(cause, effect, strength=strength)
        
    def find_causes(self, effect: str) -> List[Tuple[str, float]]:
        """Find potential causes of an effect."""
        causes = []
        for pred in self.causal_graph.predecessors(effect):
            strength = self.causal_graph[pred][effect]['strength']
            causes.append((pred, strength))
        return sorted(causes, key=lambda x: x[1], reverse=True)
    
    def find_effects(self, cause: str) -> List[Tuple[str, float]]:
        """Find potential effects of a cause."""
        effects = []
        for succ in self.causal_graph.successors(cause):
            strength = self.causal_graph[cause][succ]['strength']
            effects.append((succ, strength))
        return sorted(effects, key=lambda x: x[1], reverse=True)
    
    def intervention_effect(self, intervention: str, target: str) -> Optional[str]:
        """Estimate effect of intervention on target."""
        try:
            paths = list(nx.all_simple_paths(self.causal_graph, intervention, target))
            if paths:
                return f"Intervention {intervention} may affect {target} through {len(paths)} causal paths"
            return None
        except nx.NetworkXNoPath:
            return None


class SymbolicReasoningEngine:
    """Main symbolic reasoning engine that orchestrates all reasoning components."""
    
    def __init__(self):
        self.knowledge_base = set()  # Set of Facts
        self.rules = []  # List of Rules
        self.knowledge_graph = KnowledgeGraph()
        self.inference_engine = InferenceEngine()
        self.constraint_solver = ConstraintSolver()
        self.causal_reasoner = CausalReasoner()
        self.inference_cache = {}
        
        logger.info("Symbolic Reasoning Engine initialized")
    
    def add_fact(self, fact: Union[Fact, str]) -> None:
        """Add a fact to the knowledge base."""
        if isinstance(fact, str):
            fact = self._parse_fact(fact)
        
        if fact:
            self.knowledge_base.add(fact)
            self.knowledge_graph.add_fact(fact)
            logger.debug(f"Added fact: {fact}")
    
    def add_rule(self, rule: Union[Rule, Dict]) -> None:
        """Add a reasoning rule."""
        if isinstance(rule, dict):
            rule = Rule(**rule)
        
        self.rules.append(rule)
        logger.debug(f"Added rule: {rule}")
    
    def query(self, query: str, method: str = "forward") -> Dict[str, Any]:
        """Execute a symbolic query."""
        cache_key = f"{query}_{method}"
        if cache_key in self.inference_cache:
            return self.inference_cache[cache_key]
        
        result = {
            'query': query,
            'method': method,
            'results': [],
            'confidence': 0.0,
            'reasoning_path': []
        }
        
        if method == "forward":
            # Forward chaining inference
            derived_facts = self.inference_engine.forward_chain(
                self.knowledge_base, self.rules
            )
            
            # Find matching facts
            query_fact = self._parse_fact(query)
            if query_fact:
                for fact in derived_facts:
                    if self._facts_match(fact, query_fact):
                        result['results'].append({
                            'fact': str(fact),
                            'confidence': fact.confidence,
                            'source': fact.source
                        })
        
        elif method == "backward":
            # Backward chaining
            query_fact = self._parse_fact(query)
            if query_fact:
                proven = self.inference_engine.backward_chain(
                    query_fact, self.knowledge_base, self.rules
                )
                result['results'].append({
                    'proven': proven,
                    'confidence': 1.0 if proven else 0.0
                })
        
        elif method == "graph":
            # Graph-based reasoning
            graph_results = self._graph_query(query)
            result['results'] = graph_results
        
        # Calculate overall confidence
        if result['results']:
            confidences = [r.get('confidence', 0) for r in result['results']]
            result['confidence'] = max(confidences)
        
        result['reasoning_path'] = self.inference_engine.inference_log[-10:]  # Last 10 steps
        
        self.inference_cache[cache_key] = result
        return result
    
    def reason_causally(self, cause: str, effect: str = None) -> Dict[str, Any]:
        """Perform causal reasoning."""
        if effect:
            # Check causal relationship
            intervention_result = self.causal_reasoner.intervention_effect(cause, effect)
            return {
                'cause': cause,
                'effect': effect,
                'relationship': intervention_result,
                'causal_paths': list(nx.all_simple_paths(
                    self.causal_reasoner.causal_graph, cause, effect
                )) if intervention_result else []
            }
        else:
            # Find effects of cause
            effects = self.causal_reasoner.find_effects(cause)
            return {
                'cause': cause,
                'potential_effects': effects
            }
    
    def solve_constraints(self, variables: Dict[str, List], constraints: List) -> List[Dict]:
        """Solve constraint satisfaction problems."""
        solver = ConstraintSolver()
        
        for var, domain in variables.items():
            solver.add_variable(var, domain)
        
        for constraint in constraints:
            if callable(constraint['func']):
                solver.add_constraint(constraint['func'], constraint['variables'])
        
        return solver.solve()
    
    def explain_reasoning(self, query: str) -> Dict[str, Any]:
        """Provide explanation for reasoning process."""
        result = self.query(query)
        
        explanation = {
            'query': query,
            'reasoning_steps': self.inference_engine.inference_log,
            'applied_rules': [step['rule'] for step in self.inference_engine.inference_log],
            'derived_facts': [step['derived'] for step in self.inference_engine.inference_log],
            'confidence_factors': []
        }
        
        # Add confidence analysis
        for res in result['results']:
            explanation['confidence_factors'].append({
                'fact': res.get('fact', ''),
                'confidence': res.get('confidence', 0),
                'justification': f"Derived from rule-based inference"
            })
        
        return explanation
    
    def update_knowledge(self, updates: List[Dict]) -> None:
        """Update knowledge base with new facts and rules."""
        for update in updates:
            if update['type'] == 'fact':
                self.add_fact(update['content'])
            elif update['type'] == 'rule':
                self.add_rule(update['content'])
            elif update['type'] == 'causal':
                self.causal_reasoner.add_causal_relation(
                    update['cause'], update['effect'], update.get('strength', 1.0)
                )
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get engine statistics."""
        return {
            'facts_count': len(self.knowledge_base),
            'rules_count': len(self.rules),
            'graph_nodes': self.knowledge_graph.graph.number_of_nodes(),
            'graph_edges': self.knowledge_graph.graph.number_of_edges(),
            'causal_relations': self.causal_reasoner.causal_graph.number_of_edges(),
            'inference_cache_size': len(self.inference_cache),
            'recent_inferences': len(self.inference_engine.inference_log)
        }
    
    # Helper methods
    
    def _parse_fact(self, fact_str: str) -> Optional[Fact]:
        """Parse a string representation into a Fact object."""
        match = re.match(r'(\w+)\((.*)\)', fact_str.strip())
        if match:
            predicate = match.group(1)
            args_str = match.group(2)
            args = [arg.strip() for arg in args_str.split(',') if arg.strip()]
            return Fact(predicate, args)
        return None
    
    def _facts_match(self, fact1: Fact, fact2: Fact) -> bool:
        """Check if two facts match (considering variables)."""
        if fact1.predicate != fact2.predicate:
            return False
        
        if len(fact1.arguments) != len(fact2.arguments):
            return False
        
        # Simple matching - could be extended for variable unification
        return fact1.arguments == fact2.arguments
    
    def _graph_query(self, query: str) -> List[Dict[str, Any]]:
        """Execute graph-based query."""
        # Parse query for graph operations
        # This is a simplified implementation
        results = []
        
        if "related_to" in query:
            # Find related entities
            parts = query.split("related_to")
            if len(parts) == 2:
                entity = parts[1].strip().strip('()')
                relations = self.knowledge_graph.query_relations(entity)
                for subj, obj, data in relations:
                    results.append({
                        'relation': f"{subj} -> {obj}",
                        'type': data.get('relation', 'unknown'),
                        'confidence': data.get('confidence', 1.0)
                    })
        
        return results