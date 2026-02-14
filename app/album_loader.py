"""
Album Loader for Vinyl Playback Monitor System
Loads album data from JSON files and parses track durations.
"""

import json
from pathlib import Path
from dataclasses import dataclass


DATA_DIR = Path(__file__).parent.parent / ".data" / "albums"


@dataclass
class Track:
    position: str
    artist: str
    title: str
    duration_seconds: int


@dataclass
class Side:
    ind: str
    tracks: list[Track]


@dataclass
class Album:
    id: int
    cover: str
    sides: list[Side]


def parse_duration(duration_str: str) -> int:
    """Convert duration string (M:SS or MM:SS) to seconds."""
    if not duration_str:
        return 0
    parts = duration_str.split(":")
    if len(parts) == 2:
        minutes, seconds = int(parts[0]), int(parts[1])
        return minutes * 60 + seconds
    return 0


def load_album(album_id: int) -> Album | None:
    """Load album data from JSON file and parse durations to seconds."""
    filepath = DATA_DIR / f"{album_id}.json"
    if not filepath.exists():
        return None

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    sides = []
    for side_data in data.get("sides", []):
        tracks = []
        for track_data in side_data.get("tracks", []):
            track = Track(
                position=track_data.get("position", ""),
                artist=track_data.get("artist", ""),
                title=track_data.get("title", ""),
                duration_seconds=parse_duration(track_data.get("duration", "")),
            )
            tracks.append(track)
        sides.append(Side(ind=side_data.get("ind", ""), tracks=tracks))

    return Album(
        id=data.get("id", album_id),
        cover=data.get("cover", ""),
        sides=sides,
    )
