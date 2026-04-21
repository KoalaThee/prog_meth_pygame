"""Branch / faculty / career selection for the player's run.

Data is declared at module level so adding or renaming a faculty or career is a
one-line edit — no logic changes required. ``BranchManager`` owns the three
linked choices (branch → faculty → career) and the auto-pick rule.
"""

from __future__ import annotations

import random

from game_state import GameState


# ---- identifiers & rules --------------------------------------------------

BRANCH_SCIENCE = "science"
BRANCH_ARTS = "arts"

# Stages where a branch must be locked before stat multipliers apply.
BRANCH_STAGES = frozenset({"teenager", "young_adult"})


# ---- data tables ----------------------------------------------------------

FACULTIES_BY_BRANCH: dict[str, tuple[str, ...]] = {
    BRANCH_SCIENCE: (
        "Physics",
        "Biology",
        "Engineering",
        "Chemistry",
        "Computer Science",
    ),
    BRANCH_ARTS: (
        "Design",
        "Fine Arts",
        "Literature",
        "Media Studies",
        "Performing Arts",
    ),
}

CAREERS_BY_FACULTY: dict[str, tuple[str, ...]] = {
    "Physics": ("Physicist", "Data Scientist", "Researcher"),
    "Biology": ("Biologist", "Medical Researcher", "Biotechnology Specialist"),
    "Engineering": ("Mechanical Engineer", "Robotics Engineer", "Engineering Manager"),
    "Chemistry": ("Chemist", "Pharmacist", "Laboratory Specialist"),
    "Computer Science": ("Software Engineer", "AI Engineer", "Cybersecurity Analyst"),
    "Design": ("UX/UI Designer", "Visual Designer", "Creative Director"),
    "Fine Arts": ("Artist", "Illustrator", "Curator"),
    "Literature": ("Editor", "Reporter", "Writer"),
    "Media Studies": ("Media Producer", "Communications Specialist", "Journalist"),
    "Performing Arts": ("Performer", "Stage Director", "Creative Producer"),
}

_FALLBACK_CAREER = "Professional"


# ---- manager --------------------------------------------------------------

class BranchManager:
    """Owns the run's branch, faculty, and career choices."""

    def __init__(self) -> None:
        self.branch_choice: str | None = None
        self.faculty_choice: str | None = None
        self.career_title: str | None = None

    def ensure_for_stage(self, stage: str | None, game_state: GameState) -> bool:
        """Auto-pick a branch for ``stage`` if one isn't set yet.

        Returns ``True`` when scores are tied and the UI must prompt the user.
        """
        if self.branch_choice is not None or stage not in BRANCH_STAGES:
            return False

        if game_state.intelligence > game_state.arts:
            self.choose(BRANCH_SCIENCE)
        elif game_state.arts > game_state.intelligence:
            self.choose(BRANCH_ARTS)
        else:
            return True
        return False

    def choose(self, branch: str) -> None:
        """Commit a branch choice; derive faculty and career randomly."""
        if branch not in FACULTIES_BY_BRANCH:
            raise ValueError(f"Unknown branch: {branch!r}")
        self.branch_choice = branch
        self.faculty_choice = random.choice(FACULTIES_BY_BRANCH[branch])
        careers = CAREERS_BY_FACULTY.get(self.faculty_choice, (_FALLBACK_CAREER,))
        self.career_title = random.choice(careers)
