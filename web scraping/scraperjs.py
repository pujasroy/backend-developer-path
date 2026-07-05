#!/usr/bin/env python3
"""
CLI web scraper that handles JavaScript-rendered pages using Playwright.

Unlike requests + BeautifulSoup, this opens a REAL headless browser,
lets the page's JavaScript run, and THEN grabs the fully-loaded HTML.

Usage examples:
    python scraper_js.py https://example.com -s "h2"
    python scraper_js.py https://example.com -s "a" -a href
    python scraper_js.py https://example.com -s ".product-title" -o results.csv
    python scraper_js.py https://example.com -s ".lazy-content" --wait 3000
"""

import argparse
import sys
import csv
from playwright.sync_api import sync_playwright


def scrape(url, selector, attr=None, wait_ms=2000):
    """
    Opens a real (headless) browser, loads the page, waits for
    JavaScript to run, then extracts data matching a CSS selector.

    url:      the webpage to scrape
    selector: a CSS selector, e.g. "h2.title" or "a"
    attr:     if given, extract this HTML attribute instead of visible text
    wait_ms:  how long (in milliseconds) to wait after page load,
              giving JS time to fetch/render dynamic content
    """

    with sync_playwright() as p:
        # Launch a headless (no visible window) Chromium browser.
        # headless=False would pop up an actual browser window —
        # useful for debugging, to SEE what the scraper sees.
        browser = p.chromium.launch(headless=True)

        # A "context" is like a fresh browser profile (own cookies,
        # storage, etc). We also set a realistic User-Agent here,
        # same idea as in the requests version.
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        )

        page = context.new_page()

        # Navigate to the page. wait_until="networkidle" means:
        # "wait until the page stops making new network requests"
        # — a decent signal that dynamic content has finished loading.
        page.goto(url, wait_until="networkidle", timeout=30000)

        # Extra explicit wait, in case content loads on a delay
        # (e.g. infinite scroll, animations, delayed API calls)
        # that networkidle doesn't catch.
        page.wait_for_timeout(wait_ms)

        # Grab all elements matching the selector.
        elements = page.query_selector_all(selector)

        results = []
        for el in elements:
            if attr:
                value = el.get_attribute(attr) or ""
            else:
                value = el.inner_text().strip()
            results.append(value)

        browser.close()
        return results


def main():
    parser = argparse.ArgumentParser(
        description="CLI web scraper for JavaScript-rendered pages (Playwright)"
    )
    parser.add_argument("url", help="URL to scrape")
    parser.add_argument(
        "-s", "--selector", required=True,
        help="CSS selector to extract, e.g. 'h2.title'"
    )
    parser.add_argument(
        "-a", "--attr",
        help="Extract an attribute (e.g. 'href') instead of text"
    )
    parser.add_argument(
        "-o", "--output",
        help="Save results to a CSV file"
    )
    parser.add_argument(
        "--wait", type=int, default=2000,
        help="Milliseconds to wait after page load for JS content (default: 2000)"
    )

    args = parser.parse_args()

    try:
        results = scrape(args.url, args.selector, args.attr, args.wait)
    except Exception as e:
        print(f"Error scraping {args.url}: {e}", file=sys.stderr)
        sys.exit(1)

    if not results:
        print("No matches found for that selector.")
        return

    if args.output:
        with open(args.output, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["result"])
            for r in results:
                writer.writerow([r])
        print(f"Saved {len(results)} results to {args.output}")
    else:
        for r in results:
            print(r)


if __name__ == "__main__":
    main()