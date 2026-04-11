"""Tests for skillnir.crypto -- at-rest encryption helpers."""

from unittest.mock import patch

from skillnir.crypto import decrypt_string, encrypt_string


class TestEncryptDecryptRoundTrip:
    def test_empty_input_roundtrips_as_empty(self):
        assert encrypt_string("") == ""
        assert decrypt_string("") == ""

    def test_plaintext_roundtrip(self):
        secret = "https://chat.googleapis.com/v1/spaces/X/messages?key=Y&token=Z"
        token = encrypt_string(secret)
        assert token  # non-empty
        assert secret not in token  # plaintext is not in the ciphertext
        assert decrypt_string(token) == secret

    def test_two_encryptions_differ(self):
        # Fernet includes a timestamp + random IV, so the same plaintext
        # should produce different tokens each time.
        a = encrypt_string("hello")
        b = encrypt_string("hello")
        assert a != b
        assert decrypt_string(a) == "hello"
        assert decrypt_string(b) == "hello"


class TestDecryptFailureModes:
    def test_garbage_token_returns_empty(self):
        assert decrypt_string("not-a-real-fernet-token") == ""

    def test_corrupted_token_returns_empty(self):
        good = encrypt_string("hello")
        corrupted = good[:-5] + "XXXXX"
        assert decrypt_string(corrupted) == ""

    def test_different_machine_fingerprint_fails_to_decrypt(self):
        """Simulate copying an encrypted config to a different machine.

        We patch ``_machine_fingerprint`` between encrypt and decrypt to
        produce a different derived key, which should make decryption fail
        silently (return empty string, never raise).
        """
        token = encrypt_string("https://example.test/FAKE")

        with patch(
            "skillnir.crypto._machine_fingerprint",
            return_value=b"totally-different-machine-fingerprint",
        ):
            result = decrypt_string(token)
        assert result == ""
