#!/usr/bin/env python3
"""
Chart Visualizer - Create interactive and static visualizations.

This module provides the ChartGenerator class for creating various chart types
including pie charts, bar charts, timelines, scatter plots, histograms, and more.
"""

from __future__ import annotations
from typing import Dict, List, Any, Optional, Union, TYPE_CHECKING
import os
from pathlib import Path

try:
    import pandas as pd
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


class ChartGenerator:
    """
    Generate various chart types for metadata visualization.
    
    Supports both interactive (Plotly) and static (Matplotlib) charts.
    """
    
    def __init__(self, data: pd.DataFrame, theme: str = 'plotly_dark'):
        """
        Initialize the chart generator.
        
        Args:
            data: pandas DataFrame with metadata
            theme: Plotly theme ('plotly', 'plotly_dark', 'plotly_white')
        """
        if not PLOTLY_AVAILABLE:
            raise ImportError("plotly is required for ChartGenerator")
        
        self.data = data
        self.theme = theme
        self.figures = {}
    
    def create_pie_chart(
        self, 
        field: str, 
        title: str = None,
        top_n: int = 10,
        show_others: bool = True
    ) -> go.Figure:
        """
        Create a pie chart for categorical data.
        
        Args:
            field: Column name to visualize
            title: Chart title
            top_n: Number of top items to show
            show_others: Whether to group remaining items as "Others"
        
        Returns:
            Plotly Figure object
        """
        if field not in self.data.columns:
            raise ValueError(f"Field '{field}' not found in data")
        
        # Count values
        value_counts = self.data[field].dropna().value_counts()
        
        if len(value_counts) == 0:
            # Return empty chart
            fig = go.Figure()
            fig.add_annotation(
                text="No data available",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
            return fig
        
        # Get top N and optionally group others
        if len(value_counts) > top_n and show_others:
            top_values = value_counts.head(top_n)
            others_sum = value_counts.iloc[top_n:].sum()
            
            labels = list(top_values.index) + ['Others']
            values = list(top_values.values) + [others_sum]
        else:
            labels = list(value_counts.index)
            values = list(value_counts.values)
        
        # Create pie chart
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=0.3,  # Donut chart
            textposition='auto',
            textinfo='label+percent',
            hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
        )])
        
        fig.update_layout(
            title=title or f'{field.replace("_", " ").title()} Distribution',
            template=self.theme,
            showlegend=True,
            height=500
        )
        
        return fig
    
    def create_bar_chart(
        self,
        field: str,
        title: str = None,
        top_n: int = 15,
        horizontal: bool = True
    ) -> go.Figure:
        """
        Create a bar chart for categorical data.
        
        Args:
            field: Column name to visualize
            title: Chart title
            top_n: Number of top items to show
            horizontal: Whether to create horizontal bars
        
        Returns:
            Plotly Figure object
        """
        if field not in self.data.columns:
            raise ValueError(f"Field '{field}' not found in data")
        
        # Count values
        value_counts = self.data[field].dropna().value_counts().head(top_n)
        
        if len(value_counts) == 0:
            fig = go.Figure()
            fig.add_annotation(text="No data available", x=0.5, y=0.5, showarrow=False)
            return fig
        
        # Create bar chart
        if horizontal:
            fig = go.Figure(data=[go.Bar(
                y=value_counts.index,
                x=value_counts.values,
                orientation='h',
                marker=dict(
                    color=value_counts.values,
                    colorscale='Viridis',
                    showscale=True
                ),
                text=value_counts.values,
                textposition='auto'
            )])
            fig.update_yaxes(title='')
            fig.update_xaxes(title='Count')
        else:
            fig = go.Figure(data=[go.Bar(
                x=value_counts.index,
                y=value_counts.values,
                marker=dict(
                    color=value_counts.values,
                    colorscale='Viridis',
                    showscale=True
                ),
                text=value_counts.values,
                textposition='auto'
            )])
            fig.update_xaxes(title='')
            fig.update_yaxes(title='Count')
        
        fig.update_layout(
            title=title or f'Top {top_n} {field.replace("_", " ").title()}',
            template=self.theme,
            showlegend=False,
            height=500
        )
        
        return fig
    
    def create_timeline(
        self,
        date_field: str = 'created_date',
        title: str = None,
        group_by: str = 'day'
    ) -> go.Figure:
        """
        Create a timeline chart showing files over time.
        
        Args:
            date_field: Date column name
            title: Chart title
            group_by: Grouping period ('day', 'week', 'month', 'year')
        
        Returns:
            Plotly Figure object
        """
        if date_field not in self.data.columns:
            raise ValueError(f"Field '{date_field}' not found in data")
        
        # Convert to datetime
        dates = pd.to_datetime(self.data[date_field], errors='coerce').dropna()
        
        if len(dates) == 0:
            fig = go.Figure()
            fig.add_annotation(text="No date data available", x=0.5, y=0.5, showarrow=False)
            return fig
        
        # Group by period
        df_dates = pd.DataFrame({'date': dates})
        
        if group_by == 'day':
            df_dates['period'] = df_dates['date'].dt.date
        elif group_by == 'week':
            df_dates['period'] = df_dates['date'].dt.to_period('W').astype(str)
        elif group_by == 'month':
            df_dates['period'] = df_dates['date'].dt.to_period('M').astype(str)
        elif group_by == 'year':
            df_dates['period'] = df_dates['date'].dt.year
        
        counts = df_dates.groupby('period').size().reset_index(name='count')
        
        # Create timeline
        fig = go.Figure(data=[
            go.Scatter(
                x=counts['period'],
                y=counts['count'],
                mode='lines+markers',
                marker=dict(size=8),
                line=dict(width=2),
                fill='tozeroy',
                hovertemplate='<b>%{x}</b><br>Files: %{y}<extra></extra>'
            )
        ])
        
        fig.update_layout(
            title=title or f'Files Over Time (by {group_by})',
            xaxis_title='Date',
            yaxis_title='Number of Files',
            template=self.theme,
            height=500,
            hovermode='x unified'
        )
        
        return fig
    
    def create_scatter_plot(
        self,
        x_field: str,
        y_field: str,
        title: str = None,
        color_field: str = None,
        size_field: str = None
    ) -> go.Figure:
        """
        Create a scatter plot.
        
        Args:
            x_field: X-axis column name
            y_field: Y-axis column name
            title: Chart title
            color_field: Column for color coding
            size_field: Column for marker size
        
        Returns:
            Plotly Figure object
        """
        if x_field not in self.data.columns or y_field not in self.data.columns:
            raise ValueError(f"Fields '{x_field}' or '{y_field}' not found in data")
        
        # Filter valid data
        plot_data = self.data[[x_field, y_field]].dropna()
        
        if color_field and color_field in self.data.columns:
            plot_data[color_field] = self.data.loc[plot_data.index, color_field]
        
        if size_field and size_field in self.data.columns:
            plot_data[size_field] = self.data.loc[plot_data.index, size_field]
        
        # Create scatter plot
        fig = px.scatter(
            plot_data,
            x=x_field,
            y=y_field,
            color=color_field if color_field else None,
            size=size_field if size_field else None,
            template=self.theme,
            title=title or f'{y_field} vs {x_field}',
            hover_data=plot_data.columns.tolist()
        )
        
        fig.update_layout(height=500)
        
        return fig
    
    def create_histogram(
        self,
        field: str,
        title: str = None,
        bins: int = 30,
        show_stats: bool = True
    ) -> go.Figure:
        """
        Create a histogram with optional statistical overlays.
        
        Args:
            field: Column name to visualize
            title: Chart title
            bins: Number of bins
            show_stats: Whether to show mean/median lines
        
        Returns:
            Plotly Figure object
        """
        if field not in self.data.columns:
            raise ValueError(f"Field '{field}' not found in data")
        
        values = self.data[field].dropna()
        
        if len(values) == 0:
            fig = go.Figure()
            fig.add_annotation(text="No data available", x=0.5, y=0.5, showarrow=False)
            return fig
        
        # Create histogram
        fig = go.Figure(data=[go.Histogram(
            x=values,
            nbinsx=bins,
            marker=dict(
                color='rgba(100, 200, 255, 0.7)',
                line=dict(color='rgba(100, 200, 255, 1)', width=1)
            ),
            hovertemplate='Range: %{x}<br>Count: %{y}<extra></extra>'
        )])
        
        # Add statistical lines
        if show_stats:
            mean_val = values.mean()
            median_val = values.median()
            
            fig.add_vline(
                x=mean_val,
                line_dash="dash",
                line_color="red",
                annotation_text=f"Mean: {mean_val:.2f}",
                annotation_position="top"
            )
            
            fig.add_vline(
                x=median_val,
                line_dash="dot",
                line_color="green",
                annotation_text=f"Median: {median_val:.2f}",
                annotation_position="bottom"
            )
        
        fig.update_layout(
            title=title or f'{field.replace("_", " ").title()} Distribution',
            xaxis_title=field.replace("_", " ").title(),
            yaxis_title='Frequency',
            template=self.theme,
            height=500,
            showlegend=False
        )
        
        return fig
    
    def create_box_plot(
        self,
        field: str,
        group_by: str = None,
        title: str = None
    ) -> go.Figure:
        """
        Create a box plot to show distribution and outliers.
        
        Args:
            field: Column name to visualize
            group_by: Column to group by
            title: Chart title
        
        Returns:
            Plotly Figure object
        """
        if field not in self.data.columns:
            raise ValueError(f"Field '{field}' not found in data")
        
        if group_by and group_by in self.data.columns:
            fig = px.box(
                self.data,
                y=field,
                x=group_by,
                template=self.theme,
                title=title or f'{field} by {group_by}'
            )
        else:
            fig = go.Figure(data=[go.Box(
                y=self.data[field].dropna(),
                name=field,
                boxmean='sd'  # Show mean and standard deviation
            )])
            
            fig.update_layout(
                title=title or f'{field.replace("_", " ").title()} Distribution',
                yaxis_title=field.replace("_", " ").title(),
                template=self.theme,
                height=500
            )
        
        return fig
    
    def create_heatmap(
        self,
        fields: List[str] = None,
        title: str = "Metadata Completeness Heatmap"
    ) -> go.Figure:
        """
        Create a heatmap showing metadata completeness.
        
        Args:
            fields: List of fields to include (None for all)
            title: Chart title
        
        Returns:
            Plotly Figure object
        """
        if fields:
            data_subset = self.data[fields]
        else:
            data_subset = self.data
        
        # Create completeness matrix (1 if not null, 0 if null)
        completeness = (~data_subset.isnull()).astype(int)
        
        # Limit rows for readability
        if len(completeness) > 100:
            completeness = completeness.head(100)
        
        fig = go.Figure(data=go.Heatmap(
            z=completeness.values,
            x=completeness.columns,
            y=[f"File {i+1}" for i in range(len(completeness))],
            colorscale=[[0, 'red'], [1, 'green']],
            text=completeness.values,
            hovertemplate='Field: %{x}<br>File: %{y}<br>Present: %{z}<extra></extra>',
            showscale=True
        ))
        
        fig.update_layout(
            title=title,
            xaxis_title='Metadata Fields',
            yaxis_title='Files',
            template=self.theme,
            height=max(500, len(completeness) * 10)
        )
        
        return fig
    
    def save_figure(
        self,
        fig: go.Figure,
        filename: str,
        format: str = 'html',
        output_dir: str = 'exports'
    ):
        """
        Save a figure to file.
        
        Args:
            fig: Plotly Figure object
            filename: Output filename (without extension)
            format: Output format ('html', 'png', 'jpg', 'svg', 'pdf')
            output_dir: Output directory
        """
        # Create output directory
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Construct full path
        filepath = os.path.join(output_dir, f"{filename}.{format}")
        
        if format == 'html':
            fig.write_html(filepath)
        else:
            # Requires kaleido
            try:
                fig.write_image(filepath, format=format)
            except Exception as e:
                print(f"Error saving image: {e}")
                print("Note: Install kaleido for image export: pip install kaleido")
                # Fallback to HTML
                html_path = os.path.join(output_dir, f"{filename}.html")
                fig.write_html(html_path)
                print(f"Saved as HTML instead: {html_path}")
        
        print(f"Figure saved: {filepath}")
    
    def create_dashboard_charts(self) -> Dict[str, go.Figure]:
        """
        Create a complete set of dashboard charts.
        
        Returns:
            Dictionary of chart names to Figure objects
        """
        charts = {}
        
        # File type distribution
        if 'file_type' in self.data.columns:
            charts['file_type_pie'] = self.create_pie_chart('file_type', 'File Type Distribution')
        
        # Camera distribution (for images)
        if 'camera_model' in self.data.columns:
            charts['camera_bar'] = self.create_bar_chart('camera_model', 'Top Cameras Used')
        
        # Timeline
        if 'created_date' in self.data.columns:
            charts['timeline'] = self.create_timeline('created_date', 'Files Over Time')
        
        # File size distribution
        if 'file_size' in self.data.columns:
            file_size_mb = self.data['file_size'] / (1024 * 1024)
            temp_data = self.data.copy()
            temp_data['file_size_mb'] = file_size_mb
            temp_gen = ChartGenerator(temp_data, self.theme)
            charts['file_size_hist'] = temp_gen.create_histogram('file_size_mb', 'File Size Distribution (MB)')
        
        # Resolution scatter (if width and height available)
        if 'width' in self.data.columns and 'height' in self.data.columns:
            charts['resolution_scatter'] = self.create_scatter_plot(
                'width', 'height', 
                'Resolution Distribution',
                color_field='file_type' if 'file_type' in self.data.columns else None
            )
        
        return charts
    
    def show_all_charts(self, charts: Dict[str, go.Figure] = None):
        """
        Display all charts in browser.
        
        Args:
            charts: Dictionary of charts (if None, creates dashboard charts)
        """
        if charts is None:
            charts = self.create_dashboard_charts()
        
        for name, fig in charts.items():
            fig.show()


if __name__ == "__main__":
    # Example usage
    import pandas as pd
    import numpy as np
    
    # Create sample data
    np.random.seed(42)
    sample_data = pd.DataFrame({
        'file_name': [f'file_{i}.jpg' for i in range(100)],
        'file_type': np.random.choice(['image', 'video', 'audio'], 100, p=[0.7, 0.2, 0.1]),
        'file_size': np.random.randint(1000000, 50000000, 100),
        'camera_model': np.random.choice(['Canon EOS 5D', 'Nikon D850', 'Sony A7III', 'iPhone 13'], 100),
        'width': np.random.choice([1920, 3840, 4000, 6000], 100),
        'height': np.random.choice([1080, 2160, 3000, 4000], 100),
        'created_date': pd.date_range('2023-01-01', periods=100, freq='D')
    })
    
    # Create visualizer
    viz = ChartGenerator(sample_data)
    
    # Create and display charts
    print("Creating visualizations...")
    
    # Create pie chart
    fig1 = viz.create_pie_chart('file_type', 'File Type Distribution')
    viz.save_figure(fig1, 'file_type_distribution', format='html')
    
    # Create bar chart
    fig2 = viz.create_bar_chart('camera_model', 'Camera Usage')
    viz.save_figure(fig2, 'camera_usage', format='html')
    
    # Create timeline
    fig3 = viz.create_timeline('created_date', 'Files Over Time')
    viz.save_figure(fig3, 'timeline', format='html')
    
    print("\nCharts saved to exports/ directory")
    print("Open the .html files in a web browser to view them")
