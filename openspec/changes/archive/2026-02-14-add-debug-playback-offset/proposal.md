# Change: Add Debug Playback Offset

## Why
When testing without actual vinyl playback, we need a way to simulate elapsed time. Additionally, the audio detection has inherent latency (~10 seconds) before music is confirmed, so actual playback time is always ahead of detected time.

## What Changes
- Add `DETECTION_DELAY_SECONDS` constant (default 10 seconds) that is always added to session time
- Support optional `.data/debug.json` file with `playback` field in "MM:SS" format
- When debug file exists, add parsed playback time to session elapsed time
- This allows testing track estimation without waiting for real playback

## Impact
- Affected specs: `audio-detection` (modified - add debug offset support)
- Affected code: `app/main.py` (add constant and debug file reading)
