from django.shortcuts import render
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)

IMDB_TOP_URL = "https://www.imdb.com/chart/top/"

def fetch_imdb_top(limit=10):
    """
    Fetch top movies from IMDB Top 250.

    Tries both the old table layout and the newer list/card layout.
    If it fails, logs the error and returns [].
    """
    movies = []
    try:
        resp = requests.get(
            IMDB_TOP_URL,
            timeout=10,
            headers={
                # pretend to be a normal browser
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0 Safari/537.36"
                )
            },
        )
        resp.raise_for_status()
        html = resp.text
        soup = BeautifulSoup(html, "html.parser")

        # --- Layout 1: old table ---
        rows = soup.select("table.chart tbody tr")
        logger.info("IMDB scraper: found %d rows in table layout", len(rows))

        for row in rows[:limit]:
            title_tag = row.select_one("td.titleColumn a")
            year_tag = row.select_one("span.secondaryInfo")
            rating_tag = row.select_one("td.imdbRating strong")
            if not title_tag:
                continue
            title = title_tag.get_text(strip=True)
            href = title_tag.get("href", "#")
            link = "https://www.imdb.com" + href
            year = year_tag.get_text(strip=True).strip("()") if year_tag else ""
            rating = rating_tag.get_text(strip=True) if rating_tag else ""
            movies.append({
                "title": title,
                "year": year,
                "rating": rating,
                "url": link,
            })

        # --- Layout 2: newer list/card layout ---
        if not movies:
            items = soup.select("li.ipc-metadata-list-summary-item")
            logger.info("IMDB scraper: found %d items in list layout", len(items))
            for item in items[:limit]:
                # title
                title_tag = item.select_one("h3 a, a.ipc-title-link-wrapper")
                if not title_tag:
                    continue
                title = title_tag.get_text(strip=True)
                href = title_tag.get("href", "#")
                link = "https://www.imdb.com" + href

                # year might be somewhere like <span>1994</span> after title
                year_tag = item.select_one("span.ipc-title__meta-year, span")
                year = year_tag.get_text(strip=True) if year_tag else ""

                # rating, usually span with "rating" in class
                rating_tag = item.select_one("span[aria-label*='IMDb rating'], span.ipc-rating-star--imdb")
                rating = rating_tag.get_text(strip=True) if rating_tag else ""

                movies.append({
                    "title": title,
                    "year": year,
                    "rating": rating,
                    "url": link,
                })

        logger.info("IMDB scraper: returning %d movies", len(movies))

    except Exception as e:
        logger.error("Error fetching IMDB top list: %s", e)

    return movies
