"""Local at-rest encryption for secrets stored in ~/.skillnir/config.json.

Purpose
-------
Webhook URLs (Google Chat incoming webhooks) are *capability tokens*: anyone
with the URL can post to the space. Storing them in plaintext in
``config.json`` means:

- A config file accidentally committed to git, synced to Dropbox, backed up,
  or pasted into a log immediately leaks a working token.
- Copying the file between machines "just works", which is bad.

This module mitigates both by encrypting secrets with a key derived from a
**per-install UUID** (stored at ``~/.skillnir/client_id``) combined with a
**machine fingerprint** (hostname, username, home path, platform). The
resulting key is bound to the machine + install: a copied config file cannot
be decrypted on another machine.

Threat model — what this does NOT protect against
--------------------------------------------------
This is at-rest obfuscation, not a vault.

- Malware running as the same user on the same machine can call
  ``decrypt_string`` directly — the whole point is that the app can decrypt
  transparently, so any code running as the user can too.
- Root or anyone with read access to the machine + Python.
- Anyone who captures the plaintext at runtime via memory inspection.

If a webhook URL was ever logged, screenshotted, or printed, encryption does
NOT retroactively protect it — rotate the webhook in Google Chat instead.
"""

from __future__ import annotations

import base64
import hashlib
import platform
import sys
import uuid
from getpass import getuser
from pathlib import Path

from cryptography.fernet import Fernet, InvalidToken

# Fixed salt — the per-install uniqueness comes from CLIENT_ID_FILE, not salt.
_SALT = b"skillnir-config-v1"
_PBKDF2_ITERATIONS = 100_000
_KEY_BYTES = 32

CLIENT_ID_FILE = Path.home() / ".skillnir" / "client_id"


def _get_or_create_client_id() -> str:
    """Return the persistent per-install UUID, creating it on first call."""
    try:
        if CLIENT_ID_FILE.exists():
            existing = CLIENT_ID_FILE.read_text(encoding="utf-8").strip()
            if existing:
                return existing
    except OSError:
        pass

    cid = str(uuid.uuid4())
    try:
        CLIENT_ID_FILE.parent.mkdir(parents=True, exist_ok=True)
        CLIENT_ID_FILE.write_text(cid + "\n", encoding="utf-8")
        # Restrict to owner read/write on POSIX; best-effort on Windows.
        try:
            CLIENT_ID_FILE.chmod(0o600)
        except OSError:
            pass
    except OSError:
        # If we can't persist, fall back to an ephemeral per-process UUID.
        # Decryption will only work within this process — bad but non-fatal.
        pass
    return cid


def _machine_fingerprint() -> bytes:
    """Assemble a machine-bound input string for key derivation."""
    parts = [
        platform.node(),
        getuser(),
        sys.platform,
        str(Path.home()),
        _get_or_create_client_id(),
    ]
    return "|".join(parts).encode("utf-8")


def _derive_key() -> bytes:
    """Derive a Fernet-compatible key (base64-encoded 32 bytes)."""
    material = _machine_fingerprint()
    key_bytes = hashlib.pbkdf2_hmac(
        "sha256",
        material,
        _SALT,
        iterations=_PBKDF2_ITERATIONS,
        dklen=_KEY_BYTES,
    )
    return base64.urlsafe_b64encode(key_bytes)


def encrypt_string(plaintext: str) -> str:
    """Encrypt ``plaintext`` with the machine-bound key.

    Returns a Fernet token (URL-safe base64 ASCII). Empty input returns empty.
    """
    if not plaintext:
        return ""
    fernet = Fernet(_derive_key())
    return fernet.encrypt(plaintext.encode("utf-8")).decode("ascii")


def decrypt_string(token: str) -> str:
    """Decrypt a Fernet token with the machine-bound key.

    Returns the plaintext, or an empty string if:
    - ``token`` is empty,
    - the token was produced on a different machine / install,
    - the token is corrupt or malformed.

    Never raises.
    """
    if not token:
        return ""
    try:
        fernet = Fernet(_derive_key())
        return fernet.decrypt(token.encode("ascii")).decode("utf-8")
    except InvalidToken, ValueError, TypeError:
        return ""
