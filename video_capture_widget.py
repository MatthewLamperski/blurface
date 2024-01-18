import os
import sys
import tempfile
import time
import cv2
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QPushButton, QComboBox, QFileDialog, QHBoxLayout
from PyQt5.QtGui import QImage, QPixmap, QGuiApplication
from PyQt5.QtCore import QTimer, Qt, QSize, QEvent

class AutoFontComboBox(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.adjustFontSize()

    def adjustFontSize(self):
        # Calculate an appropriate font size based on the combo box's height
        font_size = max(8, self.height() // 16)  # Example calculation
        font = self.font()
        font.setPointSize(font_size)
        self.setFont(font)

class AutoFontButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.adjustFontSize()

    def adjustFontSize(self):
        # Calculate an appropriate font size based on the button's height
        font_size = max(8, self.height() // 16)  # Example calculation
        font = self.font()
        font.setPointSize(font_size)
        self.setFont(font)


class VideoCaptureWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("BlurFace")

        self.video_capture = cv2.VideoCapture(0)
        # Obtain the original size of the video feed
        self.original_width = self.video_capture.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.original_height = self.video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self.aspect_ratio = self.original_width / self.original_height

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

        # Set the minimum size of the window to some fraction of the original video size
        self.setMinimumSize(QSize(self.original_width // 4, self.original_height // 4))

        self.face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
        self.profile_cascade = cv2.CascadeClassifier('haarcascade_profileface.xml')

        self.record = False
        self.blurred = True
        self.video_writer = None
        self.out_file_path = None

        self.setup_ui()


    def setup_ui(self):
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)

        self.webcam_selector = AutoFontComboBox(self)
        self.enumerate_webcams()
        self.webcam_selector.currentIndexChanged.connect(self.select_webcam)

        self.record_button = AutoFontButton("Record", self)
        self.record_button.clicked.connect(self.toggle_recording)

        self.blur_button = AutoFontButton("Toggle Blur", self)
        self.blur_button.clicked.connect(self.toggle_blur)

        control_layout = QHBoxLayout()
        control_layout.addWidget(self.webcam_selector)
        control_layout.addWidget(self.record_button)
        control_layout.addWidget(self.blur_button)

        layout = QVBoxLayout()
        layout.addWidget(self.image_label)
        layout.addLayout(control_layout)
        self.setLayout(layout)

    def toggle_blur(self):
        self.blurred = not self.blurred

    def enumerate_webcams(self):
        self.webcam_selector.clear()
        index = 0
        while True:
            capture = cv2.VideoCapture(index)
            if not capture.read()[0]:
                break
            else:
                self.webcam_selector.addItem(f"Webcam {index}")
                capture.release()
            index += 1

    def select_webcam(self, index):
        # Release the current capture object
        if self.video_capture is not None:
            self.video_capture.release()
            time.sleep(0.5)  # Short delay to allow camera release

        # Attempt to initialize the new camera
        attempts = 5
        while attempts > 0:
            self.video_capture = cv2.VideoCapture(index)
            if self.video_capture.isOpened():
                ret, _ = self.video_capture.read()
                if ret:
                    break  # Camera initialized and frame read successfully
            time.sleep(1)  # Wait a bit before retrying
            attempts -= 1

        if attempts == 0:
            print("Failed to activate new camera.")
            # Handle the failure (e.g., revert to a default camera or show an error message)

    def toggle_recording(self):
        if self.record:
            self.record = False
            self.record_button.setText("Record")
            self.video_writer.release()

            options = QFileDialog.Options()
            file_name, _ = QFileDialog.getSaveFileName(self, "Save Video", "", "MP4 Files (*.mp4)", options=options)
            if file_name:
                os.rename(self.out_file_path, file_name)
        else:
            self.record_button.setText("Stop")
            self.record = True

            self.out_file_path = os.path.join(tempfile.gettempdir(), "tmp_recording.mp4")

            self.fps = self.video_capture.get(cv2.CAP_PROP_FPS)
            print(f"FPS: {self.fps}")
            if self.fps == 0:
                self.fps = 20.0

            fourcc = cv2.VideoWriter_fourcc(*'MP4V')
            w = int(self.video_capture.get(3))
            h = int(self.video_capture.get(4))
            self.video_writer = cv2.VideoWriter(self.out_file_path, fourcc, self.fps, (w, h))




    def update_frame(self):
        ret, frame = self.video_capture.read()
        if ret:

            if self.blurred:
                frame_small = cv2.resize(frame, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_LINEAR)

                gray = cv2.cvtColor(frame_small, cv2.COLOR_RGB2GRAY)
                gray = cv2.equalizeHist(gray)

                faces = self.face_cascade.detectMultiScale(gray, 1.1, 4, minSize=(30, 30))
                faces = [(x * 2, y * 2, w * 2, h * 2) for (x, y, w, h) in faces]

                profiles = self.profile_cascade.detectMultiScale(gray, 1.1, 4, minSize=(30, 30))
                profiles = [(x * 2, y * 2, w * 2, h * 2) for (x, y, w, h) in profiles]

                for (x, y, w, h) in faces:
                    face_region = frame[y:y + h, x:x + w]
                    blurred_face = cv2.GaussianBlur(face_region, (99, 99), 30)
                    frame[y:y + h, x:x + w] = blurred_face
                    border_color = (0, 255, 0)
                    border_thickness = 2
                    cv2.rectangle(frame, (x, y), (x + w, y + h), border_color, border_thickness)

                for (x, y, w, h) in profiles:
                    face_region = frame[y:y + h, x:x + w]
                    blurred_face = cv2.GaussianBlur(face_region, (99, 99), 30)
                    frame[y:y + h, x:x + w] = blurred_face
                    border_color = (0, 255, 0)
                    border_thickness = 2
                    cv2.rectangle(frame, (x, y), (x + w, y + h), border_color, border_thickness)

            if self.record:
                self.video_writer.write(frame)

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            aspect_ratio = frame.shape[1] / frame.shape[0]

            # Calculate new dimensions that fit within the label's dimensions while maintaining aspect ratio.
            new_width = min(self.image_label.width(), int(self.image_label.height() * aspect_ratio))
            new_height = min(self.image_label.height(), int(self.image_label.width() / aspect_ratio))

            # Resize the frame.
            resized_frame = cv2.resize(frame, (new_width, new_height))

            # Calculate the new bytesPerLine for the resized image
            bytes_per_line = 3 * new_width  # 3 channels (RGB) for QImage

            qt_image = QImage(resized_frame.data, resized_frame.shape[1], resized_frame.shape[0], bytes_per_line,
                              QImage.Format_RGB888)
            self.image_label.setPixmap(QPixmap.fromImage(qt_image))



    def resizeEvent(self, event):
        # Calculate the sizes based on aspect ratio
        new_width = event.size().width()
        new_height = int(new_width / self.aspect_ratio)

        # Prevent the window from being smaller than a minimum size
        if new_width < self.original_width // 4 or new_height < self.original_height // 4:
            new_width = max(new_width, self.original_width // 4)
            new_height = max(new_height, self.original_height // 4)

        # Resize the window with the new aspect ratio constrained dimensions
        self.resize(new_width, new_height)
        super().resizeEvent(event)

    def eventFilter(self, source, event):
        # Intercept the resize events
        if event.type() == QEvent.Resize:
            # Maintain the aspect ratio
            new_size = event.size()
            width = new_size.width()
            height = int(width / self.aspect_ratio)
            new_size.setHeight(height)
            self.resize(new_size)
            return True
        return super().eventFilter(source, event)

    def closeEvent(self, event):
        self.video_capture.release()


app = QApplication(sys.argv)
main_window = VideoCaptureWidget()
main_window.show()
sys.exit(app.exec_())
