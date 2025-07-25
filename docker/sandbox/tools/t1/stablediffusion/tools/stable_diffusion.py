
import json
from base64 import b64decode
from copy import deepcopy
from typing import Any, Generator, Union
from requests import get, post
from yarl import URL
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin.errors.tool import ToolProviderCredentialValidationError
from dify_plugin import Tool

DRAW_TEXT_OPTIONS = {
    "prompt": "",
    "negative_prompt": "",
    "seed": -1,
    "subseed": -1,
    "subseed_strength": 0,
    "seed_resize_from_h": -1,
    "seed_resize_from_w": -1,
    "sampler_name": "DPM++ 2M",
    "batch_size": 1,
    "n_iter": 1,
    "steps": 10,
    "cfg_scale": 7,
    "width": 512,
    "height": 512,
    "do_not_save_samples": False,
    "do_not_save_grid": False,
    "override_settings": {},
    "override_settings_restore_afterwards": True,
    "refiner_checkpoint": "",
    "refiner_switch_at": 0,
    "disable_extra_networks": False,
    "enable_hr": False,
    "firstphase_width": 0,
    "firstphase_height": 0,
    "hr_scale": 2,
    "hr_second_pass_steps": 0,
    "hr_resize_x": 0,
    "hr_resize_y": 0,
    "hr_prompt": "",
    "hr_negative_prompt": "",
    "script_args": [],
    "send_images": True,
    "save_images": False,
    "alwayson_scripts": {},
}


class StableDiffusionTool(Tool):
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        """
        invoke tools
        """
        base_url = self.runtime.credentials.get("base_url", None)
        if not base_url:
            yield self.create_text_message("Please input base_url")
        if tool_parameters.get("model"):
            self.runtime.credentials["model"] = tool_parameters["model"]
        model = self.runtime.credentials.get("model", None)
        if not model:
            yield self.create_text_message("Please input model")
        try:
            url = str(URL(base_url) / "sdapi" / "v1" / "options")
            response = post(url, data=json.dumps({"sd_model_checkpoint": model}))
            if response.status_code != 200:
                raise ToolProviderCredentialValidationError("Failed to set model, please tell user to set model")
        except Exception as e:
            raise ToolProviderCredentialValidationError("Failed to set model, please tell user to set model")
        
        yield from self.text2img(base_url, tool_parameters)

    def validate_models(self):
        """
        validate models
        """
        try:
            base_url = self.runtime.credentials.get("base_url", None)
            if not base_url:
                raise ToolProviderCredentialValidationError("Please input base_url")
            model = self.runtime.credentials.get("model", None)
            if not model:
                raise ToolProviderCredentialValidationError("Please input model")

            api_url = str(URL(base_url) / "sdapi" / "v1" / "sd-models")
            response = get(url=api_url, timeout=10)
            if response.status_code == 404:
                # try draw a picture
                for _ in self._invoke(
                    tool_parameters={
                        "prompt": "a cat",
                        "width": 1024,
                        "height": 1024,
                        "steps": 1,
                        "lora": "",
                    },
                ):
                    pass
            elif response.status_code != 200:
                raise ToolProviderCredentialValidationError("Failed to get models")
            else:
                models = [d["model_name"] for d in response.json()]
                if len([d for d in models if d == model]) > 0:
                    return self.create_text_message(json.dumps(models))
                else:
                    raise ToolProviderCredentialValidationError(f"model {model} does not exist")
        except Exception as e:
            raise ToolProviderCredentialValidationError(f"Failed to get models, {e}")

    def get_sd_models(self) -> list[str]:
        """
        get sd models
        """
        try:
            base_url = self.runtime.credentials.get("base_url", None)
            if not base_url:
                return []
            api_url = str(URL(base_url) / "sdapi" / "v1" / "sd-models")
            response = get(url=api_url, timeout=(2, 10))
            if response.status_code != 200:
                return []
            else:
                return [d["model_name"] for d in response.json()]
        except Exception as e:
            return []

    def get_sample_methods(self) -> list[str]:
        """
        get sample method
        """
        try:
            base_url = self.runtime.credentials.get("base_url", None)
            if not base_url:
                return []
            api_url = str(URL(base_url) / "sdapi" / "v1" / "samplers")
            response = get(url=api_url, timeout=(2, 10))
            if response.status_code != 200:
                return []
            else:
                return [d["name"] for d in response.json()]
        except Exception as e:
            return []

    def text2img(
        self, base_url: str, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        """
        generate image
        """
        draw_options = deepcopy(DRAW_TEXT_OPTIONS)
        draw_options.update(tool_parameters)
        prompt = tool_parameters.get("prompt", "")
        lora = tool_parameters.get("lora", "")
        model = tool_parameters.get("model", "")
        if lora:
            draw_options["prompt"] = f"{lora},{prompt}"
        else:
            draw_options["prompt"] = prompt
        draw_options["override_settings"]["sd_model_checkpoint"] = model
        try:
            url = str(URL(base_url) / "sdapi" / "v1" / "txt2img")
            response = post(url, data=json.dumps(draw_options), timeout=120)
            if response.status_code != 200:
                yield self.create_text_message("Failed to generate image")
            image = response.json()["images"][0]
            yield self.create_blob_message(
                blob=b64decode(image), meta={"mime_type": "image/png"}
            )
        except Exception as e:
            yield self.create_text_message("Failed to generate image")

    