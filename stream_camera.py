import cv2
import time


# 1. Pipeline d'ENTRÉE (Capture 1080p -> Sortie 720p via ISP)
# Si vous utilisez une caméra USB, remplacez libcamerasrc par v4l2src
gst_in = (
    "v4l2src ! device=/dev/video0 ! "
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

WIDTH_in, HEIGHT_in = 1280, 720    #Video resolution
FPS_in = 30                    #Video frame rate

WIDTH_out, HEIGHT_out = 1280, 720    #Video resolution
FPS_out = 30                    #Video frame rate

# --- GStreamer Pipeline (with hardware encoding)
gst_out = (
    f"appsrc name=mysrc is-live=true format=GST_FORMAT_TIME ! "
    f"video/x-raw,format=BGR,width={WIDTH_in},height={HEIGHT_in},framerate={FPS_in}/1 ! "
    f"videoconvert ! video/x-raw,format=I420 ! "
    f"v4l2h264enc extra-controls=\"controls,h264_profile=4, h264_level=13, video_bitrate=4000000\" ! "
    f"rtph264pay config-interval=1 pt=96 ! "
    f"udpsink host={IP_DEST} port={PORT} sync=false"
)

# Création des objets VideoCapture et VideoWriter
cap = cv2.VideoCapture(gst_in, cv2.CAP_GSTREAMER)
out = None
if STREAMING_ACTIVE:
    out = cv2.VideoWriter(gst_out, cv2.CAP_GSTREAMER, 0, FPS_out, (WIDTH_out, HEIGHT_out))

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
    exit(1)

finally:
    cap.release()
    out.release()
    print("Pipelines fermées proprement.")