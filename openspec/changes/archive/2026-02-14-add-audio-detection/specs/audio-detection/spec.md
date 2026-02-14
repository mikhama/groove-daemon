## ADDED Requirements

### Requirement: Audio Capture
The system SHALL capture audio from a USB microphone using PyAudio at a configurable sample rate (default 44100 Hz) and chunk size (default 4096 samples).

#### Scenario: Audio stream initialization
- **WHEN** the AudioDetector starts
- **THEN** it opens a mono float32 audio input stream
- **AND** continuously reads audio chunks for analysis

#### Scenario: Graceful shutdown
- **WHEN** the user presses Ctrl+C
- **THEN** the audio stream is stopped and closed
- **AND** PyAudio is terminated cleanly

### Requirement: RMS Amplitude Analysis
The system SHALL compute Root Mean Square (RMS) amplitude for each audio chunk to measure signal strength.

#### Scenario: RMS computation
- **WHEN** an audio chunk is received
- **THEN** RMS is calculated as sqrt(mean(samples^2))
- **AND** the value is compared against configurable thresholds

### Requirement: Spectral Bandwidth Analysis
The system SHALL compute spectral bandwidth using FFT to distinguish music from noise.

#### Scenario: Bandwidth computation
- **WHEN** an audio chunk is received
- **THEN** FFT is applied to compute frequency spectrum
- **AND** spectral bandwidth (weighted standard deviation from centroid) is calculated
- **AND** the value is compared against a configurable threshold (default 1000 Hz)

### Requirement: Playback State Machine
The system SHALL maintain a state machine with three states: IDLE, PLAYING, and STOPPED.

#### Scenario: Transition from IDLE to PLAYING
- **WHEN** the system is in IDLE state
- **AND** music is detected (RMS > threshold AND bandwidth > threshold)
- **AND** the condition persists for the confirmation period (default 2 seconds)
- **THEN** the system transitions to PLAYING state
- **AND** playback start time is recorded

#### Scenario: Transition from PLAYING to STOPPED
- **WHEN** the system is in PLAYING state
- **AND** silence is detected (RMS < stop threshold)
- **AND** the condition persists for the confirmation period (default 5 seconds)
- **THEN** the system transitions to STOPPED state
- **AND** session duration is added to total playback time

#### Scenario: Transition from STOPPED to PLAYING
- **WHEN** the system is in STOPPED state
- **AND** music is detected again
- **AND** the condition persists for the confirmation period
- **THEN** the system transitions to PLAYING state

### Requirement: Duration Tracking
The system SHALL track both current session duration and cumulative total playback time.

#### Scenario: Session duration tracking
- **WHEN** the system is in PLAYING state
- **THEN** elapsed time since playback start is available
- **AND** duration is formatted as MM:SS or HH:MM:SS

#### Scenario: Total duration accumulation
- **WHEN** playback stops
- **THEN** session duration is added to total playback seconds
- **AND** total hours are displayed with decimal precision

### Requirement: Real-Time Status Display
The system SHALL display real-time status in the terminal including state, durations, and audio metrics.

#### Scenario: Status line display
- **WHEN** the detector is running
- **THEN** a single-line status is updated every 0.2 seconds
- **AND** shows: state icon, state name, session duration, total duration, RMS, bandwidth

#### Scenario: State transition notification
- **WHEN** playback starts or stops
- **THEN** a banner message is printed with timestamp and duration summary
