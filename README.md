# Photos Library Extractor

Extract photos and videos from Apple Photos Library with metadata-preserving XMP sidecars.

## Features

- Extract all photos/videos from Photos Library packages
- Generate XMP sidecars matching Apple's export format
- Flexible folder organization (year/month, year only, flat, year/month/day)
- Multiple filename formats with date prefixes
- Person tags from face detection
- GPS metadata including direction, altitude, speed
- Test mode (first 20 files only)

## Requirements

- macOS
- Python 3.7+
- exiftool: `brew install exiftool`
- tkinter: `brew install python-tk`

## Usage

```bash
python3 photo_extract_gui.py
```

1. Select Photos Library package
2. Choose destination folder  
3. Configure folder structure and filenames
4. Enable test mode for validation
5. Click Extract Photos

## XMP Metadata

- GPS coordinates with precision
- Person names from face detection
- Creation dates with timezones
- EXIF GPS data (direction, altitude, speed)
- Apple Photos compatible format

## Safety

Read-only operation. Never modifies original Photos Library.