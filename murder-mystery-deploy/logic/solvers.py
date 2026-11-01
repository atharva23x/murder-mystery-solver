"""
Solvers module for the Murder Mystery:
1. BruteForceSolver: Enumerates all 125 states.
2. CSPSolver: Backtracking search with Forward Checking and AC-3.
3. ResolutionRefutationSolver: Propositional resolution theorem prover with step-by-step refutation trace.
"""
from __future__ import annotations
import time
import copy
from dataclasses import dataclass, field
from typing import List, Dict, Set, Tuple, Optional, Any

from .propositional import (
    Formula, Clue, Clause, Literal, Var, Not,
    generate_domain_cnf, evaluate_cnf, clause_to_str, literal_to_str, simplify_clauses
)
from data import CATEGORIES, VARIABLE_PREFIXES, get_var_name, parse_var_name


@dataclass
class SolveResult:
    """Standardized result returned by all three AI solvers."""
    solver_name: str
    solutions: List[Tuple[str, str, str]]  # List of (who, where, what)
    time_ms: float
    nodes_explored: int  # Nodes / worlds / assignments checked
    is_unique: bool
    status: str  # "SOLVED", "CONTRADICTION", "UNDERCONSTRAINED"
    details: Dict[str, Any] = field(default_factory=dict)
    proof_trace: List[Dict[str, Any]] = field(default_factory=list)

    @property
    def primary_solution(self) -> Optional[Tuple[str, str, str]]:
        return self.solutions[0] if len(self.solutions) == 1 else None


class BruteForceSolver:
    """
    Brute Force Engine:
    Exhaustively enumerates all 5x5x5 = 125 candidate worlds.
    Evaluates each world against all clue formulas.
    """

    def __init__(self, categories: Dict[str, List[str]] = CATEGORIES):
        self.categories = categories
        self.suspects = categories["WHO"]
        self.locations = categories["WHERE"]
        self.weapons = categories["WHAT"]

    def solve(self, clues: List[Clue]) -> SolveResult:
        start_time = time.perf_counter()
        solutions: List[Tuple[str, str, str]] = []
        combinations_checked = 0

        for who in self.suspects:
            for where in self.locations:
                for what in self.weapons:
                    combinations_checked += 1

                    # Build full 15-variable truth assignment
                    assignment: Dict[str, bool] = {}
                    for s in self.suspects:
                        assignment[get_var_name("WHO", s)] = (s == who)
                    for l in self.locations:
                        assignment[get_var_name("WHERE", l)] = (l == where)
                    for w in self.weapons:
                        assignment[get_var_name("WHAT", w)] = (w == what)

                    # Check all clues
                    all_passed = True
                    for clue in clues:
                        if not clue.formula.evaluate(assignment):
                            all_passed = False
                            break

                    if all_passed:
                        solutions.append((who, where, what))

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        if len(solutions) == 1:
            status = "SOLVED"
        elif len(solutions) == 0:
            status = "CONTRADICTION"
        else:
            status = "UNDERCONSTRAINED"

        return SolveResult(
            solver_name="Brute Force (125 Worlds)",
            solutions=solutions,
            time_ms=elapsed_ms,
            nodes_explored=combinations_checked,
            is_unique=(len(solutions) == 1),
            status=status,
            details={
                "total_combinations": len(self.suspects) * len(self.locations) * len(self.weapons),
                "combinations_checked": combinations_checked,
                "filtered_out": combinations_checked - len(solutions)
            }
        )


class CSPSolver:
    """
    Constraint Satisfaction Problem (CSP) Solver:
    - Variables: WHO, WHERE, WHAT
    - Domains: 5 values each
    - Algorithm: Backtracking search with Forward Checking and AC-3 arc consistency
    - Tracks nodes visited and backtracks triggered
    """

    def __init__(self, categories: Dict[str, List[str]] = CATEGORIES):
        self.categories = categories
        self.variables = ["WHO", "WHERE", "WHAT"]
        self.nodes_explored = 0
        self.backtracks = 0

    def solve(self, clues: List[Clue], use_ac3: bool = True) -> SolveResult:
        start_time = time.perf_counter()
        self.nodes_explored = 0
        self.backtracks = 0

        initial_domains: Dict[str, List[str]] = {
            var: list(self.categories[var]) for var in self.variables
        }

        # Step 1: Pre-process unary constraints directly on domains
        self._apply_unary_constraints(clues, initial_domains)

        # Step 2: Apply AC-3 if enabled
        if use_ac3:
            self._ac3(clues, initial_domains)

        # Step 3: Backtracking search with Forward Checking
        solutions: List[Tuple[str, str, str]] = []
        assignment: Dict[str, str] = {}
        self._backtrack(assignment, initial_domains, clues, solutions)

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        if len(solutions) == 1:
            status = "SOLVED"
        elif len(solutions) == 0:
            status = "CONTRADICTION"
        else:
            status = "UNDERCONSTRAINED"

        return SolveResult(
            solver_name="CSP (Backtracking + Forward Checking)",
            solutions=solutions,
            time_ms=elapsed_ms,
            nodes_explored=self.nodes_explored,
            is_unique=(len(solutions) == 1),
            status=status,
            details={
                "nodes_explored": self.nodes_explored,
                "backtracks": self.backtracks,
                "ac3_enabled": use_ac3
            }
        )

    def _apply_unary_constraints(self, clues: List[Clue], domains: Dict[str, List[str]]):
        """Prunes impossible values from domains using single-variable clues."""
        for clue in clues:
            vars_involved = clue.involved_vars
            # Check if this clue only involves 1 category
            cats_involved = {parse_var_name(v)[0] for v in vars_involved}
            if len(cats_involved) == 1:
                cat = list(cats_involved)[0]
                valid_vals = []
                for val in domains[cat]:
                    # Build partial assignment for this single variable
                    partial_assign = {}
                    for item in self.categories[cat]:
                        var_name = get_var_name(cat, item)
                        partial_assign[var_name] = (item == val)
                    # All other categories are unassigned, but formula only has variables from 'cat'
                    if clue.formula.evaluate(partial_assign):
                        valid_vals.append(val)
                domains[cat] = valid_vals

    def _is_consistent(self, assignment: Dict[str, str], clues: List[Clue]) -> bool:
        """Checks if current partial assignment satisfies all clues whose variables are bound."""
        # Convert assignment to propositional truth map for assigned categories
        prop_assignment: Dict[str, bool] = {}
        for cat, val in assignment.items():
            for item in self.categories[cat]:
                prop_assignment[get_var_name(cat, item)] = (item == val)

        for clue in clues:
            # Check if all variables in this clue belong to assigned categories
            all_bound = True
            for v in clue.involved_vars:
                c, _ = parse_var_name(v)
                if c not in assignment:
                    all_bound = False
                    break

            if all_bound:
                if not clue.formula.evaluate(prop_assignment):
                    return False
        return True

    def _ac3(self, clues: List[Clue], domains: Dict[str, List[str]]) -> bool:
        """AC-3 arc consistency algorithm over pairwise category constraints."""
        arcs = [
            ("WHO", "WHERE"), ("WHERE", "WHO"),
            ("WHO", "WHAT"), ("WHAT", "WHO"),
            ("WHERE", "WHAT"), ("WHAT", "WHERE")
        ]
        queue = list(arcs)

        while queue:
            xi, xj = queue.pop(0)
            if self._revise(clues, domains, xi, xj):
                if len(domains[xi]) == 0:
                    return False
                # Re-add neighboring arcs
                for xk in self.variables:
                    if xk != xi and xk != xj:
                        queue.append((xk, xi))
        return True

    def _revise(self, clues: List[Clue], domains: Dict[str, List[str]], xi: str, xj: str) -> bool:
        """Revise domain of Xi with respect to Xj."""
        revised = False
        to_remove = []

        for x_val in domains[xi]:
            # Is there any y_val in domains[xj] that is consistent?
            has_support = False
            for y_val in domains[xj]:
                test_assign = {xi: x_val, xj: y_val}
                if self._is_consistent(test_assign, clues):
                    has_support = True
                    break
            if not has_support:
                to_remove.append(x_val)
                revised = True

        for val in to_remove:
            domains[xi].remove(val)

        return revised

    def _forward_check(self, var: str, val: str, assignment: Dict[str, str],
                       domains: Dict[str, List[str]], clues: List[Clue]) -> Optional[Dict[str, List[str]]]:
        """
        Forward Checking:
        Given that var is assigned val, prune invalid values from all remaining unassigned variables.
        Returns new domains if valid, or None if any domain was wiped out (domain wipeout -> backtrack).
        """
        new_domains = {v: list(domains[v]) for v in self.variables}
        new_domains[var] = [val]

        temp_assign = dict(assignment)
        temp_assign[var] = val

        for other_var in self.variables:
            if other_var not in temp_assign:
                valid_candidates = []
                for candidate_val in new_domains[other_var]:
                    test_assign = dict(temp_assign)
                    test_assign[other_var] = candidate_val
                    if self._is_consistent(test_assign, clues):
                        valid_candidates.append(candidate_val)

                if not valid_candidates:
                    # Domain wipeout!
                    return None
                new_domains[other_var] = valid_candidates

        return new_domains

    def _backtrack(self, assignment: Dict[str, str], domains: Dict[str, List[str]],
                   clues: List[Clue], solutions: List[Tuple[str, str, str]]):
        self.nodes_explored += 1

        if len(assignment) == len(self.variables):
            solutions.append((assignment["WHO"], assignment["WHERE"], assignment["WHAT"]))
            return

        # MRV Heuristic: select unassigned variable with minimum remaining domain values
        unassigned = [v for v in self.variables if v not in assignment]
        var = min(unassigned, key=lambda v: len(domains[v]))

        for val in domains[var]:
            # Forward checking
            new_domains = self._forward_check(var, val, assignment, domains, clues)
            if new_domains is not None:
                assignment[var] = val
                self._backtrack(assignment, new_domains, clues, solutions)
                del assignment[var]
            else:
                self.backtracks += 1


class ResolutionRefutationSolver:
    """
    Propositional Resolution Refutation Theorem Prover:
    - Encodes domain axioms (at-least-one, at-most-one) and clues into CNF clauses.
    - To determine the true value of each category, it assumes the negation of candidate
      literals and applies binary propositional resolution to derive the empty clause (□).
    - Captures a complete, human-readable step-by-step proof trace for academic viva/presentation.
    """

    def __init__(self, categories: Dict[str, List[str]] = CATEGORIES):
        self.categories = categories
        self.domain_cnf = generate_domain_cnf(categories, VARIABLE_PREFIXES)

    def solve(self, clues: List[Clue]) -> SolveResult:
        start_time = time.perf_counter()

        # Build initial Knowledge Base
        kb_clauses: List[Clause] = list(self.domain_cnf)
        for clue in clues:
            kb_clauses.extend(clue.to_cnf())
        kb_clauses = simplify_clauses(kb_clauses)

        proof_trace: List[Dict[str, Any]] = []
        solved_categories: Dict[str, str] = {}
        total_clauses_generated = len(kb_clauses)

        # For each category, deduce which item is TRUE
        for cat, items in self.categories.items():
            confirmed_item: Optional[str] = None
            eliminated_items: List[str] = []

            for item in items:
                var_name = get_var_name(cat, item)

                # Test 1: Can we derive a contradiction by assuming this item is FALSE?
                # Assume ¬(Who_Ravi) = True, i.e., add clause {(var_name, False)}
                # If that leads to contradiction □, then Who_Ravi MUST be True!
                refuted_negation, steps = self._refute(kb_clauses, frozenset({(var_name, False)}))
                if refuted_negation:
                    confirmed_item = item
                    proof_trace.extend(steps)
                    break

                # Test 2: Can we derive a contradiction by assuming this item is TRUE?
                # Assume Who_Ravi is True, i.e., add clause {(var_name, True)}
                # If that leads to contradiction □, then Who_Ravi is ELIMINATED!
                refuted_pos, steps = self._refute(kb_clauses, frozenset({(var_name, True)}))
                if refuted_pos:
                    eliminated_items.append(item)
                    proof_trace.extend(steps)

            # If an item was confirmed directly by refuting its negation
            if confirmed_item:
                solved_categories[cat] = confirmed_item
            else:
                # If 4 items were eliminated, the remaining 1 must be true
                remaining = [it for it in items if it not in eliminated_items]
                if len(remaining) == 1:
                    solved_categories[cat] = remaining[0]
                    # Generate proof note: Disjunctive Syllogism
                    proof_trace.append({
                        "step": len(proof_trace) + 1,
                        "type": "Disjunctive Syllogism",
                        "clause": f"{get_var_name(cat, remaining[0])}",
                        "parents": f"Domain axiom for {cat} and eliminated: {', '.join(eliminated_items)}",
                        "explanation": f"All other {cat} options were refuted by contradiction. Therefore, {remaining[0]} must be true."
                    })

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        if len(solved_categories) == 3:
            solution = (solved_categories["WHO"], solved_categories["WHERE"], solved_categories["WHAT"])
            solutions = [solution]
            status = "SOLVED"
        else:
            # Fallback check for consistency or multiple solutions
            bf_check = BruteForceSolver(self.categories).solve(clues)
            solutions = bf_check.solutions
            status = bf_check.status

        return SolveResult(
            solver_name="Resolution Refutation (CNF Prover)",
            solutions=solutions,
            time_ms=elapsed_ms,
            nodes_explored=total_clauses_generated + len(proof_trace),
            is_unique=(len(solutions) == 1),
            status=status,
            details={
                "initial_clauses": len(kb_clauses),
                "proof_steps_count": len(proof_trace)
            },
            proof_trace=proof_trace
        )

    def _resolve(self, c1: Clause, c2: Clause) -> List[Tuple[Clause, Literal]]:
        """
        Resolves two clauses c1 and c2.
        Returns list of (resolvent, resolving_literal) for each complementary pair.
        """
        resolvents = []
        for lit in c1:
            var, pos = lit
            comp_lit = (var, not pos)
            if comp_lit in c2:
                # Construct resolvent: (c1 \ {lit}) ∪ (c2 \ {comp_lit})
                new_clause = (c1 - {lit}) | (c2 - {comp_lit})
                # Check tautology
                vars_pos = {v for v, p in new_clause if p}
                vars_neg = {v for v, p in new_clause if not p}
                if not vars_pos.intersection(vars_neg):
                    resolvents.append((frozenset(new_clause), lit))
        return resolvents

    def _refute(self, kb: List[Clause], assumption_clause: Clause, max_steps: int = 120) -> Tuple[bool, List[Dict[str, Any]]]:
        """
        Attempts to derive the empty clause □ from kb ∪ {assumption_clause}
        using Unit Resolution and Set of Support strategy.
        Returns (is_refuted, proof_steps).
        """
        # Set of Support: start with assumption
        sos = [assumption_clause]
        clauses = list(kb) + [assumption_clause]
        clauses_set = set(clauses)
        steps: List[Dict[str, Any]] = []

        step_counter = 0

        while sos and step_counter < max_steps:
            given = sos.pop(0)

            # Try resolving 'given' against all other clauses in knowledge base
            for partner in clauses:
                if partner == given:
                    continue

                for resolvent, pivot_lit in self._resolve(given, partner):
                    step_counter += 1

                    if resolvent not in clauses_set:
                        clauses_set.add(resolvent)
                        clauses.append(resolvent)
                        sos.append(resolvent)

                        step_info = {
                            "step": step_counter,
                            "resolvent": clause_to_str(resolvent),
                            "parent1": clause_to_str(given),
                            "parent2": clause_to_str(partner),
                            "pivot": literal_to_str(pivot_lit),
                            "explanation": f"Resolve {clause_to_str(given)} with {clause_to_str(partner)} on {literal_to_str(pivot_lit)}"
                        }
                        steps.append(step_info)

                        # Check for empty clause: contradiction derived!
                        if len(resolvent) == 0:
                            step_info["explanation"] = f"CONTRADICTION REACHED (□)! Assumption {clause_to_str(assumption_clause)} refuted."
                            return True, steps

        return False, []
