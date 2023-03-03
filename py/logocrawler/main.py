#!/usr/bin/env python3
import asyncio
import csv
import functools
import logging
import re
import sys
from collections.abc import Callable
from typing import IO, List, Optional, Set, Tuple, Union
from urllib.parse import urljoin, urlparse

import aiohttp
from bs4 import BeautifulSoup, element
from tqdm.asyncio import tqdm

#  from icecream import ic

logging.basicConfig(
    filename="app.log",
    filemode="w",
    format="%(asctime)s - %(message)s",
    level=logging.INFO,
)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/110.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Pragma": "no-cache",
}

MAX_CONNECTIONS_PER_HOST = 5
SEARCH_LIMIT = 10

SearchResult = Union[
    element.ResultSet, element.Tag, element.NavigableString, None
]


def get_website_list() -> Set[str]:
    websites = []
    with open(sys.stdin.fileno(), "r", newline="") as csvfile:
        reader = csv.reader(csvfile, delimiter=",")
        websites = [r[0] for r in reader]
    return set(websites)


def image_in_header(soup: BeautifulSoup) -> SearchResult:
    return soup.select("nav a > img, header a > img", limit=SEARCH_LIMIT)


def link_in_header(soup: BeautifulSoup) -> SearchResult:
    return soup.select("header * > a", limit=SEARCH_LIMIT)


def search_in_attribute(soup: BeautifulSoup) -> SearchResult:
    pat = re.compile(r"logo")

    def finder(attr: str) -> bool:
        return attr is not None and pat.search(attr) is not None

    return (
        soup.find(id=finder)
        or soup.find(class_=finder)
        or soup.find(alt=finder)
    )


def search_in_img(soup: BeautifulSoup) -> SearchResult:
    for t in soup.find_all("img", limit=SEARCH_LIMIT):
        res = search_in_attribute(soup)
        if res is not None:
            return res


def image_in_root_link(url: str, soup: BeautifulSoup) -> SearchResult:
    """
    Find <img> under <a> where <a> links to same url
    that request is sent to
    """
    links = soup.select("a > img", limit=SEARCH_LIMIT)
    for link in links:
        href: str = link.parent["href"] if "href" in link.parent.attrs else ""
        parsed_url = urlparse(href)
        if (
            href == "/"
            or parsed_url.path == "/"
            or (parsed_url.path == "" and parsed_url.netloc.endswith(url))
        ):
            return link


# TODO: handle SVG logos


def is_url(url: str) -> bool:
    return (
        url.startswith("http")
        or url.startswith("/")
        or url.startswith("../")
        or url.startswith("./")
        or re.match(r"^\w+/", url)
    )


# TODO: handle url in CSS rule
async def extract_logo(
    candidate: SearchResult,
) -> Optional[str]:
    if isinstance(candidate, list):
        # pick element that appears first in HTML
        tag = candidate[0]
    else:
        tag = candidate
    # TODO: extract svg
    if tag.name == "img":
        src = tag.attrs.get("src", "")
        return str(src) if is_url(src) else None
    else:
        img = tag.find("img")
        src = img.attrs.get("src", "") if img is not None else ""
        return src if is_url(src) else None
    return None


async def fetch_page(
    session: aiohttp.ClientSession, url: str
) -> Tuple[Optional[str], Optional[str]]:
    try:
        # TODO: handle https scheme
        async with session.get("http://" + url) as response:
            response_url = str(response.url)
            if response.status == 200:
                text = await response.read()
                return text, response_url
            else:
                logging.error(
                    f"Network Error - {url} failed with status {response.status}"
                )
                return None, response_url
    except asyncio.TimeoutError:
        logging.error(f"Network Error - {url} timed out")
        return None, None
    except aiohttp.client_exceptions.ClientResponseError:
        logging.error(f"Network Error - {url} had a problem with the response")
        return None, None
    except aiohttp.client_exceptions.ClientConnectionError:
        logging.error(f"Network Error - {url} could not connect")
        return None, None
    except aiohttp.client_exceptions.ClientPayloadError:
        logging.error(f"Network Error - {url} had a problem with the payload")
        return None, None
    return None, None


async def get_logo(
    session: aiohttp.ClientSession, base_url: str
) -> Tuple[str, Optional[str]]:
    text, response_url = await fetch_page(session, base_url)
    if text is None:
        return base_url, None
    soup = BeautifulSoup(text, "html.parser")
    strategy: List[Callable[[BeautifulSoup], SearchResult]]
    for strategy in [
        image_in_header,
        search_in_img,
        search_in_attribute,
        functools.partial(image_in_root_link, base_url),
    ]:
        candidate: SearchResult = strategy(soup)
        if candidate is not None and candidate != []:
            logo_url = await extract_logo(candidate)
            if logo_url is not None:
                return base_url, urljoin(response_url, logo_url)
            else:
                continue
    logging.error(f"Extraction Error - {base_url} logo could not be extracted")
    return base_url, None


def write_results(
    results: List[Tuple[str, Optional[str]]], ofile: IO[str] = sys.stdout
) -> None:
    csvwriter = csv.writer(
        sys.stdout, delimiter=",", quotechar="|", quoting=csv.QUOTE_MINIMAL
    )
    for r in results:
        if r[1] is not None:
            csvwriter.writerow(r)


async def main():
    loop = asyncio.get_running_loop()
    urls = await loop.run_in_executor(None, get_website_list)
    tasks = []
    connector = aiohttp.TCPConnector(limit_per_host=MAX_CONNECTIONS_PER_HOST)
    async with aiohttp.ClientSession(
        headers=HEADERS,
        connector=connector,
    ) as session:
        for url in urls:
            tasks.append(get_logo(session, url))
        results = await tqdm.gather(*tasks)
        await loop.run_in_executor(None, write_results, results)


if __name__ == "__main__":
    asyncio.run(main())
