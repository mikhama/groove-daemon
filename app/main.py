#!/usr/bin/env python3
"""
Vinyl Playback Monitor System
Detects music playback using microphone input, estimates current track, and displays status.
"""

import json
import numpy as np
import pyaudio
import time
import sys
import select
import termios
import tty
from enum import Enum
from datetime import timedelta
from pathlib import Path

from .album_loader import load_album, Album
from .track_estimator import TrackEstimator

# Detection delay compensation (seconds) - accounts for time music plays before detection confirms
DETECTION_DELAY_SECONDS = 10

# Debug file path
DEBUG_FILE = Path(__file__).parent.parent / ".data" / "debug.json"


def get_debug_playback_offset() -> float:
    """Read debug playback offset from .data/debug.json if it exists."""
    if not DEBUG_FILE.exists():
        return 0.0
    try:
        with open(DEBUG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        playback = data.get("playback", "")
        if playback and ":" in playback:
            parts = playback.split(":")
            if len(parts) == 2:
                minutes, seconds = int(parts[0]), int(parts[1])
                return minutes * 60 + seconds
    except (json.JSONDecodeError, ValueError, FileNotFoundError):
        pass
    return 0.0


class PlaybackState(Enum):
    IDLE = "IDLE"
    PLAYING = "PLAYING"
    STOPPED = "STOPPED"


class KeyboardInput:
    """Non-blocking keyboard input handler for Unix."""

    def __init__(self):
        self.input_buffer = ""
        self.old_settings = None

    def setup(self):
        """Set terminal to raw mode for non-blocking input."""
        self.old_settings = termios.tcgetattr(sys.stdin)
        tty.setcbreak(sys.stdin.fileno())

    def restore(self):
        """Restore terminal settings."""
        if self.old_settings:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.old_settings)

    def get_key(self) -> str | None:
        """Get a key if available, non-blocking. Returns None if no key."""
        if select.select([sys.stdin], [], [], 0)[0]:
            return sys.stdin.read(1)
        return None

    def process_input(self, key: str) -> tuple[str | None, str]:
        """Process key input. Returns (action, current_buffer).

        Actions: 'submit' (Enter pressed), 'next_side', 'prev_side', None
        """
        if key == "\n" or key == "\r":
            result = self.input_buffer
            self.input_buffer = ""
            return ("submit", result) if result else (None, "")
        elif key == "d":
            return ("next_side", self.input_buffer)
        elif key == "a":
            return ("prev_side", self.input_buffer)
        elif key.isdigit():
            self.input_buffer += key
            return (None, self.input_buffer)
        elif key == "\x7f" or key == "\x08":  # Backspace
            self.input_buffer = self.input_buffer[:-1]
            return (None, self.input_buffer)
        elif key == "\x1b":  # Escape - clear buffer
            self.input_buffer = ""
            return (None, "")
        return (None, self.input_buffer)


class AudioDetector:
    def __init__(
        self,
        sample_rate: int = 44100,
        chunk_size: int = 4096,
        rms_threshold: float = 0.001,
        rms_stop_threshold: float = 0.0005,
        bandwidth_threshold: float = 1000.0,
        start_confirm_seconds: float = 2.0,
        stop_confirm_seconds: float = 5.0,
        display_interval: float = 0.2,
    ):
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.rms_threshold = rms_threshold
        self.rms_stop_threshold = rms_stop_threshold
        self.bandwidth_threshold = bandwidth_threshold
        self.start_confirm_seconds = start_confirm_seconds
        self.stop_confirm_seconds = stop_confirm_seconds
        self.display_interval = display_interval

        self.state = PlaybackState.IDLE
        self.last_display_time = 0.0
        self.playback_start_time = None
        self.total_playback_seconds = 0.0
        self.candidate_start_time = None
        self.candidate_stop_time = None

        self.audio = pyaudio.PyAudio()
        self.stream = None

        # Album and track estimation
        self.album: Album | None = None
        self.track_estimator: TrackEstimator | None = None
        self.keyboard = KeyboardInput()
        self.input_display = ""

    def compute_rms(self, audio_data: np.ndarray) -> float:
        """Compute Root Mean Square amplitude."""
        return np.sqrt(np.mean(audio_data ** 2))

    def compute_spectral_bandwidth(self, audio_data: np.ndarray) -> float:
        """Compute spectral bandwidth using FFT."""
        fft_data = np.abs(np.fft.rfft(audio_data))
        freqs = np.fft.rfftfreq(len(audio_data), 1.0 / self.sample_rate)

        # Avoid division by zero
        total_power = np.sum(fft_data)
        if total_power == 0:
            return 0.0

        # Compute spectral centroid
        centroid = np.sum(freqs * fft_data) / total_power

        # Compute spectral bandwidth (weighted standard deviation)
        bandwidth = np.sqrt(np.sum(((freqs - centroid) ** 2) * fft_data) / total_power)
        return bandwidth

    def is_music_detected(self, audio_data: np.ndarray) -> bool:
        """Check if audio characteristics indicate music playback."""
        rms = self.compute_rms(audio_data)
        bandwidth = self.compute_spectral_bandwidth(audio_data)
        return rms > self.rms_threshold and bandwidth > self.bandwidth_threshold

    def is_silence_detected(self, audio_data: np.ndarray) -> bool:
        """Check if audio characteristics indicate silence."""
        rms = self.compute_rms(audio_data)
        return rms < self.rms_stop_threshold

    def format_duration(self, seconds: float) -> str:
        """Format duration as HH:MM:SS."""
        td = timedelta(seconds=int(seconds))
        hours, remainder = divmod(td.seconds + td.days * 86400, 3600)
        minutes, secs = divmod(remainder, 60)
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        return f"{minutes:02d}:{secs:02d}"

    def update_state(self, audio_data: np.ndarray) -> None:
        """Update playback state based on audio analysis."""
        current_time = time.time()
        music_detected = self.is_music_detected(audio_data)
        silence_detected = self.is_silence_detected(audio_data)

        if self.state == PlaybackState.IDLE or self.state == PlaybackState.STOPPED:
            if music_detected:
                if self.candidate_start_time is None:
                    self.candidate_start_time = current_time
                elif current_time - self.candidate_start_time >= self.start_confirm_seconds:
                    self._transition_to_playing(current_time)
            else:
                self.candidate_start_time = None

        elif self.state == PlaybackState.PLAYING:
            if silence_detected:
                if self.candidate_stop_time is None:
                    self.candidate_stop_time = current_time
                elif current_time - self.candidate_stop_time >= self.stop_confirm_seconds:
                    self._transition_to_stopped(current_time)
            else:
                self.candidate_stop_time = None

    def _transition_to_playing(self, current_time: float) -> None:
        """Transition to PLAYING state."""
        self.state = PlaybackState.PLAYING
        self.playback_start_time = current_time - self.start_confirm_seconds
        self.candidate_start_time = None
        self.candidate_stop_time = None
        print(f"\n{'='*50}")
        print(f"▶ MUSIC STARTED at {time.strftime('%H:%M:%S')}")

        # Check if we should auto-advance based on offset (debug mode)
        if self.track_estimator:
            initial_offset = DETECTION_DELAY_SECONDS + get_debug_playback_offset()
            elapsed_on_side = self.track_estimator.get_elapsed_on_current_side(initial_offset)
            side_duration = self.track_estimator.current_side_duration
            print(f"  Offset: {self.format_duration(initial_offset)} | Side {self.track_estimator.side_ind} elapsed: {self.format_duration(elapsed_on_side)} | duration: {self.format_duration(side_duration)}")
            while elapsed_on_side >= side_duration and side_duration > 0:
                if not self.track_estimator.next_side(auto_advance=True):
                    break
                print(f"  >> Auto-advanced to Side {self.track_estimator.side_ind}")
                elapsed_on_side = self.track_estimator.get_elapsed_on_current_side(initial_offset)
                side_duration = self.track_estimator.current_side_duration

        print(f"{'='*50}")

    def _transition_to_stopped(self, current_time: float) -> None:
        """Transition to STOPPED state."""
        session_duration = current_time - self.playback_start_time - self.stop_confirm_seconds
        # Effective duration includes offsets (for track estimation and auto-advance)
        effective_duration = session_duration + DETECTION_DELAY_SECONDS + get_debug_playback_offset()
        self.total_playback_seconds += session_duration
        self.state = PlaybackState.STOPPED
        self.candidate_start_time = None
        self.candidate_stop_time = None
        print(f"\n{'='*50}")
        print(f"⏹ MUSIC STOPPED at {time.strftime('%H:%M:%S')}")
        print(f"  Session duration: {self.format_duration(effective_duration)}")
        print(f"  Total playback:   {self.format_duration(self.total_playback_seconds)}")

        # Auto-advance to next side if elapsed time on current side exceeded side duration
        if self.track_estimator:
            elapsed_on_side = self.track_estimator.get_elapsed_on_current_side(effective_duration)
            side_duration = self.track_estimator.current_side_duration
            print(f"  Effective: {self.format_duration(effective_duration)} | Side {self.track_estimator.side_ind} elapsed: {self.format_duration(elapsed_on_side)} | duration: {self.format_duration(side_duration)}")
            while elapsed_on_side >= side_duration and side_duration > 0:
                if not self.track_estimator.next_side(auto_advance=True):
                    break
                print(f"  >> Auto-advanced to Side {self.track_estimator.side_ind}")
                elapsed_on_side = self.track_estimator.get_elapsed_on_current_side(effective_duration)
                side_duration = self.track_estimator.current_side_duration

        print(f"{'='*50}")

    def get_current_duration(self) -> float:
        """Get current session duration if playing, including offsets."""
        if self.state == PlaybackState.PLAYING and self.playback_start_time:
            base_duration = time.time() - self.playback_start_time
            return base_duration + DETECTION_DELAY_SECONDS + get_debug_playback_offset()
        return 0.0

    def load_album_by_id(self, album_id_str: str) -> bool:
        """Load album by ID string. Returns True if successful."""
        try:
            album_id = int(album_id_str)
            album = load_album(album_id)
            if album:
                self.album = album
                self.track_estimator = TrackEstimator(album)
                print(f"\n{'='*50}")
                print(f"Loaded album: {album_id}")
                print(f"Sides: {', '.join(s.ind for s in album.sides)}")
                print(f"{'='*50}")
                return True
            else:
                print(f"\nAlbum {album_id} not found")
                return False
        except ValueError:
            print(f"\nInvalid album ID: {album_id_str}")
            return False

    def handle_keyboard(self) -> None:
        """Handle keyboard input."""
        key = self.keyboard.get_key()
        if key is None:
            return

        action, buffer = self.keyboard.process_input(key)
        self.input_display = buffer

        if action == "submit" and buffer:
            self.load_album_by_id(buffer)
            self.input_display = ""
        elif action == "next_side" and self.track_estimator:
            if self.track_estimator.next_side():
                print(f"\n>> Side {self.track_estimator.side_ind}")
        elif action == "prev_side" and self.track_estimator:
            if self.track_estimator.prev_side():
                print(f"\n<< Side {self.track_estimator.side_ind}")

    def display_status(self, audio_data: np.ndarray) -> None:
        """Display current status on single line."""
        rms = self.compute_rms(audio_data)
        bandwidth = self.compute_spectral_bandwidth(audio_data)

        status_icon = {
            PlaybackState.IDLE: "⏸",
            PlaybackState.PLAYING: "▶",
            PlaybackState.STOPPED: "⏹",
        }[self.state]

        current_duration = self.get_current_duration()
        total = self.total_playback_seconds + (current_duration if self.state == PlaybackState.PLAYING else 0)

        # Auto-advance side if elapsed time on current side exceeds side duration
        if self.track_estimator and self.state == PlaybackState.PLAYING:
            elapsed_on_side = self.track_estimator.get_elapsed_on_current_side(current_duration)
            side_duration = self.track_estimator.current_side_duration
            if elapsed_on_side >= side_duration and side_duration > 0:
                if self.track_estimator.next_side(auto_advance=True):
                    print(f"\n  >> Auto-advanced to Side {self.track_estimator.side_ind}")

        # Build track info
        track_info = ""
        side_info = ""
        if self.track_estimator:
            elapsed_on_side = self.track_estimator.get_elapsed_on_current_side(current_duration)
            side_info = f"Side {self.track_estimator.side_ind}"
            track = self.track_estimator.get_current_track(elapsed_on_side)
            if track:
                track_info = f"{track.artist} - {track.title}"

        # Build status line
        if self.input_display:
            # Show input being typed
            status = f"\r{status_icon} {self.state.value:8} | Enter album ID: {self.input_display}_"
        elif track_info:
            # Show track info
            status = (
                f"\r{status_icon} {self.state.value:8} | {side_info} | "
                f"{self.format_duration(current_duration):>8} | {track_info[:40]:<40}"
            )
        elif self.album:
            # Album loaded but no track (maybe not playing)
            status = (
                f"\r{status_icon} {self.state.value:8} | {side_info} | "
                f"Session: {self.format_duration(current_duration):>8} | "
                f"Total: {self.format_duration(total):>8}"
            )
        else:
            # No album - show hint
            hint = "Type album ID + Enter" if self.state != PlaybackState.PLAYING else ""
            status = (
                f"\r{status_icon} {self.state.value:8} | "
                f"Session: {self.format_duration(current_duration):>8} | "
                f"Total: {self.format_duration(total):>8} | {hint}"
            )

        # Clear line and print
        print(f"{status:<100}", end="", flush=True)

    def start(self) -> None:
        """Start audio detection."""
        print("Vinyl Playback Monitor")
        print("=" * 50)
        print(f"Sample Rate: {self.sample_rate} Hz")
        print(f"Chunk Size: {self.chunk_size}")
        print(f"RMS Start Threshold: {self.rms_threshold}")
        print(f"RMS Stop Threshold: {self.rms_stop_threshold}")
        print(f"Bandwidth Threshold: {self.bandwidth_threshold} Hz")
        print(f"Start Confirm: {self.start_confirm_seconds}s")
        print(f"Stop Confirm: {self.stop_confirm_seconds}s")
        print("=" * 50)
        print("Controls: [a] prev side  [d] next side  [0-9+Enter] load album")
        print("Press Ctrl+C to stop")
        print("=" * 50)
        print()

        self.keyboard.setup()

        try:
            self.stream = self.audio.open(
                format=pyaudio.paFloat32,
                channels=1,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size,
            )

            while True:
                raw_data = self.stream.read(self.chunk_size, exception_on_overflow=False)
                audio_data = np.frombuffer(raw_data, dtype=np.float32)

                self.handle_keyboard()
                self.update_state(audio_data)

                # Throttle display updates to reduce CPU usage
                current_time = time.time()
                if current_time - self.last_display_time >= self.display_interval:
                    self.display_status(audio_data)
                    self.last_display_time = current_time

        except KeyboardInterrupt:
            print("\n\nStopping...")
        finally:
            self.keyboard.restore()
            self.stop()

    def stop(self) -> None:
        """Stop audio detection and cleanup."""
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        self.audio.terminate()

        print("\n" + "=" * 50)
        print("Session Summary")
        print("=" * 50)
        print(f"Total playback time: {self.format_duration(self.total_playback_seconds)}")
        print(f"Total hours: {self.total_playback_seconds / 3600:.2f}h")
        print("=" * 50)


def main():
    detector = AudioDetector()
    detector.start()


if __name__ == "__main__":
    main()
