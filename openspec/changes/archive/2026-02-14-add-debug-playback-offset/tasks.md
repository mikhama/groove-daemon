# Tasks

## 1. Detection Delay Constant
- [x] 1.1 Add `DETECTION_DELAY_SECONDS = 10` constant to main.py
- [x] 1.2 Add detection delay to `get_current_duration()` calculation

## 2. Debug Playback Offset
- [x] 2.1 Create function to read and parse `.data/debug.json`
- [x] 2.2 Parse `playback` field from "MM:SS" format to seconds
- [x] 2.3 Add debug offset to `get_current_duration()` calculation

## 3. Testing
- [x] 3.1 Test with debug.json containing `{"playback": "05:00"}`
- [x] 3.2 Verify track estimation reflects offset time
