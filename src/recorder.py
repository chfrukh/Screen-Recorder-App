import cv2
import pyautogui
import numpy as np
import threading
import time
import sounddevice as sd
import soundfile as sf

class ScreenRecorder(threading.Thread):
    """
    A screen recorder that captures the screen and optionally records mic audio.
    """

    def __init__(self, filename, fps=10, region=None,
                 mic_enabled=True, mic_volume=1.0, noise_reduction=False):
        super(ScreenRecorder, self).__init__()
        self.filename = filename
        self.fps = fps
        self.is_recording = False
        self.is_paused = False
        self.region = region
        self.screen_size = self._get_screen_size(region)

        # Audio options
        self.mic_enabled = mic_enabled
        self.mic_volume = mic_volume
        self.noise_reduction = noise_reduction

        # Internal
        self.video_writer = None
        self.audio_frames = []
        self.audio_thread = None

    def _get_screen_size(self, region):
        if region:
            _, _, width, height = region
            return (width, height)
        else:
            return pyautogui.size()

    def run(self):
        """
        Start the screen recording loop and optionally audio recording.
        """
        # Initialize video writer
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        self.video_writer = cv2.VideoWriter(self.filename, fourcc, self.fps, self.screen_size)

        print(f"[INFO] Recording started! Saving video to {self.filename}")

        # Start audio recording in another thread
        if self.mic_enabled:
            print("[INFO] Microphone recording enabled.")
            self.audio_frames = []
            self.audio_thread = threading.Thread(target=self.record_audio)
            self.audio_thread.start()

        self.is_recording = True
        while self.is_recording:
            if self.is_paused:
                time.sleep(0.1)
                continue

            # Screenshot (full screen or region)
            frame = self.capture_screen()

            # Write video frame
            self.video_writer.write(frame)

        # Cleanup
        self.video_writer.release()
        print("[INFO] Video recording stopped and saved!")

        # Stop audio and save it
        if self.mic_enabled:
            self.audio_thread.join()
            self.save_audio()

    def capture_screen(self):
        if self.region:
            x, y, w, h = self.region
            screenshot = pyautogui.screenshot(region=(x, y, w, h))
        else:
            screenshot = pyautogui.screenshot()

        frame = np.array(screenshot)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return frame

    def record_audio(self):
        """
        Records microphone audio and appends it to self.audio_frames.
        """
        samplerate = 44100
        duration = 0.1  # Capture in chunks
        print("[INFO] Audio recording thread started.")
        while self.is_recording:
            audio_data = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype='float32')
            sd.wait()

            # Apply volume control
            audio_data *= self.mic_volume

            # Dummy noise reduction placeholder (you can add real filters here)
            if self.noise_reduction:
                audio_data = self.apply_dummy_noise_reduction(audio_data)

            self.audio_frames.append(audio_data.copy())

        print("[INFO] Audio recording thread stopped.")

    def apply_dummy_noise_reduction(self, audio_data):
        """
        A simple noise reduction placeholder.
        """
        return audio_data * 0.8  # Just reducing overall volume for example purposes

    def save_audio(self):
        """
        Saves audio frames to a file (WAV for simplicity).
        """
        if not self.audio_frames:
            print("[WARN] No audio recorded.")
            return

        audio_filename = self.filename.replace(".avi", "_audio.wav")
        audio_data = np.concatenate(self.audio_frames, axis=0)
        sf.write(audio_filename, audio_data, 44100)
        print(f"[INFO] Audio saved to {audio_filename}")

    # --- Control Methods ---
    def start_recording(self):
        if not self.is_recording:
            self.start()
            print("[INFO] Recorder thread started.")

    def pause_recording(self):
        if self.is_recording and not self.is_paused:
            self.is_paused = True
            print("[INFO] Recording paused.")

    def resume_recording(self):
        if self.is_recording and self.is_paused:
            self.is_paused = False
            print("[INFO] Recording resumed.")

    def stop_recording(self):
        if self.is_recording:
            self.is_recording = False
            print("[INFO] Stopping recorder thread...")

    def set_mic_volume(self, volume):
        """
        Update mic volume in real time (0.0 to 1.0)
        """
        self.mic_volume = volume
        print(f"[INFO] Mic volume updated to {volume}")

    def set_noise_reduction(self, enabled):
        """
        Enable or disable noise reduction.
        """
        self.noise_reduction = enabled
        print(f"[INFO] Noise reduction {'enabled' if enabled else 'disabled'}")
