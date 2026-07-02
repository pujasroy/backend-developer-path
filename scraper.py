#!/usr/bin/env python3
"""
Simple CLI web scraper.

Usage examples:
    python scraper.py https://example.com -s "h2"
    python scraper.py https://example.com -s "a" -a href
    python scraper.py https://example.com -s ".product-title" -o results.csv
"""

import argparse
import requests
from bs4 import BeautifulSoup
import sys
import csv


def scrape(url, selector, attr=None):
    """
    Fetches a page and extracts data matching a CSS selector.

    url:      the webpage to scrape
    selector: a CSS selector, e.g. "h2.title" or "a"
    attr:     if given, extract this HTML attribute (e.g. "href")
              instead of the element's visible text
    """

    # Pretend to be a browser — some servers block requests
    # that don't send a recognizable User-Agent header.
    headers = {"User-Agent": "Mozilla/5.0 (compatible; MyScraper/1.0)"}

    # Download the page. timeout=10 stops the request from
    # hanging forever if the server is slow/unresponsive.
    resp = requests.get(url, headers=headers, timeout=10)

    # If the server returned an error status (404, 500, etc.),
    # this raises an exception instead of silently continuing.
    resp.raise_for_status()

    # Parse the raw HTML text into a searchable tree structure.
    soup = BeautifulSoup(resp.text, "html.parser")

    # Find every element that matches the given CSS selector.
    elements = soup.select(selector)

    results = []
    for el in elements:
        if attr:
            # Extract an attribute value, e.g. el.get("href")
            # Returns "" if the attribute doesn't exist.
            value = el.get(attr, "")
        else:
            # Extract the visible text, stripping extra whitespace.
            value = el.get_text(strip=True)
        results.append(value)

    return results


def main():
    # --- Define the command-line interface ---
    parser = argparse.ArgumentParser(description="Simple CLI web scraper")

    # Positional argument: no flag needed, just typed directly after the script name.
    parser.add_argument("url", help="URL to scrape")

    # Required flag: the CSS selector to search for.
    parser.add_argument(
        "-s", "--selector", required=True,
        help="CSS selector to extract, e.g. 'h2.title'"
    )

    # Optional flag: extract an attribute instead of text.
    parser.add_argument(
        "-a", "--attr",
        help="Extract an attribute (e.g. 'href') instead of text"
    )

    # Optional flag: save results to a CSV file instead of printing.
    parser.add_argument(
        "-o", "--output",
        help="Save results to a CSV file"
    )

    # Parse whatever the user typed into args.url, args.selector, etc.
    args = parser.parse_args()

    # --- Run the scraper, handling network errors gracefully ---
    try:
        results = scrape(args.url, args.selector, args.attr)
    except requests.RequestException as e:
        # e.g. bad URL, no internet connection, site down, timeout
        print(f"Error fetching {args.url}: {e}", file=sys.stderr)
        sys.exit(1)  # exit code 1 = something went wrong (Unix convention)

    # If the selector didn't match anything, say so and stop.
    if not results:
        print("No matches found for that selector.")
        return

    # --- Output the results ---
    if args.output:
        # Write results to a CSV file, one result per row.
        with open(args.output, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["result"])  # header row
            for r in results:
                writer.writerow([r])
        print(f"Saved {len(results)} results to {args.output}")
    else:
        # No output file given — just print to the terminal.
        for r in results:
            print(r)


# This block only runs if the file is executed directly
# (not if it's imported as a module elsewhere).
if __name__ == "__main__":
    main()