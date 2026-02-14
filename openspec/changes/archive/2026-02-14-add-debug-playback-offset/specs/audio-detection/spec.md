## ADDED Requirements

### Requirement: Detection Delay Compensation
The system SHALL compensate for detection latency by adding a constant offset to session time.

#### Scenario: Detection delay offset
- **WHEN** calculating session elapsed time
- **THEN** add `DETECTION_DELAY_SECONDS` constant (default 10 seconds) to the elapsed time
- **AND** this offset accounts for the time music plays before detection confirms

### Requirement: Debug Playback Offset
The system SHALL support an optional debug file to add extra time to session elapsed time.

#### Scenario: Debug file with playback time
- **WHEN** `.data/debug.json` exists with a `playback` field (e.g., "05:30")
- **THEN** parse the value as MM:SS and add to session elapsed time
- **AND** this allows testing track estimation without real playback

#### Scenario: Offsets affect auto-advance
- **WHEN** playback stops and effective duration (including offsets) exceeds side duration
- **THEN** the system auto-advances to the next side
- **AND** this allows testing side auto-advance with debug offset

#### Scenario: Debug file missing or invalid
- **WHEN** `.data/debug.json` does not exist or has no valid `playback` field
- **THEN** no debug offset is added
- **AND** the system continues normally
