import speech_recognition as sr
from pynput import keyboard
from pynput.keyboard import Controller
import threading

key_controller = Controller()
recognizer = sr.Recognizer()

print("Starting script...")

# This will hold the ongoing audio data
audio_data = []

# Flag to indicate recording status
is_recording = False

with sr.Microphone() as mic:
    SAMPLE_RATE = mic.SAMPLE_RATE
    SAMPLE_WIDTH = mic.SAMPLE_WIDTH


def background_recording():
    global is_recording, audio_data

    with sr.Microphone() as source:
        print("Microphone initialized...")  # Debug print
        while is_recording:
            print("Attempting to record...")  # Debug print
            audio_chunk = recognizer.listen(source, timeout=2)
            audio_data.append(audio_chunk)
            print(f"Captured audio chunk of length: {len(audio_chunk.get_wav_data())}")  # Debug print

def start_capture():
    global is_recording
    is_recording = True
    threading.Thread(target=background_recording).start()

def stop_and_process_audio():
    global is_recording, audio_data
    is_recording = False

    # Combine audio chunks into a single audio data object
    audio = sr.AudioData(b''.join([chunk.get_wav_data() for chunk in audio_data]), 
                         mic.SAMPLE_RATE, 
                         mic.SAMPLE_WIDTH)

    try:
        # Using CMU Sphinx
        text = recognizer.recognize_sphinx(audio)
        key_controller.type(text)
        print('Voice typing activated!')
    except sr.UnknownValueError:
        print("Sphinx could not understand the audio")
    except sr.RequestError:
        print("Sphinx error")



hotkey = {keyboard.Key.f9}
current_keys = set()

def on_key_down(key):
    if any([key in hotkey, key in current_keys]):
        current_keys.add(key)
        if all(k in current_keys for k in hotkey) and not is_recording:
            start_capture()

def on_key_up(key):
    global current_keys
    if key in current_keys:
        current_keys.remove(key)
        if not any(k in current_keys for k in hotkey) and is_recording:
            stop_and_process_audio()

with keyboard.Listener(on_press=on_key_down, on_release=on_key_up) as l:
    l.join()