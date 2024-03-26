import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'utils')))
from VideoCutter import *

VIDEO_PATH = r"C:\Users\aymen\OneDrive\Bureau\test-yolo_with-venv\video\v1.mp4"
a=detect_and_categorize_objects(VIDEO_PATH)
for key, value in a.items():
    print(key, value)
    extract_video_segment(VIDEO_PATH,categorisation=key,time_segments=value)