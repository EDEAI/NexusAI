from typing import Any

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError
import boto3

class Botos3Provider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            """
            IMPLEMENT YOUR VALIDATION HERE
            """
            required_keys = ["S3_ENDPOINT", "S3_ACCESS_KEY", "S3_SECRET_KEY", "BUCKET_NAME"]
            for key in required_keys:
                if key not in credentials:
                    raise ToolProviderCredentialValidationError(f"Missing required credential: {key}")
            s3_client = boto3.client(
                's3',
                endpoint_url=credentials["S3_ENDPOINT"],
                aws_access_key_id=credentials["S3_ACCESS_KEY"],
                aws_secret_access_key=credentials["S3_SECRET_KEY"],
            )
            s3_client.list_objects_v2(Bucket=credentials["BUCKET_NAME"])# This will raise an error if credentials are invalid
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))
