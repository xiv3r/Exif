"""
Data models for metadata storage and validation.
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, validator
from pathlib import Path


class FileMetadata(BaseModel):
    """Base metadata model for all file types."""
    
    file_path: str
    file_name: str
    file_type: str
    file_size: int  # in bytes
    mime_type: Optional[str] = None
    created_date: Optional[datetime] = None
    modified_date: Optional[datetime] = None
    processed_date: datetime = Field(default_factory=datetime.now)
    
    @validator('file_path')
    def validate_path(cls, v):
        """Ensure file path exists."""
        if not Path(v).exists():
            raise ValueError(f"File does not exist: {v}")
        return str(Path(v).resolve())
    
    @property
    def file_size_mb(self) -> float:
        """Return file size in MB."""
        return self.file_size / (1024 * 1024)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class GPSCoordinates(BaseModel):
    """GPS coordinate data model."""
    
    latitude: float
    longitude: float
    altitude: Optional[float] = None
    latitude_ref: Optional[str] = None  # N or S
    longitude_ref: Optional[str] = None  # E or W
    
    @validator('latitude')
    def validate_latitude(cls, v):
        """Ensure latitude is valid."""
        if not -90 <= v <= 90:
            raise ValueError(f"Invalid latitude: {v}")
        return v
    
    @validator('longitude')
    def validate_longitude(cls, v):
        """Ensure longitude is valid."""
        if not -180 <= v <= 180:
            raise ValueError(f"Invalid longitude: {v}")
        return v
    
    def to_google_maps_url(self) -> str:
        """Generate Google Maps URL."""
        return f"https://www.google.com/maps?q={self.latitude},{self.longitude}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "altitude": self.altitude,
            "maps_url": self.to_google_maps_url()
        }


class ImageMetadata(FileMetadata):
    """Metadata model for image files."""
    
    width: Optional[int] = None
    height: Optional[int] = None
    camera_make: Optional[str] = None
    camera_model: Optional[str] = None
    lens_model: Optional[str] = None
    focal_length: Optional[float] = None
    aperture: Optional[float] = None
    shutter_speed: Optional[str] = None
    iso: Optional[int] = None
    flash: Optional[str] = None
    orientation: Optional[int] = None
    color_space: Optional[str] = None
    date_taken: Optional[datetime] = None
    gps_coordinates: Optional[GPSCoordinates] = None
    software: Optional[str] = None
    
    @property
    def resolution(self) -> Optional[str]:
        """Return resolution as string."""
        if self.width and self.height:
            return f"{self.width}x{self.height}"
        return None
    
    @property
    def megapixels(self) -> Optional[float]:
        """Calculate megapixels."""
        if self.width and self.height:
            return round((self.width * self.height) / 1_000_000, 2)
        return None


class VideoMetadata(FileMetadata):
    """Metadata model for video files."""
    
    duration: Optional[float] = None  # in seconds
    width: Optional[int] = None
    height: Optional[int] = None
    codec: Optional[str] = None
    frame_rate: Optional[float] = None
    bitrate: Optional[int] = None
    audio_codec: Optional[str] = None
    audio_sample_rate: Optional[int] = None
    audio_channels: Optional[int] = None
    
    @property
    def resolution(self) -> Optional[str]:
        """Return resolution as string."""
        if self.width and self.height:
            return f"{self.width}x{self.height}"
        return None
    
    @property
    def duration_formatted(self) -> Optional[str]:
        """Return duration in HH:MM:SS format."""
        if self.duration:
            hours = int(self.duration // 3600)
            minutes = int((self.duration % 3600) // 60)
            seconds = int(self.duration % 60)
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        return None


class AudioMetadata(FileMetadata):
    """Metadata model for audio files."""
    
    title: Optional[str] = None
    artist: Optional[str] = None
    album: Optional[str] = None
    album_artist: Optional[str] = None
    genre: Optional[str] = None
    year: Optional[int] = None
    track_number: Optional[int] = None
    duration: Optional[float] = None  # in seconds
    bitrate: Optional[int] = None
    sample_rate: Optional[int] = None
    channels: Optional[int] = None
    codec: Optional[str] = None
    
    @property
    def duration_formatted(self) -> Optional[str]:
        """Return duration in MM:SS format."""
        if self.duration:
            minutes = int(self.duration // 60)
            seconds = int(self.duration % 60)
            return f"{minutes:02d}:{seconds:02d}"
        return None


class DocumentMetadata(FileMetadata):
    """Metadata model for document files."""
    
    title: Optional[str] = None
    author: Optional[str] = None
    subject: Optional[str] = None
    creator: Optional[str] = None
    producer: Optional[str] = None
    keywords: Optional[List[str]] = None
    page_count: Optional[int] = None
    word_count: Optional[int] = None
    creation_date: Optional[datetime] = None
    modification_date: Optional[datetime] = None


class StatisticalSummary(BaseModel):
    """Statistical summary model."""
    
    total_files: int
    file_types: Dict[str, int]
    total_size_mb: float
    average_size_mb: float
    date_range: Optional[Dict[str, datetime]] = None
    unique_devices: Optional[int] = None
    files_with_gps: Optional[int] = None
    most_common_camera: Optional[str] = None
    most_common_resolution: Optional[str] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class BatchProcessResult(BaseModel):
    """Result of batch processing."""
    
    total_files: int
    successful: int
    failed: int
    processing_time: float  # in seconds
    errors: List[Dict[str, str]] = []
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate percentage."""
        if self.total_files == 0:
            return 0.0
        return round((self.successful / self.total_files) * 100, 2)
