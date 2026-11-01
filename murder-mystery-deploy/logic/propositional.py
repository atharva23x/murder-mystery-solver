"""
Propositional Logic module:
Defines AST nodes, evaluation, CNF conversion, and domain constraints.
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Dict, Set, List, Tuple, FrozenSet, Union
import itertools

# A Literal is a tuple of (variable_name: str, is_positive: bool)
# e.g. ("Who_Ravi", True) represents Who_Ravi
#      ("Who_Ravi", False) represents ¬Who_Ravi
Literal = Tuple[str, bool]

# A Clause is a disjunction of literals represented as a frozenset
# e.g. frozenset({("Who_Ravi", False), ("Where_Kitchen", True)}) represents (¬Who_Ravi ∨ Where_Kitchen)
# An empty clause frozenset() represents FALSE (Contradiction / □)
Clause = FrozenSet[Literal]


def literal_to_str(lit: Literal) -> str:
    """Format literal as readable string with ¬ symbol."""
    var, pos = lit
    return var if pos else f"¬{var}"


def clause_to_str(clause: Clause) -> str:
    """Format clause as readable disjunction: (A ∨ ¬B)."""
    if not clause:
        return "□ (Contradiction)"
    sorted_lits = sorted(list(clause), key=lambda x: (x[0], not x[1]))
    return "(" + " ∨ ".join(literal_to_str(l) for l in sorted_lits) + ")"


def evaluate_cnf(clauses: List[Clause], assignment: Dict[str, bool]) -> bool:
    """Evaluate a set of CNF clauses against a full or partial assignment."""
    for clause in clauses:
        clause_satisfied = False
        for var, pos in clause:
            val = assignment.get(var)
            if val is not None and val == pos:
                clause_satisfied = True
                break
        if not clause_satisfied:
            # If all literals in this clause are assigned and none satisfied, clause is False
            all_assigned = all(var in assignment for var, _ in clause)
            if all_assigned:
                return False
    return True


class Formula(ABC):
    """Abstract Base Class for Propositional Logic Formulas."""

    @abstractmethod
    def evaluate(self, assignment: Dict[str, bool]) -> bool:
        """Evaluate truth value given a variable assignment dictionary."""
        pass

    @abstractmethod
    def get_variables(self) -> Set[str]:
        """Return the set of all variable names present in the formula."""
        pass

    @abstractmethod
    def to_nnf(self) -> Formula:
        """Convert formula to Negation Normal Form (negations pushed directly to variables)."""
        pass

    @abstractmethod
    def to_cnf_clauses(self) -> List[Clause]:
        """Convert formula into a list of simplified CNF clauses."""
        pass

    @abstractmethod
    def pretty(self) -> str:
        """Return user-friendly unicode logic representation."""
        pass

    def __repr__(self) -> str:
        return self.pretty()


class Var(Formula):
    """Propositional variable (e.g. Who_Ravi, Where_Library)."""

    def __init__(self, name: str):
        self.name = name

    def evaluate(self, assignment: Dict[str, bool]) -> bool:
        return bool(assignment.get(self.name, False))

    def get_variables(self) -> Set[str]:
        return {self.name}

    def to_nnf(self) -> Formula:
        return self

    def to_cnf_clauses(self) -> List[Clause]:
        return [frozenset({(self.name, True)})]

    def pretty(self) -> str:
        return self.name

    def __eq__(self, other) -> bool:
        return isinstance(other, Var) and self.name == other.name

    def __hash__(self) -> int:
        return hash(self.name)


class Not(Formula):
    """Negation operator: ¬A."""

    def __init__(self, operand: Formula):
        self.operand = operand

    def evaluate(self, assignment: Dict[str, bool]) -> bool:
        return not self.operand.evaluate(assignment)

    def get_variables(self) -> Set[str]:
        return self.operand.get_variables()

    def to_nnf(self) -> Formula:
        # Double negation elimination: ¬(¬P) => P
        if isinstance(self.operand, Not):
            return self.operand.operand.to_nnf()
        # De Morgan's: ¬(P ∧ Q) => ¬P ∨ ¬Q
        if isinstance(self.operand, And):
            return Or(*[Not(op).to_nnf() for op in self.operand.operands])
        # De Morgan's: ¬(P ∨ Q) => ¬P ∧ ¬Q
        if isinstance(self.operand, Or):
            return And(*[Not(op).to_nnf() for op in self.operand.operands])
        # ¬(P → Q) => P ∧ ¬Q
        if isinstance(self.operand, Implies):
            return And(self.operand.antecedent.to_nnf(), Not(self.operand.consequent).to_nnf())
        # ¬(P ↔ Q) => (P ∧ ¬Q) ∨ (¬P ∧ Q)
        if isinstance(self.operand, Iff):
            p = self.operand.left
            q = self.operand.right
            return Or(And(p.to_nnf(), Not(q).to_nnf()), And(Not(p).to_nnf(), q.to_nnf()))
        # ¬(P ⊕ Q) => (P ∧ Q) ∨ (¬P ∧ ¬Q)
        if isinstance(self.operand, Xor):
            p = self.operand.left
            q = self.operand.right
            return Or(And(p.to_nnf(), q.to_nnf()), And(Not(p).to_nnf(), Not(q).to_nnf()))
        # Literal negation: ¬Var
        return self

    def to_cnf_clauses(self) -> List[Clause]:
        nnf = self.to_nnf()
        if isinstance(nnf, Not) and isinstance(nnf.operand, Var):
            return [frozenset({(nnf.operand.name, False)})]
        return nnf.to_cnf_clauses()

    def pretty(self) -> str:
        if isinstance(self.operand, Var):
            return f"¬{self.operand.name}"
        return f"¬({self.operand.pretty()})"

    def __eq__(self, other) -> bool:
        return isinstance(other, Not) and self.operand == other.operand

    def __hash__(self) -> int:
        return hash(("Not", self.operand))


class And(Formula):
    """Conjunction operator: A ∧ B ∧ ..."""

    def __init__(self, *operands: Formula):
        self.operands: List[Formula] = list(operands)

    def evaluate(self, assignment: Dict[str, bool]) -> bool:
        return all(op.evaluate(assignment) for op in self.operands)

    def get_variables(self) -> Set[str]:
        vars_set: Set[str] = set()
        for op in self.operands:
            vars_set.update(op.get_variables())
        return vars_set

    def to_nnf(self) -> Formula:
        return And(*[op.to_nnf() for op in self.operands])

    def to_cnf_clauses(self) -> List[Clause]:
        # In CNF, And of clauses is simply the union of all clauses
        clauses: List[Clause] = []
        for op in self.operands:
            clauses.extend(op.to_cnf_clauses())
        return simplify_clauses(clauses)

    def pretty(self) -> str:
        return " ∧ ".join(op.pretty() if isinstance(op, Var) or isinstance(op, Not) else f"({op.pretty()})" for op in self.operands)


class Or(Formula):
    """Disjunction operator: A ∨ B ∨ ..."""

    def __init__(self, *operands: Formula):
        self.operands: List[Formula] = list(operands)

    def evaluate(self, assignment: Dict[str, bool]) -> bool:
        return any(op.evaluate(assignment) for op in self.operands)

    def get_variables(self) -> Set[str]:
        vars_set: Set[str] = set()
        for op in self.operands:
            vars_set.update(op.get_variables())
        return vars_set

    def to_nnf(self) -> Formula:
        return Or(*[op.to_nnf() for op in self.operands])

    def to_cnf_clauses(self) -> List[Clause]:
        # Distribute Or over And
        # If A has clauses {c1, c2} and B has clauses {d1, d2}, A ∨ B has clauses {c1 ∪ d1, c1 ∪ d2, c2 ∪ d1, ...}
        op_clause_lists = [op.to_cnf_clauses() for op in self.operands]
        combined_clauses: List[Clause] = []
        for combo in itertools.product(*op_clause_lists):
            merged = set()
            for c in combo:
                merged.update(c)
            combined_clauses.append(frozenset(merged))
        return simplify_clauses(combined_clauses)

    def pretty(self) -> str:
        return " ∨ ".join(op.pretty() if isinstance(op, Var) or isinstance(op, Not) else f"({op.pretty()})" for op in self.operands)


class Implies(Formula):
    """Implication operator: Antecedent → Consequent."""

    def __init__(self, antecedent: Formula, consequent: Formula):
        self.antecedent = antecedent
        self.consequent = consequent

    def evaluate(self, assignment: Dict[str, bool]) -> bool:
        return (not self.antecedent.evaluate(assignment)) or self.consequent.evaluate(assignment)

    def get_variables(self) -> Set[str]:
        return self.antecedent.get_variables() | self.consequent.get_variables()

    def to_nnf(self) -> Formula:
        # P → Q  ≡  ¬P ∨ Q
        return Or(Not(self.antecedent).to_nnf(), self.consequent.to_nnf())

    def to_cnf_clauses(self) -> List[Clause]:
        return self.to_nnf().to_cnf_clauses()

    def pretty(self) -> str:
        return f"({self.antecedent.pretty()} → {self.consequent.pretty()})"


class Iff(Formula):
    """Biconditional operator: Left ↔ Right (if and only if)."""

    def __init__(self, left: Formula, right: Formula):
        self.left = left
        self.right = right

    def evaluate(self, assignment: Dict[str, bool]) -> bool:
        return self.left.evaluate(assignment) == self.right.evaluate(assignment)

    def get_variables(self) -> Set[str]:
        return self.left.get_variables() | self.right.get_variables()

    def to_nnf(self) -> Formula:
        # P ↔ Q  ≡  (¬P ∨ Q) ∧ (¬Q ∨ P)
        left_nnf = self.left.to_nnf()
        right_nnf = self.right.to_nnf()
        c1 = Or(Not(left_nnf).to_nnf(), right_nnf)
        c2 = Or(Not(right_nnf).to_nnf(), left_nnf)
        return And(c1, c2)

    def to_cnf_clauses(self) -> List[Clause]:
        return self.to_nnf().to_cnf_clauses()

    def pretty(self) -> str:
        return f"({self.left.pretty()} ↔ {self.right.pretty()})"


class Xor(Formula):
    """Exclusive OR operator: Left ⊕ Right (either one, but not both)."""

    def __init__(self, left: Formula, right: Formula):
        self.left = left
        self.right = right

    def evaluate(self, assignment: Dict[str, bool]) -> bool:
        return self.left.evaluate(assignment) != self.right.evaluate(assignment)

    def get_variables(self) -> Set[str]:
        return self.left.get_variables() | self.right.get_variables()

    def to_nnf(self) -> Formula:
        # P ⊕ Q  ≡  (P ∨ Q) ∧ (¬P ∨ ¬Q)
        left_nnf = self.left.to_nnf()
        right_nnf = self.right.to_nnf()
        c1 = Or(left_nnf, right_nnf)
        c2 = Or(Not(left_nnf).to_nnf(), Not(right_nnf).to_nnf())
        return And(c1, c2)

    def to_cnf_clauses(self) -> List[Clause]:
        return self.to_nnf().to_cnf_clauses()

    def pretty(self) -> str:
        return f"({self.left.pretty()} ⊕ {self.right.pretty()})"


def simplify_clauses(clauses: List[Clause]) -> List[Clause]:
    """
    Simplifies a set of CNF clauses:
    1. Removes tautologies (clauses containing both P and ¬P).
    2. Removes duplicate clauses.
    3. Removes subsumed clauses (if c1 ⊆ c2, c2 is redundant).
    """
    valid_clauses: Set[Clause] = set()

    for clause in clauses:
        vars_pos = {var for var, pos in clause if pos}
        vars_neg = {var for var, pos in clause if not pos}

        # Check for tautology: P ∨ ¬P is always True
        if vars_pos.intersection(vars_neg):
            continue

        valid_clauses.add(clause)

    # Subsumption check
    result: List[Clause] = []
    sorted_clauses = sorted(list(valid_clauses), key=len)
    for c in sorted_clauses:
        # If c is a superset of an already accepted clause, c is subsumed
        if any(accepted.issubset(c) for accepted in result):
            continue
        result.append(c)

    return result


class Clue:
    """Represents a game clue with unique ID, plain English text, and logical formula."""

    def __init__(self, clue_id: str, text: str, formula: Formula, clue_type: str = "general"):
        self.id = clue_id
        self.text = text
        self.formula = formula
        self.clue_type = clue_type
        self.involved_vars = sorted(list(formula.get_variables()))

    def to_cnf(self) -> List[Clause]:
        return self.formula.to_cnf_clauses()

    def __repr__(self) -> str:
        return f"Clue({self.id}: '{self.text}' => {self.formula.pretty()})"


def generate_domain_cnf(categories: Dict[str, List[str]], prefix_map: Dict[str, str]) -> List[Clause]:
    """
    Generates exact propositional domain axioms for the puzzle.
    For each category:
    1. At least one option is true: (X1 ∨ X2 ∨ X3 ∨ X4 ∨ X5)
    2. At most one option is true: ¬Xi ∨ ¬Xj for all pairs i < j (pairwise exclusivity)
    Total clauses: 3 * (1 + 10) = 33 clauses.
    """
    clauses: List[Clause] = []

    for cat, items in categories.items():
        prefix = prefix_map[cat]
        var_names = [f"{prefix}_{item}" for item in items]

        # At-least-one clause: (V1 ∨ V2 ∨ ... ∨ V5)
        at_least_one = frozenset((v, True) for v in var_names)
        clauses.append(at_least_one)

        # At-most-one clauses: (¬Vi ∨ ¬Vj) for all i < j
        for i in range(len(var_names)):
            for j in range(i + 1, len(var_names)):
                at_most_one = frozenset({(var_names[i], False), (var_names[j], False)})
                clauses.append(at_most_one)

    return clauses
