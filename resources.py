"""
resources.py
------------
Edit in-game resources: cat food, XP, rare tickets, platinum tickets,
leadership points, platinum shards, and more.

Byte offsets are for the EN version. Check data/offsets.json for
other versions/regions or to update after a game patch.
"""

from editor.save_file import SaveFile


# ── Known byte offsets (EN, latest verified version) ──────────────────────────
# Community-sourced. Format: (offset_in_plaintext, size_in_bytes)

OFFSETS = {
    "catfood":            (0x0004, 4),
    "xp":                 (0x0008, 4),
    "rare_tickets":       (0x0018, 4),
    "platinum_tickets":   (0x001c, 4),
    "leadership":         (0x0028, 4),
    "platinum_shards":    (0x0034, 4),
    "cat_energy":         (0x0038, 4),
    "battle_items_0":     (0x003c, 4),   # Speed up
    "battle_items_1":     (0x0040, 4),   # Treasure radar
    "battle_items_2":     (0x0044, 4),   # Rich cat
    "battle_items_3":     (0x0048, 4),   # Cat CPU
    "battle_items_4":     (0x004c, 4),   # Cat jobs
    "battle_items_5":     (0x0050, 4),   # Sniper the cat
}

MAX_SAFE = {
    "catfood":          99_999,
    "xp":            9_999_999,
    "rare_tickets":       9_999,
    "platinum_tickets":     999,
    "leadership":         9_999,
    "platinum_shards":    9_999,
    "cat_energy":           999,
    "battle_items":       9_999,
}

BATTLE_ITEM_NAMES = [
    "Speed Up",
    "Treasure Radar",
    "Rich Cat",
    "Cat CPU",
    "Cat Jobs",
    "Sniper the Cat",
]


class ResourceEditor:
    """
    Read and modify Battle Cats resource values in a decrypted save file.

    Usage:
        res = ResourceEditor(save)
        res.set_catfood(99999)
        res.set_xp(9999999)
        res.set_rare_tickets(99)
        res.set_platinum_tickets(10)
        res.set_battle_item(0, 99)   # Speed Up x99
        print(res.summary())
    """

    def __init__(self, save: SaveFile):
        self.save = save

    # ── Getters ─────────────────────────────────────────────────────────────

    def get_catfood(self) -> int:
        return self._read("catfood")

    def get_xp(self) -> int:
        return self._read("xp")

    def get_rare_tickets(self) -> int:
        return self._read("rare_tickets")

    def get_platinum_tickets(self) -> int:
        return self._read("platinum_tickets")

    def get_leadership(self) -> int:
        return self._read("leadership")

    def get_platinum_shards(self) -> int:
        return self._read("platinum_shards")

    def get_cat_energy(self) -> int:
        return self._read("cat_energy")

    def get_battle_item(self, index: int) -> int:
        """Get quantity of a battle item (0=Speed Up … 5=Sniper)."""
        self._validate_item_index(index)
        offset, size = OFFSETS[f"battle_items_{index}"]
        return self.save.read_int(offset, size)

    # ── Setters ─────────────────────────────────────────────────────────────

    def set_catfood(self, amount: int):
        """Set cat food amount (max safe: 99,999)."""
        self._write("catfood", amount, MAX_SAFE["catfood"])

    def set_xp(self, amount: int):
        """Set XP amount (max safe: 9,999,999)."""
        self._write("xp", amount, MAX_SAFE["xp"])

    def set_rare_tickets(self, amount: int):
        """Set rare ticket count."""
        self._write("rare_tickets", amount, MAX_SAFE["rare_tickets"])

    def set_platinum_tickets(self, amount: int):
        """Set platinum ticket count."""
        self._write("platinum_tickets", amount, MAX_SAFE["platinum_tickets"])

    def set_leadership(self, amount: int):
        """Set leadership points."""
        self._write("leadership", amount, MAX_SAFE["leadership"])

    def set_platinum_shards(self, amount: int):
        """Set platinum shard count."""
        self._write("platinum_shards", amount, MAX_SAFE["platinum_shards"])

    def set_cat_energy(self, amount: int):
        """Set cat energy (stamina) amount."""
        self._write("cat_energy", amount, MAX_SAFE["cat_energy"])

    def set_battle_item(self, index: int, amount: int):
        """
        Set quantity of a battle item.
        index: 0=Speed Up, 1=Treasure Radar, 2=Rich Cat,
               3=Cat CPU, 4=Cat Jobs, 5=Sniper
        """
        self._validate_item_index(index)
        offset, size = OFFSETS[f"battle_items_{index}"]
        clamped = min(amount, MAX_SAFE["battle_items"])
        self.save.write_int(offset, clamped, size)
        print(f"  ✓ Battle item [{BATTLE_ITEM_NAMES[index]}] → {clamped:,}")

    def set_all_battle_items(self, amount: int):
        """Set all 6 battle items to the given amount."""
        for i in range(6):
            self.set_battle_item(i, amount)

    def max_resources(self):
        """Set all resources to their maximum safe values."""
        self.set_catfood(MAX_SAFE["catfood"])
        self.set_xp(MAX_SAFE["xp"])
        self.set_rare_tickets(MAX_SAFE["rare_tickets"])
        self.set_platinum_tickets(MAX_SAFE["platinum_tickets"])
        self.set_leadership(MAX_SAFE["leadership"])
        self.set_platinum_shards(MAX_SAFE["platinum_shards"])
        self.set_cat_energy(MAX_SAFE["cat_energy"])
        self.set_all_battle_items(MAX_SAFE["battle_items"])
        print("🎉 All resources maxed!")

    # ── Summary ─────────────────────────────────────────────────────────────

    def summary(self) -> str:
        lines = [
            "┌─────────────────────────────────┐",
            "│       Resource Summary          │",
            "├─────────────────────────────────┤",
            f"│  Cat Food        : {self.get_catfood():>10,}  │",
            f"│  XP              : {self.get_xp():>10,}  │",
            f"│  Rare Tickets    : {self.get_rare_tickets():>10,}  │",
            f"│  Platinum Tickets: {self.get_platinum_tickets():>10,}  │",
            f"│  Leadership      : {self.get_leadership():>10,}  │",
            f"│  Platinum Shards : {self.get_platinum_shards():>10,}  │",
            f"│  Cat Energy      : {self.get_cat_energy():>10,}  │",
            "├─────────────────────────────────┤",
        ]
        for i, name in enumerate(BATTLE_ITEM_NAMES):
            lines.append(f"│  {name:<18}: {self.get_battle_item(i):>10,}  │")
        lines.append("└─────────────────────────────────┘")
        return "\n".join(lines)

    # ── Internal ─────────────────────────────────────────────────────────────

    def _read(self, key: str) -> int:
        offset, size = OFFSETS[key]
        return self.save.read_int(offset, size)

    def _write(self, key: str, value: int, max_val: int):
        clamped = min(value, max_val)
        if clamped != value:
            print(f"  ⚠ {key} clamped from {value:,} to {clamped:,} (max safe: {max_val:,})")
        offset, size = OFFSETS[key]
        self.save.write_int(offset, clamped, size)
        print(f"  ✓ {key} → {clamped:,}")

    @staticmethod
    def _validate_item_index(index: int):
        if not (0 <= index <= 5):
            raise ValueError(f"Battle item index must be 0–5, got {index}")
