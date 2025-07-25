import requests

API_ENDPOINT = "https://api.minimaxi.com/v1"


class MiniMaxBaseTool:
    def __init__(self, api_key: str, group_id: str):
        self.api_key = api_key
        self.group_id = group_id
        if not self.api_key:
            raise ValueError("Api key are required")
        if not self.group_id:
            raise ValueError("Group id are required")

    def _get_headers(self) -> dict:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
        }
        return headers

    def _request(self, method: str, url: str, **kwargs) -> requests.Response:
        return requests.request(method, url, headers=self._get_headers(), **kwargs)

    def text_to_image(
        self,
        model: str,
        prompt: str,
        aspect_ratio: str,
        response_format: str,
        prompt_optimizer: bool,
        n: int,
    ) -> requests.Response:
        response = self._request(
            "POST",
            f"{API_ENDPOINT}/image_generation",
            json={
                "model": model,
                "prompt": prompt,
                "aspect_ratio": aspect_ratio,
                "response_format": response_format,
                "prompt_optimizer": prompt_optimizer,
                "n": n,
            },
        )
        return response

    def music_upload(
        self, file_name: str, file_blob: bytes, mime_type: str
    ) -> requests.Response:
        files = [("file", (file_name, file_blob, mime_type))]
        response = self._request(
            "POST",
            f"{API_ENDPOINT}/music_upload",
            data={"purpose": "song"},
            files=files,
        )
        return response

    def music_generation(
        self,
        model: str,
        refer_voice: str,
        refer_instrumental: str,
        refer_vocal: str,
        lyrics: str,
    ) -> requests.Response:
        response = self._request(
            "POST",
            f"{API_ENDPOINT}/music_generation",
            json={
                "model": model,
                "refer_voice": refer_voice,
                "refer_instrumental": refer_instrumental,
                "refer_vocal": refer_vocal,
                "lyrics": lyrics,
            },
        )
        return response

    def file_upload(
        self, file_name: str, file_blob: bytes, mime_type: str, purpose: str
    ) -> requests.Response:
        files = [("file", (file_name, file_blob, mime_type))]
        response = self._request(
            "POST",
            f"{API_ENDPOINT}/files/upload",
            params={
                "GroupId": self.group_id,
            },
            data={"purpose": purpose},
            files=files,
        )
        return response

    def voice_clone(
        self,
        model: str,
        file_id: str,
        voice_id: str,
        text: str,
        accuracy: float,
        need_noise_reduction: bool,
        need_volume_normalization: bool,
    ) -> requests.Response:
        response = self._request(
            "POST",
            f"{API_ENDPOINT}/voice_clone",
            json={
                "model": model,
                "file_id": file_id,
                "voice_id": voice_id,
                "text": text,
                "accuracy": accuracy,
                "need_noise_reduction": need_noise_reduction,
                "need_volume_normalization": need_volume_normalization,
            },
        )
        return response

    def video_generation_task(self, task_id: str):
        response = self._request(
            "GET",
            f"{API_ENDPOINT}/query/video_generation",
            params={"task_id": task_id},
        )
        return response

    def video_generation(
        self,
        model: str,
        prompt: str,
        prompt_optimizer: bool,
        duration: int,
        resolution: str,
        first_frame_image: str,
    ) -> requests.Response:
        response = self._request(
            "POST",
            f"{API_ENDPOINT}/video_generation",
            data={
                "model": model,
                "prompt": prompt,
                "prompt_optimizer": prompt_optimizer,
                "duration": duration,
                "resolution": resolution,
                "first_frame_image": first_frame_image,
            },
        )
        return response

    def file_retrieve(self, file_id: str) -> requests.Response:
        response = self._request(
            "GET",
            f"{API_ENDPOINT}/files/retrieve",
            params={"GroupId": self.group_id, "file_id": file_id},
        )
        return response

    def file_list(self, purpose: str) -> requests.Response:
        response = self._request(
            "GET",
            f"{API_ENDPOINT}/files/list",
            params={"GroupId": self.group_id, "purpose": purpose},
        )
        return response
