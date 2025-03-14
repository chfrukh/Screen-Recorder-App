from PyQt5.QtWidgets import (
    QWidget, QPushButton, QVBoxLayout, QLabel, QFileDialog,
    QHBoxLayout, QSlider, QCheckBox
)
from PyQt5.QtCore import Qt
from recorder import ScreenRecorder  # Ensure filename is used in __init__
from utils import ScreenRegionSelector
import datetime
import os

class RecorderUI(QWidget):
    def __init__(self):
        super().__init__()
        self.recorder = None
        self.save_folder = None
        self.region = None
        self.mic_enabled = True
        self.is_paused = False
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('🔥 Screen Recorder with Mic Options 🔥')
        self.setGeometry(300, 200, 600, 150)
        self.setStyleSheet("""
            QWidget {
                background-color: #222;
                color: #fff;
                font-family: Arial;
                font-size: 14px;
            }
            QPushButton {
                background-color: #333;
                border: 2px solid #555;
                border-radius: 20px;
                padding: 10px 20px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #555;
            }
            QLabel {
                color: #ccc;
            }
        """)

        main_layout = QVBoxLayout()

        # Top toolbar
        toolbar = QHBoxLayout()

        self.select_folder_btn = QPushButton('📂')
        self.select_folder_btn.clicked.connect(self.select_save_folder)
        toolbar.addWidget(self.select_folder_btn)

        self.region_btn = QPushButton('📐')
        self.region_btn.clicked.connect(self.select_region)
        toolbar.addWidget(self.region_btn)

        self.mic_btn = QPushButton('🎙️')
        self.mic_btn.setCheckable(True)
        self.mic_btn.setChecked(True)
        self.mic_btn.clicked.connect(self.toggle_mic)
        toolbar.addWidget(self.mic_btn)

        self.record_btn = QPushButton('▶️')
        self.record_btn.clicked.connect(self.toggle_recording)
        toolbar.addWidget(self.record_btn)

        self.pause_btn = QPushButton('⏸️')
        self.pause_btn.clicked.connect(self.toggle_pause_resume)
        toolbar.addWidget(self.pause_btn)

        main_layout.addLayout(toolbar)

        # Mic options: volume + noise reduction
        mic_options_layout = QHBoxLayout()

        mic_label = QLabel("🎙️ Mic Volume")
        mic_options_layout.addWidget(mic_label)

        self.mic_volume_slider = QSlider(Qt.Horizontal)
        self.mic_volume_slider.setMinimum(0)
        self.mic_volume_slider.setMaximum(100)
        self.mic_volume_slider.setValue(80)
        self.mic_volume_slider.valueChanged.connect(self.update_mic_volume)
        mic_options_layout.addWidget(self.mic_volume_slider)

        self.noise_reduction_checkbox = QCheckBox("Noise Reduction")
        self.noise_reduction_checkbox.setChecked(True)
        self.noise_reduction_checkbox.stateChanged.connect(self.toggle_noise_reduction)
        mic_options_layout.addWidget(self.noise_reduction_checkbox)

        main_layout.addLayout(mic_options_layout)

        # Status display
        self.status_label = QLabel("Status: Ready")
        self.status_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.status_label)

        self.setLayout(main_layout)

    # --- Button Actions ---

    def select_save_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder to Save Recordings")
        if folder:
            self.save_folder = folder
            self.status_label.setText(f"✅ Folder Selected:\n{self.save_folder}")
        else:
            self.status_label.setText("❗ Folder selection canceled.")

    def select_region(self):
        self.region = ScreenRegionSelector.get_selected_region()
        if self.region:
            self.status_label.setText(f"✅ Region Selected: {self.region}")
        else:
            self.status_label.setText("❗ Region selection canceled.")

    def toggle_mic(self):
        self.mic_enabled = not self.mic_enabled
        self.mic_btn.setText("🔇" if not self.mic_enabled else "🎙️")
        self.status_label.setText(f"🎙️ Mic {'Disabled' if not self.mic_enabled else 'Enabled'}")

    def update_mic_volume(self, value):
        if self.recorder:
            self.recorder.set_mic_volume(value / 100.0)
        self.status_label.setText(f"🎚️ Mic Volume: {value}%")

    def toggle_noise_reduction(self, state):
        enabled = state == Qt.Checked
        if self.recorder:
            self.recorder.set_noise_reduction(enabled)
        self.status_label.setText("🛠️ Noise Reduction " + ("Enabled" if enabled else "Disabled"))

    def toggle_recording(self):
        if not self.recorder:
            # Start recording
            if not self.save_folder:
                self.status_label.setText("❗ Please select a folder first!")
                return

            current_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            file_name = f"recording_{current_time}.avi"
            full_path = os.path.join(self.save_folder, file_name)

            # Make sure filename param is used!
            self.recorder = ScreenRecorder(
                filename=full_path,
                region=self.region,
                mic_enabled=self.mic_enabled,
                mic_volume=self.mic_volume_slider.value() / 100.0,
                noise_reduction=self.noise_reduction_checkbox.isChecked()
            )
            self.recorder.start_recording()

            self.record_btn.setText('⏹️')
            self.status_label.setText(f"🔴 Recording Started!\nSaving to:\n{file_name}")
        else:
            # Stop recording
            self.recorder.stop_recording()
            self.recorder = None
            self.record_btn.setText('▶️')
            self.status_label.setText("🛑 Recording Stopped & Saved.")

    def toggle_pause_resume(self):
        if not self.recorder:
            self.status_label.setText("❗ No recording in progress!")
            return

        if not self.is_paused:
            self.recorder.pause_recording()
            self.is_paused = True
            self.pause_btn.setText('▶️')
            self.status_label.setText("⏸️ Recording Paused.")
        else:
            self.recorder.resume_recording()
            self.is_paused = False
            self.pause_btn.setText('⏸️')
            self.status_label.setText("▶️ Recording Resumed.")
