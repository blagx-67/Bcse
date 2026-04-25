"""
units.py
--------
Unlock cats, set their levels, and manage plus levels (talents).

The save file stores cat data in a flat array starting at a fixed offset.
Each cat entry is a sequence of short integers representing:
  [unlock_flag, level, plus_level, current_form, ...]

Cat IDs map 1:1 to their index in this array.
"""

import json
from pathlib import Path
from typing import Optional

from editor.save_file import SaveFile


# ── Array configuration ────────────────────────────────────────────────────────

# Offset where the cat data array starts in the plaintext save
CAT_ARRAY_OFFSET = 0x0400

# Number of bytes per cat entry
CAT_ENTRY_SIZE = 16  # bytes; exact layout below

# Fields within each entry (relative byte offsets, all 2-byte little-endian)
FIELD_UNLOCK_FLAG = 0   # 0 = locked, 1 = unlocked
FIELD_LEVEL       = 2   # current level (1–30 base, up to 50 with treasures)
FIELD_PLUS_LEVEL  = 4   # plus level (talent upgrade level, 0–90)
FIELD_CURRENT_FORM = 6  # current evolution form (0=base, 1=evolved, 2=true form)

# Maximum total number of cats (plenty of headroom for future additions)
MAX_CATS = 700

MAX_LEVEL = 30
MAX_LEVEL_WITH_CATSEYES = 60
MAX_PLUS_LEVEL = 90

# Basic cat IDs (unlocked from the start in normal play)
BASIC_CAT_IDS = list(range(0, 27))   # IDs 0–26

# Load unit name table
_DATA_PATH = Path(__file__).parent.parent / "data" / "units.json"
_UNIT_NAMES: dict[int, str] = {}

if _DATA_PATH.exists():
    with open(_DATA_PATH) as f:
        _raw = json.load(f)
    _UNIT_NAMES = {int(k): v for k, v in _raw.items()}


class UnitEditor:
    """
    Manage cat unit unlock status and levels.

    Usage:
        units = UnitEditor(save)
        units.unlock_cat(25)                          # Unlock Bahamut Cat
        units.set_cat_level(25, level=30, plus=90)    # Max level
        units.unlock_all_basic_cats()
        units.set_true_form(25)                        # Evolve to true form
    """

    def __init__(self, save: SaveFile):
        self.save = save

    # ── Read ─────────────────────────────────────────────────────────────────

    def is_unlocked(self, cat_id: int) -> bool:
        return self._read_field(cat_id, FIELD_UNLOCK_FLAG) != 0

    def get_level(self, cat_id: int) -> int:
        return self._read_field(cat_id, FIELD_LEVEL)

    def get_plus_level(self, cat_id: int) -> int:
        return self._read_field(cat_id, FIELD_PLUS_LEVEL)

    def get_form(self, cat_id: int) -> int:
        """0 = base, 1 = evolved, 2 = true form."""
        return self._read_field(cat_id, FIELD_CURRENT_FORM)

    def get_cat_name(self, cat_id: int) -> str:
        return _UNIT_NAMES.get(cat_id, f"Cat #{cat_id}")

    # ── Unlock ───────────────────────────────────────────────────────────────

    def unlock_cat(self, cat_id: int):
        """Unlock a cat (set unlock flag to 1)."""
        self._validate_id(cat_id)
        self._write_field(cat_id, FIELD_UNLOCK_FLAG, 1)
        name = self.get_cat_name(cat_id)
        print(f"  ✓ Unlocked: [{cat_id:>3}] {name}")

    def lock_cat(self, cat_id: int):
        """Lock a cat (remove it from the roster)."""
        self._validate_id(cat_id)
        self._write_field(cat_id, FIELD_UNLOCK_FLAG, 0)

    def unlock_cats(self, cat_ids: list[int]):
        """Unlock a list of cats by ID."""
        for cid in cat_ids:
            self.unlock_cat(cid)

    def unlock_all_basic_cats(self):
        """Unlock all basic (normal chapter) cats (IDs 0–26)."""
        print("🐱 Unlocking all basic cats…")
        self.unlock_cats(BASIC_CAT_IDS)

    def unlock_all_cats(self):
        """
        Unlock ALL cats in the game (use with caution — may unlock
        cats you haven't legitimately obtained yet).
        """
        print(f"🐱 Unlocking all {len(_UNIT_NAMES)} known cats…")
        for cat_id in _UNIT_NAMES:
            self.unlock_cat(cat_id)

    # ── Level ────────────────────────────────────────────────────────────────

    def set_cat_level(
        self,
        cat_id: int,
        level: int,
        plus_level: int = 0,
    ):
        """Set a cat's level and plus level."""
        self._validate_id(cat_id)
        level = max(1, min(level, MAX_LEVEL_WITH_CATSEYES))
        plus_level = max(0, min(plus_level, MAX_PLUS_LEVEL))

        self._write_field(cat_id, FIELD_LEVEL, level)
        self._write_field(cat_id, FIELD_PLUS_LEVEL, plus_level)
        name = self.get_cat_name(cat_id)
        print(f"  ✓ [{cat_id:>3}] {name} → Lv.{level}+{plus_level}")

    def max_cat_level(self, cat_id: int):
        """Max a cat's level (30+90 = max with catseyes)."""
        self.set_cat_level(cat_id, level=30, plus_level=90)

    def max_all_unlocked(self):
        """Max the level of every currently unlocked cat."""
        print("⬆️  Maxing all unlocked cats…")
        for cat_id in range(MAX_CATS):
            if self.is_unlocked(cat_id):
                self.set_cat_level(cat_id, level=30, plus_level=90)

    # ── Forms ────────────────────────────────────────────────────────────────

    def set_base_form(self, cat_id: int):
        self._validate_id(cat_id)
        self._write_field(cat_id, FIELD_CURRENT_FORM, 0)

    def set_evolved_form(self, cat_id: int):
        self._validate_id(cat_id)
        self._write_field(cat_id, FIELD_CURRENT_FORM, 1)

    def set_true_form(self, cat_id: int):
        """Unlock the true (third) form of a cat."""
        self._validate_id(cat_id)
        self._write_field(cat_id, FIELD_CURRENT_FORM, 2)
        name = self.get_cat_name(cat_id)
        print(f"  ✓ [{cat_id:>3}] {name} → True Form ✨")

    # ── Convenience ──────────────────────────────────────────────────────────

    def unlock_and_max(self, cat_id: int, true_form: bool = False):
        """Unlock a cat, max its level, and optionally set true form."""
        self.unlock_cat(cat_id)
        self.max_cat_level(cat_id)
        if true_form:
            self.set_true_form(cat_id)

    # ── Summary ──────────────────────────────────────────────────────────────

    def summary(self, show_locked: bool = False) -> str:
        lines = ["Cat Roster:"]
        unlocked_count = 0
        for cat_id in range(MAX_CATS):
            unlocked = self.is_unlocked(cat_id)
            if not unlocked and not show_locked:
                continue
            if unlocked:
                unlocked_count += 1
            name = self.get_cat_name(cat_id)
            lv = self.get_level(cat_id)
            plus = self.get_plus_level(cat_id)
            form = ["Base", "Evolved", "True Form"][min(self.get_form(cat_id), 2)]
            status = "✅" if unlocked else "❌"
            lines.append(
                f"  {status} [{cat_id:>3}] {name:<28} Lv.{lv:>2}+{plus:>2}  {form}"
            )
        lines.insert(1, f"  Unlocked: {unlocked_count} cats")
        return "\n".join(lines)

    # ── Internal ─────────────────────────────────────────────────────────────

    def _offset(self, cat_id: int, field: int) -> int:
        return CAT_ARRAY_OFFSET + cat_id * CAT_ENTRY_SIZE + field

    def _read_field(self, cat_id: int, field: int) -> int:
        offset = self._offset(cat_id, field)
        return self.save.read_int(offset, size=2)

    def _write_field(self, cat_id: int, field: int, value: int):
        offset = self._offset(cat_id, field)
        self.save.write_int(offset, value, size=2)

    @staticmethod
    def _validate_id(cat_id: int):
        if not (0 <= cat_id < MAX_CATS):
            raise ValueError(f"cat_id must be 0–{MAX_CATS - 1}, got {cat_id}")
