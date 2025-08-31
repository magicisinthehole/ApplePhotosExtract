# Photos Library Package Analysis

## Overview

This document details the structure and organization of macOS Photos Library packages (`.photoslibrary`) and provides a roadmap for creating extraction tools to recover original filenames and metadata.

## Package Structure

```
Photos Library.photoslibrary/
├── database/           # SQLite databases containing all metadata
│   ├── Photos.sqlite   # Main database with asset records
│   ├── Photos.sqlite-shm
│   ├── Photos.sqlite-wal
│   ├── metaSchema.db
│   └── photos.db
├── originals/          # Original photo/video files
│   ├── 0/             # Files organized by first character of UUID
│   ├── 1/
│   ├── ...
│   ├── A/
│   ├── B/
│   └── F/
├── resources/          # Thumbnails and other resources
├── private/            # Additional processing files
├── external/           # External references
├── internal/           # Internal processing files
└── scopes/             # Library scope data
```

## Database Schema

### Key Tables

#### ZASSET
Primary table containing basic asset information:
- `Z_PK`: Primary key
- `ZUUID`: Unique identifier for the asset
- `ZFILENAME`: Internal filename (UUID + extension)
- `ZDIRECTORY`: Single hex character directory (0-9, A-F)
- `ZDATECREATED`: Creation timestamp
- `ZLATITUDE`, `ZLONGITUDE`: GPS coordinates
- `ZUNIFORMTYPEIDENTIFIER`: File type (e.g., public.jpeg)
- `ZWIDTH`, `ZHEIGHT`: Image dimensions

#### ZADDITIONALASSETATTRIBUTES
Extended metadata for assets:
- `ZASSET`: Foreign key to ZASSET table
- `ZORIGINALFILENAME`: **Original filename before import**
- `ZORIGINALFILESIZE`: Original file size
- `ZTITLE`: User-assigned title
- `ZIMPORTEDBY`: Import source
- `ZCAMERACAPTUREDEVICE`: Camera type indicator

#### ZEXTENDEDATTRIBUTES
EXIF and technical metadata:
- `ZASSET`: Foreign key to ZASSET table
- `ZCAMERAMAKE`, `ZCAMERAMODEL`: Camera information
- `ZFOCALLENGTH`, `ZAPERTURE`: Camera settings
- `ZISO`, `ZSHUTTERSPEED`: Exposure settings
- `ZLATITUDE`, `ZLONGITUDE`: GPS coordinates (duplicate)

## File Organization

### Storage Pattern
Files are stored using this pattern:
```
originals/{ZDIRECTORY}/{ZFILENAME}
```

**Example:**
- Database record: `ZDIRECTORY='E'`, `ZFILENAME='E8907267-1CAB-4476-8B6A-F3719E3A5CC3.jpeg'`
- Actual path: `originals/E/E8907267-1CAB-4476-8B6A-F3719E3A5CC3.jpeg`
- Original name: `View All Photos  Be prepared.jpg`

### Directory Distribution
Files are distributed across directories `0-9` and `A-F` based on the first character of their UUID filename.

## Data Relationships

### Core Join Query
```sql
SELECT 
    a.ZDIRECTORY || '/' || a.ZFILENAME as internal_path,
    aaa.ZORIGINALFILENAME as original_name,
    datetime(a.ZDATECREATED + 978307200, 'unixepoch') as created_date,
    a.ZLATITUDE, a.ZLONGITUDE,
    ext.ZCAMERAMAKE, ext.ZCAMERAMODEL,
    a.ZUNIFORMTYPEIDENTIFIER as file_type
FROM ZASSET a 
LEFT JOIN ZADDITIONALASSETATTRIBUTES aaa ON a.ZADDITIONALATTRIBUTES = aaa.Z_PK
LEFT JOIN ZEXTENDEDATTRIBUTES ext ON a.ZEXTENDEDATTRIBUTES = ext.Z_PK
WHERE a.ZTRASHEDSTATE = 0  -- Exclude deleted photos
```

**Note:** macOS timestamps use Core Data format (seconds since 2001-01-01). Add 978307200 to convert to Unix timestamp.

## Sample Data

| Internal Path | Original Filename | Camera | Created |
|---------------|------------------|---------|---------|
| E/E8907267-1CAB-4476-8B6A-F3719E3A5CC3.jpeg | View All Photos  Be prepared.jpg | - | 2010-08-27 |
| D/DBDD176E-4D44-4CC4-9557-1DD269C1F1DB.jpeg | IMG_4823.JPG | Canon EOS-1Ds Mark III | 2011-06-12 |

## Extraction Program Requirements

### Basic Algorithm
1. Connect to `Photos.sqlite` database
2. Query asset metadata using join across tables
3. For each asset:
   - Read file from `originals/{directory}/{uuid_filename}`
   - Extract original filename from database
   - Copy file to output directory with original name
   - Preserve timestamps and metadata

### Considerations
- **Filename collisions**: Handle duplicate original filenames
- **Missing metadata**: Some assets may lack original filenames
- **File types**: Support various formats (JPEG, HEIC, PNG, MOV, etc.)
- **Timestamps**: Convert Core Data timestamps correctly
- **Deleted photos**: Filter out trashed assets (`ZTRASHEDSTATE = 0`)

### Additional Metadata Available
- GPS coordinates
- Camera EXIF data
- Import session information
- User-assigned keywords and descriptions
- Face detection data (separate tables)
- Album associations

## Technical Notes

### Database Access
- SQLite database may be locked while Photos app is running
- Use read-only connections to avoid corruption
- Handle WAL (Write-Ahead Logging) files appropriately

### File Permissions
- Original files have restricted permissions (600)
- May require elevated permissions or ownership changes

### Completeness
This analysis covers the core structure needed for basic extraction. The Photos database contains additional tables for:
- Albums and collections
- Face recognition data
- Shared photo streams
- Cloud sync status
- Edit history

## Conclusion

Creating an extraction program is highly feasible. The Photos Library package maintains clear relationships between:
1. Internal UUID-based filenames in the filesystem
2. Original filenames in the database
3. Complete metadata including EXIF, GPS, and user data

A simple Python or shell script could effectively extract and reorganize photos with their original names and metadata preserved.