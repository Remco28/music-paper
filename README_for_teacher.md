# Band Transcription Tool (MVP)

This app runs locally and converts a song into:
- a full conductor score PDF
- assigned, non-empty part PDFs for concert band instruments

## What You Need (Windows)
1. **Python 3.11** (project runtime)
2. MuseScore 4 (installed and available as `mscore` command, or update `MUSESCORE_CMD` in `config.py`)
3. FFmpeg (required by pydub/yt-dlp workflows)

## First Launch (Windows)
1. Open this project folder.
2. Double-click `start.bat`.
3. A local browser tab opens at `http://localhost:8501`.

## Manual Setup (any OS)
```
python3.11 -m venv venv
# Linux/macOS: source venv/bin/activate
# Windows:     venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py --server.headless true --server.port 8501
```

## WSL Setup (Ubuntu via Deadsnakes)
Use this if Python 3.12 remains your system default and you want a dedicated Python 3.11 project venv.

```bash
sudo apt update
sudo apt install -y software-properties-common
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3.11-dev

# from project root
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run app.py --server.headless true --server.port 8501
```

## Basic Workflow
1. Choose input source:
   - upload local audio file, or
   - paste single-video YouTube URL (no playlists).
2. Click audio preparation button.
3. Run stem separation.
4. Assign each stem to a target instrument (leave unneeded stems as `Unassigned`).
5. Set song metadata and optional simplification settings.
6. Click `Transcribe for Concert Band`.
7. Download ZIP containing rendered outputs.

## Simplification
- `Student Simplification Mode` applies preset cleanup.
- `Advanced Simplification Settings` lets you tune quantization, min note duration, and density threshold.

## Notes
- No login/authentication in MVP.
- Processing runs locally after dependencies are installed.
- If a stage fails, the app displays the command error so issues can be fixed directly.
