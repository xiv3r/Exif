# 📸 Exif - Comprehensive Metadata Tool  

<p align="center">
  <img src="https://https://github.com/AryanVBW/Exif/releases/download/Exif/ExIF-Logo_BackgroundWhite.png" alt="Exif Logo" height="200">
</p>

## 🔎 Overview  
**Exif** is a powerful metadata extraction and management tool that supports multiple file types including **images, videos, audio, and documents**.  
It provides:  
- 🖥️ A **modern GUI** for beginners  
- 💻 A **command-line interface (CLI)** for advanced users  

Use Exif to **extract, analyze, edit, and remove metadata** with ease.  

---

## 🖼️ GUI Screenshots  

### Main Interface  
<p align="center">
  <img src="images/screenshot.png" alt="Exif GUI Main Interface" width="800">
</p>

### Document Metadata View  
<p align="center">
  <img src="images/screenshot_pdf.png" alt="Exif GUI PDF Metadata" width="800">
</p>

---

## 🚀 Features  

### Image Support  
- Extract EXIF data (camera model, ISO, shutter speed, etc.)  
- View image properties (dimensions, color profile, format)  
- Extract GPS data & view location on Google Maps  
- Remove metadata for privacy  

### Video Support  
- Extract video metadata (codec, duration, resolution, frame rate)  
- Get audio stream details  
- View technical specifications  

### Audio Support  
- Extract ID3 tags (artist, album, track)  
- View bitrate, sample rate, channels  
- Manage audio properties  

### Document Support  
- Extract metadata from **PDF, DOCX, TXT**  
- Read author, title, creation/modification dates  

### Location Features  
- Generate Google Maps links from GPS metadata  
- View exact file location in browser  

---

## 📂 Supported File Formats  

| Category   | Formats |
|------------|---------|
| **Images** | JPG, JPEG, PNG, GIF, BMP, TIFF |
| **Videos** | MP4, AVI, MOV, MKV |
| **Audio**  | MP3, WAV, FLAC |
| **Docs**   | PDF, DOC/DOCX, TXT |

---

## ⚡ Installation  

### Prerequisites  
- Python **3.8+**  
- Install dependencies:  
```bash
pip install -r requirements.txt
```

### GUI Application  
```bash
git clone https://github.com/AryanVBW/Exif.git
cd Exif
python exif-gui.py
```

### CLI Tool  
```bash
git clone https://github.com/AryanVBW/Exif.git
cd Exif
python exif-cli.py path/to/file
```

---

## 🛠️ Usage Examples  

### Extract metadata from image  
```bash
python exif-cli.py photo.jpg
```

### Save metadata to JSON  
```bash
python exif-cli.py video.mp4 --format json --save metadata.json
```

### Remove EXIF data from image  
```bash
python remove-exif.py image.jpg
```

### Auto-open GPS in Google Maps  
```bash
python exif-cli.py photo.jpg --open-maps
```

### Batch process multiple files  
```bash
python exif-cli.py *.jpg --format json
```

---

## 📖 Command Reference  

| Command | Description | Example |
|---------|-------------|---------|
| `--format json` | Export metadata in JSON format | `python exif-cli.py file.jpg --format json` |
| `--save file.json` | Save metadata to file | `python exif-cli.py file.mp4 --save meta.json` |
| `--open-maps` | Open GPS location in Google Maps | `python exif-cli.py photo.jpg --open-maps` |
| `-all=` | Remove all metadata from file | `python remove-exif.py file.jpg` |
| `-overwrite_original` | Overwrite files without backup | `python exif-cli.py file.jpg -overwrite_original` |

---

## 🏷️ Metadata Fields Explained  

- **EXIF (Exchangeable Image File Format)** → Camera settings (aperture, shutter speed, ISO, flash, orientation)  
- **IPTC (International Press Telecommunications Council)** → Captions, copyright, creator, keywords  
- **XMP (Extensible Metadata Platform)** → Adobe fields (title, description, author, subject)  
- **GPS Metadata** → Latitude, longitude, altitude, timestamp  
- **Audio Tags (ID3, Vorbis, etc.)** → Artist, album, track number, genre  

---

## 🛑 Troubleshooting  

| Problem | Solution |
|---------|----------|
| `Permission denied` | Run with `sudo` on Linux/macOS |
| Backup files clutter folder (`_original`) | Use `-overwrite_original` flag |
| Missing metadata fields | Not all file formats support every tag |
| Garbled characters in output | Use UTF-8 encoding: `exiftool -charset UTF8 file.jpg` |
| GUI not starting | Ensure all dependencies from `requirements.txt` are installed |

---

## ❓ FAQ  

**Q1: Is Exif safe to use?**  
✅ Yes, but always back up your files before modifying metadata.  

**Q2: Does Exif overwrite files?**  
By default, backups are created. Use `-overwrite_original` to skip them.  

**Q3: Is it cross-platform?**  
Yes, works on **Windows, macOS, and Linux**.  

**Q4: Can Exif handle videos and audio files?**  
Yes, basic metadata extraction is supported for video and audio formats.  

**Q5: How can I see all available metadata fields in a file?**  
Run:  
```bash
python exif-cli.py file.jpg --format json
```

---

## 📜 License  
This project is licensed under the MIT License – see [LICENSE](LICENSE).  

---

## 👨‍💻 Credits  
- Developed by **AryanVBW**  
- Inspired by David Bombal’s [Exif script](https://github.com/davidbombal/red-python-scripts/blob/main/exif.py)  
- Thanks to the open-source community for contributions and testing  

---

