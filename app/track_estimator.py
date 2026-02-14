"""
Track Estimator for Vinyl Playback Monitor System
Estimates current track based on elapsed playback time.
"""

from dataclasses import dataclass
from .album_loader import Album, Track


@dataclass
class CurrentTrack:
    artist: str
    title: str
    position: str
    side_ind: str


class TrackEstimator:
    def __init__(self, album: Album):
        self.album = album
        self.current_side_index = 0
        self.completed_sides_duration = 0.0  # Cumulative duration of sides we've passed

    @property
    def current_side(self):
        """Get the current side."""
        if 0 <= self.current_side_index < len(self.album.sides):
            return self.album.sides[self.current_side_index]
        return None

    @property
    def side_ind(self) -> str:
        """Get current side indicator (A, B, C, D)."""
        side = self.current_side
        return side.ind if side else ""

    @property
    def current_side_duration(self) -> float:
        """Get total duration of current side in seconds."""
        side = self.current_side
        if not side:
            return 0.0
        return sum(track.duration_seconds for track in side.tracks)

    def get_elapsed_on_current_side(self, total_elapsed: float) -> float:
        """Get elapsed time on current side (total minus completed sides)."""
        return max(0.0, total_elapsed - self.completed_sides_duration)

    def next_side(self, auto_advance: bool = False) -> bool:
        """Advance to next side. Returns True if side changed.

        Args:
            auto_advance: If True, update completed_sides_duration (for auto-advance).
                         If False, keep elapsed time relative to new side (manual switch).
        """
        if self.current_side_index < len(self.album.sides) - 1:
            if auto_advance:
                # Add current side's duration to completed total before advancing
                self.completed_sides_duration += self.current_side_duration
            self.current_side_index += 1
            return True
        return False

    def prev_side(self, auto_advance: bool = False) -> bool:
        """Go to previous side. Returns True if side changed.

        Args:
            auto_advance: If True, update completed_sides_duration.
                         If False, keep elapsed time relative to new side (manual switch).
        """
        if self.current_side_index > 0:
            if auto_advance:
                self.current_side_index -= 1
                # Subtract the new current side's duration from completed total
                self.completed_sides_duration -= self.current_side_duration
                self.completed_sides_duration = max(0.0, self.completed_sides_duration)
            else:
                self.current_side_index -= 1
            return True
        return False

    def get_current_track(self, elapsed_seconds: float) -> CurrentTrack | None:
        """Estimate current track based on elapsed time on current side."""
        side = self.current_side
        if not side or not side.tracks:
            return None

        cumulative = 0.0
        for track in side.tracks:
            cumulative += track.duration_seconds
            if elapsed_seconds < cumulative:
                return CurrentTrack(
                    artist=track.artist,
                    title=track.title,
                    position=track.position,
                    side_ind=side.ind,
                )

        # Elapsed time exceeds side duration - return last track
        last_track = side.tracks[-1]
        return CurrentTrack(
            artist=last_track.artist,
            title=last_track.title,
            position=last_track.position,
            side_ind=side.ind,
        )
