import json
import re
import requests
import feedparser
from datetime import datetime, timezone
from urllib.parse import quote


# ==========================================
# BARSAL FOOTBALL NEWS SYSTEM
# ==========================================

RSS_BASE = "https://news.google.com/rss/search?q={}&hl=en-US&gl=US&ceid=US:en"


# ==========================================
# NEWS CATEGORIES
# ==========================================

queries = {

    "laliga":
        "La Liga football",

    "premier":
        "Premier League football England",

    "seriea":
        "Serie A Italy football",

    "transfers":
        "football transfer news",

    "important":
        "football breaking news",

    "Barcelona":
        "Barcelona football",

    "Real Madrid":
        "Real Madrid football",

    "Atletico Madrid":
        "Atletico Madrid football",

    "Arsenal":
        "Arsenal football",

    "Liverpool":
        "Liverpool football",

    "Manchester City":
        "Manchester City football",

    "Manchester United":
        "Manchester United football",

    "Inter Miami":
        "Inter Miami football",

    "Al Nassr":
        "Al Nassr football",

    "Paris Saint-Germain":
        "Paris Saint-Germain football",

    "Bayern Munich":
        "Bayern Munich football",

    "Inter Milan":
        "Inter Milan football",

    "Chelsea":
        "Chelsea football",

    "Tottenham":
        "Tottenham football",

    "Juventus":
        "Juventus football",

    "AC Milan":
        "AC Milan football",

    "Borussia Dortmund":
        "Borussia Dortmund football"

}


# ==========================================
# TEAM NAMES
# ==========================================

teams = {

    "Barcelona":
        "بارسلونا",

    "Real Madrid":
        "رئال مادرید",

    "Atletico Madrid":
        "اتلتیکو مادرید",

    "Arsenal":
        "آرسنال",

    "Liverpool":
        "لیورپول",

    "Manchester City":
        "منچسترسیتی",

    "Manchester United":
        "منچستریونایتد",

    "Inter Miami":
        "اینتر میامی",

    "Al Nassr":
        "النصر",

    "Paris Saint-Germain":
        "پاری‌سن‌ژرمن",

    "Bayern Munich":
        "بایرن مونیخ",

    "Inter Milan":
        "اینتر",

    "Chelsea":
        "چلسی",

    "Tottenham":
        "تاتنهام",

    "Juventus":
        "یوونتوس",

    "AC Milan":
        "آث میلان",

    "Borussia Dortmund":
        "بوروسیا دورتموند"

}


# ==========================================
# CLEAN TEXT
# ==========================================

def clean_text(text):

    if not text:
        return ""

    text = re.sub(
        r"<[^>]+>",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# ==========================================
# FIND TEAM
# ==========================================

def detect_team(title):

    title_lower = title.lower()

    for english_name in teams:

        if english_name.lower() in title_lower:

            return english_name

    return ""


# ==========================================
# GET RSS NEWS
# ==========================================

def get_news(category, query):

    news = []

    url = RSS_BASE.format(
        quote(query)
    )

    try:

        response = requests.get(
            url,
            timeout=20,
            headers={
                "User-Agent":
                "Mozilla/5.0 BARSAL-News-Bot"
            }
        )

        response.raise_for_status()

        feed = feedparser.parse(
            response.content
        )

        for item in feed.entries[:15]:

            title = clean_text(
                item.get(
                    "title",
                    ""
                )
            )

            link = item.get(
                "link",
                ""
            )

            summary = clean_text(
                item.get(
                    "summary",
                    ""
                )
            )

            if not title or not link:
                continue

            team = ""

            if category in teams:

                team = category

            else:

                team = detect_team(
                    title
                )

            source = ""

            try:

                source = clean_text(
                    item.source.title
                )

            except:

                source = "منبع خبری"


            published = item.get(
                "published",
                ""
            )


            important = (
                category == "important"
            )


            # Transfer news
            if category == "transfers":

                important = False


            news.append({

                "category":
                    category,

                "team":
                    team,

                "team_fa":
                    teams.get(
                        team,
                        ""
                    ),

                "title":
                    title,

                "summary":
                    summary[:300],

                "source":
                    source,

                "url":
                    link,

                "time":
                    published,

                "important":
                    important

            })


    except Exception as error:

        print(
            "ERROR:",
            category,
            error
        )


    return news


# ==========================================
# MAIN
# ==========================================

all_news = []

seen_titles = set()


for category, query in queries.items():

    print(
        "Getting:",
        category
    )

    category_news = get_news(
        category,
        query
    )

    for item in category_news:

        title_key = (
            item["title"]
            .lower()
            .strip()
        )

        if title_key in seen_titles:

            continue

        seen_titles.add(
            title_key
        )

        all_news.append(
            item
        )


# ==========================================
# SORT NEWS
# ==========================================

def sort_key(item):

    return item.get(
        "time",
        ""
    )


all_news.sort(
    key=sort_key,
    reverse=True
)


# ==========================================
# LIMIT FILE SIZE
# ==========================================

all_news = all_news[:200]


# ==========================================
# SAVE
# ==========================================

with open(
    "news.json",
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        all_news,
        file,
        ensure_ascii=False,
        indent=2
    )


print()
print(
    "================================"
)

print(
    "BARSAL NEWS UPDATED"
)

print(
    "Total news:",
    len(all_news)
)

print(
    "Time:",
    datetime.now(
        timezone.utc
    ).isoformat()
)

print(
    "================================"
)
