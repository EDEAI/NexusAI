import requests


class CivitAI:
    # Base on https://developer.civitai.com/docs/api/public-rest
    def __init__(self, api_key=None):
        self._api_key = api_key

    def _call(self, url, params, with_key=False) -> dict:
        headers = {
            "Content-Type": "application/json",
        }
        if with_key:
            if self._api_key is None:
                raise Exception("api_key not found")
            headers["Authorization"] = f"Bearer {self._api_key}"
        response = requests.get(
            url, headers=headers, params=params
        )
        if response.status_code != 200:
            raise Exception(f"Failed fetching: {response.text}")
        return response.json()

    def get_creators(self, limit=20, page=None, query=None) -> dict:
        params = {"limit": limit}
        if page is not None:
            params["page"] = page
        if query is not None:
            params["query"] = query
        response_dict = self._call(
            "https://civitai.com/api/v1/creators", params, True)
        return response_dict

    def get_images(self, limit=20, postId=None, modelId=None, modelVersionId=None, username=None, nsfw=None, sort=None, period=None, page=None) -> dict:
        params = {"limit": limit}
        if postId is not None:
            params["postId"] = postId
        if modelId is not None:
            params["modelId"] = modelId
        if modelVersionId is not None:
            params["modelVersionId"] = modelVersionId
        if username is not None:
            params["username"] = username
        if nsfw is not None:
            params["nsfw"] = nsfw
        if sort is not None:
            params["sort"] = sort
        if period is not None:
            params["period"] = period
        if page is not None:
            params["page"] = page
        response_dict = self._call(
            "https://civitai.com/api/v1/images", params, True)
        return response_dict

    def get_models(self, limit=20, page=None, query=None, tag=None, username=None, types=None, sort=None, period=None, favorites=False, hidden=False, primaryFileOnly=False, allowNoCredit=False, allowDerivatives=False, allowDifferentLicenses=False, allowCommercialUse=None, nsfw=False, supportsGeneration=False) -> dict:
        params = {"limit": limit}
        if page is not None:
            params["page"] = page
        if query is not None:
            params["query"] = query
        if tag is not None:
            params["tag"] = tag
        if username is not None:
            params["username"] = username
        if types is not None:
            params["types"] = types
        if sort is not None:
            params["sort"] = sort
        if period is not None:
            params["period"] = period
        if favorites is not None:
            params["favorites"] = favorites
        if hidden is not None:
            params["hidden"] = hidden
        if primaryFileOnly is not None:
            params["primaryFileOnly"] = primaryFileOnly
        # if allowNoCredit is not None: # Commented out because of unknown error
        #    params["allowNoCredit"] = allowNoCredit
        # if allowDerivatives is not None: # Commented out because of unknown error
        #    params["allowDerivatives"] = allowDerivatives
        if allowDifferentLicenses is not None:
            params["allowDifferentLicenses"] = allowDifferentLicenses
        # if allowCommercialUse is not None: # Commented out because of unknown error
        #    params["allowCommercialUse"] = allowCommercialUse
        if nsfw is not None:
            params["nsfw"] = nsfw
        if supportsGeneration is not None:
            params["supportsGeneration"] = supportsGeneration
        response_dict = self._call(
            "https://civitai.com/api/v1/models", params, True)
        return response_dict

    def get_model_details(self, modelId: str) -> dict:
        response_dict = self._call(
            "https://civitai.com/api/v1/models/"+modelId, {}, True)
        return response_dict

    def get_model_version(self, modelVersionId: str) -> dict:
        response_dict = self._call(
            "https://civitai.com/api/v1/model-versions/"+modelVersionId, {}, True)
        return response_dict

    def get_model_by_hash(self, hash: str) -> dict:
        response_dict = self._call(
            "https://civitai.com/api/v1/model-versions/by-hash/"+hash, {}, True)
        return response_dict

    def get_tags(self, limit=20, page=None, query=None) -> dict:
        params = {"limit": limit}
        if page is not None:
            params["page"] = page
        if query is not None:
            params["query"] = query
        response_dict = self._call(
            "https://civitai.com/api/v1/tags", params, True)
        return response_dict
