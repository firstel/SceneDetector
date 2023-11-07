import os
import sys
from threading import Thread, Event

from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtWidgets import (
    QMainWindow,
    QPushButton,
    QApplication,
    QFileDialog,
    QComboBox,
    QLabel,
    QLineEdit,
    QProgressBar,
    QVBoxLayout,
    QWidget,
)
from scenedetect import (
    detect,
    AdaptiveDetector,
    split_video_ffmpeg,
    ThresholdDetector,
    ContentDetector,
)


class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.resize(400, 80)
        self.setWindowTitle("Scene detection")

        self.filename = None

        self.central_widget = QWidget()
        self.main_layout = QVBoxLayout()
        self.central_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.central_widget)

        self.browser = QPushButton("Browse files")
        self.browser.clicked.connect(self.get_files)
        self.main_layout.addWidget(self.browser)

        self.selected_file = QLabel("No file selected")
        self.main_layout.addWidget(self.selected_file)

        self.detectors = QComboBox()
        self.detectors.addItems(
            ["ContentDetector", "ThresholdDetector", "AdaptiveDetector"]
        )
        self.detectors.currentTextChanged.connect(self.detector_changed)
        self.main_layout.addWidget(self.detectors)

        self.threshold_widget = QWidget()
        self.threshold_layout = QVBoxLayout()
        self.threshold_widget.setLayout(self.threshold_layout)
        self.main_layout.addWidget(self.threshold_widget)

        self.threshold_label = QLabel("Enter threshold value:")
        self.threshold_layout.addWidget(self.threshold_label)

        self.threshold_value = QLineEdit()
        self.threshold_layout.addWidget(self.threshold_value)
        self.threshold_value.setText("3.0")
        self.threshold_value.setValidator(QDoubleValidator())

        self.threshold_widget.hide()

        self.action_button = QPushButton("Action")
        self.action_button.setEnabled(False)
        self.action_button.clicked.connect(self.process_video)
        self.main_layout.addWidget(self.action_button)

        self.status = QLabel("Status: Idle")
        self.main_layout.addWidget(self.status)
        self.status.hide()

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Set the range to 0 to activate Marquee mode
        self.main_layout.addWidget(self.progress_bar)
        self.progress_bar.hide()

        self.main_layout.addStretch()

    def detector_changed(self):
        if self.detectors.currentText() == "ThresholdDetector":
            self.threshold_widget.show()
        else:
            self.threshold_widget.hide()

    def get_files(self):
        self.filename, commit = QFileDialog.getOpenFileName(
            self, "Single File", "D:\programming-1\pySceneDetector", "*.mp4"
        )
        if not commit:
            return

        if self.filename is None:
            self.selected_file.setText("No file selected")
            self.action_button.setEnabled(False)

        self.selected_file.setText(f"Selected file: {self.filename}")
        self.action_button.setEnabled(True)


    def process_video(self):
        threshold = float(self.threshold_value.text())
        model = self.detectors.currentText()

        thr1 = Thread(target=self.get_frames, args=[self.filename, model, threshold])
        thr1.start()
        self.status.setText("Status: Detecting Scenes...")
        self.status.show()
        self.progress_bar.show()

    @staticmethod
    def get_frames(path, model, threshold):
        detector_choice = {
            "ThresholdDetector": ThresholdDetector(threshold=threshold),
            "ContentDetector": ContentDetector(),
            "AdaptiveDetector": AdaptiveDetector(),
        }

        scene_list = detect(
            path, detector=detector_choice[model], show_progress=True
        )

        if not scene_list:
            print("No scenes detected.")
            return

        save_loc = f"{path.split('.')[0]} splited Scene"
        try:
            os.mkdir(save_loc)
        except FileExistsError:
            pass

        split_video_ffmpeg(
            path,
            scene_list=scene_list,
            output_file_template=f"{save_loc}/scene $SCENE_NUMBER.mp4",
            show_progress=True,
        )


def main():
    app = QApplication([])
    app.setStyle("Fusion")
    font = app.font()
    font.setPointSize(10)
    app.setFont(font)

    main_window = MainWindow()
    main_window.resize(600, 500)
    main_window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
