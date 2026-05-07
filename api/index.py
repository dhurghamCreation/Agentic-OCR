import sys
import os

# Add the root directory to the path so Vercel can see your files
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# REPLACE "app" WITH THE NAME OF YOUR MAIN VISUAL STUDIO FILE
from app import app as application

# This makes Vercel use YOUR Visual Studio code
handler = application

