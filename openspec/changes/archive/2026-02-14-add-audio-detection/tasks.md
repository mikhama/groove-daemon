# Tasks

## 1. Project Setup
- [x] 1.1 Initialize Poetry project with `pyproject.toml`
- [x] 1.2 Configure in-project virtualenv via `poetry.toml`
- [x] 1.3 Add dependencies: numpy, pyaudio

## 2. Audio Detection Implementation
- [x] 2.1 Create `app/audio_detector.py` module
- [x] 2.2 Implement `PlaybackState` enum (IDLE, PLAYING, STOPPED)
- [x] 2.3 Implement `AudioDetector` class with configurable thresholds
- [x] 2.4 Implement RMS amplitude computation
- [x] 2.5 Implement spectral bandwidth computation via FFT
- [x] 2.6 Implement state machine transitions with confirmation delays
- [x] 2.7 Implement session and total duration tracking
- [x] 2.8 Implement terminal display with real-time status

## 3. Documentation
- [x] 3.1 Add module docstrings
- [x] 3.2 Update OpenSpec with audio-detection capability spec
