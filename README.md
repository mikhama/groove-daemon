# groove-daemon
Raspberry Pi–based system for monitoring vinyl playback. Tracks stylus usage time using acoustic detection, identifies records via RFID, and estimates the currently playing track based on playback timing. No modifications to turntable or audio chain required.

## Development
- Install dependencies with `poetry shell && poetry install`.
- Run with `poetry run python -m app.main`.
