import cv2
import time
import sys


# 1. Pipeline d'ENTRÉE (Capture 1080p -> Sortie 720p via ISP)
# Si vous utilisez une caméra USB, remplacez libcamerasrc par v4l2src
gst_in = (
    "v4l2src device=/dev/video0 ! "
    "image/jpeg,width=1920,height=1080,framerate=30/1 ! "
    "jpegdec ! "
    "videoconvert ! video/x-raw,format=BGR ! appsink"
)
#"video/x-raw,width=1280,height=720,framerate=30/1 ! "

# 2. Pipeline de SORTIE (Streaming réseau UDP)
# Remplacez l'IP par celle de votre PC récepteur
STREAMING_ACTIVE = True
IP_DEST = input("Type IP (or 1 for default=192.169.2.9 or 0 to deactivate streaming ) : ")#"192.168.2.9"    #Destination PC IP
if IP_DEST == "0":
    IP_DEST = "0.0.0.0"
    STREAMING_ACTIVE = False
elif IP_DEST == "1":
    IP_DEST = "192.168.2.9"

PORT = 5000

WIDTH, HEIGHT = 1920, 1080    #Video resolution
FPS = 30                    #Video frame rate

# --- GStreamer Pipeline (with hardware encoding)
gst_out = (
    f"appsrc ! "
    f"video/x-raw,format=BGR,width={WIDTH},height={HEIGHT},framerate={FPS}/1 ! "
    f"videoconvert ! "
    f"video/x-raw,format=I420 ! "
    f"v4l2h264enc extra-controls=\"controls,h264_profile=4,h264_level=13,video_bitrate=4000000,h264_i_frame_period=15\" ! "
    f"video/x-h264,level=(string)4,profile=high,stream-format=byte-stream ! " # On force le caps-filter qui marche dans ton terminal
    f"h264parse ! "                    # Indispensable pour stabiliser le flux matériel
    f"rtph264pay config-interval=1 pt=96 aggregate-mode=none ! "
    f"udpsink host={IP_DEST} port=5000 sync=false async=false"
)

#


# Création des objets VideoCapture et VideoWriter
#cap = cv2.VideoCapture(gst_in, cv2.CAP_GSTREAMER)

cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
cap.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)
cap.set(cv2.CAP_PROP_FPS, FPS)

cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
out = None
if STREAMING_ACTIVE:
    out = cv2.VideoWriter(gst_out, cv2.CAP_GSTREAMER, 0, FPS, (WIDTH, HEIGHT), True)

if not cap.isOpened() or (STREAMING_ACTIVE and not out.isOpened()):
    print("Erreur : Impossible d'ouvrir les pipelines GStreamer")
    exit()

print(f"Streaming vers {IP_DEST}:{PORT} en {HEIGHT}p... \n\nctrl+C to stop")

start_time = time.monotonic_ns()
frame_count = 0

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # --- DÉBUT DU TRAITEMENT OPENCV ---
        # Exemple simple : Détection de visages ou dessin
        cv2.putText(frame, f"Pi4 - Detection Active - Frame {frame_count}",
                    (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # Insérez votre modèle de détection ici (YOLO, Haar, etc.)
        # --- FIN DU TRAITEMENT OPENCV ---

        # Envoi vers le pipeline de streaming
        if out is not None and out.isOpened():
            out.write(frame)

        frame_count += 1

except KeyboardInterrupt:
    print("\nArrêt du programme...")
    sys.exit(1)

finally:
    cap.release()
    if out is not None and out.isOpened():
        out.release()
    print("Pipelines fermées proprement.")