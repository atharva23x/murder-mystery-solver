"""
Puzzle Generator module:
Generates unique, guaranteed-solvable murder mystery puzzles across Easy, Medium, and Hard difficulties.
Also provides step-by-step elimination grid tracking for pedagogic explanation.
"""
from __future__ import annotations
import random
from typing import List, Dict, Tuple, Set, Optional, Any

from .propositional import (
    Formula, Var, Not, And, Or, Implies, Iff, Xor, Clue
)
from .solvers import BruteForceSolver
from data import CATEGORIES, VARIABLE_PREFIXES, get_var_name, parse_var_name, SUSPECTS, LOCATIONS, WEAPONS


class PuzzleGenerator:
    """
    Generates murder mystery logic puzzles with mathematical uniqueness guarantees.
    """

    def __init__(self, categories: Dict[str, List[str]] = CATEGORIES):
        self.categories = categories
        self.suspects = categories["WHO"]
        self.locations = categories["WHERE"]
        self.weapons = categories["WHAT"]
        self.solver = BruteForceSolver(categories)

    def generate(self, difficulty: str = "Medium", seed: Optional[int] = None) -> Tuple[Tuple[str, str, str], List[Clue]]:
        """
        Generates a puzzle with guaranteed unique solution.
        Returns:
            ((secret_who, secret_where, secret_what), list_of_clues)
        """
        if seed is not None:
            random.seed(seed)

        # 1. Pick secret true solution
        secret_who = random.choice(self.suspects)
        secret_where = random.choice(self.locations)
        secret_what = random.choice(self.weapons)
        secret = (secret_who, secret_where, secret_what)

        # 2. Build full truth assignment for secret
        secret_assignment = self._secret_assignment(secret)

        # 3. Target number of clues based on difficulty
        difficulty = difficulty.capitalize()
        if difficulty == "Easy":
            target_clue_count = 6
            allowed_types = ["negation", "disjunction", "implication"]
        elif difficulty == "Hard":
            target_clue_count = 4
            allowed_types = ["implication", "biconditional", "xor", "disjunction"]
        else:  # Medium
            target_clue_count = 5
            allowed_types = ["negation", "disjunction", "implication", "biconditional", "xor"]

        # 4. Generate candidate clues and prune until exactly 1 solution remains
        clues: List[Clue] = []
        clue_id_counter = 1

        # Generate candidate clue pool
        candidate_clues = self._generate_candidate_pool(secret, secret_assignment, allowed_types)
        random.shuffle(candidate_clues)

        current_solutions = self.solver.solve(clues).solutions

        # Add clues iteratively to reach uniqueness
        for cand_clue in candidate_clues:
            # Test if candidate clue prunes at least one wrong solution
            test_clues = clues + [cand_clue]
            new_solutions = self.solver.solve(test_clues).solutions

            if len(new_solutions) < len(current_solutions) and secret in new_solutions:
                cand_clue.id = f"C{clue_id_counter}"
                clue_id_counter += 1
                clues.append(cand_clue)
                current_solutions = new_solutions

                if len(current_solutions) == 1:
                    break

        # If more clues are desired to meet difficulty target count (without making it invalid)
        if len(clues) < target_clue_count and len(current_solutions) == 1:
            for cand_clue in candidate_clues:
                if cand_clue in clues:
                    continue
                test_clues = clues + [cand_clue]
                check_res = self.solver.solve(test_clues)
                if check_res.is_unique and check_res.primary_solution == secret:
                    cand_clue.id = f"C{clue_id_counter}"
                    clue_id_counter += 1
                    clues.append(cand_clue)
                    if len(clues) >= target_clue_count:
                        break

        # Verification check: Ensure puzzle is 100% uniquely solvable
        final_check = self.solver.solve(clues)
        if not final_check.is_unique or final_check.primary_solution != secret:
            # Fallback recursion with new random seed if constraint search had an anomaly
            return self.generate(difficulty=difficulty)

        return secret, clues

    def _secret_assignment(self, secret: Tuple[str, str, str]) -> Dict[str, bool]:
        """Build the full truth assignment for one (who, where, what) solution."""
        who, where, what = secret
        assignment: Dict[str, bool] = {}
        for s in self.suspects:
            assignment[get_var_name("WHO", s)] = (s == who)
        for l in self.locations:
            assignment[get_var_name("WHERE", l)] = (l == where)
        for w in self.weapons:
            assignment[get_var_name("WHAT", w)] = (w == what)
        return assignment

    @staticmethod
    def _all_categories_open(solutions: List[Tuple[str, str, str]]) -> bool:
        """True when no single category has been narrowed to one option."""
        if not solutions:
            return False
        return all(len({world[idx] for world in solutions}) >= 2 for idx in range(3))

    def build_for_solution(self, secret: Tuple[str, str, str],
                           difficulty: str = "Medium",
                           seed: Optional[int] = None,
                           ensure_unique: bool = True) -> List[Clue]:
        """Build a case file that is guaranteed to fit a *chosen* solution.

        Unlike :meth:`generate`, the truth is supplied by the caller (the player
        authors the crime). Every clue is consistent with that truth.

        With ``ensure_unique=True`` the file narrows the 125 worlds to exactly
        one, so it solves the case on its own. With ``ensure_unique=False`` it
        stops at the difficulty's clue count and is deliberately *not* unique:
        the detective still needs the player's hints to close the case.
        """
        who, where, what = secret
        if who not in self.suspects or where not in self.locations or what not in self.weapons:
            raise ValueError(f"Unknown solution: {secret!r}")

        if seed is not None:
            random.seed(seed)

        difficulty = difficulty.capitalize()
        targets = {
            "Easy": (6, ["negation", "disjunction", "implication"]),
            "Hard": (4, ["implication", "biconditional", "xor", "disjunction"]),
        }
        target_count, allowed_types = targets.get(
            difficulty, (5, ["negation", "disjunction", "implication", "biconditional", "xor"])
        )

        assignment = self._secret_assignment(secret)
        pool = self._generate_candidate_pool(secret, assignment, allowed_types)
        random.shuffle(pool)

        clues: List[Clue] = []
        current_solutions = self.solver.solve(clues).solutions
        counter = 1

        if not ensure_unique:
            # Build a deliberately open case file. It must never narrow a
            # category to a single option, and it stays short enough that the
            # player's hints still decide the case.
            partial_counts = {"Easy": 4, "Medium": 3, "Hard": 2}
            partial_target = partial_counts.get(difficulty, 3)
            used_texts = set()

            for cand in pool:
                if len(clues) >= partial_target:
                    break
                if cand.text in used_texts:
                    continue
                res = self.solver.solve(clues + [cand])
                if secret not in res.solutions:
                    continue
                if not self._all_categories_open(res.solutions):
                    continue
                clues.append(cand)
                used_texts.add(cand.text)
                current_solutions = res.solutions

            # At least one clue should actually mention the real culprit;
            # otherwise the file feels unrelated to the player's case.
            if clues and not any(who in c.text for c in clues):
                for cand in pool:
                    if cand.text in used_texts or who not in cand.text:
                        continue
                    trial = clues[:-1] + [cand]
                    res = self.solver.solve(trial)
                    if secret in res.solutions and self._all_categories_open(res.solutions):
                        clues[-1] = cand
                        current_solutions = res.solutions
                        break

            for idx, clue in enumerate(clues, start=1):
                clue.id = f"C{idx}"

            if not clues or secret not in current_solutions:
                raise RuntimeError("Could not build an open case file for this solution.")
            return clues

        # Greedily keep only clues that remove wrong worlds and keep the truth alive.
        for cand in pool:
            if len(current_solutions) == 1:
                break
            res = self.solver.solve(clues + [cand])
            if secret in res.solutions and len(res.solutions) < len(current_solutions):
                cand.id = f"C{counter}"
                counter += 1
                clues.append(cand)
                current_solutions = res.solutions

        # Safety net: three direct confirmations always pin the case exactly.
        if len(current_solutions) != 1:
            direct = {
                "WHO": f"The culprit was {who}.",
                "WHERE": f"The crime happened in the {where}.",
                "WHAT": f"The weapon was the {what}.",
            }
            for cat, item in (("WHO", who), ("WHERE", where), ("WHAT", what)):
                cand = Clue("", direct[cat], Var(get_var_name(cat, item)), "confirmation")
                res = self.solver.solve(clues + [cand])
                cand.id = f"C{counter}"
                counter += 1
                clues.append(cand)
                current_solutions = res.solutions
                if len(current_solutions) == 1:
                    break

        # Pad up to the difficulty's clue count without ever weakening the file.
        if len(current_solutions) == 1:
            for cand in pool:
                if len(clues) >= target_count:
                    break
                if any(c.text == cand.text for c in clues):
                    continue
                res = self.solver.solve(clues + [cand])
                if res.is_unique and res.primary_solution == secret:
                    cand.id = f"C{counter}"
                    counter += 1
                    clues.append(cand)

        final_check = self.solver.solve(clues)
        if not final_check.is_unique or final_check.primary_solution != secret:
            raise RuntimeError(
                "Could not build a unique case file for the chosen solution. "
                "Try a different case file depth."
            )

        return clues

    def _generate_candidate_pool(self, secret: Tuple[str, str, str],
                                 secret_assign: Dict[str, bool],
                                 allowed_types: List[str]) -> List[Clue]:
        """Creates an extensive pool of valid clues consistent with the secret."""
        pool: List[Clue] = []
        who_star, where_star, what_star = secret

        # 1. Negations (The weapon was not the Knife / Dev is not guilty)
        if "negation" in allowed_types:
            for s in self.suspects:
                if s != who_star:
                    v = get_var_name("WHO", s)
                    pool.append(Clue("", f"The suspect is not {s}.", Not(Var(v)), "negation"))
            for l in self.locations:
                if l != where_star:
                    v = get_var_name("WHERE", l)
                    pool.append(Clue("", f"The crime was not committed in the {l}.", Not(Var(v)), "negation"))
            for w in self.weapons:
                if w != what_star:
                    v = get_var_name("WHAT", w)
                    pool.append(Clue("", f"The weapon used was not the {w}.", Not(Var(v)), "negation"))

        # 2. Disjunctions (Either Ravi or Meera did it / In Garden or Ballroom)
        if "disjunction" in allowed_types:
            # Suspect pairs where one is the culprit
            for s in self.suspects:
                if s != who_star:
                    v_true = get_var_name("WHO", who_star)
                    v_false = get_var_name("WHO", s)
                    pair = [v_true, v_false]
                    random.shuffle(pair)
                    names = [parse_var_name(p)[1] for p in pair]
                    pool.append(Clue("", f"The culprit was either {names[0]} or {names[1]}.", Or(Var(pair[0]), Var(pair[1])), "disjunction"))

            # Location pairs
            for l in self.locations:
                if l != where_star:
                    v_true = get_var_name("WHERE", where_star)
                    v_false = get_var_name("WHERE", l)
                    pair = [v_true, v_false]
                    random.shuffle(pair)
                    names = [parse_var_name(p)[1] for p in pair]
                    pool.append(Clue("", f"The murder occurred either in the {names[0]} or the {names[1]}.", Or(Var(pair[0]), Var(pair[1])), "disjunction"))

            # Weapon pairs
            for w in self.weapons:
                if w != what_star:
                    v_true = get_var_name("WHAT", what_star)
                    v_false = get_var_name("WHAT", w)
                    pair = [v_true, v_false]
                    random.shuffle(pair)
                    names = [parse_var_name(p)[1] for p in pair]
                    pool.append(Clue("", f"The weapon was either the {names[0]} or the {names[1]}.", Or(Var(pair[0]), Var(pair[1])), "disjunction"))

        # 3. Implications (If in Kitchen, weapon was Poison)
        if "implication" in allowed_types:
            # True premise -> True conclusion (e.g. Where_Kitchen -> Weapon_Poison)
            v_who = get_var_name("WHO", who_star)
            v_where = get_var_name("WHERE", where_star)
            v_what = get_var_name("WHAT", what_star)

            pool.append(Clue("", f"If {who_star} is the culprit, then the weapon was the {what_star}.", Implies(Var(v_who), Var(v_what)), "implication"))
            pool.append(Clue("", f"If the crime was in the {where_star}, the weapon was the {what_star}.", Implies(Var(v_where), Var(v_what)), "implication"))
            pool.append(Clue("", f"If the crime was in the {where_star}, {who_star} is responsible.", Implies(Var(v_where), Var(v_who)), "implication"))

            # False premise -> Any conclusion (e.g. If in Garden [false], weapon was Knife)
            for l in self.locations:
                if l != where_star:
                    foil_where = get_var_name("WHERE", l)
                    for w in self.weapons:
                        if w != what_star:
                            foil_what = get_var_name("WHAT", w)
                            pool.append(Clue("", f"If the murder was in the {l}, the weapon was the {w}.", Implies(Var(foil_where), Var(foil_what)), "implication"))
                    for s in self.suspects:
                        if s != who_star:
                            foil_who = get_var_name("WHO", s)
                            pool.append(Clue("", f"If {s} committed the crime, it happened in the {l}.", Implies(Var(foil_who), Var(foil_where)), "implication"))

        # 4. Biconditionals (Rope was used if and only if in Garden)
        if "biconditional" in allowed_types:
            v_where = get_var_name("WHERE", where_star)
            v_what = get_var_name("WHAT", what_star)
            v_who = get_var_name("WHO", who_star)

            # Both True
            pool.append(Clue("", f"The weapon was the {what_star} if and only if the crime was in the {where_star}.", Iff(Var(v_what), Var(v_where)), "biconditional"))
            pool.append(Clue("", f"{who_star} is guilty if and only if the weapon was the {what_star}.", Iff(Var(v_who), Var(v_what)), "biconditional"))
            pool.append(Clue("", f"{who_star} is guilty if and only if the location was the {where_star}.", Iff(Var(v_who), Var(v_where)), "biconditional"))

            # Both False
            for l in self.locations:
                if l != where_star:
                    for w in self.weapons:
                        if w != what_star:
                            pool.append(Clue("", f"The {w} was used if and only if the murder took place in the {l}.", Iff(Var(get_var_name("WHAT", w)), Var(get_var_name("WHERE", l))), "biconditional"))

        # 5. Exclusive OR (Either Ravi or Garden, but not both)
        if "xor" in allowed_types:
            # One True, One False
            for s in self.suspects:
                if s != who_star:
                    v_true = get_var_name("WHERE", where_star)
                    v_false = get_var_name("WHO", s)
                    pool.append(Clue("", f"Either {s} did it or the location was the {where_star}, but not both.", Xor(Var(v_false), Var(v_true)), "xor"))
            for w in self.weapons:
                if w != what_star:
                    v_true = get_var_name("WHO", who_star)
                    v_false = get_var_name("WHAT", w)
                    pool.append(Clue("", f"Either {who_star} is the culprit or the {w} was used, but not both.", Xor(Var(v_true), Var(v_false)), "xor"))

        return pool

    def track_eliminations(self, clues: List[Clue]) -> List[Dict[str, Any]]:
        """
        Calculates the state of the 3x5 elimination grid after each clue is introduced.
        Returns a list of step states:
        [
          {
            "step_index": 0,
            "clue": None (Initial),
            "grid": { "WHO": {"Ravi": "POSSIBLE", ...}, ... },
            "remaining_worlds": 125,
            "eliminated_this_step": []
          },
          ...
        ]
        Grid states:
        - "POSSIBLE" (Green)
        - "ELIMINATED" (Red)
        - "CONFIRMED" (Gold)
        """
        steps_history: List[Dict[str, Any]] = []

        # Step 0: Initial state before any clues
        initial_grid = {
            cat: {item: "POSSIBLE" for item in items}
            for cat, items in self.categories.items()
        }
        steps_history.append({
            "step_index": 0,
            "clue": None,
            "grid": initial_grid,
            "remaining_worlds": 125,
            "eliminated_this_step": [],
            "explanation": "Initial state: All 15 entities (125 combinations) are theoretically possible."
        })

        active_clues: List[Clue] = []
        prev_eliminated: Set[str] = set()

        for idx, clue in enumerate(clues, start=1):
            active_clues.append(clue)
            res = self.solver.solve(active_clues)
            remaining_worlds = res.solutions

            # Count occurrences of each entity in remaining worlds
            entity_counts = {
                cat: {item: 0 for item in items}
                for cat, items in self.categories.items()
            }
            for (w, l, k) in remaining_worlds:
                entity_counts["WHO"][w] += 1
                entity_counts["WHERE"][l] += 1
                entity_counts["WHAT"][k] += 1

            current_grid: Dict[str, Dict[str, str]] = {}
            current_eliminated: Set[str] = set()

            for cat, items in self.categories.items():
                current_grid[cat] = {}
                for item in items:
                    cnt = entity_counts[cat][item]
                    if cnt == 0:
                        current_grid[cat][item] = "ELIMINATED"
                        current_eliminated.add(get_var_name(cat, item))
                    elif cnt == len(remaining_worlds):
                        current_grid[cat][item] = "CONFIRMED"
                    else:
                        current_grid[cat][item] = "POSSIBLE"

            newly_eliminated = [
                f"{parse_var_name(v)[1]} ({parse_var_name(v)[0]})"
                for v in sorted(list(current_eliminated - prev_eliminated))
            ]
            prev_eliminated = current_eliminated

            explanation = (
                f"Applying {clue.id} ('{clue.text}') reduced possible worlds from "
                f"{steps_history[-1]['remaining_worlds']} to {len(remaining_worlds)}."
            )
            if newly_eliminated:
                explanation += f" Eliminated: {', '.join(newly_eliminated)}."

            steps_history.append({
                "step_index": idx,
                "clue": clue,
                "grid": current_grid,
                "remaining_worlds": len(remaining_worlds),
                "eliminated_this_step": newly_eliminated,
                "explanation": explanation
            })

        return steps_history


def generate_puzzle(difficulty: str = "Medium", seed: Optional[int] = None) -> Tuple[Tuple[str, str, str], List[Clue]]:
    """Helper shortcut function to generate a puzzle."""
    gen = PuzzleGenerator()
    return gen.generate(difficulty=difficulty, seed=seed)
