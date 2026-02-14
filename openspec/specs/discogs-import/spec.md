# discogs-import Specification

## Purpose
TBD - created by archiving change add-discogs-downloader. Update Purpose after archive.
## Requirements
### Requirement: Interactive Album Search
The script SHALL search Discogs and let the user select from results.

#### Scenario: Search with artist and album
- **WHEN** the user runs `python app/discogs_download.py "Linkin Park - Papercuts"`
- **THEN** the script searches Discogs via `https://api.discogs.com/database/search`
- **AND** filters results to vinyl format releases
- **AND** displays a numbered list of results with artist, title, year, and format

#### Scenario: Search with album only
- **WHEN** the user runs `python app/discogs_download.py "Stranger Things 4 Soundtrack"`
- **THEN** the script searches Discogs with the query
- **AND** displays matching vinyl releases for selection

#### Scenario: User selects a result
- **WHEN** search results are displayed
- **THEN** the user is prompted to enter a number to select a release
- **AND** the selected release details are fetched and saved

#### Scenario: User cancels search
- **WHEN** the user enters 'q' or empty input at the selection prompt
- **THEN** the script exits without downloading

#### Scenario: No results found
- **WHEN** the search returns no matching vinyl releases
- **THEN** the script prints an error message indicating no matches
- **AND** exits with a non-zero status code

### Requirement: Fetch Release Details
The script SHALL fetch full release details from Discogs after user selection.

#### Scenario: Fetch full release data
- **WHEN** the user selects a release from search results
- **THEN** the script fetches full release data from `https://api.discogs.com/releases/{id}`

#### Scenario: Rate limit handling
- **WHEN** the Discogs API returns a 429 rate limit error
- **THEN** the script waits and retries the request
- **AND** respects the Retry-After header if provided

### Requirement: Transform and Save Album Data
The script SHALL transform Discogs API response into a simplified format and save as JSON.

#### Scenario: JSON file creation
- **WHEN** release data is successfully fetched
- **THEN** a JSON file is created at `.data/albums/{discogs_id}.json`
- **AND** the file contains the transformed album data

#### Scenario: Data transformation
- **WHEN** the release data is transformed
- **THEN** the output contains: id, cover (primary image), and sides with tracks
- **AND** each track has: position, artist, title, duration
- **AND** duration format is preserved as-is from Discogs

#### Scenario: Side grouping
- **WHEN** tracklist positions contain letters (A1, A2, B1, B2, etc.)
- **THEN** tracks are grouped into sides by the position letter
- **AND** each side has an `ind` field with the letter

#### Scenario: Artist resolution
- **WHEN** a track has its own artists array
- **THEN** use the first track artist name
- **OTHERWISE** use the first album artist name

#### Scenario: Missing duration warning
- **WHEN** any track has an empty or missing duration
- **THEN** the script prints a warning that durations need manual fill
- **AND** the track is still saved with empty duration

### Requirement: CLI Interface
The script SHALL accept a single search query argument.

#### Scenario: Basic usage
- **WHEN** the user runs `python app/discogs_download.py "query"`
- **THEN** the script searches Discogs and displays results for selection

#### Scenario: Missing arguments
- **WHEN** the user runs the script without any arguments
- **THEN** the script prints usage instructions
- **AND** exits with a non-zero status code

