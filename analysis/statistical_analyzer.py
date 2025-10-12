#!/usr/bin/env python3
"""
Statistical Analyzer - Comprehensive statistical analysis of metadata.

This module provides the StatisticalAnalyzer class for analyzing metadata patterns,
calculating statistics, and generating insights.
"""

from typing import Dict, List, Any, Optional, Tuple
from collections import Counter
from datetime import datetime, timedelta
import json

try:
    import pandas as pd
    import numpy as np
    from scipy import stats
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False


class StatisticalAnalyzer:
    """
    Performs statistical analysis on metadata collections.
    
    Provides descriptive statistics, frequency analysis, temporal patterns,
    and correlation analysis for metadata fields.
    """
    
    def __init__(self, data: pd.DataFrame = None):
        """
        Initialize the analyzer.
        
        Args:
            data: pandas DataFrame with metadata (optional)
        """
        if not SCIPY_AVAILABLE:
            raise ImportError("pandas, numpy, and scipy are required for StatisticalAnalyzer")
        
        self.data = data
        self._cache = {}
    
    def set_data(self, data: pd.DataFrame):
        """Set or update the data."""
        self.data = data
        self._cache = {}  # Clear cache
    
    def calculate_descriptive_stats(self, field: str) -> Dict[str, Any]:
        """
        Calculate descriptive statistics for a numeric field.
        
        Args:
            field: Name of the field to analyze
        
        Returns:
            Dictionary with statistics
        """
        if self.data is None or field not in self.data.columns:
            return {}
        
        series = self.data[field].dropna()
        
        if len(series) == 0:
            return {}
        
        if not pd.api.types.is_numeric_dtype(series):
            return {}
        
        stats_dict = {
            'count': int(series.count()),
            'mean': float(series.mean()),
            'median': float(series.median()),
            'std': float(series.std()),
            'min': float(series.min()),
            'max': float(series.max()),
            'q25': float(series.quantile(0.25)),
            'q75': float(series.quantile(0.75)),
        }
        
        # Mode (can be multiple values)
        try:
            mode_result = stats.mode(series, keepdims=True)
            stats_dict['mode'] = float(mode_result.mode[0])
        except:
            pass
        
        # Interquartile range
        stats_dict['iqr'] = stats_dict['q75'] - stats_dict['q25']
        
        # Coefficient of variation
        if stats_dict['mean'] != 0:
            stats_dict['cv'] = (stats_dict['std'] / stats_dict['mean']) * 100
        
        return stats_dict
    
    def frequency_distribution(self, field: str, top_n: int = 10) -> List[Tuple[Any, int]]:
        """
        Calculate frequency distribution for a categorical field.
        
        Args:
            field: Name of the field to analyze
            top_n: Number of top items to return
        
        Returns:
            List of (value, count) tuples
        """
        if self.data is None or field not in self.data.columns:
            return []
        
        series = self.data[field].dropna()
        
        if len(series) == 0:
            return []
        
        value_counts = series.value_counts()
        return list(value_counts.head(top_n).items())
    
    def temporal_analysis(self, date_field: str = 'created_date') -> Dict[str, Any]:
        """
        Analyze temporal patterns in the data.
        
        Args:
            date_field: Name of the date field to analyze
        
        Returns:
            Dictionary with temporal statistics
        """
        if self.data is None or date_field not in self.data.columns:
            return {}
        
        # Convert to datetime if needed
        dates = pd.to_datetime(self.data[date_field], errors='coerce').dropna()
        
        if len(dates) == 0:
            return {}
        
        analysis = {
            'date_range': {
                'start': dates.min().isoformat(),
                'end': dates.max().isoformat(),
                'span_days': (dates.max() - dates.min()).days
            },
            'count': len(dates)
        }
        
        # Group by various time periods
        df_dates = pd.DataFrame({'date': dates})
        
        # By year
        df_dates['year'] = df_dates['date'].dt.year
        analysis['by_year'] = df_dates['year'].value_counts().to_dict()
        
        # By month
        df_dates['month'] = df_dates['date'].dt.month
        analysis['by_month'] = df_dates['month'].value_counts().to_dict()
        
        # By day of week
        df_dates['dayofweek'] = df_dates['date'].dt.dayofweek
        dow_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        dow_counts = df_dates['dayofweek'].value_counts()
        analysis['by_day_of_week'] = {dow_names[k]: v for k, v in dow_counts.items()}
        
        # By hour (if time information available)
        df_dates['hour'] = df_dates['date'].dt.hour
        analysis['by_hour'] = df_dates['hour'].value_counts().to_dict()
        
        # Most active periods
        analysis['most_active_year'] = int(df_dates['year'].mode().iloc[0]) if len(df_dates) > 0 else None
        analysis['most_active_month'] = int(df_dates['month'].mode().iloc[0]) if len(df_dates) > 0 else None
        analysis['most_active_day'] = dow_names[int(df_dates['dayofweek'].mode().iloc[0])] if len(df_dates) > 0 else None
        
        return analysis
    
    def correlation_matrix(self, fields: List[str]) -> Dict[str, Any]:
        """
        Calculate correlation matrix for numeric fields.
        
        Args:
            fields: List of field names to analyze
        
        Returns:
            Dictionary with correlation data
        """
        if self.data is None:
            return {}
        
        # Filter to numeric fields that exist
        valid_fields = [f for f in fields if f in self.data.columns and pd.api.types.is_numeric_dtype(self.data[f])]
        
        if len(valid_fields) < 2:
            return {'error': 'Need at least 2 numeric fields'}
        
        # Calculate correlation matrix
        corr_matrix = self.data[valid_fields].corr()
        
        # Convert to dict format
        result = {
            'fields': valid_fields,
            'matrix': corr_matrix.to_dict(),
            'pairs': []
        }
        
        # Extract significant correlations (|r| > 0.5)
        for i, field1 in enumerate(valid_fields):
            for field2 in valid_fields[i+1:]:
                corr_value = corr_matrix.loc[field1, field2]
                if abs(corr_value) > 0.5:
                    result['pairs'].append({
                        'field1': field1,
                        'field2': field2,
                        'correlation': float(corr_value),
                        'strength': 'strong' if abs(corr_value) > 0.7 else 'moderate'
                    })
        
        return result
    
    def group_analysis(
        self, 
        group_by: str, 
        aggregate_fields: List[str],
        agg_func: str = 'mean'
    ) -> Dict[str, Any]:
        """
        Group data and calculate aggregate statistics.
        
        Args:
            group_by: Field to group by
            aggregate_fields: Fields to aggregate
            agg_func: Aggregation function ('mean', 'sum', 'count', etc.)
        
        Returns:
            Dictionary with grouped results
        """
        if self.data is None or group_by not in self.data.columns:
            return {}
        
        # Filter valid aggregate fields
        valid_fields = [f for f in aggregate_fields if f in self.data.columns]
        
        if not valid_fields:
            return {}
        
        # Perform groupby operation
        grouped = self.data.groupby(group_by)[valid_fields].agg(agg_func)
        
        return {
            'group_by': group_by,
            'aggregate_function': agg_func,
            'results': grouped.to_dict()
        }
    
    def detect_outliers(
        self, 
        field: str, 
        method: str = 'iqr',
        threshold: float = 1.5
    ) -> Dict[str, Any]:
        """
        Detect outliers in a numeric field.
        
        Args:
            field: Field name to analyze
            method: Detection method ('iqr', 'zscore', 'modified_zscore')
            threshold: Threshold for outlier detection
        
        Returns:
            Dictionary with outlier information
        """
        if self.data is None or field not in self.data.columns:
            return {}
        
        series = self.data[field].dropna()
        
        if len(series) == 0 or not pd.api.types.is_numeric_dtype(series):
            return {}
        
        outliers = []
        
        if method == 'iqr':
            # Interquartile Range method
            q1 = series.quantile(0.25)
            q3 = series.quantile(0.75)
            iqr = q3 - q1
            lower_bound = q1 - threshold * iqr
            upper_bound = q3 + threshold * iqr
            
            outlier_mask = (series < lower_bound) | (series > upper_bound)
            outliers = series[outlier_mask].tolist()
            
            result = {
                'method': 'iqr',
                'threshold': threshold,
                'bounds': {
                    'lower': float(lower_bound),
                    'upper': float(upper_bound)
                },
                'outlier_count': len(outliers),
                'outlier_percentage': (len(outliers) / len(series)) * 100,
                'outliers': outliers[:100]  # Limit to 100
            }
            
        elif method == 'zscore':
            # Z-score method
            mean = series.mean()
            std = series.std()
            z_scores = np.abs((series - mean) / std)
            
            outlier_mask = z_scores > threshold
            outliers = series[outlier_mask].tolist()
            
            result = {
                'method': 'zscore',
                'threshold': threshold,
                'mean': float(mean),
                'std': float(std),
                'outlier_count': len(outliers),
                'outlier_percentage': (len(outliers) / len(series)) * 100,
                'outliers': outliers[:100]
            }
        
        elif method == 'modified_zscore':
            # Modified Z-score (more robust)
            median = series.median()
            mad = np.median(np.abs(series - median))
            modified_z_scores = 0.6745 * (series - median) / mad
            
            outlier_mask = np.abs(modified_z_scores) > threshold
            outliers = series[outlier_mask].tolist()
            
            result = {
                'method': 'modified_zscore',
                'threshold': threshold,
                'median': float(median),
                'mad': float(mad),
                'outlier_count': len(outliers),
                'outlier_percentage': (len(outliers) / len(series)) * 100,
                'outliers': outliers[:100]
            }
        
        else:
            result = {'error': f'Unknown method: {method}'}
        
        return result
    
    def camera_analysis(self) -> Dict[str, Any]:
        """Analyze camera/device usage patterns."""
        if self.data is None:
            return {}
        
        analysis = {}
        
        # Camera distribution
        if 'camera_model' in self.data.columns:
            camera_counts = self.data['camera_model'].value_counts()
            analysis['camera_distribution'] = camera_counts.head(10).to_dict()
            analysis['unique_cameras'] = int(camera_counts.count())
            analysis['most_used_camera'] = camera_counts.index[0] if len(camera_counts) > 0 else None
        
        # Lens distribution
        if 'lens_model' in self.data.columns:
            lens_counts = self.data['lens_model'].value_counts()
            analysis['lens_distribution'] = lens_counts.head(10).to_dict()
        
        # Camera settings analysis
        if 'iso' in self.data.columns:
            analysis['iso_stats'] = self.calculate_descriptive_stats('iso')
        
        if 'aperture' in self.data.columns:
            analysis['aperture_stats'] = self.calculate_descriptive_stats('aperture')
        
        if 'focal_length' in self.data.columns:
            analysis['focal_length_stats'] = self.calculate_descriptive_stats('focal_length')
        
        return analysis
    
    def resolution_analysis(self) -> Dict[str, Any]:
        """Analyze image/video resolution patterns."""
        if self.data is None:
            return {}
        
        analysis = {}
        
        if 'width' in self.data.columns and 'height' in self.data.columns:
            # Create resolution strings
            resolutions = self.data.apply(
                lambda row: f"{int(row['width'])}x{int(row['height'])}" 
                if pd.notna(row['width']) and pd.notna(row['height']) else None,
                axis=1
            ).dropna()
            
            if len(resolutions) > 0:
                res_counts = resolutions.value_counts()
                analysis['resolution_distribution'] = res_counts.head(10).to_dict()
                analysis['most_common_resolution'] = res_counts.index[0] if len(res_counts) > 0 else None
            
            # Calculate megapixels
            megapixels = (self.data['width'] * self.data['height'] / 1_000_000).dropna()
            if len(megapixels) > 0:
                analysis['megapixels_stats'] = {
                    'mean': float(megapixels.mean()),
                    'median': float(megapixels.median()),
                    'min': float(megapixels.min()),
                    'max': float(megapixels.max())
                }
        
        return analysis
    
    def gps_analysis(self) -> Dict[str, Any]:
        """Analyze GPS location patterns."""
        if self.data is None:
            return {}
        
        analysis = {}
        
        if 'gps_latitude' in self.data.columns and 'gps_longitude' in self.data.columns:
            gps_data = self.data[['gps_latitude', 'gps_longitude']].dropna()
            
            analysis['files_with_gps'] = len(gps_data)
            analysis['gps_percentage'] = (len(gps_data) / len(self.data)) * 100
            
            if len(gps_data) > 0:
                analysis['latitude_range'] = {
                    'min': float(gps_data['gps_latitude'].min()),
                    'max': float(gps_data['gps_latitude'].max())
                }
                analysis['longitude_range'] = {
                    'min': float(gps_data['gps_longitude'].min()),
                    'max': float(gps_data['gps_longitude'].max())
                }
                
                # Approximate center point
                analysis['center_point'] = {
                    'latitude': float(gps_data['gps_latitude'].mean()),
                    'longitude': float(gps_data['gps_longitude'].mean())
                }
        
        return analysis
    
    def file_size_analysis(self) -> Dict[str, Any]:
        """Analyze file size patterns."""
        if self.data is None or 'file_size' not in self.data.columns:
            return {}
        
        # Convert to MB
        file_sizes_mb = self.data['file_size'] / (1024 * 1024)
        
        analysis = {
            'total_size_gb': float(file_sizes_mb.sum() / 1024),
            'size_stats_mb': {
                'mean': float(file_sizes_mb.mean()),
                'median': float(file_sizes_mb.median()),
                'min': float(file_sizes_mb.min()),
                'max': float(file_sizes_mb.max()),
                'std': float(file_sizes_mb.std())
            }
        }
        
        # Size distribution by ranges
        bins = [0, 1, 5, 10, 50, 100, float('inf')]
        labels = ['<1MB', '1-5MB', '5-10MB', '10-50MB', '50-100MB', '>100MB']
        size_categories = pd.cut(file_sizes_mb, bins=bins, labels=labels)
        analysis['size_distribution'] = size_categories.value_counts().to_dict()
        
        return analysis
    
    def get_summary_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive summary report.
        
        Returns:
            Dictionary with all analysis results
        """
        if self.data is None:
            return {'error': 'No data available'}
        
        report = {
            'generated_at': datetime.now().isoformat(),
            'total_files': len(self.data),
            'overview': {}
        }
        
        # File type distribution
        if 'file_type' in self.data.columns:
            report['overview']['file_type_distribution'] = self.data['file_type'].value_counts().to_dict()
        
        # Temporal analysis
        if 'created_date' in self.data.columns:
            report['temporal_analysis'] = self.temporal_analysis('created_date')
        
        # Camera analysis (for images)
        if 'camera_model' in self.data.columns:
            report['camera_analysis'] = self.camera_analysis()
        
        # Resolution analysis
        if 'width' in self.data.columns:
            report['resolution_analysis'] = self.resolution_analysis()
        
        # GPS analysis
        if 'gps_latitude' in self.data.columns:
            report['gps_analysis'] = self.gps_analysis()
        
        # File size analysis
        if 'file_size' in self.data.columns:
            report['file_size_analysis'] = self.file_size_analysis()
        
        return report
    
    def export_report(self, output_path: str, format: str = 'json'):
        """
        Export analysis report to file.
        
        Args:
            output_path: Path to output file
            format: Export format ('json' or 'txt')
        """
        report = self.get_summary_report()
        
        if format == 'json':
            with open(output_path, 'w') as f:
                json.dump(report, f, indent=2, default=str)
        elif format == 'txt':
            with open(output_path, 'w') as f:
                self._write_report_text(f, report)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def _write_report_text(self, f, report: Dict[str, Any], indent: int = 0):
        """Write report in text format (recursive)."""
        for key, value in report.items():
            if isinstance(value, dict):
                f.write('  ' * indent + f"{key}:\n")
                self._write_report_text(f, value, indent + 1)
            elif isinstance(value, list):
                f.write('  ' * indent + f"{key}: {len(value)} items\n")
            else:
                f.write('  ' * indent + f"{key}: {value}\n")


if __name__ == "__main__":
    # Example usage with sample data
    import pandas as pd
    import numpy as np
    
    # Create sample data
    np.random.seed(42)
    sample_data = pd.DataFrame({
        'file_name': [f'image_{i}.jpg' for i in range(100)],
        'file_type': ['image'] * 100,
        'file_size': np.random.randint(1000000, 10000000, 100),
        'camera_model': np.random.choice(['Canon EOS 5D', 'Nikon D850', 'Sony A7III'], 100),
        'iso': np.random.choice([100, 200, 400, 800, 1600], 100),
        'aperture': np.random.choice([1.8, 2.8, 4.0, 5.6, 8.0], 100),
        'focal_length': np.random.choice([24, 35, 50, 85, 135], 100),
        'width': 4000,
        'height': 3000,
        'created_date': pd.date_range('2023-01-01', periods=100, freq='D')
    })
    
    # Create analyzer
    analyzer = StatisticalAnalyzer(sample_data)
    
    # Generate report
    report = analyzer.get_summary_report()
    
    print("Statistical Analysis Report")
    print("=" * 50)
    print(f"Total files: {report['total_files']}")
    print(f"\nFile types: {report['overview']['file_type_distribution']}")
    
    if 'camera_analysis' in report:
        print(f"\nMost used camera: {report['camera_analysis'].get('most_used_camera')}")
