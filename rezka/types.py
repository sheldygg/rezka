from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel

if TYPE_CHECKING:
    from .client import Client


class Season(BaseModel):
    id: str
    text: str


class Episode(BaseModel):
    id: str
    text: str
    season: str


class Translator(BaseModel):
    id: str
    name: str


class Thumbnail(BaseModel):
    large: str | None = None
    mini: str


class Rating(BaseModel):
    imdb: str
    kinopoisk: str


class Stream(BaseModel):
    quality: str
    urls: list[str]


class Movie(BaseModel):
    id: str
    title: str
    original_title: str
    thumbnail: Thumbnail
    rating: Rating
    tranlators: list[Translator]

    async def get_movie_stream(self, client: Client, translator_id: str):
        return await client.get_movie_stream(id=self.id, tranlator_id=translator_id)


class Series(BaseModel):
    id: str
    title: str
    original_title: str
    thumbnail: Thumbnail
    rating: Rating
    tranlators: list[Translator]

    async def get_episodes(self, client: Client, translator_id: str):
        return await client.get_episodes(self.id, translator_id=translator_id)

    async def get_seasons(self, client: Client, translator_id: str):
        return await client.get_seasons(self.id, translator_id=translator_id)


Video = Movie | Series
