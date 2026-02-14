# Change: Add Audio-Based Playback Detection

## Why
The vinyl playback monitor system needs to detect when music is playing without connecting to the turntable or audio chain. This is the foundational capability that enables stylus hour tracking and track estimation.

## What Changes
- Add `AudioDetector` class that captures audio via USB microphone
- Implement RMS amplitude and spectral bandwidth analysis for playback detection
- Implement state machine (IDLE → PLAYING → STOPPED) with configurable confirmation thresholds
- Track session and cumulative playback duration
- Display real-time status in terminal

## Impact
- Affected specs: `audio-detection` (new capability)
- Affected code: `app/audio_detector.py` (new file)
- Dependencies added: `numpy`, `pyaudio` via Poetry
