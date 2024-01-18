from setuptools import setup

APP = ['video_capture_widget.py']
DATA_FILES = ['haarcascade_frontalface_default.xml', 'haarcascade_profileface.xml']
OPTIONS = {
    'argv_emulation': False,
    'packages': ['cv2', 'numpy', 'PyQt5', ],
    'plist': {
        'CFBundleName': 'BlurFace',
        'CFBundleDisplayName': 'BlurFace',
        'CFBundleIdentifier': 'com.tabslab.blurface',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0',
        'NSCameraUsageDescription': 'This application requires camera access to record video.'
    },
    'iconfile': 'icon.icns',
    'resources': DATA_FILES,
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)