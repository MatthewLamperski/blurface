from distutils.core import setup
import py2exe
import os
import sys

# Find the directory where the Haar cascade files are located
haar_cascade_directory = os.path.dirname('.')
haar_cascade_files = [os.path.join(haar_cascade_directory, 'haarcascade_frontalface_default.xml'),
                      os.path.join(haar_cascade_directory, 'haarcascade_profileface.xml')]

# Define the data_files to include the Haar cascade files
data_files = [('data', haar_cascade_files)]

# Define options for py2exe
options = {
    'py2exe': {
        'bundle_files': 1,  # Bundle everything into a single file
        'compressed': True, # Compress the library archive
        'includes': ['PyQt5.QtWidgets', 'cv2'], # Include these modules
    }
}

# Setup configuration
setup(
    name='BlurFace',
    version='1.0',
    description='Record a video with all faces blurred!',
    author='Matthew Lamperski',
    windows=[{'script': 'video_capture_widget.py'}],  # Replace with your main script
    options=options,
    zipfile=None,  # Include everything in the exe, instead of a zipfile
    data_files=data_files
)
