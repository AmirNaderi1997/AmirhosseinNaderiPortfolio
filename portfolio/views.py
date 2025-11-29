from django.shortcuts import render
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)

IMDB_TOP_URL = "https://www.imdb.com/chart/top/"

# Simple in-memory cache so we don’t hammer IMDB on every request
IMDB_CACHE = {
    "movies": [],
    "last_fetch": None,
}


def fetch_imdb_top(limit=10, max_age_minutes=60):
    """
    Fetch top movies from IMDB Top 250.

    Uses a simple in-memory cache:
    - If we fetched movies less than `max_age_minutes` ago, return cached.
    - Otherwise, try to fetch again (with short timeout).
    """

    now = datetime.now()

    # 1) Return cached data if fresh enough
    if IMDB_CACHE["last_fetch"] is not None:
        age = now - IMDB_CACHE["last_fetch"]
        if age < timedelta(minutes=max_age_minutes) and IMDB_CACHE["movies"]:
            logger.info("IMDB scraper: using cached data (%d movies, age=%s)", len(IMDB_CACHE["movies"]), age)
            # still respect `limit` when returning cached
            return IMDB_CACHE["movies"][:limit]

    movies = []
    try:
        resp = requests.get(
            IMDB_TOP_URL,
            timeout=2,  # SHORT timeout so page does not hang
            headers={
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

        # --- Layout 1: old table layout ---
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

            movies.append(
                {
                    "title": title,
                    "year": year,
                    "rating": rating,
                    "url": link,
                }
            )

        # --- Layout 2: newer list/card layout (fallback) ---
        if not movies:
            items = soup.select("li.ipc-metadata-list-summary-item")
            logger.info("IMDB scraper: found %d items in list layout", len(items))

            for item in items[:limit]:
                title_tag = item.select_one("h3 a, a.ipc-title-link-wrapper")
                if not title_tag:
                    continue

                title = title_tag.get_text(strip=True)
                href = title_tag.get("href", "#")
                link = "https://www.imdb.com" + href

                year_tag = item.select_one("span.ipc-title__meta-year, span")
                year = year_tag.get_text(strip=True) if year_tag else ""

                rating_tag = item.select_one(
                    "span[aria-label*='IMDb rating'], span.ipc-rating-star--imdb"
                )
                rating = rating_tag.get_text(strip=True) if rating_tag else ""

                movies.append(
                    {
                        "title": title,
                        "year": year,
                        "rating": rating,
                        "url": link,
                    }
                )

        logger.info("IMDB scraper: fetched %d movies from network", len(movies))

        # Update cache only if we got something
        if movies:
            IMDB_CACHE["movies"] = movies
            IMDB_CACHE["last_fetch"] = now

    except Exception as e:
        logger.error("Error fetching IMDB top list: %s", e)
        # On error, if we have old cache, use it
        if IMDB_CACHE["movies"]:
            logger.info("IMDB scraper: using stale cached data due to error")
            return IMDB_CACHE["movies"][:limit]

    return movies[:limit]


def index(request):
    projects = [
        {
            "title": "GitHub AI Chatbot",
            "url": "https://amirnaderi1997.github.io/github-ai-chatbot/",
            "description": (
                "A web-based AI chatbot that uses large language models to answer user questions. "
                "It demonstrates integration between frontend UI and an AI backend, solving the "
                "problem of interactive Q&A directly in the browser."
            ),
            "tags": ["Python", "JavaScript", "AI", "Web Integration"],
        },
        {
            "title": "Wikipedia Scraper",
            "url": "https://amirnaderi1997.github.io/wikipedia/",
            "description": (
                "A tool that fetches and structures information from Wikipedia pages. "
                "It solves the problem of quickly extracting clean, focused data from noisy web pages."
            ),
            "tags": ["Python", "Web Scraping", "Data Extraction"],
        },
        {
            "title": "Weather App",
            "url": "https://amirnaderi1997.github.io/weather/",
            "description": (
                "A simple, user-friendly weather dashboard that consumes public APIs to show "
                "current weather and forecasts. It solves the problem of quickly checking weather "
                "conditions in a clean interface."
            ),
            "tags": ["JavaScript", "API", "Frontend"],
        },
    ]

    about_me = (
        "Hi, I'm Amirhossein Naderi. I have a strong background in system administration and Python programming. "
        "I have extensive experience working with Unix-based systems and Bash scripting, as well as managing networks "
        "and working with various protocols at the transport and application layers, such as SSH, HTTPS, and FTP. "
        "My main expertise in Python is web scraping and data extraction from websites, but I also have experience "
        "working with different types of APIs, including REST APIs and SOAP APIs."
    )

    education = {
        "degree": "B.S. in Metallurgy Engineering",
        "university": "Arak University",
        "year": "2022",
    }

    skills = [
        "System Administration: Expert in Unix-based systems, Bash scripting.",
        "Networking: Strong knowledge of transfer/application layers, protocols like HTTP, HTTPS, FTP.",
        "Programming: Proficient in Python, web scraping, data extraction from websites like Instagram and Wikipedia.",
    ]

    imdb_movies = fetch_imdb_top(limit=10)

    context = {
        "projects": projects,
        "about_me": about_me,
        "education": education,
        "skills": skills,
        "imdb_movies": imdb_movies,
        "server_time": datetime.now(),
    }
    return render(request, "portfolio/index.html", context)
