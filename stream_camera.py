import cv2, signal, sys

# --- CONFIGURATION ---
PC_IP = input("PC IP : ")#"192.168.2.9"    #Destination PC IP
PORT = 5000
WIDTH, HEIGHT = 640, 480    #Video resolution
FPS = 30                    #Video frame rate

# --- GStreamer Pipeline (with hardware encoding)
gst_pipeline_out = (
    f"appsrc ! videoconvert ! v4l2h264enc extra-controls=\"controls, h264_profile=4, h264_level=13, video_bitrate=2000000\" ! " #video_bitrate : compression 2Mbps
    f"rtph264pay config-interval=1 pt=96 ! "
    f"udpsink host={PC_IP} port={PORT}"
)

def main():
    # Initialisation capture caméra
    cap = cv2.VideoCapture(0)                   #'/dev/video0' -> USB
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)
    cap.set(cv2.CAP_PROP_FPS, FPS)

    # Initialisation de l'écrivain GStreamer
    out = cv2.VideoWriter(gst_pipeline_out, cv2.CAP_GSTREAMER, 0, FPS, (WIDTH, HEIGHT), True)

    if not out.isOpened():
        print("Erreur: Impossible d'ouvrir le pipeline GStreamer")
        sys.exit(1)

    print(f"Streaming vers {PC_IP}:{PORT}... \n\nctrl+C to stop")

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # --- TON TRAITEMENT OPENCV ICI ---
            # Exemple : Dessiner sur l'image
            cv2.putText(frame, "H.264 HW Encoded", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            # ---------------------------------

            # Envoi de la frame traitée au pipeline
            out.write(frame)

    except KeyboardInterrupt:
        print("\nArrêt du stream...")
    finally:
        cap.release()
        out.release()
        print("Ressources libérées.")

if __name__ == "__main__":
    main()