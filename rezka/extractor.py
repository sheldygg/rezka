import re
from base64 import b64decode

from lxml.html import HtmlElement, fromstring

from .enums import VideoType
from .types import (
    Episode,
    Movie,
    Rating,
    Season,
    Series,
    Stream,
    Thumbnail,
    Translator,
    Video,
)


class Extractor:
    def __init__(self):
        self._trash_codes = [
            b"QEA=",
            b"QCM=",
            b"QCE=",
            b"QF4=",
            b"QCQ=",
            b"I0A=",
            b"IyM=",
            b"IyE=",
            b"I14=",
            b"IyQ=",
            b"IUA=",
            b"ISM=",
            b"ISE=",
            b"IV4=",
            b"ISQ=",
            b"XkA=",
            b"XiM=",
            b"XiE=",
            b"Xl4=",
            b"XiQ=",
            b"JEA=",
            b"JCM=",
            b"JCE=",
            b"JF4=",
            b"JCQ=",
            b"QEBA",
            b"QEAj",
            b"QEAh",
            b"QEBe",
            b"QEAk",
            b"QCNA",
            b"QCMj",
            b"QCMh",
            b"QCNe",
            b"QCMk",
            b"QCFA",
            b"QCEj",
            b"QCEh",
            b"QCFe",
            b"QCEk",
            b"QF5A",
            b"QF4j",
            b"QF4h",
            b"QF5e",
            b"QF4k",
            b"QCRA",
            b"QCQj",
            b"QCQh",
            b"QCRe",
            b"QCQk",
            b"I0BA",
            b"I0Aj",
            b"I0Ah",
            b"I0Be",
            b"I0Ak",
            b"IyNA",
            b"IyMj",
            b"IyMh",
            b"IyNe",
            b"IyMk",
            b"IyFA",
            b"IyEj",
            b"IyEh",
            b"IyFe",
            b"IyEk",
            b"I15A",
            b"I14j",
            b"I14h",
            b"I15e",
            b"I14k",
            b"IyRA",
            b"IyQj",
            b"IyQh",
            b"IyRe",
            b"IyQk",
            b"IUBA",
            b"IUAj",
            b"IUAh",
            b"IUBe",
            b"IUAk",
            b"ISNA",
            b"ISMj",
            b"ISMh",
            b"ISNe",
            b"ISMk",
            b"ISFA",
            b"ISEj",
            b"ISEh",
            b"ISFe",
            b"ISEk",
            b"IV5A",
            b"IV4j",
            b"IV4h",
            b"IV5e",
            b"IV4k",
            b"ISRA",
            b"ISQj",
            b"ISQh",
            b"ISRe",
            b"ISQk",
            b"XkBA",
            b"XkAj",
            b"XkAh",
            b"XkBe",
            b"XkAk",
            b"XiNA",
            b"XiMj",
            b"XiMh",
            b"XiNe",
            b"XiMk",
            b"XiFA",
            b"XiEj",
            b"XiEh",
            b"XiFe",
            b"XiEk",
            b"Xl5A",
            b"Xl4j",
            b"Xl4h",
            b"Xl5e",
            b"Xl4k",
            b"XiRA",
            b"XiQj",
            b"XiQh",
            b"XiRe",
            b"XiQk",
            b"JEBA",
            b"JEAj",
            b"JEAh",
            b"JEBe",
            b"JEAk",
            b"JCNA",
            b"JCMj",
            b"JCMh",
            b"JCNe",
            b"JCMk",
            b"JCFA",
            b"JCEj",
            b"JCEh",
            b"JCFe",
            b"JCEk",
            b"JF5A",
            b"JF4j",
            b"JF4h",
            b"JF5e",
            b"JF4k",
            b"JCRA",
            b"JCQj",
            b"JCQh",
            b"JCRe",
            b"JCQk",
        ]
        self._source_regex = r"\[(.*?)\](.*?)\sor\s(.*?)\sor\s(.*?)$"

    @staticmethod
    def extract_seasons(raw_data: str) -> list[Season]:
        tree = fromstring(raw_data)
        seasons = []
        raw_seasons = tree.xpath('//li[@class="b-simple_season__item"] | //li[@class="b-simple_season__item active"]')

        for raw_season in raw_seasons:
            seasons.append(Season(id=raw_season.get("data-tab_id"), text=raw_season.text_content().strip()))

        return seasons

    @staticmethod
    def extract_episodes(raw_data: str) -> list[Episode]:
        tree = fromstring(raw_data)
        episodes = []
        raw_seasons = tree.xpath('//ul[contains(@class, "b-simple_episodes__list")]')
        for raw_season in raw_seasons:
            for episode in raw_season.xpath('.//li[contains(@class, "b-simple_episode__item")]'):
                episodes.append(
                    Episode(
                        id=episode.get("data-episode_id"),
                        text=episode.text,
                        season=episode.get("data-season_id"),
                    )
                )
        return episodes

    @staticmethod
    def get_tranlators(tree: HtmlElement) -> list[Translator]:
        tranlators = []
        translators = tree.xpath('//ul[@id="translators-list"]')[0]

        for translator in translators.xpath("./li"):
            tranlators.append(
                Translator(
                    id=translator.get("data-translator_id"),
                    name=translator.text.strip(),
                )
            )
        return tranlators

    @staticmethod
    def get_id(tree: HtmlElement) -> str:
        return tree.xpath('//*[@id="post_id"]')[0].get("value")

    @staticmethod
    def get_thumbnail(tree: HtmlElement) -> Thumbnail:
        large = tree.xpath(
            '//*[@id="main"]/div[4]/div/div[2]/div[1]/div[4]/div[1]/div '
            '| //*[@id="main"]/div[4]/div/div[2]/div[1]/div[3]/div[1]/div'
        )[0].get("href")
        mini = tree.xpath(
            '//*[@id="main"]/div[4]/div/div[2]/div[1]/div[3]/div[1]/div/a/img '
            '| //*[@id="main"]/div[4]/div/div[2]/div[1]/div[4]/div[1]/div/a/img'
        )[0].get("src")

        return Thumbnail(large=large, mini=mini)

    @staticmethod
    def get_ratings(tree: HtmlElement) -> Rating:
        imdb = tree.xpath('//*[@class="b-post__info_rates imdb"]/span[@class="bold"]/text()')[0]
        kp = tree.xpath('//*[@class="b-post__info_rates kp"]/span[@class="bold"]/text()')[0]
        return Rating(imdb=imdb, kinopoisk=kp)

    @staticmethod
    def get_titles(tree: HtmlElement) -> tuple[str, str]:
        title = tree.xpath('//*[@id="main"]/div[4]/div/div[2]/div[1]/div[1]/h1')[0].text
        original_title = tree.xpath('//*[@id="main"]/div[4]/div/div[2]/div[1]/div[2]')[0].text
        return title, original_title

    @staticmethod
    def get_type(tree: HtmlElement) -> str:
        return tree.xpath('//meta[@property="og:type"]')[0].get("content")

    def get_movie_info(self, tree: HtmlElement) -> Movie:
        title, original_title = self.get_titles(tree)

        return Movie(
            id=self.get_id(tree),
            title=title,
            original_title=original_title,
            thumbnail=self.get_thumbnail(tree),
            rating=self.get_ratings(tree),
            tranlators=self.get_tranlators(tree),
        )

    def get_series_info(self, tree: HtmlElement) -> Series:
        title, original_title = self.get_titles(tree)

        return Series(
            id=self.get_id(tree),
            title=title,
            original_title=original_title,
            thumbnail=self.get_thumbnail(tree),
            rating=self.get_ratings(tree),
            tranlators=self.get_tranlators(tree),
        )

    def info(self, raw_data: str) -> Video:
        tree = fromstring(raw_data)
        video_type = self.get_type(tree)

        if video_type == VideoType.SERIES:
            return self.get_series_info(tree)

        elif video_type == VideoType.MOVIE:
            return self.get_movie_info(tree)

        raise ValueError(f"Unknown video type: {video_type!r}")

    def extract_streams(self, data: str) -> list[Stream]:
        streams = []
        trash_string = "".join(data.replace("#h", "").split("//_//"))

        for code in self._trash_codes:
            trash_string = trash_string.replace(code.decode(), "")

        qualities = b64decode(trash_string).decode().split(",")
        for quality in qualities:
            mathes = re.search(self._source_regex, quality)
            if not mathes:
                raise ValueError(f"Bad quality {quality!r}")
            streams.append(Stream(quality=mathes.group(1), urls=list(mathes.groups()[1:])))

        return streams
