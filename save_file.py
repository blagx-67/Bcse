"""
save_file.py
------------
Core class for loading, parsing, and writing Battle Cats save files.
All editors operate on a SaveFile instance.
"""

import os
import shutil
import struct
from datetime import datetime
from pathlib import Path
from typing import Optional

from editor.crypto import SaveCrypto


class SaveFile:
    """
    Represents a loaded (and optionally decrypted) Battle Cats save file.

    Usage:
        save = SaveFile("SAVE_DATA", region="en")
        save.decrypt()
        # ... make edits via editor modules ...
        save.encrypt()
        save.write("SAVE_DATA_EDITED")
    """

    def __init__(self, path: str, region: str = "en"):
        self.path = Path(path)
        self.region = region.lower()
        self.crypto = SaveCrypto(region=self.region)

        self._raw: bytes = b""        # Original encrypted bytes
        self.data: bytearray = bytearray()  # Decrypted, mutable bytes
        self._decrypted = False

        self._load()

    # ── I/O ────────────────────────────────────────────────────────────────

    def _load(self):
        """Read the raw save file from disk."""
        if not self.path.exists():
            raise FileNotFoundError(f"Save file not found: {self.path}")
        with open(self.path, "rb") as f:
            self._raw = f.read()
        print(f"📂 Loaded save file: {self.path} ({len(self._raw):,} bytes)")

    def decrypt(self):
        """Decrypt the raw save data into `self.data`."""
        plaintext = self.crypto.decrypt(self._raw)
        self.data = bytearray(plaintext)
        self._decrypted = True
        print(f"🔓 Decrypted successfully ({len(self.data):,} bytes plaintext)")

    def encrypt(self):
        """Re-encrypt `self.data` back to `self._raw`."""
        if not self._decrypted:
            raise RuntimeError("Cannot encrypt: data has not been decrypted yet.")
        self._raw = self.crypto.encrypt(bytes(self.data))
        print(f"🔒 Re-encrypted ({len(self._raw):,} bytes)")

    def write(self, output_path: Optional[str] = None):
        """Write the (re-encrypted) save file to disk."""
        dest = Path(output_path) if output_path else self.path
        # Auto-backup the original if overwriting
        if dest == self.path and dest.exists():
            self._backup()
        with open(dest, "wb") as f:
            f.write(self._raw)
        print(f"✅ Written to: {dest}")

    def _backup(self):
        """Create a timestamped backup of the original save file."""
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.path.parent / f"{self.path.name}.bak_{ts}"
        shutil.copy2(self.path, backup_path)
        print(f"💾 Backup created: {backup_path}")

    # ── Low-level read/write helpers ────────────────────────────────────────

    def read_int(self, offset: int, size: int = 4, signed: bool = False) -> int:
        """Read a little-endian integer from the decrypted data."""
        self._require_decrypted()
        raw = bytes(self.data[offset : offset + size])
        return int.from_bytes(raw, "little", signed=signed)

    def write_int(self, offset: int, value: int, size: int = 4, signed: bool = False):
        """Write a little-endian integer into the decrypted data."""
        self._require_decrypted()
        value = max(0, value) if not signed else value
        encoded = value.to_bytes(size, "little", signed=signed)
        self.data[offset : offset + size] = encoded

    def read_bytes(self, offset: int, length: int) -> bytes:
        """Read raw bytes from the decrypted data."""
        self._require_decrypted()
        return bytes(self.data[offset : offset + length])

    def write_bytes(self, offset: int, data: bytes):
        """Write raw bytes into the decrypted data."""
        self._require_decrypted()
        self.data[offset : offset + len(data)] = data

    def _require_decrypted(self):
        if not self._decrypted:
            raise RuntimeError(
                "Save file has not been decrypted yet. Call .decrypt() first."
            )

    # ── Info ───────────────────────────────────────────────────────────────

    def __repr__(self):
        status = "decrypted" if self._decrypted else "encrypted"
        return f"<SaveFile '{self.path.name}' region={self.region} [{status}]>"

    def dump_hex(self, offset: int, length: int = 64):
        """Print a hex dump around a given offset (for debugging)."""
        chunk = self.read_bytes(offset, length)
        for i in range(0, len(chunk), 16):
            row = chunk[i : i + 16]
            hex_part = " ".join(f"{b:02x}" for b in row)
            asc_part = "".join(chr(b) if 32 <= b < 127 else "." for b in row)
            print(f"  {offset+i:08x}  {hex_part:<47}  {asc_part}")
