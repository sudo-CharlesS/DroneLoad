import cv2
import time
import sys
from flask import Flask, Response

app = Flask(__name__)


PORT = 5000
WIDTH, HEIGHT = 1920, 1080    #Video resolution
FPS = 30


cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
cap.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)
cap.set(cv2.CAP_PROP_FPS, FPS)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

STREAMING_ACTIVE = input("Activate streaming ? (y/n) : ") == "y" or "Y"

def generate_frames():
    print(f"Streaming en {HEIGHT}p... \n\nctrl+C to stop")
    prev_time = time.time()
    frame_count = 0
    fps=0
    try:
        while True:
                success, frame = cap.read()
                if not success:
                        break

                cv2.putText(frame, f"Pi4 - Detection Active - FPS {fps}",
                            (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

                if STREAMING_ACTIVE:
                    ret, buffer = cv2.imencode('.jpg', frame)
                    yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

                    frame_count += 1
                    current_time = time.time()
                    if current_time - prev_time >= 1.0:
                        print(f"FPS Réels : {frame_count}")
                        fps=frame_count
                        fps_count = 0
                        prev_time = current_time

    except KeyboardInterrupt:
        print("\nArrêt du programme...")
        sys.exit(1)

    finally:
        cap.release()

@app.route('/')
def index():
        return '<img src="/video_feed" style="width:100%">'

@app.route('/video_feed')
def video_feed():
        return Response(generate_frames(), mimetype='multipart/x-mixed-replace;boundary=frame')

if __name__ == "__main__":
        app.run(host='0.0.0.0', port=PORT)
