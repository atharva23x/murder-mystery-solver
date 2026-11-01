"""
Logic package for Murder Mystery Logic Solver:
Propositional logic AST, CNF transformations, AI Solvers, and Puzzle Generation.
"""
from .propositional import (
    Formula, Var, Not, And, Or, Implies, Iff, Xor,
    Clue, Clause, Literal, generate_domain_cnf, evaluate_cnf
)
from .solvers import BruteForceSolver, CSPSolver, ResolutionRefutationSolver, SolveResult
from .generator import PuzzleGenerator, generate_puzzle

__all__ = [
    "Formula", "Var", "Not", "And", "Or", "Implies", "Iff", "Xor",
    "Clue", "Clause", "Literal", "generate_domain_cnf", "evaluate_cnf",
    "BruteForceSolver", "CSPSolver", "ResolutionRefutationSolver", "SolveResult",
    "PuzzleGenerator", "generate_puzzle"
]
