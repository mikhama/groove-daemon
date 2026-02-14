# track-estimation Specification

## Purpose
TBD - created by archiving change add-track-estimation. Update Purpose after archive.
## Requirements
### Requirement: Album Loading
The system SHALL load album data from JSON files in `.data/albums/` directory.

#### Scenario: Load album by ID
- **WHEN** the user enters an album ID
- **THEN** the system loads `.data/albums/{id}.json`
- **AND** parses track durations from "M:SS" or "MM:SS" format to seconds

#### Scenario: Album not found
- **WHEN** the user enters an ID that doesn't exist
- **THEN** the system displays an error message
- **AND** remains in the current state without loading

#### Scenario: Duration parsing
- **WHEN** a track duration is "3:45"
- **THEN** it is parsed to 225 seconds
- **WHEN** a track duration is empty
- **THEN** it is treated as 0 seconds (user must fill manually)

### Requirement: Side Management
The system SHALL track the current side and allow manual side switching.

#### Scenario: Initial side selection
- **WHEN** an album is loaded
- **THEN** the current side is set to "A" (first side)

#### Scenario: Next side
- **WHEN** the user presses `d`
- **THEN** the system advances to the next side (A→B→C→D)
- **AND** session time continues without reset

#### Scenario: Previous side
- **WHEN** the user presses `a`
- **THEN** the system goes to the previous side (D→C→B→A)
- **AND** session time continues without reset

#### Scenario: Side boundary
- **WHEN** user presses next on the last side
- **THEN** the side does not change (stays on last side)
- **WHEN** user presses previous on the first side
- **THEN** the side does not change (stays on first side)

#### Scenario: Automatic side advancement
- **WHEN** playback stops (transitions to STOPPED)
- **AND** elapsed time exceeded the current side's total duration
- **THEN** the system automatically advances to the next side
- **AND** displays a message indicating side change

### Requirement: Track Estimation
The system SHALL estimate the current track based on elapsed playback time on the current side.

#### Scenario: Calculate current track
- **WHEN** playback is active on a side
- **THEN** the system sums track durations until elapsed time is exceeded
- **AND** the track where cumulative duration exceeds elapsed time is the current track

#### Scenario: Elapsed time exceeds side duration during playback
- **WHEN** elapsed time on current side exceeds side duration during playback
- **THEN** the system auto-advances to the next side
- **AND** track estimation uses elapsed time relative to current side

#### Scenario: Track display format
- **WHEN** the current track is estimated
- **THEN** it is displayed as "{artist} - {title}"

### Requirement: Keyboard Input
The system SHALL accept keyboard input for album selection and side control.

#### Scenario: Album ID entry
- **WHEN** the user types a number and presses Enter
- **THEN** the system attempts to load that album
- **AND** this works in any state (IDLE, PLAYING, or STOPPED)

#### Scenario: Input display
- **WHEN** the user is typing an album ID
- **THEN** the typed characters are displayed on screen in real-time

#### Scenario: Side control during playback
- **WHEN** the system is in PLAYING state
- **AND** the user presses `d` or `a`
- **THEN** the side changes accordingly

#### Scenario: Non-blocking input
- **WHEN** keyboard input is checked
- **THEN** it does not block the audio processing loop

### Requirement: Status Display Integration
The system SHALL display the current track in the status line alongside existing metrics.

#### Scenario: Status with track info
- **WHEN** an album is loaded and playback is active
- **THEN** the status line shows: state, current track, side, session duration, total duration

#### Scenario: Status without album
- **WHEN** no album is loaded
- **THEN** the status line shows existing info without track display
- **AND** a hint is shown: "Press Enter to type album ID"

