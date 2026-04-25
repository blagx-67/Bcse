"""
stages.py
---------
Mark stages as cleared or uncleaned.

The save file stores stage completion as bitfields or byte flags in arrays.
Each chapter has a fixed number of stages. A cleared stage has its flag
set to 1 (or a non-zero value); an uncleared stage is 0.

Chapter index reference:
  0 = Empire of Cats (EoC)     — 3 sub-chapters × 48 stages
  1 = Into the Future (ItF)    — 3 sub-chapters × 48 stages
  2 = Cats of the Cosmos (CotC)— 3 sub-chapters × 49 stages
  3 = Stories of Legend (SoL)  — ~50 maps × variable stages

Special stages (Collaboration, Advent, etc.) have their own arrays.
"""

import json
from pathlib import Path
from typing import Optional

from editor.save_file import SaveFile


# ── Stage array offsets ────────────────────────────────────────────────────────

STAGE_ARRAY_CONFIG = {
    # (base_offset, stages_per_chapter, sub_chapters)
    "empire_of_cats":      (0x1000, 48, 3),
    "into_the_future":     (0x1100, 48, 3),
    "cats_of_the_cosmos":  (0x1200, 49, 3),
    "stories_of_legend":   (0x1400, 48, 50),  # 50 maps
}

# Stars (difficulty levels) per chapter — each star is a separate completion flag
CHAPTER_STARS = {
    "empire_of_cats":      1,
    "into_the_future":     1,
    "cats_of_the_cosmos":  1,
    "stories_of_legend":   3,
}

# Offset for individual monthly/event stages is complex and version-dependent.
# We expose a generic raw-offset API for those.

# Load stage name table
_DATA_PATH = Path(__file__).parent.parent / "data" / "stages.json"
_STAGE_DATA: dict = {}
if _DATA_PATH.exists():
    with open(_DATA_PATH) as f:
        _STAGE_DATA = json.load(f)


class StageEditor:
    """
    Complete or reset stages in a Battle Cats save file.

    Usage:
        stages = StageEditor(save)
        stages.complete_stage("empire_of_cats", sub_chapter=0, stage_id=47)
        stages.complete_all_empire_of_cats()
        stages.complete_all_into_the_future()
        stages.complete_all_cats_of_the_cosmos()
        stages.complete_all_stories_of_legend()
        stages.complete_all()
    """

    def __init__(self, save: SaveFile):
        self.save = save

    # ── Empire of Cats ────────────────────────────────────────────────────────

    def complete_stage_eoc(self, sub_chapter: int, stage_id: int):
        """
        Complete a single Empire of Cats stage.
        sub_chapter: 0, 1, or 2
        stage_id: 0–47 (47 = Moon/boss)
        """
        self._complete("empire_of_cats", sub_chapter, stage_id)

    def complete_all_empire_of_cats(self):
        """Complete all 3×48 Empire of Cats stages."""
        print("🗺️  Completing all Empire of Cats stages…")
        self._complete_chapter("empire_of_cats")

    # ── Into the Future ───────────────────────────────────────────────────────

    def complete_stage_itf(self, sub_chapter: int, stage_id: int):
        """
        Complete a single Into the Future stage.
        sub_chapter: 0, 1, or 2
        stage_id: 0–47
        """
        self._complete("into_the_future", sub_chapter, stage_id)

    def complete_all_into_the_future(self):
        """Complete all 3×48 Into the Future stages."""
        print("🗺️  Completing all Into the Future stages…")
        self._complete_chapter("into_the_future")

    # ── Cats of the Cosmos ────────────────────────────────────────────────────

    def complete_stage_cotc(self, sub_chapter: int, stage_id: int):
        """
        Complete a single Cats of the Cosmos stage.
        sub_chapter: 0, 1, or 2
        stage_id: 0–48
        """
        self._complete("cats_of_the_cosmos", sub_chapter, stage_id)

    def complete_all_cats_of_the_cosmos(self):
        """Complete all 3×49 Cats of the Cosmos stages."""
        print("🗺️  Completing all Cats of the Cosmos stages…")
        self._complete_chapter("cats_of_the_cosmos")

    # ── Stories of Legend ─────────────────────────────────────────────────────

    def complete_sol_map(self, map_id: int, star: int = 0):
        """
        Complete all stages in a Stories of Legend map.
        map_id: 0–49
        star: 0 = 1-star, 1 = 2-star, 2 = 3-star
        """
        config = STAGE_ARRAY_CONFIG["stories_of_legend"]
        base_offset, stages_per_map, num_maps = config
        stars = CHAPTER_STARS["stories_of_legend"]

        if not (0 <= map_id < num_maps):
            raise ValueError(f"map_id must be 0–{num_maps-1}")
        if not (0 <= star < stars):
            raise ValueError(f"star must be 0–{stars-1}")

        offset = base_offset + (star * num_maps * stages_per_map + map_id * stages_per_map)
        for stage in range(stages_per_map):
            self.save.write_int(offset + stage, 1, size=1)

        print(f"  ✓ SoL Map {map_id} ({star+1}★) — all stages cleared")

    def complete_all_stories_of_legend(self, stars: int = 1):
        """
        Complete all Stories of Legend maps.
        stars: 1, 2, or 3 — how many star difficulties to complete.
        """
        print(f"🗺️  Completing all SoL maps ({stars}★)…")
        num_maps = STAGE_ARRAY_CONFIG["stories_of_legend"][2]
        for star in range(stars):
            for map_id in range(num_maps):
                self.complete_sol_map(map_id, star=star)

    # ── Complete everything ───────────────────────────────────────────────────

    def complete_all(self):
        """Complete all main chapters (EoC, ItF, CotC, SoL 1★)."""
        self.complete_all_empire_of_cats()
        self.complete_all_into_the_future()
        self.complete_all_cats_of_the_cosmos()
        self.complete_all_stories_of_legend(stars=1)
        print("🎉 All main story stages completed!")

    # ── Reset ─────────────────────────────────────────────────────────────────

    def reset_stage_eoc(self, sub_chapter: int, stage_id: int):
        """Mark an Empire of Cats stage as not cleared."""
        self._reset("empire_of_cats", sub_chapter, stage_id)

    def reset_all_empire_of_cats(self):
        """Reset all EoC stages to uncleared."""
        print("🔄 Resetting all Empire of Cats stages…")
        self._reset_chapter("empire_of_cats")

    # ── Generic raw-offset API ────────────────────────────────────────────────

    def complete_raw(self, offset: int, count: int = 1, value: int = 1):
        """
        Write completion flags at a raw byte offset.
        Useful for event/collaboration stages whose offsets you know.
        """
        for i in range(count):
            self.save.write_int(offset + i, value, size=1)
        print(f"  ✓ {count} stage flag(s) at offset 0x{offset:x} set to {value}")

    # ── Summary ───────────────────────────────────────────────────────────────

    def chapter_progress(self, chapter: str) -> dict:
        """Return {cleared, total} for a given chapter."""
        config = STAGE_ARRAY_CONFIG.get(chapter)
        if not config:
            raise ValueError(f"Unknown chapter '{chapter}'")
        base, stages_per_sub, num_subs = config
        total = stages_per_sub * num_subs
        cleared = 0
        for i in range(total):
            if self.save.read_int(base + i, size=1) != 0:
                cleared += 1
        return {"chapter": chapter, "cleared": cleared, "total": total}

    def summary(self) -> str:
        lines = ["Stage Progress:"]
        for chapter in STAGE_ARRAY_CONFIG:
            try:
                prog = self.chapter_progress(chapter)
                pct = prog["cleared"] / prog["total"] * 100 if prog["total"] else 0
                lines.append(
                    f"  {chapter:<28}: {prog['cleared']:>4}/{prog['total']:<4} ({pct:.0f}%)"
                )
            except Exception:
                lines.append(f"  {chapter:<28}: (error reading progress)")
        return "\n".join(lines)

    # ── Internal ─────────────────────────────────────────────────────────────

    def _offset_for(self, chapter: str, sub_chapter: int, stage_id: int) -> int:
        base, stages_per_sub, num_subs = STAGE_ARRAY_CONFIG[chapter]
        if not (0 <= sub_chapter < num_subs):
            raise ValueError(f"sub_chapter must be 0–{num_subs-1}")
        if not (0 <= stage_id < stages_per_sub):
            raise ValueError(f"stage_id must be 0–{stages_per_sub-1}")
        return base + sub_chapter * stages_per_sub + stage_id

    def _complete(self, chapter: str, sub_chapter: int, stage_id: int):
        offset = self._offset_for(chapter, sub_chapter, stage_id)
        self.save.write_int(offset, 1, size=1)
        label = _STAGE_DATA.get(chapter, {}).get(str(sub_chapter), {}).get(
            str(stage_id), f"Stage {stage_id}"
        )
        print(f"  ✓ {chapter} [{sub_chapter}][{stage_id}] {label} — cleared")

    def _reset(self, chapter: str, sub_chapter: int, stage_id: int):
        offset = self._offset_for(chapter, sub_chapter, stage_id)
        self.save.write_int(offset, 0, size=1)

    def _complete_chapter(self, chapter: str):
        config = STAGE_ARRAY_CONFIG[chapter]
        base, stages_per_sub, num_subs = config
        total = stages_per_sub * num_subs
        for i in range(total):
            self.save.write_int(base + i, 1, size=1)
        print(f"  ✓ {total} stages cleared in {chapter}")

    def _reset_chapter(self, chapter: str):
        config = STAGE_ARRAY_CONFIG[chapter]
        base, stages_per_sub, num_subs = config
        total = stages_per_sub * num_subs
        for i in range(total):
            self.save.write_int(base + i, 0, size=1)
        print(f"  ✓ {total} stages reset in {chapter}")
