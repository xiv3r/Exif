#!/usr/bin/env python3
"""
Data Storage - SQLite database management for metadata storage.

This module provides the MetadataDatabase class for storing, querying,
and managing metadata in a SQLite database.
"""

import sqlite3
import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from contextlib import contextmanager

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False


class MetadataDatabase:
    """
    SQLite database manager for metadata storage.
    
    Handles storage and retrieval of file metadata with support for
    different file types (images, videos, audio, documents).
    """
    
    def __init__(self, db_path: str = "data/metadata.db"):
        """
        Initialize database connection.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        
        # Ensure directory exists
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self._create_tables()
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable dict-like access
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def _create_tables(self):
        """Create database tables if they don't exist."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Files table (base information for all files)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_path TEXT UNIQUE NOT NULL,
                    file_name TEXT NOT NULL,
                    file_type TEXT NOT NULL,
                    file_size INTEGER NOT NULL,
                    mime_type TEXT,
                    created_date TIMESTAMP,
                    modified_date TIMESTAMP,
                    processed_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(file_path)
                )
            ''')
            
            # Image metadata table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS image_metadata (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_id INTEGER NOT NULL,
                    width INTEGER,
                    height INTEGER,
                    camera_make TEXT,
                    camera_model TEXT,
                    lens_model TEXT,
                    focal_length REAL,
                    aperture REAL,
                    shutter_speed TEXT,
                    iso INTEGER,
                    flash TEXT,
                    orientation INTEGER,
                    color_space TEXT,
                    date_taken TIMESTAMP,
                    gps_latitude REAL,
                    gps_longitude REAL,
                    gps_altitude REAL,
                    software TEXT,
                    format TEXT,
                    FOREIGN KEY (file_id) REFERENCES files(id) ON DELETE CASCADE
                )
            ''')
            
            # Video metadata table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS video_metadata (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_id INTEGER NOT NULL,
                    duration REAL,
                    width INTEGER,
                    height INTEGER,
                    codec TEXT,
                    frame_rate REAL,
                    bitrate INTEGER,
                    audio_codec TEXT,
                    audio_sample_rate INTEGER,
                    audio_channels INTEGER,
                    FOREIGN KEY (file_id) REFERENCES files(id) ON DELETE CASCADE
                )
            ''')
            
            # Audio metadata table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS audio_metadata (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_id INTEGER NOT NULL,
                    title TEXT,
                    artist TEXT,
                    album TEXT,
                    album_artist TEXT,
                    genre TEXT,
                    year INTEGER,
                    track_number INTEGER,
                    duration REAL,
                    bitrate INTEGER,
                    sample_rate INTEGER,
                    channels INTEGER,
                    codec TEXT,
                    FOREIGN KEY (file_id) REFERENCES files(id) ON DELETE CASCADE
                )
            ''')
            
            # Document metadata table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS document_metadata (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_id INTEGER NOT NULL,
                    title TEXT,
                    author TEXT,
                    subject TEXT,
                    creator TEXT,
                    producer TEXT,
                    keywords TEXT,
                    page_count INTEGER,
                    word_count INTEGER,
                    creation_date TIMESTAMP,
                    modification_date TIMESTAMP,
                    FOREIGN KEY (file_id) REFERENCES files(id) ON DELETE CASCADE
                )
            ''')
            
            # Generic metadata fields (key-value pairs)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS metadata_fields (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_id INTEGER NOT NULL,
                    field_name TEXT NOT NULL,
                    field_value TEXT,
                    FOREIGN KEY (file_id) REFERENCES files(id) ON DELETE CASCADE
                )
            ''')
            
            # Create indexes for better query performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_files_type ON files(file_type)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_files_created ON files(created_date)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_image_camera ON image_metadata(camera_model)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_image_gps ON image_metadata(gps_latitude, gps_longitude)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_audio_artist ON audio_metadata(artist)')
            
            conn.commit()
    
    def insert_file(self, metadata: Dict[str, Any]) -> int:
        """
        Insert file metadata into database.
        
        Args:
            metadata: Dictionary with file metadata
        
        Returns:
            File ID
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Insert into files table
            cursor.execute('''
                INSERT OR REPLACE INTO files 
                (file_path, file_name, file_type, file_size, mime_type, created_date, modified_date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                metadata.get('file_path'),
                metadata.get('file_name'),
                metadata.get('file_type'),
                metadata.get('file_size'),
                metadata.get('mime_type'),
                metadata.get('created_date'),
                metadata.get('modified_date')
            ))
            
            file_id = cursor.lastrowid
            
            # Insert type-specific metadata
            file_type = metadata.get('file_type')
            
            if file_type == 'image':
                self._insert_image_metadata(cursor, file_id, metadata)
            elif file_type == 'video':
                self._insert_video_metadata(cursor, file_id, metadata)
            elif file_type == 'audio':
                self._insert_audio_metadata(cursor, file_id, metadata)
            elif file_type == 'document':
                self._insert_document_metadata(cursor, file_id, metadata)
            
            conn.commit()
            return file_id
    
    def _insert_image_metadata(self, cursor, file_id: int, metadata: Dict[str, Any]):
        """Insert image-specific metadata."""
        gps = metadata.get('gps_coordinates', {})
        
        cursor.execute('''
            INSERT INTO image_metadata 
            (file_id, width, height, camera_make, camera_model, lens_model, 
             focal_length, aperture, shutter_speed, iso, flash, orientation,
             color_space, date_taken, gps_latitude, gps_longitude, gps_altitude,
             software, format)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            file_id,
            metadata.get('width'),
            metadata.get('height'),
            metadata.get('camera_make'),
            metadata.get('camera_model'),
            metadata.get('lens_model'),
            metadata.get('focal_length'),
            metadata.get('aperture'),
            metadata.get('shutter_speed'),
            metadata.get('iso'),
            metadata.get('flash'),
            metadata.get('orientation'),
            metadata.get('color_space'),
            metadata.get('date_taken'),
            gps.get('latitude') if gps else None,
            gps.get('longitude') if gps else None,
            gps.get('altitude') if gps else None,
            metadata.get('software'),
            metadata.get('format')
        ))
    
    def _insert_video_metadata(self, cursor, file_id: int, metadata: Dict[str, Any]):
        """Insert video-specific metadata."""
        cursor.execute('''
            INSERT INTO video_metadata 
            (file_id, duration, width, height, codec, frame_rate, bitrate,
             audio_codec, audio_sample_rate, audio_channels)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            file_id,
            metadata.get('duration'),
            metadata.get('width'),
            metadata.get('height'),
            metadata.get('codec'),
            metadata.get('frame_rate'),
            metadata.get('bitrate'),
            metadata.get('audio_codec'),
            metadata.get('audio_sample_rate'),
            metadata.get('audio_channels')
        ))
    
    def _insert_audio_metadata(self, cursor, file_id: int, metadata: Dict[str, Any]):
        """Insert audio-specific metadata."""
        cursor.execute('''
            INSERT INTO audio_metadata 
            (file_id, title, artist, album, album_artist, genre, year,
             track_number, duration, bitrate, sample_rate, channels, codec)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            file_id,
            metadata.get('title'),
            metadata.get('artist'),
            metadata.get('album'),
            metadata.get('album_artist'),
            metadata.get('genre'),
            metadata.get('year'),
            metadata.get('track_number'),
            metadata.get('duration'),
            metadata.get('bitrate'),
            metadata.get('sample_rate'),
            metadata.get('channels'),
            metadata.get('codec')
        ))
    
    def _insert_document_metadata(self, cursor, file_id: int, metadata: Dict[str, Any]):
        """Insert document-specific metadata."""
        keywords = metadata.get('keywords')
        if isinstance(keywords, list):
            keywords = ','.join(keywords)
        
        cursor.execute('''
            INSERT INTO document_metadata 
            (file_id, title, author, subject, creator, producer, keywords,
             page_count, word_count, creation_date, modification_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            file_id,
            metadata.get('title'),
            metadata.get('author'),
            metadata.get('subject'),
            metadata.get('creator'),
            metadata.get('producer'),
            keywords,
            metadata.get('page_count'),
            metadata.get('word_count'),
            metadata.get('creation_date'),
            metadata.get('modification_date')
        ))
    
    def insert_batch(self, metadata_list: List[Dict[str, Any]]) -> List[int]:
        """
        Insert multiple files at once.
        
        Args:
            metadata_list: List of metadata dictionaries
        
        Returns:
            List of file IDs
        """
        file_ids = []
        for metadata in metadata_list:
            try:
                file_id = self.insert_file(metadata)
                file_ids.append(file_id)
            except Exception as e:
                print(f"Error inserting {metadata.get('file_path')}: {e}")
        return file_ids
    
    def query_files(
        self, 
        file_type: Optional[str] = None,
        limit: Optional[int] = None,
        offset: int = 0,
        order_by: str = "processed_date DESC"
    ) -> List[Dict[str, Any]]:
        """
        Query files from database.
        
        Args:
            file_type: Filter by file type
            limit: Maximum number of results
            offset: Number of results to skip
            order_by: SQL ORDER BY clause
        
        Returns:
            List of file metadata dictionaries
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            query = "SELECT * FROM files"
            params = []
            
            if file_type:
                query += " WHERE file_type = ?"
                params.append(file_type)
            
            query += f" ORDER BY {order_by}"
            
            if limit:
                query += " LIMIT ?"
                params.append(limit)
            
            if offset:
                query += " OFFSET ?"
                params.append(offset)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            return [dict(row) for row in rows]
    
    def get_file_by_id(self, file_id: int) -> Optional[Dict[str, Any]]:
        """Get complete file metadata by ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get base file info
            cursor.execute("SELECT * FROM files WHERE id = ?", (file_id,))
            file_row = cursor.fetchone()
            
            if not file_row:
                return None
            
            file_data = dict(file_row)
            file_type = file_data['file_type']
            
            # Get type-specific metadata
            if file_type == 'image':
                cursor.execute("SELECT * FROM image_metadata WHERE file_id = ?", (file_id,))
                meta_row = cursor.fetchone()
                if meta_row:
                    file_data.update(dict(meta_row))
            
            elif file_type == 'video':
                cursor.execute("SELECT * FROM video_metadata WHERE file_id = ?", (file_id,))
                meta_row = cursor.fetchone()
                if meta_row:
                    file_data.update(dict(meta_row))
            
            elif file_type == 'audio':
                cursor.execute("SELECT * FROM audio_metadata WHERE file_id = ?", (file_id,))
                meta_row = cursor.fetchone()
                if meta_row:
                    file_data.update(dict(meta_row))
            
            elif file_type == 'document':
                cursor.execute("SELECT * FROM document_metadata WHERE file_id = ?", (file_id,))
                meta_row = cursor.fetchone()
                if meta_row:
                    file_data.update(dict(meta_row))
            
            return file_data
    
    def get_files_with_gps(self) -> List[Dict[str, Any]]:
        """Get all files with GPS coordinates."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT f.*, i.gps_latitude, i.gps_longitude, i.gps_altitude
                FROM files f
                JOIN image_metadata i ON f.id = i.file_id
                WHERE i.gps_latitude IS NOT NULL AND i.gps_longitude IS NOT NULL
            ''')
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def get_unique_cameras(self) -> List[Tuple[str, int]]:
        """Get list of unique cameras with file counts."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT camera_model, COUNT(*) as count
                FROM image_metadata
                WHERE camera_model IS NOT NULL
                GROUP BY camera_model
                ORDER BY count DESC
            ''')
            
            return cursor.fetchall()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            stats = {}
            
            # Total files
            cursor.execute("SELECT COUNT(*) FROM files")
            stats['total_files'] = cursor.fetchone()[0]
            
            # Files by type
            cursor.execute('''
                SELECT file_type, COUNT(*) as count
                FROM files
                GROUP BY file_type
            ''')
            stats['files_by_type'] = dict(cursor.fetchall())
            
            # Total size
            cursor.execute("SELECT SUM(file_size) FROM files")
            total_bytes = cursor.fetchone()[0] or 0
            stats['total_size_mb'] = round(total_bytes / (1024 * 1024), 2)
            stats['average_size_mb'] = round(total_bytes / stats['total_files'] / (1024 * 1024), 2) if stats['total_files'] > 0 else 0
            
            # Date range
            cursor.execute("SELECT MIN(created_date), MAX(created_date) FROM files WHERE created_date IS NOT NULL")
            min_date, max_date = cursor.fetchone()
            if min_date and max_date:
                stats['date_range'] = {'min': min_date, 'max': max_date}
            
            # Unique cameras
            cursor.execute("SELECT COUNT(DISTINCT camera_model) FROM image_metadata WHERE camera_model IS NOT NULL")
            stats['unique_cameras'] = cursor.fetchone()[0]
            
            # Files with GPS
            cursor.execute("SELECT COUNT(*) FROM image_metadata WHERE gps_latitude IS NOT NULL")
            stats['files_with_gps'] = cursor.fetchone()[0]
            
            return stats
    
    def export_to_dataframe(self, file_type: Optional[str] = None):
        """
        Export data to pandas DataFrame.
        
        Args:
            file_type: Filter by file type (optional)
        
        Returns:
            pandas DataFrame
        """
        if not PANDAS_AVAILABLE:
            raise ImportError("pandas is required for DataFrame export")
        
        with self.get_connection() as conn:
            if file_type:
                if file_type == 'image':
                    query = '''
                        SELECT f.*, i.*
                        FROM files f
                        LEFT JOIN image_metadata i ON f.id = i.file_id
                        WHERE f.file_type = 'image'
                    '''
                elif file_type == 'video':
                    query = '''
                        SELECT f.*, v.*
                        FROM files f
                        LEFT JOIN video_metadata v ON f.id = v.file_id
                        WHERE f.file_type = 'video'
                    '''
                elif file_type == 'audio':
                    query = '''
                        SELECT f.*, a.*
                        FROM files f
                        LEFT JOIN audio_metadata a ON f.id = a.file_id
                        WHERE f.file_type = 'audio'
                    '''
                elif file_type == 'document':
                    query = '''
                        SELECT f.*, d.*
                        FROM files f
                        LEFT JOIN document_metadata d ON f.id = d.file_id
                        WHERE f.file_type = 'document'
                    '''
                else:
                    query = "SELECT * FROM files WHERE file_type = ?"
            else:
                query = "SELECT * FROM files"
            
            df = pd.read_sql_query(query, conn)
            return df
    
    def delete_file(self, file_id: int) -> bool:
        """Delete file and its metadata."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM files WHERE id = ?", (file_id,))
            return cursor.rowcount > 0
    
    def delete_all(self) -> int:
        """Delete all data from database."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM files")
            count = cursor.fetchone()[0]
            
            cursor.execute("DELETE FROM files")
            cursor.execute("DELETE FROM image_metadata")
            cursor.execute("DELETE FROM video_metadata")
            cursor.execute("DELETE FROM audio_metadata")
            cursor.execute("DELETE FROM document_metadata")
            cursor.execute("DELETE FROM metadata_fields")
            
            return count
    
    def vacuum(self):
        """Optimize database (reclaim space after deletions)."""
        with self.get_connection() as conn:
            conn.execute("VACUUM")


if __name__ == "__main__":
    # Example usage
    db = MetadataDatabase("data/test_metadata.db")
    
    # Insert sample data
    sample_data = {
        'file_path': '/path/to/image.jpg',
        'file_name': 'image.jpg',
        'file_type': 'image',
        'file_size': 1024000,
        'mime_type': 'image/jpeg',
        'created_date': datetime.now(),
        'modified_date': datetime.now(),
        'width': 1920,
        'height': 1080,
        'camera_make': 'Canon',
        'camera_model': 'EOS 5D Mark IV'
    }
    
    file_id = db.insert_file(sample_data)
    print(f"Inserted file with ID: {file_id}")
    
    # Get statistics
    stats = db.get_statistics()
    print("\nDatabase Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
