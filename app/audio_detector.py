#!/usr/bin/env python3
"""
Audio Detector for Vinyl Playback Monitor System
Detects music playback using microphone input and displays state/duration.
"""

import numpy as np
import pyaudio
import time
from enum import Enum
from datetime import timedelta


class PlaybackState(Enum):
    IDLE = "IDLE"
    PLAYING = "PLAYING"
    STOPPED = "STOPPED"


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
        print(f"{'='*50}")

    def _transition_to_stopped(self, current_time: float) -> None:
        """Transition to STOPPED state."""
        session_duration = current_time - self.playback_start_time - self.stop_confirm_seconds
        self.total_playback_seconds += session_duration
        self.state = PlaybackState.STOPPED
        self.candidate_start_time = None
        self.candidate_stop_time = None
        print(f"\n{'='*50}")
        print(f"⏹ MUSIC STOPPED at {time.strftime('%H:%M:%S')}")
        print(f"  Session duration: {self.format_duration(session_duration)}")
        print(f"  Total playback:   {self.format_duration(self.total_playback_seconds)}")
        print(f"{'='*50}")

    def get_current_duration(self) -> float:
        """Get current session duration if playing."""
        if self.state == PlaybackState.PLAYING and self.playback_start_time:
            return time.time() - self.playback_start_time
        return 0.0

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

        status = (
            f"\r{status_icon} {self.state.value:8} | "
            f"Session: {self.format_duration(current_duration):>8} | "
            f"Total: {self.format_duration(total):>8} | "
            f"RMS: {rms:.4f} | BW: {bandwidth:>7.1f} Hz"
        )
        print(status, end="", flush=True)

    def start(self) -> None:
        """Start audio detection."""
        print("Vinyl Playback Monitor - Audio Detector")
        print("=" * 50)
        print(f"Sample Rate: {self.sample_rate} Hz")
        print(f"Chunk Size: {self.chunk_size}")
        print(f"RMS Start Threshold: {self.rms_threshold}")
        print(f"RMS Stop Threshold: {self.rms_stop_threshold}")
        print(f"Bandwidth Threshold: {self.bandwidth_threshold} Hz")
        print(f"Start Confirm: {self.start_confirm_seconds}s")
        print(f"Stop Confirm: {self.stop_confirm_seconds}s")
        print("=" * 50)
        print("\nListening... (Press Ctrl+C to stop)\n")

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

                self.update_state(audio_data)

                # Throttle display updates to reduce CPU usage
                current_time = time.time()
                if current_time - self.last_display_time >= self.display_interval:
                    self.display_status(audio_data)
                    self.last_display_time = current_time

        except KeyboardInterrupt:
            print("\n\nStopping...")
        finally:
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
