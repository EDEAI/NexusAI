import json
from dify_plugin.errors.tool import ToolProviderCredentialValidationError
from tools.spark_img_generation import spark_response
from dify_plugin import ToolProvider


class SparkProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict) -> None:
        try:
            if "APPID" not in credentials or not credentials.get("APPID"):
                raise ToolProviderCredentialValidationError("APPID is required.")
            if "APISecret" not in credentials or not credentials.get("APISecret"):
                raise ToolProviderCredentialValidationError("APISecret is required.")
            if "APIKey" not in credentials or not credentials.get("APIKey"):
                raise ToolProviderCredentialValidationError("APIKey is required.")
            appid = credentials.get("APPID")
            apisecret = credentials.get("APISecret")
            apikey = credentials.get("APIKey")
            prompt = "a cute black dog"
            try:
                response = spark_response(prompt, appid, apikey, apisecret)
                data = json.loads(response)
                code = data["header"]["code"]
                if code == 0:
                    pass
                else:
                    raise ToolProviderCredentialValidationError("image generate error, code:{}".format(code))
            except Exception as e:
                raise ToolProviderCredentialValidationError("APPID APISecret APIKey is invalid. {}".format(e))
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))
