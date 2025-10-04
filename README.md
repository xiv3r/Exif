# Exif - Comprehensive Metadata Tool

<p align="center">
  <img src="https://github.com/AryanVBW/Exif/releases/download/Exif/ExIF-Logo_BackgroundWhite.png" alt="Exif Logo" height="200">
</p>

## Overview
Exif is a powerful metadata extraction tool that supports multiple file types including images, videos, audio files, and documents. It provides both a modern GUI interface and a comprehensive CLI tool for extracting detailed metadata from your files.

## GUI Application Screenshots

### Main Interface
<p align="center">
  <img src="images/screenshot.png" alt="Exif GUI Main Interface" width="800">
</p>

### Document Metadata View
<p align="center">
  <img src="images/screenshot_pdf.png" alt="Exif GUI PDF Metadata" width="800">
</p>

## Features

### 🖼️ Image Support
- Extract EXIF data from images (JPG, JPEG, PNG, GIF, BMP, TIFF)
- View image properties (dimensions, format, color profile)
- Extract GPS coordinates and view locations on Google Maps
- Remove EXIF data for privacy

### 🎥 Video Support
- Extract video metadata (duration, resolution, codec, frame rate)
- Get audio stream information
- View technical specifications

### 🎵 Audio Support
- Extract ID3 tags and audio properties
- View artist, album, and track information
- Get technical details (bitrate, sample rate, channels)

### 📄 Document Support
- Extract metadata from PDF files
- Read DOCX document properties
- View creation and modification dates

### 🌐 Location Features
- Extract GPS coordinates from images
- Generate Google Maps links
- View locations directly in your browser

### 📊 Visualization Dashboard (NEW!)
- **Interactive visualizations** of metadata across multiple files
- **Dark mode dashboard** with Power BI-style layout
- **7+ chart types**: pie charts, bar charts, timelines, scatter plots, histograms, box plots
- **Statistical analysis**: file type distribution, camera usage, ISO/aperture patterns, resolution analysis
- **Export options**: View charts in browser, save as HTML
- **Fully interactive**: Hover for details, zoom, pan, and more

## Installation

### Prerequisites
- Python 3.8 or higher
- Required libraries (install using pip):
```bash
pip install -r requirements.txt
```

### Quick Setup
Run the automated setup script:
```bash
bash setup.sh
```

This will:
- Create a virtual environment
- Install all dependencies
- Set up the project structure
- Configure the environment

### GUI Application
1. Clone the repository:
```bash
git clone https://github.com/AryanVBW/Exif.git
cd Exif
```

2. Run the GUI application:
```bash
python exif-gui.py
```

### CLI Tool
1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Basic usage:
```bash
python exif-cli.py path/to/your/file
```

3. Advanced options:
```bash
# View metadata in JSON format
python exif-cli.py path/to/your/file --format json

# Save metadata to a file
python exif-cli.py path/to/your/file --save metadata.json

# Automatically open Google Maps for location data
python exif-cli.py path/to/your/file --open-maps
```

### 📊 Visualization Dashboard

#### Quick Test (Sample Data)
Run a quick test with automatically generated sample data:
```bash
python test_visualizations.py
```
This will:
- Generate 150 sample files with realistic metadata
- Create 7 interactive visualizations
- Open the dashboard in your browser
- Save charts to `exports/test_visualizations/`

#### Full Demo (Your Files)
Process your actual media files and create visualizations:
```bash
python demo_visualizations.py
```
This will:
- Scan your `media/` directory for files
- Extract metadata from all supported file types
- Perform statistical analysis
- Generate comprehensive visualizations
- Create an interactive dashboard
- Save to `exports/` directory

#### Dashboard Features
The visualization dashboard includes:
- **File Types**: Pie chart showing file type distribution
- **Camera Models**: Bar chart of most-used cameras
- **Timeline**: Line chart of files over time
- **File Sizes**: Histogram with size distribution
- **Resolution**: Scatter plot of image dimensions
- **ISO Settings**: Distribution of ISO values
- **Aperture**: Box plot of aperture settings by camera

All charts are **fully interactive**:
- Hover to see detailed information
- Click and drag to zoom into specific areas
- Double-click to reset the view
- Use toolbar to save charts as PNG
- Click "⤢" icon to open chart in new tab

## Supported File Types

### Images
- JPG/JPEG
- PNG
- GIF
- BMP
- TIFF

### Videos
- MP4
- AVI
- MOV
- MKV

### Audio
- MP3
- WAV
- FLAC

### Documents
- PDF
- DOC/DOCX
- TXT

## Requirements

### Core Dependencies
- Python 3.8+
- Pillow
- exifread
- moviepy
- eyed3
- python-magic
- ffmpeg
- pdfplumber
- python-docx
- mutagen
- rich

### Visualization Dependencies
- plotly (5.11+) - Interactive charts
- pandas - Data manipulation
- numpy - Numerical operations
- matplotlib - Static visualizations
- seaborn - Statistical graphics

### Installation
All dependencies can be installed with:
```bash
pip install -r requirements.txt
pip install -r requirements-dashboard.txt
```

Or use the automated setup:
```bash
bash setup.sh
```

## Project Structure

```
Exif/
├── exif-gui.py              # GUI application (tkinter-based)
├── exif-cli.py              # Command-line interface tool
├── exif-main.py             # Main CLI script
├── exif.py                  # Terminal output version
├── remove-exif.py           # Remove EXIF data from images
├── test_visualizations.py   # Quick test with sample data
├── demo_visualizations.py   # Full demo with your files
├── setup.sh                 # Automated setup script
├── requirements.txt         # Core dependencies
├── requirements-dashboard.txt # Visualization dependencies
├── core/                    # Core modules
│   ├── data_models.py       # Data structures (Pydantic models)
│   ├── metadata_aggregator.py # Batch processing & extraction
│   └── data_storage.py      # SQLite database operations
├── analysis/                # Analysis modules
│   └── statistical_analyzer.py # Statistical analysis
├── visualization/           # Visualization modules
│   └── visualizer.py        # Chart generation (Plotly)
├── exports/                 # Generated visualizations
├── media/                   # Your media files (for processing)
└── data/                    # Database storage
```

## Usage Examples

### Extract Metadata from Single File
```bash
python exif-cli.py photo.jpg
```

### Process Multiple Files
```bash
python demo_visualizations.py
```

### View in GUI
```bash
python exif-gui.py
```

### Quick Visualization Test
```bash
python test_visualizations.py
```

## Dashboard Screenshots
The visualization dashboard provides a modern, dark-mode interface similar to Power BI:
- All charts visible at once (no scrolling)
- 4x2 grid layout on desktop
- Fully responsive design
- Interactive tooltips and zoom
- Professional dark theme

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Credits
Created by AryanVBW

## Features
- Extract exif data of images jpg, jpeg, png.
- Clear exif data of images.
- Save data in a text file.
- Modern GUI application for easy metadata extraction.
- Support for multiple file types including images, videos, and audio.
## Supported Formats
 - Images:
     - PNG, JPG, JPEG, GIF, BMP, TIFF
 - **Videos** :
     - MP4, MKV, AVI, MOV
 - **Audio** :
     - MP3 (limited support, additional library may be required)
 - OutputThe script will display metadata information for each file.If the output is set to a file, the results will be saved in exif_data.txt.
## Installation and usage instructions:

### Command Line Usage
- Add .jpg to subfolder ./images from where the script is stored. 
- Note: Most social media sites strip exif data from uploaded photos.

### GUI Application Usage
1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Run the GUI application:
```bash
python exif-gui.py
```

3. Features of the GUI application:
   - Modern, professional interface
   - File type auto-detection
   - Support for multiple file formats
   - Save metadata to JSON or text files
   - Easy-to-use file browser
   - Detailed metadata display

## Prerequisites 
1. Install python3
   - Debian, Ubuntu, Etc: `sudo apt-get install python3`
   - Fedora, Oracle, Red Hat, etc: `su -c "yum install python"`
   - Windows: [Python for Windows](https://www.python.org/downloads/windows/)

2. Install required libraries:
   ```bash 
   python3 -m pip install --upgrade pip
   python3 -m pip install --upgrade Pillow
   pip install Pillow moviepy eyed3 python-magic
   ```

## Installation 

### Command Line Tools
```bash
git clone https://github.com/AryanVBW/Exif.git
cd Exif
python3 exif-main.py
```

### To remove exif data from images, use the following command:
```bash
python3 remove-exif.py
```
## 📸🎥🔍 Direct Use 

Discover the hidden details in your media files effortlessly! Simply run this script and:

  - 🌐 Enter the path to your images, videos, or audio files.
  - 💾 Choose where to save the extracted Exif data.

Unearth the metadata magic with style!

### Command Line Usage
```bash
git clone https://github.com/AryanVBW/Exif.git
cd Exif
python3 exif-raw.py
```

### For printing JPG output directly on terminal or PowerShell:
```bash
git clone https://github.com/AryanVBW/Exif.git
cd Exif
python3 exif.py
```

### GUI Application
For a more user-friendly experience, use the GUI application:
```bash
python exif-gui.py
```

The GUI application provides:
- 🖼️ Easy file selection
- 🔍 Auto file type detection
- 📊 Detailed metadata display
- 💾 Save options (JSON/TXT)
- 🎨 Modern, professional interface

### Thank You 🙏

This project was inspired by the incredible YouTube tutorial "[EXIF Data Project in Python](https://youtu.be/A_itRNhbgZk?si=sHaWhNV9tn4cVwWC)", which provided valuable insights into building an Exif data tool.

A heartfelt thanks to David Bombal for his fantastic [exif.py script on GitHub](https://github.com/davidbombal/red-python-scripts/blob/main/exif.py), which served as a guiding resource during development.

To the open-source community, developers, and testers: your support makes this project thrive.

Let's continue exploring the stories hidden within our media files!
<p align="center"> 
  Visitor count<br>
  <img src="https://profile-counter.glitch.me/Aryanvbw/count.svg" />
</p>
