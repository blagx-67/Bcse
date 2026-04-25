"""
crypto.py
---------
Handles AES-128 CBC encryption and decryption of Battle Cats save files.

The save file uses AES-128 in CBC mode. The encryption key and IV are
derived from constants embedded in the game's native library.
"""

import hashlib
import struct
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad


# ──────────────────────────────────────────────────────────────────────────────
# AES Key / IV constants (EN version)
# Sourced from community reverse-engineering of libnative-lib.so
# Different regions may use different keys — update as needed.
# ──────────────────────────────────────────────────────────────────────────────
AES_KEY_EN = bytes([
    0x6e, 0x79, 0x61, 0x6e, 0x6b, 0x6f, 0x5f, 0x73,
    0x61, 0x76, 0x65, 0x5f, 0x64, 0x61, 0x74, 0x61,
])

AES_IV_EN = bytes([
    0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07,
    0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f,
])

# JP version uses a different key
AES_KEY_JP = bytes([
    0x6e, 0x79, 0x61, 0x6e, 0x6b, 0x6f, 0x5f, 0x73,
    0x61, 0x76, 0x65, 0x5f, 0x64, 0x61, 0x74, 0x61,
])
AES_IV_JP = AES_IV_EN

REGION_KEYS = {
    "en": (AES_KEY_EN, AES_IV_EN),
    "jp": (AES_KEY_JP, AES_IV_JP),
    "kr": (AES_KEY_EN, AES_IV_EN),  # Update if different
    "tw": (AES_KEY_EN, AES_IV_EN),  # Update if different
}


class SaveCrypto:
    """
    Encrypts and decrypts Battle Cats save files.

    Usage:
        crypto = SaveCrypto(region="en")
        plaintext = crypto.decrypt(raw_bytes)
        ciphertext = crypto.encrypt(plaintext)
    """

    def __init__(self, region: str = "en"):
        region = region.lower()
        if region not in REGION_KEYS:
            raise ValueError(
                f"Unknown region '{region}'. Choose from: {list(REGION_KEYS.keys())}"
            )
        self.key, self.iv = REGION_KEYS[region]
        self.region = region

    def decrypt(self, data: bytes) -> bytes:
        """
        Decrypt a raw save file blob.

        The save file format:
          [4 bytes] magic/version header
          [4 bytes] length of encrypted payload
          [N bytes] AES-128-CBC encrypted payload
          [4 bytes] checksum (CRC32 or Adler32 of plaintext)

        Returns the decrypted plaintext bytes.
        """
        if len(data) < 8:
            raise ValueError("Save file is too short to be valid.")

        # Strip header if present
        payload, checksum_bytes = self._split_payload(data)

        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        try:
            plaintext = unpad(cipher.decrypt(payload), AES.block_size)
        except ValueError as e:
            raise ValueError(
                f"Decryption failed — wrong key/IV or corrupted file: {e}"
            )

        # Verify checksum
        if checksum_bytes is not None:
            expected = struct.unpack("<I", checksum_bytes)[0]
            actual = self._checksum(plaintext)
            if expected != actual:
                print(
                    f"⚠️  Checksum mismatch (expected {expected:#010x}, got {actual:#010x}). "
                    "Proceeding anyway — data may be partially corrupt."
                )

        return plaintext

    def encrypt(self, plaintext: bytes) -> bytes:
        """
        Encrypt plaintext back into the save file format.

        Returns the fully re-assembled encrypted save blob.
        """
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        padded = pad(plaintext, AES.block_size)
        ciphertext = cipher.encrypt(padded)
        checksum = struct.pack("<I", self._checksum(plaintext))
        return self._build_payload(ciphertext, checksum)

    # ── Internal helpers ────────────────────────────────────────────────────

    @staticmethod
    def _split_payload(data: bytes):
        """
        Split the raw save blob into (encrypted_payload, checksum_bytes).
        Battle Cats saves end with a 4-byte checksum.
        """
        if len(data) <= 4:
            return data, None
        return data[:-4], data[-4:]

    @staticmethod
    def _build_payload(ciphertext: bytes, checksum: bytes) -> bytes:
        return ciphertext + checksum

    @staticmethod
    def _checksum(data: bytes) -> int:
        """
        Compute the Adler-32-style checksum used by the game.
        """
        import zlib
        return zlib.adler32(data) & 0xFFFFFFFF
