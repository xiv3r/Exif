#!/usr/bin/env python3
"""
Metadata Aggregator - Batch processing and collection of metadata from multiple files.

This module provides the MetadataAggregator class for scanning directories,
processing multiple files, and extracting metadata efficiently.
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Optional, Any, Callable
from datetime import datetime
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import magic
import json

# Import existing extractors
from PIL import Image
from PIL.ExifTags import GPSTAGS, TAGS
import exifread
import eyed3

try:
    import moviepy.editor as mp
except ImportError:
    mp = None

try:
    import pdfplumber
except ImportError:
    pdfplumber = None

try:
    from docx import Document as DocxDocument
except ImportError:
    DocxDocument = None

from .data_models import (
    FileMetadata, ImageMetadata, VideoMetadata, 
    AudioMetadata, DocumentMetadata, GPSCoordinates,
    BatchProcessResult
)


class MetadataAggregator:
    """
    Aggregates metadata from multiple files across different formats.
    
    Supports:
    - Images: JPG, JPEG, PNG, GIF, BMP, TIFF
    - Videos: MP4, AVI, MOV, MKV, WMV
    - Audio: MP3, WAV, FLAC, AAC, OGG
    - Documents: PDF, DOCX
    """
    
    SUPPORTED_EXTENSIONS = {
        'image': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif'],
        'video': ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm'],
        'audio': ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a', '.wma'],
        'document': ['.pdf', '.docx']
    }
    
    def __init__(self, verbose: bool = True):
        """
        Initialize the MetadataAggregator.
        
        Args:
            verbose: Whether to print progress information
        """
        self.verbose = verbose
        self.mime = magic.Magic(mime=True)
        self.results: List[Dict[str, Any]] = []
        self.errors: List[Dict[str, str]] = []
        self._progress_callback: Optional[Callable] = None
        
    def scan_directory(
        self, 
        path: str, 
        recursive: bool = True,
        file_types: Optional[List[str]] = None
    ) -> List[str]:
        """
        Scan directory for supported files.
        
        Args:
            path: Directory path to scan
            recursive: Whether to scan subdirectories
            file_types: List of file types to include (e.g., ['image', 'video'])
        
        Returns:
            List of file paths
        """
        path_obj = Path(path)
        
        if not path_obj.exists():
            raise ValueError(f"Path does not exist: {path}")
        
        if not path_obj.is_dir():
            raise ValueError(f"Path is not a directory: {path}")
        
        # Determine which extensions to look for
        extensions = []
        if file_types is None:
            # Include all supported types
            for exts in self.SUPPORTED_EXTENSIONS.values():
                extensions.extend(exts)
        else:
            for ft in file_types:
                if ft in self.SUPPORTED_EXTENSIONS:
                    extensions.extend(self.SUPPORTED_EXTENSIONS[ft])
        
        # Scan for files
        files = []
        if recursive:
            for ext in extensions:
                files.extend(path_obj.rglob(f"*{ext}"))
                files.extend(path_obj.rglob(f"*{ext.upper()}"))
        else:
            for ext in extensions:
                files.extend(path_obj.glob(f"*{ext}"))
                files.extend(path_obj.glob(f"*{ext.upper()}"))
        
        # Convert to strings and remove duplicates
        file_paths = sorted(list(set(str(f) for f in files)))
        
        if self.verbose:
            print(f"Found {len(file_paths)} files in {path}")
        
        return file_paths
    
    def detect_file_type(self, file_path: str) -> str:
        """
        Detect file type based on extension and MIME type.
        
        Args:
            file_path: Path to file
        
        Returns:
            File type ('image', 'video', 'audio', 'document', 'unknown')
        """
        ext = Path(file_path).suffix.lower()
        
        for file_type, extensions in self.SUPPORTED_EXTENSIONS.items():
            if ext in extensions:
                return file_type
        
        return 'unknown'
    
    def process_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Process a single file and extract metadata.
        
        Args:
            file_path: Path to file
        
        Returns:
            Dictionary with metadata or None if failed
        """
        try:
            file_type = self.detect_file_type(file_path)
            
            if file_type == 'image':
                return self._process_image(file_path)
            elif file_type == 'video':
                return self._process_video(file_path)
            elif file_type == 'audio':
                return self._process_audio(file_path)
            elif file_type == 'document':
                return self._process_document(file_path)
            else:
                return self._process_generic(file_path)
                
        except Exception as e:
            self.errors.append({
                'file': file_path,
                'error': str(e),
                'type': 'processing_error'
            })
            if self.verbose:
                print(f"Error processing {file_path}: {e}")
            return None
    
    def _process_image(self, file_path: str) -> Dict[str, Any]:
        """Extract metadata from image file."""
        metadata = {
            'file_path': file_path,
            'file_name': os.path.basename(file_path),
            'file_type': 'image',
            'file_size': os.path.getsize(file_path),
            'mime_type': self.mime.from_file(file_path),
            'created_date': datetime.fromtimestamp(os.path.getctime(file_path)),
            'modified_date': datetime.fromtimestamp(os.path.getmtime(file_path)),
        }
        
        # Extract EXIF data
        try:
            with open(file_path, 'rb') as f:
                tags = exifread.process_file(f, details=False)
                
                # Basic image info
                if 'Image ImageWidth' in tags:
                    metadata['width'] = int(str(tags['Image ImageWidth']))
                if 'Image ImageLength' in tags:
                    metadata['height'] = int(str(tags['Image ImageLength']))
                
                # Camera info
                if 'Image Make' in tags:
                    metadata['camera_make'] = str(tags['Image Make']).strip()
                if 'Image Model' in tags:
                    metadata['camera_model'] = str(tags['Image Model']).strip()
                if 'EXIF LensModel' in tags:
                    metadata['lens_model'] = str(tags['EXIF LensModel']).strip()
                
                # Camera settings
                if 'EXIF FocalLength' in tags:
                    focal = tags['EXIF FocalLength']
                    metadata['focal_length'] = float(focal.values[0].num) / float(focal.values[0].den)
                if 'EXIF FNumber' in tags:
                    fnum = tags['EXIF FNumber']
                    metadata['aperture'] = float(fnum.values[0].num) / float(fnum.values[0].den)
                if 'EXIF ExposureTime' in tags:
                    metadata['shutter_speed'] = str(tags['EXIF ExposureTime'])
                if 'EXIF ISOSpeedRatings' in tags:
                    metadata['iso'] = int(str(tags['EXIF ISOSpeedRatings']))
                
                # Date taken
                if 'EXIF DateTimeOriginal' in tags:
                    date_str = str(tags['EXIF DateTimeOriginal'])
                    try:
                        metadata['date_taken'] = datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S')
                    except:
                        pass
                
                # GPS data
                gps_data = self._extract_gps_from_tags(tags)
                if gps_data:
                    metadata['gps_coordinates'] = gps_data
                
        except Exception as e:
            if self.verbose:
                print(f"Warning: Could not extract EXIF from {file_path}: {e}")
        
        # Get basic image info with PIL
        try:
            with Image.open(file_path) as img:
                if 'width' not in metadata:
                    metadata['width'] = img.width
                if 'height' not in metadata:
                    metadata['height'] = img.height
                metadata['format'] = img.format
        except:
            pass
        
        return metadata
    
    def _extract_gps_from_tags(self, tags: Dict) -> Optional[Dict[str, Any]]:
        """Extract GPS coordinates from EXIF tags."""
        try:
            lat = tags.get('GPS GPSLatitude')
            lat_ref = tags.get('GPS GPSLatitudeRef')
            lon = tags.get('GPS GPSLongitude')
            lon_ref = tags.get('GPS GPSLongitudeRef')
            
            if not all([lat, lat_ref, lon, lon_ref]):
                return None
            
            # Convert to decimal degrees
            def convert_to_degrees(value):
                d = float(value.values[0].num) / float(value.values[0].den)
                m = float(value.values[1].num) / float(value.values[1].den)
                s = float(value.values[2].num) / float(value.values[2].den)
                return d + (m / 60.0) + (s / 3600.0)
            
            latitude = convert_to_degrees(lat)
            longitude = convert_to_degrees(lon)
            
            if str(lat_ref) == 'S':
                latitude = -latitude
            if str(lon_ref) == 'W':
                longitude = -longitude
            
            gps_dict = {
                'latitude': latitude,
                'longitude': longitude,
                'latitude_ref': str(lat_ref),
                'longitude_ref': str(lon_ref)
            }
            
            # Altitude if available
            if 'GPS GPSAltitude' in tags:
                alt = tags['GPS GPSAltitude']
                gps_dict['altitude'] = float(alt.values[0].num) / float(alt.values[0].den)
            
            return gps_dict
            
        except Exception as e:
            return None
    
    def _process_video(self, file_path: str) -> Dict[str, Any]:
        """Extract metadata from video file."""
        metadata = {
            'file_path': file_path,
            'file_name': os.path.basename(file_path),
            'file_type': 'video',
            'file_size': os.path.getsize(file_path),
            'mime_type': self.mime.from_file(file_path),
            'created_date': datetime.fromtimestamp(os.path.getctime(file_path)),
            'modified_date': datetime.fromtimestamp(os.path.getmtime(file_path)),
        }
        
        if mp is None:
            return metadata
        
        try:
            clip = mp.VideoFileClip(file_path)
            metadata['duration'] = clip.duration
            metadata['width'] = clip.w
            metadata['height'] = clip.h
            metadata['frame_rate'] = clip.fps
            
            if clip.audio:
                metadata['audio_channels'] = clip.audio.nchannels
                metadata['audio_sample_rate'] = clip.audio.fps
            
            clip.close()
        except Exception as e:
            if self.verbose:
                print(f"Warning: Could not extract video metadata from {file_path}: {e}")
        
        return metadata
    
    def _process_audio(self, file_path: str) -> Dict[str, Any]:
        """Extract metadata from audio file."""
        metadata = {
            'file_path': file_path,
            'file_name': os.path.basename(file_path),
            'file_type': 'audio',
            'file_size': os.path.getsize(file_path),
            'mime_type': self.mime.from_file(file_path),
            'created_date': datetime.fromtimestamp(os.path.getctime(file_path)),
            'modified_date': datetime.fromtimestamp(os.path.getmtime(file_path)),
        }
        
        try:
            audiofile = eyed3.load(file_path)
            if audiofile and audiofile.tag:
                tag = audiofile.tag
                metadata['title'] = tag.title
                metadata['artist'] = tag.artist
                metadata['album'] = tag.album
                metadata['album_artist'] = tag.album_artist
                metadata['genre'] = str(tag.genre) if tag.genre else None
                
                if tag.recording_date:
                    metadata['year'] = tag.recording_date.year
                
                if tag.track_num:
                    metadata['track_number'] = tag.track_num[0]
            
            if audiofile and audiofile.info:
                info = audiofile.info
                metadata['duration'] = info.time_secs
                metadata['bitrate'] = info.bit_rate[1] if info.bit_rate else None
                metadata['sample_rate'] = info.sample_freq
        except Exception as e:
            if self.verbose:
                print(f"Warning: Could not extract audio metadata from {file_path}: {e}")
        
        return metadata
    
    def _process_document(self, file_path: str) -> Dict[str, Any]:
        """Extract metadata from document file."""
        metadata = {
            'file_path': file_path,
            'file_name': os.path.basename(file_path),
            'file_type': 'document',
            'file_size': os.path.getsize(file_path),
            'mime_type': self.mime.from_file(file_path),
            'created_date': datetime.fromtimestamp(os.path.getctime(file_path)),
            'modified_date': datetime.fromtimestamp(os.path.getmtime(file_path)),
        }
        
        ext = Path(file_path).suffix.lower()
        
        if ext == '.pdf' and pdfplumber is not None:
            try:
                with pdfplumber.open(file_path) as pdf:
                    metadata['page_count'] = len(pdf.pages)
                    
                    if pdf.metadata:
                        meta = pdf.metadata
                        metadata['title'] = meta.get('Title')
                        metadata['author'] = meta.get('Author')
                        metadata['subject'] = meta.get('Subject')
                        metadata['creator'] = meta.get('Creator')
                        metadata['producer'] = meta.get('Producer')
                        
                        if meta.get('CreationDate'):
                            try:
                                # Parse PDF date format
                                date_str = meta['CreationDate'].replace('D:', '').split('+')[0].split('-')[0]
                                metadata['creation_date'] = datetime.strptime(date_str[:14], '%Y%m%d%H%M%S')
                            except:
                                pass
            except Exception as e:
                if self.verbose:
                    print(f"Warning: Could not extract PDF metadata from {file_path}: {e}")
        
        elif ext == '.docx' and DocxDocument is not None:
            try:
                doc = DocxDocument(file_path)
                core_props = doc.core_properties
                
                metadata['title'] = core_props.title
                metadata['author'] = core_props.author
                metadata['subject'] = core_props.subject
                metadata['keywords'] = core_props.keywords.split(',') if core_props.keywords else None
                metadata['creation_date'] = core_props.created
                metadata['modification_date'] = core_props.modified
                
                # Count words
                word_count = 0
                for para in doc.paragraphs:
                    word_count += len(para.text.split())
                metadata['word_count'] = word_count
                
            except Exception as e:
                if self.verbose:
                    print(f"Warning: Could not extract DOCX metadata from {file_path}: {e}")
        
        return metadata
    
    def _process_generic(self, file_path: str) -> Dict[str, Any]:
        """Extract basic metadata from unsupported file types."""
        return {
            'file_path': file_path,
            'file_name': os.path.basename(file_path),
            'file_type': 'unknown',
            'file_size': os.path.getsize(file_path),
            'mime_type': self.mime.from_file(file_path),
            'created_date': datetime.fromtimestamp(os.path.getctime(file_path)),
            'modified_date': datetime.fromtimestamp(os.path.getmtime(file_path)),
        }
    
    def process_batch(
        self, 
        file_list: List[str],
        max_workers: int = 4,
        show_progress: bool = True
    ) -> BatchProcessResult:
        """
        Process multiple files in parallel.
        
        Args:
            file_list: List of file paths to process
            max_workers: Maximum number of parallel workers
            show_progress: Whether to show progress bar
        
        Returns:
            BatchProcessResult with statistics
        """
        start_time = time.time()
        self.results = []
        self.errors = []
        
        successful = 0
        failed = 0
        
        # Create progress bar
        progress_bar = tqdm(
            total=len(file_list),
            desc="Processing files",
            disable=not show_progress
        )
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_file = {
                executor.submit(self.process_file, file_path): file_path 
                for file_path in file_list
            }
            
            # Process completed tasks
            for future in as_completed(future_to_file):
                file_path = future_to_file[future]
                try:
                    result = future.result()
                    if result:
                        self.results.append(result)
                        successful += 1
                    else:
                        failed += 1
                except Exception as e:
                    failed += 1
                    self.errors.append({
                        'file': file_path,
                        'error': str(e),
                        'type': 'execution_error'
                    })
                
                progress_bar.update(1)
        
        progress_bar.close()
        
        processing_time = time.time() - start_time
        
        result = BatchProcessResult(
            total_files=len(file_list),
            successful=successful,
            failed=failed,
            processing_time=processing_time,
            errors=self.errors
        )
        
        if self.verbose:
            print(f"\nProcessing complete:")
            print(f"  Total: {result.total_files}")
            print(f"  Successful: {result.successful}")
            print(f"  Failed: {result.failed}")
            print(f"  Success rate: {result.success_rate}%")
            print(f"  Time: {processing_time:.2f}s")
        
        return result
    
    def get_results(self) -> List[Dict[str, Any]]:
        """Get all processing results."""
        return self.results
    
    def get_results_by_type(self, file_type: str) -> List[Dict[str, Any]]:
        """Get results filtered by file type."""
        return [r for r in self.results if r.get('file_type') == file_type]
    
    def export_results(self, output_path: str, format: str = 'json') -> None:
        """
        Export results to file.
        
        Args:
            output_path: Path to output file
            format: Export format ('json' or 'csv')
        """
        if format == 'json':
            with open(output_path, 'w') as f:
                json.dump(self.results, f, indent=2, default=str)
        elif format == 'csv':
            try:
                import pandas as pd
                df = pd.DataFrame(self.results)
                df.to_csv(output_path, index=False)
            except ImportError:
                raise ImportError("pandas is required for CSV export")
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        if self.verbose:
            print(f"Results exported to {output_path}")


if __name__ == "__main__":
    # Example usage
    import argparse
    
    parser = argparse.ArgumentParser(description="Aggregate metadata from files")
    parser.add_argument("path", help="Directory path to scan")
    parser.add_argument("--recursive", "-r", action="store_true", help="Scan recursively")
    parser.add_argument("--types", "-t", nargs="+", help="File types to process")
    parser.add_argument("--output", "-o", help="Output file path")
    parser.add_argument("--format", "-f", choices=['json', 'csv'], default='json', help="Output format")
    parser.add_argument("--workers", "-w", type=int, default=4, help="Number of parallel workers")
    
    args = parser.parse_args()
    
    # Create aggregator
    aggregator = MetadataAggregator(verbose=True)
    
    # Scan directory
    files = aggregator.scan_directory(args.path, recursive=args.recursive, file_types=args.types)
    
    if not files:
        print("No files found!")
        sys.exit(1)
    
    # Process files
    result = aggregator.process_batch(files, max_workers=args.workers)
    
    # Export if requested
    if args.output:
        aggregator.export_results(args.output, format=args.format)
    else:
        # Print summary
        print("\nSample results:")
        for i, item in enumerate(aggregator.get_results()[:3]):
            print(f"\n{i+1}. {item['file_name']}:")
            for key, value in list(item.items())[:10]:
                print(f"   {key}: {value}")
