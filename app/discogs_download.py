#!/usr/bin/env python3
"""
Discogs Album Downloader for Vinyl Playback Monitor System
Downloads album metadata from Discogs API and saves as JSON.
"""

import json
import sys
import time
from pathlib import Path

import requests

DISCOGS_API_BASE = "https://api.discogs.com"
USER_AGENT = "VinylPlaybackMonitor/0.1"
DATA_DIR = Path(__file__).parent.parent / ".data" / "albums"


def make_request(url: str, params: dict | None = None, max_retries: int = 3) -> dict:
    """Make request to Discogs API with retry logic for rate limiting."""
    headers = {"User-Agent": USER_AGENT}

    for _ in range(max_retries):
        response = requests.get(url, params=params, headers=headers, timeout=30)

        if response.status_code == 200:
            return response.json()

        if response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", 60))
            print(f"Rate limited. Waiting {retry_after} seconds...")
            time.sleep(retry_after)
            continue

        if response.status_code == 404:
            raise ValueError(f"Not found: {url}")

        response.raise_for_status()

    raise RuntimeError(f"Max retries exceeded for {url}")


def search_releases(query: str) -> list[dict]:
    """Search for vinyl releases on Discogs by query."""
    url = f"{DISCOGS_API_BASE}/database/search"
    params = {
        "q": query,
        "format": "vinyl",
        "type": "release",
    }

    data = make_request(url, params)
    return data.get("results", [])


def display_results(results: list[dict], max_display: int = 10) -> None:
    """Display numbered list of search results."""
    print(f"\nFound {len(results)} results (showing up to {max_display}):\n")
    for i, result in enumerate(results[:max_display], 1):
        title = result.get("title", "Unknown")
        year = result.get("year", "N/A")
        formats = ", ".join(result.get("format", []))
        print(f"  {i}. {title} ({year}) [{formats}]")
    print()


def prompt_selection(max_choice: int) -> int | None:
    """Prompt user to select a result. Returns None if cancelled."""
    try:
        choice = input(f"Enter number (1-{max_choice}) or 'q' to quit: ").strip()
    except (EOFError, KeyboardInterrupt):
        return None

    if not choice or choice.lower() == "q":
        return None

    try:
        num = int(choice)
        if 1 <= num <= max_choice:
            return num
        print(f"Please enter a number between 1 and {max_choice}")
        return prompt_selection(max_choice)
    except ValueError:
        print("Invalid input. Enter a number or 'q' to quit.")
        return prompt_selection(max_choice)


def fetch_release(release_id: int) -> dict:
    """Fetch full release details from Discogs."""
    url = f"{DISCOGS_API_BASE}/releases/{release_id}"
    return make_request(url)


def get_side_letter(position: str) -> str:
    """Extract side letter from position (e.g., 'A1' -> 'A', 'B2' -> 'B')."""
    for char in position:
        if char.isalpha():
            return char.upper()
    return ""


def transform_release(release: dict) -> tuple[dict, bool]:
    """Transform Discogs release to simplified format. Returns (data, has_missing_durations)."""
    album_artists = release.get("artists", [])
    default_artist = album_artists[0].get("name", "Unknown") if album_artists else "Unknown"

    # Get primary cover image
    cover = ""
    for img in release.get("images", []):
        if img.get("type") == "primary":
            cover = img.get("uri", "")
            break

    # Group tracks by side
    sides_dict: dict[str, list[dict]] = {}
    has_missing_durations = False

    for track in release.get("tracklist", []):
        position = track.get("position", "")
        side_letter = get_side_letter(position)
        if not side_letter:
            continue

        # Resolve artist: track artist first, fallback to album artist
        track_artists = track.get("artists", [])
        artist = track_artists[0].get("name") if track_artists else default_artist

        duration = track.get("duration", "")
        if not duration:
            has_missing_durations = True

        track_data = {
            "position": position,
            "artist": artist,
            "title": track.get("title", ""),
            "duration": duration,
        }

        if side_letter not in sides_dict:
            sides_dict[side_letter] = []
        sides_dict[side_letter].append(track_data)

    # Convert to list sorted by side letter
    sides = [
        {"ind": letter, "tracks": tracks}
        for letter, tracks in sorted(sides_dict.items())
    ]

    transformed = {
        "id": release.get("id"),
        "cover": cover,
        "sides": sides,
    }

    return transformed, has_missing_durations


def save_release(release: dict) -> Path:
    """Transform and save Discogs release data as JSON file."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    transformed, has_missing_durations = transform_release(release)

    if has_missing_durations:
        print("\n⚠ WARNING: Some tracks have missing durations. Please fill them manually.")

    release_id = transformed.get("id")
    filename = f"{release_id}.json"
    filepath = DATA_DIR / filename

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(transformed, f, indent=2, ensure_ascii=False)

    return filepath


def download_album(query: str) -> Path | None:
    """Search for album on Discogs, let user select, and save raw response as JSON."""
    print(f"Searching for: {query}")

    results = search_releases(query)
    if not results:
        raise ValueError(f"No vinyl releases found for: {query}")

    display_results(results)

    max_choice = min(len(results), 10)
    selection = prompt_selection(max_choice)

    if selection is None:
        print("Cancelled.")
        return None

    selected = results[selection - 1]
    release_id = selected.get("id")
    print(f"\nFetching release details for: {selected.get('title')}...")

    release = fetch_release(release_id)
    filepath = save_release(release)

    print(f"Saved to: {filepath}")

    return filepath


def main():
    if len(sys.argv) < 2:
        print("Usage: python discogs_download.py <query>")
        print('Examples:')
        print('  python discogs_download.py "Linkin Park - Papercuts"')
        print('  python discogs_download.py "Stranger Things 4 Soundtrack"')
        sys.exit(1)

    query = " ".join(sys.argv[1:])

    try:
        result = download_album(query)
        if result is None:
            sys.exit(0)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except requests.RequestException as e:
        print(f"Network error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
