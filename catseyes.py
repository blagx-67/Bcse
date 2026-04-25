"""
catseyes.py
-----------
Edit catseye (talent seed / upgrade material) quantities.

Catseyes allow you to upgrade a cat's level beyond the normal cap.
There is one type per rarity tier.
"""

from editor.save_file import SaveFile


# ── Catseye offsets (EN version) ──────────────────────────────────────────────
#
# Each catseye type is stored as a 4-byte little-endian int.
#
CATSEYE_OFFSETS = {
    "basic":       0x0060,   # Basic (Normal) catseye — blue
    "special":     0x0064,   # Special catseye — green
    "rare":        0x0068,   # Rare catseye — yellow
    "super_rare":  0x006c,   # Super Rare catseye — orange
    "uber_rare":   0x0070,   # Uber Rare catseye — red
    "legend_rare": 0x0074,   # Legend Rare catseye — rainbow
}

CATSEYE_DISPLAY = {
    "basic":       ("🔵", "Basic (Normal)"),
    "special":     ("🟢", "Special"),
    "rare":        ("🟡", "Rare"),
    "super_rare":  ("🟠", "Super Rare"),
    "uber_rare":   ("🔴", "Uber Rare"),
    "legend_rare": ("🌈", "Legend Rare"),
}

MAX_CATSEYES = 9_999


class CatseyeEditor:
    """
    Read and modify catseye quantities in a Battle Cats save file.

    Usage:
        eyes = CatseyeEditor(save)
        eyes.set_rare_catseyes(99)
        eyes.set_uber_rare_catseyes(50)
        eyes.max_all()
        print(eyes.summary())
    """

    def __init__(self, save: SaveFile):
        self.save = save

    # ── Getters ─────────────────────────────────────────────────────────────

    def get(self, rarity: str) -> int:
        self._validate(rarity)
        return self.save.read_int(CATSEYE_OFFSETS[rarity])

    def get_basic_catseyes(self) -> int:
        return self.get("basic")

    def get_special_catseyes(self) -> int:
        return self.get("special")

    def get_rare_catseyes(self) -> int:
        return self.get("rare")

    def get_super_rare_catseyes(self) -> int:
        return self.get("super_rare")

    def get_uber_rare_catseyes(self) -> int:
        return self.get("uber_rare")

    def get_legend_rare_catseyes(self) -> int:
        return self.get("legend_rare")

    # ── Setters ─────────────────────────────────────────────────────────────

    def set(self, rarity: str, amount: int):
        """Generic setter. rarity must be one of CATSEYE_OFFSETS keys."""
        self._validate(rarity)
        clamped = min(amount, MAX_CATSEYES)
        self.save.write_int(CATSEYE_OFFSETS[rarity], clamped)
        emoji, label = CATSEYE_DISPLAY[rarity]
        print(f"  ✓ {emoji} {label} Catseyes → {clamped:,}")

    def set_basic_catseyes(self, amount: int):
        self.set("basic", amount)

    def set_special_catseyes(self, amount: int):
        self.set("special", amount)

    def set_rare_catseyes(self, amount: int):
        self.set("rare", amount)

    def set_super_rare_catseyes(self, amount: int):
        self.set("super_rare", amount)

    def set_uber_rare_catseyes(self, amount: int):
        self.set("uber_rare", amount)

    def set_legend_rare_catseyes(self, amount: int):
        self.set("legend_rare", amount)

    def max_all(self):
        """Set all catseye types to maximum safe value."""
        for rarity in CATSEYE_OFFSETS:
            self.set(rarity, MAX_CATSEYES)
        print("🌈 All catseyes maxed!")

    def set_all(self, amount: int):
        """Set every catseye type to the same amount."""
        for rarity in CATSEYE_OFFSETS:
            self.set(rarity, amount)

    # ── Summary ─────────────────────────────────────────────────────────────

    def summary(self) -> str:
        lines = [
            "┌────────────────────────────────────────┐",
            "│            Catseye Summary             │",
            "├────────────────────────────────────────┤",
        ]
        for rarity, (emoji, label) in CATSEYE_DISPLAY.items():
            amount = self.get(rarity)
            lines.append(f"│  {emoji} {label:<22}: {amount:>6,}  │")
        lines.append("└────────────────────────────────────────┘")
        return "\n".join(lines)

    # ── Internal ─────────────────────────────────────────────────────────────

    @staticmethod
    def _validate(rarity: str):
        if rarity not in CATSEYE_OFFSETS:
            valid = list(CATSEYE_OFFSETS.keys())
            raise ValueError(f"Unknown catseye rarity '{rarity}'. Valid: {valid}")
