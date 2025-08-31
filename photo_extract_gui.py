#!/usr/bin/env python3

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import sqlite3
import subprocess
import json
from datetime import datetime
from pathlib import Path
import threading

class PhotoExtractGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Photos Library Extractor")
        self.root.geometry("600x650")
        
        # Variables
        self.library_path = tk.StringVar()
        self.destination_path = tk.StringVar()
        self.folder_structure = tk.StringVar(value="year_month")
        self.filename_format = tk.StringVar(value="date_original")
        self.include_xmp = tk.BooleanVar(value=True)
        self.include_keywords = tk.BooleanVar(value=True)
        self.include_person_tags = tk.BooleanVar(value=True)
        
        self.create_widgets()
        
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        row = 0
        
        # Library selection
        ttk.Label(main_frame, text="Photos Library:").grid(row=row, column=0, sticky=tk.W, pady=(0, 5))
        ttk.Entry(main_frame, textvariable=self.library_path, width=50).grid(row=row, column=1, sticky=(tk.W, tk.E), padx=(10, 5), pady=(0, 5))
        ttk.Button(main_frame, text="Browse", command=self.browse_library).grid(row=row, column=2, pady=(0, 5))
        row += 1
        
        # Destination selection
        ttk.Label(main_frame, text="Destination:").grid(row=row, column=0, sticky=tk.W, pady=(0, 5))
        ttk.Entry(main_frame, textvariable=self.destination_path, width=50).grid(row=row, column=1, sticky=(tk.W, tk.E), padx=(10, 5), pady=(0, 5))
        ttk.Button(main_frame, text="Browse", command=self.browse_destination).grid(row=row, column=2, pady=(0, 5))
        row += 1
        
        # Separator
        ttk.Separator(main_frame, orient='horizontal').grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=15)
        row += 1
        
        # Folder structure options
        ttk.Label(main_frame, text="Folder Structure:", font=('TkDefaultFont', 10, 'bold')).grid(row=row, column=0, columnspan=3, sticky=tk.W, pady=(0, 10))
        row += 1
        
        folder_frame = ttk.Frame(main_frame)
        folder_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Radiobutton(folder_frame, text="Year/Month (2024/01)", variable=self.folder_structure, value="year_month").pack(anchor=tk.W)
        ttk.Radiobutton(folder_frame, text="Year only (2024)", variable=self.folder_structure, value="year_only").pack(anchor=tk.W)
        ttk.Radiobutton(folder_frame, text="Flat (no subfolders)", variable=self.folder_structure, value="flat").pack(anchor=tk.W)
        ttk.Radiobutton(folder_frame, text="Year/Month/Day (2024/01/15)", variable=self.folder_structure, value="year_month_day").pack(anchor=tk.W)
        row += 1
        
        # Filename format options
        ttk.Label(main_frame, text="Filename Format:", font=('TkDefaultFont', 10, 'bold')).grid(row=row, column=0, columnspan=3, sticky=tk.W, pady=(10, 10))
        row += 1
        
        filename_frame = ttk.Frame(main_frame)
        filename_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Radiobutton(filename_frame, text="Date + Original (20240115_IMG_1234.jpg)", variable=self.filename_format, value="date_original").pack(anchor=tk.W)
        ttk.Radiobutton(filename_frame, text="Original filename only (IMG_1234.jpg)", variable=self.filename_format, value="original_only").pack(anchor=tk.W)
        ttk.Radiobutton(filename_frame, text="Date only (20240115_143022.jpg)", variable=self.filename_format, value="date_only").pack(anchor=tk.W)
        ttk.Radiobutton(filename_frame, text="Date + Time + Original (20240115_143022_IMG_1234.jpg)", variable=self.filename_format, value="datetime_original").pack(anchor=tk.W)
        row += 1
        
        # Separator
        ttk.Separator(main_frame, orient='horizontal').grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=15)
        row += 1
        
        # Metadata options
        ttk.Label(main_frame, text="Metadata Options:", font=('TkDefaultFont', 10, 'bold')).grid(row=row, column=0, columnspan=3, sticky=tk.W, pady=(0, 10))
        row += 1
        
        metadata_frame = ttk.Frame(main_frame)
        metadata_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Checkbutton(metadata_frame, text="Include XMP sidecar files", variable=self.include_xmp).pack(anchor=tk.W)
        ttk.Checkbutton(metadata_frame, text="Include keywords in XMP", variable=self.include_keywords).pack(anchor=tk.W)
        ttk.Checkbutton(metadata_frame, text="Include person tags in XMP", variable=self.include_person_tags).pack(anchor=tk.W)
        
        # Test mode option
        self.test_mode = tk.BooleanVar(value=False)
        ttk.Checkbutton(metadata_frame, text="Test mode (first 20 files only)", variable=self.test_mode).pack(anchor=tk.W)
        row += 1
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(20, 5))
        row += 1
        
        # Status label
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(main_frame, textvariable=self.status_var).grid(row=row, column=0, columnspan=3, sticky=tk.W, pady=(0, 10))
        row += 1
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=row, column=0, columnspan=3, pady=20)
        
        self.extract_button = ttk.Button(button_frame, text="Extract Photos", command=self.start_extraction)
        self.extract_button.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="Exit", command=self.root.quit).pack(side=tk.LEFT)
        
    def browse_library(self):
        library_path = filedialog.askopenfilename(
            title="Select Photos Library Package",
            filetypes=[("All files", "*.*")]
        )
        if library_path:
            self.library_path.set(library_path)
            
    def browse_destination(self):
        destination_path = filedialog.askdirectory(
            title="Select Destination Folder"
        )
        if destination_path:
            self.destination_path.set(destination_path)
            
    def validate_inputs(self):
        if not self.library_path.get():
            messagebox.showerror("Missing Input", "Please select a Photos Library")
            return False
            
        if not self.destination_path.get():
            messagebox.showerror("Missing Input", "Please select a destination folder")
            return False
            
        if not os.path.exists(self.library_path.get()):
            messagebox.showerror("Invalid Path", "Photos Library path does not exist")
            return False
            
        if not os.path.exists(self.destination_path.get()):
            messagebox.showerror("Invalid Path", "Destination path does not exist")
            return False
            
        # Check if library contains Photos.sqlite
        db_path = os.path.join(self.library_path.get(), "database", "Photos.sqlite")
        if not os.path.exists(db_path):
            messagebox.showerror("Invalid Library", "Selected library does not contain Photos.sqlite database")
            return False
            
        return True
        
    def start_extraction(self):
        if not self.validate_inputs():
            return
            
        # Disable the extract button during processing
        self.extract_button.configure(state='disabled')
        self.status_var.set("Starting extraction...")
        self.progress_var.set(0)
        
        # Start extraction in a separate thread
        extraction_thread = threading.Thread(target=self.run_extraction)
        extraction_thread.daemon = True
        extraction_thread.start()
        
    def run_extraction(self):
        try:
            self.extract_photos()
        except Exception as e:
            messagebox.showerror("Extraction Error", f"An error occurred during extraction:\n{str(e)}")
        finally:
            # Re-enable the extract button
            self.extract_button.configure(state='normal')
            self.status_var.set("Ready")
            self.progress_var.set(0)
            
    def get_folder_path(self, creation_date):
        """Generate folder path based on selected structure"""
        if self.folder_structure.get() == "flat":
            return ""
        elif self.folder_structure.get() == "year_only":
            return str(creation_date.year)
        elif self.folder_structure.get() == "year_month":
            return f"{creation_date.year}/{creation_date.month:02d}"
        elif self.folder_structure.get() == "year_month_day":
            return f"{creation_date.year}/{creation_date.month:02d}/{creation_date.day:02d}"
        return ""
        
    def get_filename(self, original_filename, creation_date):
        """Generate filename based on selected format"""
        base_name, ext = os.path.splitext(original_filename)
        date_str = creation_date.strftime("%Y%m%d")
        datetime_str = creation_date.strftime("%Y%m%d_%H%M%S")
        
        if self.filename_format.get() == "original_only":
            return original_filename
        elif self.filename_format.get() == "date_only":
            return f"{datetime_str}{ext}"
        elif self.filename_format.get() == "date_original":
            return f"{date_str}_{original_filename}"
        elif self.filename_format.get() == "datetime_original":
            return f"{datetime_str}_{original_filename}"
        return original_filename
        
    def extract_photos(self):
        library_path = self.library_path.get()
        destination_path = self.destination_path.get()
        
        db_path = os.path.join(library_path, "database", "Photos.sqlite")
        originals_path = os.path.join(library_path, "originals")
        
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get total count for progress tracking
        cursor.execute("SELECT COUNT(*) FROM ZASSET WHERE ZTRASHEDSTATE = 0")
        total_assets = cursor.fetchone()[0]
        
        self.root.after(0, lambda: self.status_var.set(f"Found {total_assets} assets to extract"))
        
        # Query all assets (using exact query structure from working version)
        query = """
        SELECT 
            a.ZUUID, 
            a.ZFILENAME, 
            a.ZDIRECTORY,
            aaa.ZORIGINALFILENAME,
            a.ZDATECREATED,
            a.ZLATITUDE, 
            a.ZLONGITUDE,
            ext.ZCAMERAMAKE,
            ext.ZCAMERAMODEL,
            ext.ZFOCALLENGTH,
            ext.ZAPERTURE,
            ext.ZISO,
            ext.ZSHUTTERSPEED,
            ext.ZFLASHFIRED,
            ext.ZLATITUDE as ext_lat,
            ext.ZLONGITUDE as ext_lon,
            ext.ZTIMEZONEOFFSET,
            ext.ZTIMEZONENAME
        FROM ZASSET a 
        LEFT JOIN ZADDITIONALASSETATTRIBUTES aaa ON a.ZADDITIONALATTRIBUTES = aaa.Z_PK 
        LEFT JOIN ZEXTENDEDATTRIBUTES ext ON a.ZEXTENDEDATTRIBUTES = ext.Z_PK
        WHERE a.ZTRASHEDSTATE = 0
        ORDER BY a.ZDATECREATED
        """
        
        cursor.execute(query)
        all_assets = cursor.fetchall()
        
        # Limit to first 20 files in test mode
        if self.test_mode.get():
            assets = all_assets[:20]
            self.root.after(0, lambda: self.status_var.set(f"Test mode: Processing first 20 of {len(all_assets)} assets"))
        else:
            assets = all_assets
        
        processed = 0
        successful = 0
        
        for asset in assets:
            # Unpack all metadata fields exactly like working version
            uuid, filename, directory, original_filename, date_created, lat, lon, make, model, focal_length, aperture, iso, shutter_speed, flash_fired, ext_lat, ext_lon, timezone_offset, timezone_name = asset
            
            # Use original filename if available, otherwise use filename
            if not original_filename:
                original_filename = filename
                
            # Convert Core Data timestamp to datetime
            if not date_created:
                continue
                
            creation_date = datetime.fromtimestamp(date_created + 978307200)
                
            # Update progress
            processed += 1
            progress = (processed / len(assets)) * 100
            self.root.after(0, lambda p=progress: self.progress_var.set(p))
            self.root.after(0, lambda f=original_filename: self.status_var.set(f"Processing: {f}"))
            
            # Find original file using directory path from database
            original_file = os.path.join(originals_path, directory, filename)
            
            if not os.path.exists(original_file):
                continue
                
            # Generate destination paths
            folder_path = self.get_folder_path(creation_date)
            new_filename = self.get_filename(original_filename, creation_date)
            
            # Create destination directory
            if folder_path:
                dest_dir = os.path.join(destination_path, folder_path)
                os.makedirs(dest_dir, exist_ok=True)
            else:
                dest_dir = destination_path
                
            dest_file = os.path.join(dest_dir, new_filename)
            
            # Copy original file
            try:
                import shutil
                shutil.copy2(original_file, dest_file)
                successful += 1
                
                # Generate XMP if requested
                if self.include_xmp.get():
                    # Get keywords exactly like working version
                    keywords = self.get_asset_keywords(uuid, conn)
                    self.generate_xmp_file(dest_file, asset, keywords, conn)
                    
            except Exception as e:
                print(f"Error copying {original_filename}: {e}")
                continue
                
        conn.close()
        
        # Show completion message
        self.root.after(0, lambda: messagebox.showinfo(
            "Extraction Complete", 
            f"Successfully extracted {successful} out of {total_assets} photos"
        ))
        
    def generate_xmp_file(self, image_path, asset_data, keywords, conn):
        """Generate XMP sidecar matching Apple Photos format exactly like working version"""
        try:
            # Unpack all metadata exactly like working version
            uuid, filename, directory, original_filename, date_created, lat, lon, make, model, focal_length, aperture, iso, shutter_speed, flash_fired, ext_lat, ext_lon, timezone_offset, timezone_name = asset_data
            
            # Use extended attributes coordinates if available (higher precision)
            if ext_lat is not None and ext_lon is not None:
                lat, lon = ext_lat, ext_lon
            
            # Create XMP sidecar using exact logic from working version
            xmp_path = os.path.splitext(image_path)[0] + ".xmp"
            self.create_xmp_sidecar(asset_data, keywords, xmp_path, image_path)
                
        except Exception as e:
            print(f"Error generating XMP for {original_filename}: {e}")
            
    def get_asset_keywords(self, uuid, conn):
        """Get keywords/tags and person names for an asset exactly like working version"""
        # Get regular keywords
        keyword_query = """
        SELECT k.ZTITLE
        FROM ZASSET a 
        LEFT JOIN ZADDITIONALASSETATTRIBUTES aaa ON a.ZADDITIONALATTRIBUTES = aaa.Z_PK 
        LEFT JOIN Z_1KEYWORDS z1k ON aaa.Z_PK = z1k.Z_1ASSETATTRIBUTES 
        LEFT JOIN ZKEYWORD k ON z1k.Z_51KEYWORDS = k.Z_PK 
        WHERE a.ZUUID = ? AND k.ZTITLE IS NOT NULL
        """
        
        # Get person names
        person_query = """
        SELECT DISTINCT p.ZDISPLAYNAME
        FROM ZASSET a 
        LEFT JOIN ZDETECTEDFACE df ON a.Z_PK = df.ZASSETFORFACE
        LEFT JOIN ZPERSON p ON df.ZPERSONFORFACE = p.Z_PK
        WHERE a.ZUUID = ? AND p.ZDISPLAYNAME IS NOT NULL AND p.ZDISPLAYNAME != ''
        """
        
        cursor = conn.cursor()
        
        # Get keywords
        cursor.execute(keyword_query, (uuid,))
        keywords = [row[0] for row in cursor.fetchall()]
        
        # Get person names
        cursor.execute(person_query, (uuid,))
        people = [row[0] for row in cursor.fetchall()]
        
        # Combine all tags
        return keywords + people
            
    def core_data_to_datetime(self, timestamp, timezone_offset=None):
        """Convert Core Data timestamp to ISO format with proper timezone from database"""
        if not timestamp or timestamp == 0:
            return None
        # Core Data epoch is 2001-01-01, Unix epoch is 1970-01-01
        # Difference is 978307200 seconds
        unix_timestamp = timestamp + 978307200
        dt = datetime.fromtimestamp(unix_timestamp)
        
        # Use timezone offset from database if available
        if timezone_offset is not None:
            try:
                # Convert seconds to hours
                tz_hours = int(timezone_offset) / 3600
                tz_sign = '+' if tz_hours >= 0 else '-'
                tz_formatted = f'{tz_sign}{abs(int(tz_hours)):02d}:00'
            except (ValueError, TypeError):
                return None  # Unable to process timezone
        else:
            # No timezone data available
            return None
        
        return dt.strftime(f'%Y-%m-%dT%H:%M:%S{tz_formatted}')
            
    def extract_exif_data(self, image_path):
        """Extract EXIF data using exiftool with individual field extraction"""
        exif_data = {}
        
        try:
            # GPS Direction
            result = subprocess.run(['exiftool', '-n', '-s', '-s', '-s', '-GPSImgDirection', image_path], 
                                   capture_output=True, text=True)
            if result.returncode == 0 and result.stdout.strip():
                try:
                    exif_data['gps_direction'] = float(result.stdout.strip())
                except ValueError:
                    pass
                    
            # GPS Direction Reference
            result = subprocess.run(['exiftool', '-s', '-s', '-s', '-GPSImgDirectionRef', image_path], 
                                   capture_output=True, text=True)
            if result.returncode == 0 and result.stdout.strip():
                ref_value = result.stdout.strip()
                if ref_value in ['T', 'M']:
                    exif_data['gps_direction_ref'] = ref_value
                    
            # GPS Altitude
            result = subprocess.run(['exiftool', '-n', '-s', '-s', '-s', '-GPSAltitude', image_path], 
                                   capture_output=True, text=True)
            if result.returncode == 0 and result.stdout.strip():
                try:
                    exif_data['gps_altitude'] = float(result.stdout.strip())
                except ValueError:
                    pass
                    
            # GPS Altitude Reference
            result = subprocess.run(['exiftool', '-s', '-s', '-s', '-GPSAltitudeRef', image_path], 
                                   capture_output=True, text=True)
            if result.returncode == 0 and result.stdout.strip():
                ref_value = result.stdout.strip()
                if 'Above Sea Level' in ref_value or ref_value == '0':
                    exif_data['gps_altitude_ref'] = '0'
                elif 'Below Sea Level' in ref_value or ref_value == '1':
                    exif_data['gps_altitude_ref'] = '1'
                    
            # GPS Speed
            result = subprocess.run(['exiftool', '-n', '-s', '-s', '-s', '-GPSSpeed', image_path], 
                                   capture_output=True, text=True)
            if result.returncode == 0 and result.stdout.strip():
                try:
                    exif_data['gps_speed'] = float(result.stdout.strip())
                except ValueError:
                    pass
                    
            # GPS Speed Reference
            result = subprocess.run(['exiftool', '-s', '-s', '-s', '-GPSSpeedRef', image_path], 
                                   capture_output=True, text=True)
            if result.returncode == 0 and result.stdout.strip():
                ref_value = result.stdout.strip()
                if ref_value in ['K', 'M', 'N']:
                    exif_data['gps_speed_ref'] = ref_value
                    
            # GPS TimeStamp - extract and format to Apple's format
            result_time = subprocess.run(['exiftool', '-s', '-s', '-s', '-GPSTimeStamp', image_path], 
                                        capture_output=True, text=True)
            result_date = subprocess.run(['exiftool', '-s', '-s', '-s', '-GPSDateStamp', image_path], 
                                        capture_output=True, text=True)
            
            if result_time.returncode == 0 and result_time.stdout.strip():
                time_val = result_time.stdout.strip()
                if result_date.returncode == 0 and result_date.stdout.strip():
                    date_val = result_date.stdout.strip()
                    try:
                        # Parse date like "2025:07:29" and time like "18:48:59"
                        date_parts = date_val.split(':')
                        if len(date_parts) == 3 and len(time_val.split(':')) >= 2:
                            exif_data['gps_time_stamp'] = f"{date_parts[0]}-{date_parts[1]}-{date_parts[2]}T{time_val}Z"
                        else:
                            exif_data['gps_time_stamp'] = time_val
                    except:
                        exif_data['gps_time_stamp'] = time_val
                else:
                    exif_data['gps_time_stamp'] = time_val
                    
        except Exception:
            pass
            
        return exif_data
        
    def create_xmp_sidecar(self, metadata, keywords, output_path, original_file_path):
        """Generate XMP sidecar matching Apple Photos format - exact copy from working version"""
        
        uuid, filename, directory, original_filename, date_created, lat, lon, make, model, focal_length, aperture, iso, shutter_speed, flash_fired, ext_lat, ext_lon, timezone_offset, timezone_name = metadata
        
        # Use extended attributes coordinates if available (higher precision)
        if ext_lat is not None and ext_lon is not None:
            lat, lon = ext_lat, ext_lon
        
        # Extract GPS data from EXIF using individual field calls for accuracy
        import subprocess
        
        gps_positioning_error = None
        gps_direction = None
        gps_direction_ref = None
        gps_altitude = None
        gps_altitude_ref = None
        gps_speed = None
        gps_speed_ref = None
        gps_time_stamp = None
        
        try:
            # GPSHPositioningError - extract if available
            result_pos_error = subprocess.run(['exiftool', '-n', '-s', '-s', '-s', '-GPSHPositioningError', original_file_path], 
                                             capture_output=True, text=True)
            if result_pos_error.returncode == 0 and result_pos_error.stdout.strip():
                try:
                    gps_positioning_error = float(result_pos_error.stdout.strip())
                except ValueError:
                    pass
            
            # GPS Direction (use Dest Bearing when different from Img Direction)
            result_img_dir = subprocess.run(['exiftool', '-n', '-s', '-s', '-s', '-GPSImgDirection', original_file_path], 
                                           capture_output=True, text=True)
            result_dest_bearing = subprocess.run(['exiftool', '-n', '-s', '-s', '-s', '-GPSDestBearing', original_file_path], 
                                                capture_output=True, text=True)
            
            gps_img_direction = None
            gps_dest_bearing = None
            
            if result_img_dir.returncode == 0 and result_img_dir.stdout.strip():
                try:
                    gps_img_direction = float(result_img_dir.stdout.strip())
                except ValueError:
                    pass
                    
            if result_dest_bearing.returncode == 0 and result_dest_bearing.stdout.strip():
                try:
                    gps_dest_bearing = float(result_dest_bearing.stdout.strip())
                except ValueError:
                    pass
            
            # Choose direction based on Apple's logic - use dest bearing when significantly different
            if gps_img_direction is not None and gps_dest_bearing is not None:
                if abs(gps_img_direction - gps_dest_bearing) > 10:
                    gps_direction = gps_dest_bearing
                else:
                    gps_direction = gps_img_direction
            elif gps_img_direction is not None:
                gps_direction = gps_img_direction
            elif gps_dest_bearing is not None:
                gps_direction = gps_dest_bearing
                
            # GPS Direction Reference
            result_dir_ref = subprocess.run(['exiftool', '-s', '-s', '-s', '-GPSImgDirectionRef', original_file_path], 
                                           capture_output=True, text=True)
            if result_dir_ref.returncode == 0 and result_dir_ref.stdout.strip():
                ref_value = result_dir_ref.stdout.strip()
                if 'True North' in ref_value or ref_value == 'T':
                    gps_direction_ref = 'T'
                    
            # GPS Altitude
            result_alt = subprocess.run(['exiftool', '-n', '-s', '-s', '-s', '-GPSAltitude', original_file_path], 
                                       capture_output=True, text=True)
            if result_alt.returncode == 0 and result_alt.stdout.strip():
                try:
                    gps_altitude = float(result_alt.stdout.strip())
                except ValueError:
                    pass
                    
            # GPS Altitude Reference
            result_alt_ref = subprocess.run(['exiftool', '-s', '-s', '-s', '-GPSAltitudeRef', original_file_path], 
                                           capture_output=True, text=True)
            if result_alt_ref.returncode == 0 and result_alt_ref.stdout.strip():
                ref_value = result_alt_ref.stdout.strip()
                if 'Above Sea Level' in ref_value or ref_value == '0':
                    gps_altitude_ref = '0'
                elif 'Below Sea Level' in ref_value or ref_value == '1':
                    gps_altitude_ref = '1'
                    
            # GPS Speed
            result_speed = subprocess.run(['exiftool', '-n', '-s', '-s', '-s', '-GPSSpeed', original_file_path], 
                                         capture_output=True, text=True)
            if result_speed.returncode == 0 and result_speed.stdout.strip():
                try:
                    gps_speed = float(result_speed.stdout.strip())
                except ValueError:
                    pass
                    
            # GPS Speed Reference
            result_speed_ref = subprocess.run(['exiftool', '-s', '-s', '-s', '-GPSSpeedRef', original_file_path], 
                                             capture_output=True, text=True)
            if result_speed_ref.returncode == 0 and result_speed_ref.stdout.strip():
                ref_value = result_speed_ref.stdout.strip()
                if ref_value in ['K', 'M', 'N']:
                    gps_speed_ref = ref_value
                    
            # GPS TimeStamp - extract and format to Apple's format
            result_time = subprocess.run(['exiftool', '-s', '-s', '-s', '-GPSTimeStamp', original_file_path], 
                                        capture_output=True, text=True)
            result_date = subprocess.run(['exiftool', '-s', '-s', '-s', '-GPSDateStamp', original_file_path], 
                                        capture_output=True, text=True)
            
            if result_time.returncode == 0 and result_time.stdout.strip():
                time_val = result_time.stdout.strip()
                if result_date.returncode == 0 and result_date.stdout.strip():
                    date_val = result_date.stdout.strip()
                    # Convert to Apple's format: YYYY-MM-DDTHH:MM:SSZ
                    try:
                        # Parse date like "2025:07:29" and time like "18:48:59"
                        date_parts = date_val.split(':')
                        if len(date_parts) == 3 and len(time_val.split(':')) >= 2:
                            gps_time_stamp = f"{date_parts[0]}-{date_parts[1]}-{date_parts[2]}T{time_val}Z"
                        else:
                            gps_time_stamp = time_val
                    except:
                        gps_time_stamp = time_val
                else:
                    gps_time_stamp = time_val
                
        except Exception:
            pass
        
        # Check if we have GPS data to determine namespaces
        has_gps_data = (lat and lon and lat != -180.0 and lon != -180.0) or gps_direction or gps_altitude or gps_speed
        
        # Create XMP with proper namespaces to match Apple format
        xmp_content = '''<x:xmpmeta xmlns:x="adobe:ns:meta/" x:xmptk="XMP Core 6.0.0">
   <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
      <rdf:Description rdf:about=""'''
        
        # Add namespaces in Apple's order: dc first if present, then exif, then photoshop
        if keywords:
            xmp_content += '\n            xmlns:dc="http://purl.org/dc/elements/1.1/"'
        if has_gps_data:
            xmp_content += '\n            xmlns:exif="http://ns.adobe.com/exif/1.0/"'
        if date_created:
            xmp_content += '\n            xmlns:photoshop="http://ns.adobe.com/photoshop/1.0/"'
        
        xmp_content += '>\n'
        
        # Add GPS data in Apple's exact order (only if we have GPS coordinates)
        if lat and lon and lat != -180.0 and lon != -180.0:
            # Check if we should include GPS direction/speed (Apple includes as 0.0 when GPS data exists)
            include_direction = gps_direction is not None
            include_speed = gps_speed is not None
            
            # If no EXIF direction/speed but GPS data exists, Apple includes 0.0 values
            if not include_direction and (gps_altitude is not None):
                include_direction = True
                gps_direction = 0.0
                gps_direction_ref = 'T'
                
            if not include_speed and (gps_altitude is not None):
                include_speed = True
                gps_speed = 0.0
                gps_speed_ref = 'K'
            
            if include_direction:
                # Order for files WITH direction data
                xmp_content += f'         <exif:GPSImgDirection>{gps_direction}</exif:GPSImgDirection>\n'
                if gps_altitude_ref:
                    xmp_content += f'         <exif:GPSAltitudeRef>{gps_altitude_ref}</exif:GPSAltitudeRef>\n'
                if gps_altitude is not None:
                    xmp_content += f'         <exif:GPSAltitude>{gps_altitude}</exif:GPSAltitude>\n'
                xmp_content += f'         <exif:GPSLatitudeRef>{"N" if lat >= 0 else "S"}</exif:GPSLatitudeRef>\n'
                xmp_content += f'         <exif:GPSLatitude>{abs(lat)}</exif:GPSLatitude>\n'
                xmp_content += f'         <exif:GPSLongitudeRef>{"W" if lon < 0 else "E"}</exif:GPSLongitudeRef>\n'
                if gps_direction_ref:
                    xmp_content += f'         <exif:GPSImgDirectionRef>{gps_direction_ref}</exif:GPSImgDirectionRef>\n'
                xmp_content += f'         <exif:GPSLongitude>{abs(lon)}</exif:GPSLongitude>\n'
                if include_speed:
                    xmp_content += f'         <exif:GPSSpeed>{gps_speed}</exif:GPSSpeed>\n'
                    if gps_speed_ref:
                        xmp_content += f'         <exif:GPSSpeedRef>{gps_speed_ref}</exif:GPSSpeedRef>\n'
                if gps_time_stamp:
                    xmp_content += f'         <exif:GPSTimeStamp>{gps_time_stamp}</exif:GPSTimeStamp>\n'
            else:
                # Order for files WITHOUT direction data (like MOV files)
                xmp_content += f'         <exif:GPSLongitude>{abs(lon)}</exif:GPSLongitude>\n'
                xmp_content += f'         <exif:GPSLongitudeRef>{"W" if lon < 0 else "E"}</exif:GPSLongitudeRef>\n'
                xmp_content += f'         <exif:GPSLatitudeRef>{"N" if lat >= 0 else "S"}</exif:GPSLatitudeRef>\n'
                if gps_altitude_ref:
                    xmp_content += f'         <exif:GPSAltitudeRef>{gps_altitude_ref}</exif:GPSAltitudeRef>\n'
                xmp_content += '         <exif:GPSHPositioningError>0.0</exif:GPSHPositioningError>\n'
                xmp_content += f'         <exif:GPSLatitude>{abs(lat)}</exif:GPSLatitude>\n'
                if gps_time_stamp:
                    xmp_content += f'         <exif:GPSTimeStamp>{gps_time_stamp}</exif:GPSTimeStamp>\n'
                if gps_altitude is not None:
                    xmp_content += f'         <exif:GPSAltitude>{gps_altitude}</exif:GPSAltitude>\n'
        
        # Add content in Apple's order: dc:subject first, then DateCreated
        if keywords:
            xmp_content += '         <dc:subject>\n'
            xmp_content += '            <rdf:Seq>\n'
            for keyword in keywords:
                xmp_content += f'               <rdf:li>{keyword}</rdf:li>\n'
            xmp_content += '            </rdf:Seq>\n'
            xmp_content += '         </dc:subject>\n'
        
        # Add creation date
        if date_created:
            formatted_date = self.core_data_to_datetime(date_created, timezone_offset)
            if formatted_date:
                xmp_content += f'         <photoshop:DateCreated>{formatted_date}</photoshop:DateCreated>\n'
        
        xmp_content += '''      </rdf:Description>
   </rdf:RDF>
</x:xmpmeta>
'''
        
        # Write XMP file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(xmp_content)

def main():
    root = tk.Tk()
    app = PhotoExtractGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()