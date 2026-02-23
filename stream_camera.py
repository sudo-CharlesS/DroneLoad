import cv2
from flask import Flask, Response

app = Flask(__name__)

cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
#cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
cap.set(cv2.CAP_PROP_FPS, 30)

cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

def generate_frames():
        while True:
                success, frame = cap.read()
                if not success:
                        break
                else:
                        ret, buffer = cv2.imencode('.jpg', frame)
                        yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

@app.route('/')
def index():
        return '<img src="/video_feed" style="width:100%">'

@app.route('/video_feed')
def video_feed():
        return Response(generate_frames(), mimetype='multipart/x-mixed-replace;boundary=frame')

if __name__ == "__main__":
        app.run(host='0.0.0.0', port=5000)
