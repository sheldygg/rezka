import json
from http import HTTPMethod
from typing import Callable
from urllib.parse import urljoin

from aiohttp import ClientSession

from .extractor import Extractor
from .types import Episode, Season, Video

JsonLoads = Callable[..., dict]


class Client:
    def __init__(
        self,
        base_url: str = "https://rezka.ag/",
        json_loads: JsonLoads = json.loads,
    ):
        self.endpoint = urljoin(base_url, "ajax/get_cdn_series/")
        self.json_loads = json_loads

        self._session = ClientSession()
        self._base_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome"
            "/81.0.4044.138 Safari/537.36"
        }
        self._extractor = Extractor()

    async def _make_request(
        self,
        url: str,
        method: HTTPMethod = HTTPMethod.GET,
        data: dict | None = None,
        headers: dict | None = None,
        return_json: bool = False,
    ) -> dict | str:
        if headers is None:
            headers = self._base_headers
        else:
            headers.update(self._base_headers)

        async with self._session.request(
            method=method,
            url=url,
            data=data,
            headers=headers,
        ) as resp:
            response_text = await resp.text()
            if return_json:
                return self.json_loads(response_text)
            return response_text

    async def close(self) -> None:
        await self._session.close()

    async def info(self, url: str) -> Video:
        raw_data = await self._make_request(url=url)
        return self._extractor.info(raw_data)

    async def get_movie_stream(self, id: str, tranlator_id: str):
        data = {"id": id, "translator_id": tranlator_id, "action": "get_movie"}

        response = await self._make_request(url=self.endpoint, method=HTTPMethod.POST, data=data, return_json=True)
        if response["success"]:
            return self._extractor.extract_streams(response["url"])
        raise RuntimeError(response["message"])

    async def get_episode_stream(
        self,
        id: str,
        translator_id: str,
        season: int,
        episode: int,
    ):
        data = {
            "id": id,
            "translator_id": translator_id,
            "season": season,
            "episode": episode,
            "action": "get_stream",
        }
        response = await self._make_request(url=self.endpoint, method=HTTPMethod.POST, data=data, return_json=True)
        if response["success"]:
            return self._extractor.extract_streams(response["url"])
        raise RuntimeError(response["message"])

    async def get_seasons(self, id: str, translator_id: str) -> list[Season]:
        data = {"id": id, "translator_id": translator_id, "action": "get_episodes"}
        response = await self._make_request(url=self.endpoint, method=HTTPMethod.POST, data=data, return_json=True)
        if response["success"]:
            return self._extractor.extract_seasons(response["seasons"])

        raise ValueError(response["message"])

    async def get_episodes(self, id: str, translator_id: str) -> list[Episode]:
        data = {"id": id, "translator_id": translator_id, "action": "get_episodes"}
        response = await self._make_request(url=self.endpoint, method=HTTPMethod.POST, data=data, return_json=True)
        if response["success"]:
            return self._extractor.extract_episodes(response["episodes"])

        raise ValueError(response["message"])
