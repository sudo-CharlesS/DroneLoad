import cv2, time
from flask import Flask, Response

app = Flask(__name__)

cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
cap.set(cv2.CAP_PROP_FPS, 30)

cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)


def generate_frames():
    prev_time = time.time()
    fps_count = 0
    fps=0
    while True:
            success, frame = cap.read()
            if not success:
                    break
            else:
                cv2.putText(frame, f"Pi4 - Detection Active - FPS {fps}",
                            (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)


                ret, buffer = cv2.imencode('.jpg', frame)
                yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

                fps_count += 1
                current_time = time.time()
                if current_time - prev_time >= 1.0:
                    print(f"FPS Réels : {fps_count}")
                    fps=fps_count
                    fps_count = 0
                    prev_time = current_time

@app.route('/')
def index():
        return '<img src="/video_feed" style="width:100%">'

@app.route('/video_feed')
def video_feed():
        return Response(generate_frames(), mimetype='multipart/x-mixed-replace;boundary=frame')

if __name__ == "__main__":
        app.run(host='0.0.0.0', port=5000)
