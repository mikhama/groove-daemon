# Project Context

## Purpose
Vinyl Playback Monitor System - A non-invasive, offline, microphone-based device that:
- Detects when a vinyl record is playing via environmental audio analysis
- Tracks stylus usage time (cumulative hours)
- Identifies which album is playing via RFID tags
- Estimates the current track based on elapsed time
- Displays album, side, track, elapsed time, and total stylus hours

The system is a probabilistic observer that preserves the ritual of vinyl listening without interfering with the turntable or audio chain.

## Tech Stack
- Python 3.10+
- Poetry (dependency management)
- NumPy (audio processing, FFT, RMS computation)
- PyAudio (audio capture from USB microphone)
- SQLite or JSON (local data storage)
- Target hardware: Raspberry Pi Zero 2 W or Pi 4
- OLED (SSD1306) or IPS display for UI output
- RFID Reader (RC522 or similar) for album identification

## Project Conventions

### Code Style
- Python with type hints
- Modules organized by functionality (audio_detector, rfid_reader, track_estimator, etc.)
- Configuration via constructor parameters with sensible defaults
- Enum classes for state management

### Architecture Patterns
- State machine pattern for playback detection (IDLE → PLAYING → STOPPED)
- Event-driven audio processing with configurable thresholds
- Separation of concerns: detection, tracking, display, storage as independent modules
- Planned modules: `audio_detector.py`, `rfid_reader.py`, `track_estimator.py`, `stylus_counter.py`, `display_manager.py`, `state_machine.py`, `database_manager.py`

### Testing Strategy
- Unit tests for audio processing algorithms (RMS, spectral bandwidth)
- Integration tests for state machine transitions
- Manual testing with actual vinyl playback for threshold tuning

### Git Workflow
- One developer - single branch

## Domain Context
- Playback detection uses RMS amplitude and spectral bandwidth analysis
- Music detected when: RMS > threshold AND spectral bandwidth > threshold for ≥ N seconds
- Silence detected when: RMS < lower threshold for ≥ M seconds
- Track estimation is deterministic time-based mapping (not audio fingerprinting)
- Side switching (A/B) requires manual toggle or heuristic detection (90% side completion)
- Detection is probabilistic (~90-95% reliability in stable environments)

## Important Constraints
### Hard Constraints
- No modification to turntable hardware or tonearm
- No splitting RCA cables or connection to audio chain
- No paid APIs (Shazam, Audd, etc.)
- Fully offline operation
- Fully reversible and external

### Soft Constraints
- Elegant and minimal design
- Accept probabilistic detection (not industrial-grade certainty)
- Optimal microphone placement: near speaker, away from conversation zone

## External Dependencies
- No external services or APIs (fully offline)
- Local storage only (SQLite or JSON files)
- Hardware dependencies: USB microphone, RFID reader, display module
