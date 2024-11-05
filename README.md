# Hand-Triggered GIF Capture System

## Overview
This project implements a computer vision system that controls video mapping through OSC messages based on hand gesture detection. The system captures video input from a camera, processes it to detect specific hand gestures (open hand in both left and right orientation), and triggers sequences in a video mapping setup through OSC communication. When a gesture is recognized and held for a specified duration, the system also captures a sequence of frames and compiles them into a high-quality GIF.

## System Logic
The application follows this workflow:
1. Continuously processes camera input using computer vision to detect open hand gestures
2. When a valid gesture is detected and maintained for 4 seconds:
   - Sends initial OSC trigger to the video mapping software
   - Captures a sequence of frames
   - Generates a GIF from the captured sequence
   - Sends additional OSC messages to control different mapping sequences
3. The video mapping control is achieved through OSC channels:
   - `/sequences/seq1/play`
   - `/sequences/seq2/play`
   - `/sequences/seq3/play`

## Features
- Real-time hand detection and tracking
- Support for both left and right hand detection
- Visual feedback through an on-screen interface
- Automatic GIF creation from captured frames
- OSC message integration for video mapping control
- Robust camera handling with automatic reconnection

## Requirements
- Python 3.x
- OpenCV
- MediaPipe
- Python-OSC
- NumPy
- Pillow
- tqdm

## Quick Start
1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Run the main script:
```bash
python main.py
```

3. Show an open hand to the camera and hold it for 4 seconds to trigger the video mapping sequence and capture.

## Configuration
The system uses default settings that can be modified in the code:
- Hand detection confidence threshold
- Required hand hold duration
- Frame capture settings
- GIF quality and format settings
- OSC communication parameters

## Output
- Captured GIFs are saved in the `captured_gifs` directory with timestamps in the filename format: `YYYYMMDD_HHMMSS.gif`
- OSC messages are sent to localhost:8000 (configurable in the code)

## Notes
- The system requires a working webcam
- Good lighting conditions will improve hand detection accuracy
- The camera will automatically reinitialize if disconnected
- Ensure your video mapping software is configured to receive OSC messages on the specified port

---
*This is an ongoing project and features may be added or modified in future updates.*
