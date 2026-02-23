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
IP_DEST = input("PC IP (0 to deactivate streaming : ")#"192.168.2.9"    #Destination PC IP
if IP_DEST == "0":
    IP_DEST = "0.0.0.0"
    STREAMING_ACTIVE = False
PORT = 5000

WIDTH_in, HEIGHT_in = 1920, 1080    #Video resolution
FPS_in = 30                    #Video frame rate

WIDTH_out, HEIGHT_out = 1280, 720    #Video resolution
FPS_out = 30                    #Video frame rate

# --- GStreamer Pipeline (with hardware encoding)
"""
gst_out = (
    f"appsrc ! "
    f"video/x-raw,format=BGR ! "
    f"queue ! "
    f"videoconvert ! video/x-raw,format=I420 ! "
    f"v4l2h264enc  extra-controls=\"controls,h264_profile=4,h264_level=13,video_bitrate=8000000\" ! "
    f"rtph264pay config-interval=1 pt=96 ! "
    f"udpsink host={IP_DEST} port=5000 sync=false"
)
"""
gst_out = (
    f"appsrc ! "
    f"video/x-raw,format=BGR,width={WIDTH_in},height={HEIGHT_in},framerate={FPS_in}/1 ! "
    f"videoconvert ! "
    f"video/x-raw,format=I420 ! "
    f"v4l2h264enc tune=zerolatency extra-controls=\"controls,h264_profile=4,h264_level=13,video_bitrate=8000000\" ! "
    f"video/x-h264,profile=high,stream-format=byte-stream ! " # On force le caps-filter qui marche dans ton terminal
    f"h264parse ! "                    # Indispensable pour stabiliser le flux matériel
    f"rtph264pay config-interval=1 pt=96 aggregate-mode=none ! "
    f"udpsink host={IP_DEST} port=5000 sync=false async=false"
)

#level=(string)4


# Création des objets VideoCapture et VideoWriter
cap = cv2.VideoCapture(gst_in, cv2.CAP_GSTREAMER)
out = None
if STREAMING_ACTIVE:
    out = cv2.VideoWriter(gst_out, cv2.CAP_GSTREAMER, 0, FPS_in, (WIDTH_in, HEIGHT_in), True)

if not cap.isOpened() or (STREAMING_ACTIVE and not out.isOpened()):
    print("Erreur : Impossible d'ouvrir les pipelines GStreamer")
    exit()

print(f"Streaming vers {IP_DEST}:{PORT} en 720p... \n\nctrl+C to stop")

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