from typing import Any

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError

from tools.aes_decrypt.aes_decrypt import AesDecryptTool
from tools.aes_encrypt.aes_encrypt import AesEncryptTool
from tools.ed25519_keygen.ed25519_keygen import Ed25519KeygenTool
from tools.ed25519_sign.ed25519_sign import Ed25519SigningTool
from tools.ed25519_verify.ed25519_verify import Ed25519VerificationTool
from tools.hmac_sign.hmac_sign import HmacSignTool
from tools.md5sum.md5sum import Md5SumTool
from tools.rsa_decrypt.rsa_decrypt import RsaDecryptTool
from tools.rsa_encrypt.rsa_encrypt import RsaEncryptTool
from tools.rsa_keygen.rsa_keygen import RsaKeygenTool
from tools.sha256sum.sha256sum import Sha256SumTool


class CryptoProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            """
            IMPLEMENT YOUR VALIDATION HERE
            """
            # Signing
            Sha256SumTool.from_credentials({})
            Md5SumTool.from_credentials({})
            HmacSignTool.from_credentials({})

            # Ed25519
            Ed25519KeygenTool.from_credentials({})
            Ed25519SigningTool.from_credentials({})
            Ed25519VerificationTool.from_credentials({})

            # RSA
            RsaKeygenTool.from_credentials({})
            RsaEncryptTool.from_credentials({})
            RsaDecryptTool.from_credentials({})

            # AES
            AesEncryptTool.from_credentials({})
            AesDecryptTool.from_credentials({})
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))
