from pgpy.constants import PubKeyAlgorithm, KeyFlags, HashAlgorithm, SymmetricKeyAlgorithm, CompressionAlgorithm, EllipticCurveOID
from pgpy import PGPKey, PGPMessage, PGPSignature, PGPUID
from pgpy.errors import PGPError

# Encrypt, decrypt, sign, and verify text messages using GPG (GnuPG).
# 使用 GPG (GnuPG) 加密、解密、签名和验证文本消息。
def encrypt_message(plaintext: str, recipient_pubkey_str: str) -> str:
    """Encrypts a message using the recipient's public key.

    Args:
        plaintext: The plaintext string to encrypt.
        recipient_pubkey_str: The recipient's PGP public key as an
            ASCII-armored string.

    Returns:
        The encrypted PGP message as an ASCII-armored string.

    Raises:
        ValueError: If the encryption process fails (e.g., due to an invalid
            public key or other PGP processing issues).
        PGPError: If a specific error occurs within the pgpy library during
            key loading or encryption.
    """
    try:
        pubkey, _ = PGPKey.from_blob(recipient_pubkey_str)
        # Create a PGP message from the plaintext string (file=False indicates string data)
        message = PGPMessage.new(plaintext, file=False)
        encrypted_message = pubkey.encrypt(message)
        return str(encrypted_message)
        # return str(PGPKey.from_blob(recipient_pubkey_str)[0].encrypt(PGPMessage.new(plaintext, file=False)))
    except PGPError as e:
        raise ValueError(f"Encryption failed due to PGP error: {e}") from e
    except Exception as e:
        raise ValueError(f"Encryption failed: {e}") from e


def decrypt_message(ciphertext: str, private_key_str: str, passphrase: str = None) -> str:
    """Decrypts a message using the recipient's private key.

    Args:
        ciphertext: The encrypted PGP message as an ASCII-armored string.
        private_key_str: The recipient's PGP private key as an ASCII-armored
            string.
        passphrase: The passphrase for the private key, if it is protected.
            Defaults to None.

    Returns:
        The decrypted plaintext string.

    Raises:
        ValueError: If the decryption process fails (e.g., due to an invalid
            private key, missing or incorrect passphrase for a protected key,
            or other PGP processing issues).
        PGPError: If a specific error occurs within the pgpy library during
            key loading, unlocking, or decryption.
    """
    try:
        privkey, _ = PGPKey.from_blob(private_key_str)
        encrypted_message = PGPMessage.from_blob(ciphertext)

        if privkey.is_protected:
            if not passphrase:
                raise ValueError(
                    "Private key is passphrase protected, but no passphrase provided.")
            # PGPError can be raised here if passphrase is wrong
            with privkey.unlock(passphrase):
                decrypted_message = privkey.decrypt(encrypted_message)
        else:
            decrypted_message = privkey.decrypt(encrypted_message)

        # .message returns bytes, decode assuming utf-8
        if isinstance(decrypted_message.message, bytes):
            return decrypted_message.message.decode('utf-8')
        return decrypted_message.message  # Already a string
    except PGPError as e:
        # Catches errors like incorrect passphrase or decryption failures
        raise ValueError(f"Decryption failed due to PGP error: {e}") from e
    except Exception as e:
        raise ValueError(f"Decryption failed: {e}") from e
    # return PGPKey.from_blob(private_key_str)[0].decrypt(PGPMessage.from_blob(ciphertext), passphrase=passphrase).message.decode('utf-8')


def sign_message(plaintext: str, private_key_str: str, passphrase: str = None) -> str:
    """Signs a message using the sender's private key, generating a detached signature.

    Args:
        plaintext: The plaintext string to sign.
        private_key_str: The signer's PGP private key as an ASCII-armored
            string.
        passphrase: The passphrase for the private key, if it is protected.
            Defaults to None.

    Returns:
        The detached PGP signature as an ASCII-armored string.

    Raises:
        ValueError: If the signing process fails (e.g., due to an invalid
            private key, missing or incorrect passphrase for a protected key,
            or other PGP processing issues).
        PGPError: If a specific error occurs within the pgpy library during
            key loading, unlocking, or signing.
    """
    try:
        privkey, _ = PGPKey.from_blob(private_key_str)
        message_to_sign = plaintext  # pgpy sign method accepts bytes or string

        if privkey.is_protected:
            if not passphrase:
                raise ValueError(
                    "Private key is passphrase protected, but no passphrase provided.")
            # PGPError can be raised here if passphrase is wrong
            with privkey.unlock(passphrase):
                signature_obj = privkey.sign(message_to_sign)
        else:
            signature_obj = privkey.sign(message_to_sign)

        return str(signature_obj)
    except PGPError as e:
        # Catches errors like incorrect passphrase or signing failures
        raise ValueError(f"Signing failed due to PGP error: {e}") from e
    except Exception as e:
        raise ValueError(f"Signing failed: {e}") from e


def verify_message(original_message: str, signature_blob: str, signer_pubkey_str: str) -> bool:
    """Verifies a detached signature against the original message using the signer's public key.

    Args:
        original_message: The original plaintext message that was signed.
        signature_blob: The detached PGP signature as an ASCII-armored string.
        signer_pubkey_str: The signer's PGP public key as an ASCII-armored
            string.

    Returns:
        True if the signature is valid for the message and public key, False otherwise.

    Raises:
        PGPError: If an error occurs during the loading of the key or
            signature, or if the signature itself is malformed. Note that
            a signature simply failing verification typically results in a
            False return value, not an exception, unless there's a problem
            processing the data.
    """
    try:
        pubkey, _ = PGPKey.from_blob(signer_pubkey_str)
        signature = PGPSignature.from_blob(signature_blob)

        # pubkey.verify returns the key if successful, raises PGPError otherwise.
        try:
            verification_result = pubkey.verify(original_message, signature)
            # Verification successful if no exception is raised and result is not None
            return verification_result is not None
        except PGPError:
            # Specific PGP errors during verify() indicate verification failure.
            return False

    except PGPError as e:
        # Errors during loading keys/signatures.
        # Consider logging this error if debugging is needed.
        # print(f"Verification setup failed due to PGPError: {e}")
        raise ValueError(
            f"Verification failed due to PGP error: {e}") from e
    except Exception as e:
        # Catch other potential errors during key/signature loading.
        # Consider logging this error if debugging is needed.
        # print(f"Verification encountered an unexpected error: {e}")
        raise ValueError(f"Verification failed: {e}") from e


def generate_key_pair(real_name: str, email: str, passphrase: str = None, key_type: PubKeyAlgorithm = PubKeyAlgorithm.EdDSA, key_param=None) -> tuple[str, str]:
    """Generates a new PGP key pair (primary signing key and optional encryption subkey).

    Args:
        real_name: The real name for the User ID (e.g., "John Doe").
        email: The email address for the User ID (e.g., "john.doe@example.com").
        passphrase: Optional passphrase to protect the private key.
        key_type: The algorithm for the primary key (default: EdDSA).
            If a signing-only type (like EdDSA, ECDSA, DSA, RSASign) is chosen,
            an appropriate encryption subkey (e.g., ECDH Curve25519) will be added.
        key_param: Key length (for RSA/DSA/ElGamal, e.g., 3072) or elliptic curve
            (for EdDSA/ECDSA/ECDH, e.g., EllipticCurveOID.Ed25519).
            Defaults are provided for common types if None.

    Returns:
        A tuple containing (private_key_armored, public_key_armored).

    Raises:
        RuntimeError: If any error occurs during key generation.
        PGPError: If a specific pgpy library error occurs.
        ValueError: If key_param is invalid or missing when required.
    """
    try:
        primary_param_to_use = key_param
        add_encryption_subkey = False

        # Determine primary key parameters and if an encryption subkey is needed
        if key_type in [PubKeyAlgorithm.RSAEncryptOrSign, PubKeyAlgorithm.ElGamal]:
            if primary_param_to_use is None:
                primary_param_to_use = 3072
            elif not isinstance(primary_param_to_use, int):
                raise ValueError(
                    f"key_param must be an integer for {key_type.name}")
        elif key_type in [PubKeyAlgorithm.DSA, PubKeyAlgorithm.RSASign]:
            add_encryption_subkey = True
            if primary_param_to_use is None:
                primary_param_to_use = 3072
            elif not isinstance(primary_param_to_use, int):
                raise ValueError(
                    f"key_param must be an integer for {key_type.name}")
        elif key_type in [PubKeyAlgorithm.EdDSA, PubKeyAlgorithm.ECDSA]:
            add_encryption_subkey = True
            if primary_param_to_use is None:
                primary_param_to_use = EllipticCurveOID.Ed25519 if key_type == PubKeyAlgorithm.EdDSA else EllipticCurveOID.NIST_P256
            elif not isinstance(primary_param_to_use, EllipticCurveOID):
                raise ValueError(
                    f"key_param must be an EllipticCurveOID for {key_type.name}")
        elif key_type == PubKeyAlgorithm.ECDH:
            if primary_param_to_use is None:
                primary_param_to_use = EllipticCurveOID.Curve25519
            elif not isinstance(primary_param_to_use, EllipticCurveOID):
                raise ValueError(
                    f"key_param must be an EllipticCurveOID for {key_type.name}")
        else:
            raise ValueError(
                f"Unsupported key type or missing parameter logic: {key_type.name}")

        # Generate Primary Key
        primary_key = PGPKey.new(key_type, primary_param_to_use)

        # Add User ID with appropriate flags
        uid = PGPUID.new(real_name, email=email)
        primary_usage = {KeyFlags.Certify, KeyFlags.Sign}
        if key_type.can_encrypt:
            primary_usage |= {KeyFlags.EncryptCommunications,
                              KeyFlags.EncryptStorage}
        if key_type in [PubKeyAlgorithm.EdDSA, PubKeyAlgorithm.ECDSA]:
            primary_usage |= {KeyFlags.Authentication}

        primary_key.add_uid(
            uid,
            usage=primary_usage,
            hashes=[HashAlgorithm.SHA512,
                    HashAlgorithm.SHA384, HashAlgorithm.SHA256],
            ciphers=[SymmetricKeyAlgorithm.AES256,
                     SymmetricKeyAlgorithm.AES192, SymmetricKeyAlgorithm.AES128],
            compression=[CompressionAlgorithm.ZLIB, CompressionAlgorithm.BZ2,
                         CompressionAlgorithm.ZIP, CompressionAlgorithm.Uncompressed]
        )

        # Add Encryption Subkey if primary key is signing-only
        if add_encryption_subkey:
            # Default to ECDH/Curve25519 for subkey, compatible with Ed/EcDSA
            subkey_curve = EllipticCurveOID.Curve25519
            subkey_algo = PubKeyAlgorithm.ECDH
            # Consider using ElGamal subkey if primary is DSA? (Less common now)
            # if key_type == PubKeyAlgorithm.DSA:
            #    subkey_algo = PubKeyAlgorithm.ElGamal
            #    subkey_curve = 3072 # Or appropriate size

            subkey = PGPKey.new(subkey_algo, subkey_curve)
            primary_key.add_subkey(
                subkey, usage={KeyFlags.EncryptCommunications, KeyFlags.EncryptStorage})

        # Protect Key with passphrase if provided
        if passphrase:
            primary_key.protect(
                passphrase, SymmetricKeyAlgorithm.AES256, HashAlgorithm.SHA512)

        # Export Keys
        private_key_str = str(primary_key)
        public_key_str = str(primary_key.pubkey)

        return private_key_str, public_key_str
    except PGPError as e:
        raise RuntimeError(
            f"Key generation failed due to PGP error: {e}") from e
    except Exception as e:
        raise RuntimeError(f"Key generation failed: {e}") from e


# Example usage and testing block
if __name__ == "__main__":
    print("Generating EdDSA key pair (with ECDH subkey)...")
    try:
        priv_key_str, pub_key_str = generate_key_pair(
            "Test User Modern", "test-modern@example.com", "secret-modern")
        print("Modern key pair generated.")
        # print("\nPrivate Key:\n", priv_key_str) # Uncomment to view
        print("\nPublic Key:\n", pub_key_str)

        # Test Encryption & Decryption (uses subkey)
        print("\nTesting Encryption & Decryption...")
        original_message = "Hello, this is a modern secret message!"
        encrypted = encrypt_message(original_message, pub_key_str)
        decrypted = decrypt_message(encrypted, priv_key_str, "secret-modern")
        print(f"Original:  {original_message}")
        print(f"Decrypted: {decrypted}")
        assert original_message == decrypted
        print("Encryption/Decryption test PASSED.")

        # Test Signing & Verification (uses primary key)
        print("\nTesting Signing & Verification...")
        message_to_sign = "This message needs to be signed with EdDSA."
        signed_signature_blob = sign_message(
            message_to_sign, priv_key_str, "secret-modern")
        is_valid = verify_message(
            message_to_sign, signed_signature_blob, pub_key_str)
        print(f"Message: {message_to_sign}")
        print(f"Signature valid (correct key): {is_valid}")
        assert is_valid is True
        print("Signing/Verification test PASSED.")

        # Test Verification Failure
        print("\nTesting verification failure (wrong key)...")
        try:
            other_priv, other_pub = generate_key_pair(
                "Another User", "another@example.com", key_type=PubKeyAlgorithm.RSAEncryptOrSign, key_param=3072)
            is_valid_wrong_key = verify_message(
                message_to_sign, signed_signature_blob, str(other_pub))
            print(f"Signature valid (wrong key): {is_valid_wrong_key}")
            assert is_valid_wrong_key is False
            print("Verification failure test PASSED.")
        except Exception as e:
            print(f"Verification failure test encountered an error: {e}")

    except Exception as e:
        print(f"\nAn error occurred during testing: {e}")
