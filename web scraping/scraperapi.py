#!/usr/bin/env python3
"""
Scrapes all quotes from quotes.toscrape.com/scroll by calling its
hidden JSON API directly — no HTML parsing, no browser needed.

This is the API we found earlier via DevTools -> Network -> Fetch/XHR
while scrolling the page. It returns pages of quotes as clean JSON.
"""

import requests
import json
import time

# This is the pattern we spotted in DevTools: /api/quotes?page=N
BASE_URL = "https://quotes.toscrape.com/api/quotes"


def fetch_all_quotes():
    all_quotes = []
    page = 1

    while True:
        # Call the API directly for this page number.
        response = requests.get(BASE_URL, params={"page": page}, timeout=10)
        response.raise_for_status()

        # Parse the JSON response straight into a Python dict.
        # No BeautifulSoup needed -- this IS the structured data already.
        data = response.json()

        quotes = data.get("quotes", [])
        if not quotes:
            # No quotes returned -- we've run out of pages, stop looping.
            break

        for q in quotes:
            all_quotes.append({
                "text": q.get("text"),
                "author": q.get("author", {}).get("name"),
                "tags": q.get("tags", []),
            })

        print(f"Page {page}: fetched {len(quotes)} quotes")

        # has_next tells us whether to keep going, straight from the API.
        if not data.get("has_next", False):
            break

        page += 1

        # Small delay between requests -- basic politeness/rate limiting,
        # so we don't hammer the server with rapid-fire requests.
        time.sleep(0.5)

    return all_quotes


def main():
    quotes = fetch_all_quotes()

    print(f"\nTotal quotes collected: {len(quotes)}")

    # Save everything to a JSON file for later use.
    with open("quotes.json", "w", encoding="utf-8") as f:
        json.dump(quotes, f, indent=2, ensure_ascii=False)

    print("Saved to quotes.json")

    # Print the first few as a sanity check.
    for q in quotes[:3]:
        print(f"\n\"{q['text']}\"\n  — {q['author']} {q['tags']}")


if __name__ == "__main__":
    main()