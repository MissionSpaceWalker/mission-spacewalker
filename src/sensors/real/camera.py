#!/usr/bin/env python3

import subprocess
import time
import threading

def capture_image():
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = f"image_{timestamp}.jpg"
    try:
        subprocess.run(["rpicam-still", "-o", filename, "--nopreview"], check=True)
        print(f"[✓] Image captured: {filename}")
    except subprocess.CalledProcessError as e:
        print(f"[!] Failed to capture image: {e}")

def record_video(duration=None, stop_event=None):
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = f"video_{timestamp}.h264"
    print(f"[•] Recording video to {filename}...")

    try:
        if duration:
            subprocess.run(["rpicam-vid", "-o", filename, "-t", str(int(duration) * 1000), "--nopreview"], check=True)
        else:
            process = subprocess.Popen(["rpicam-vid", "-o", filename, "--timeout", "0", "--nopreview"])
            stop_event.wait()
            process.terminate()
            print(f"[✓] Stopped recording video: {filename}")
    except Exception as e:
        print(f"[!] Failed to record video: {e}")

def main():
    print("📷 Camera Control")
    print("Type one of the following:")
    print("- `capture` to take a picture")
    print("- `record <seconds>` to record a video")
    print("- `record` to start infinite recording (type `stop` to stop)")
    print("- `exit` to quit")

    video_thread = None
    stop_event = threading.Event()

    while True:
        try:
            cmd = input(">>> ").strip().lower()
            if cmd == "capture":
                capture_image()

            elif cmd.startswith("record"):
                parts = cmd.split()
                if len(parts) == 2 and parts[1].isdigit():
                    record_video(duration=int(parts[1]))
                else:
                    if video_thread and video_thread.is_alive():
                        print("[!] Already recording.")
                    else:
                        stop_event.clear()
                        video_thread = threading.Thread(target=record_video, kwargs={"stop_event": stop_event})
                        video_thread.start()

            elif cmd == "stop":
                if video_thread and video_thread.is_alive():
                    stop_event.set()
                    video_thread.join()
                else:
                    print("[!] Not currently recording.")

            elif cmd == "exit":
                if video_thread and video_thread.is_alive():
                    stop_event.set()
                    video_thread.join()
                break

            else:
                print("[!] Unknown command. Try `capture`, `record`, `record <seconds>`, or `stop`.")

        except KeyboardInterrupt:
            print("\n[!] Keyboard interrupt received.")
            if video_thread and video_thread.is_alive():
                stop_event.set()
                video_thread.join()
            break


if __name__ == "__main__":
    main()
