import cv2
import time
import sys
from gstream import VideoGStreamer
from flaskstream import VideoFStreamer

Width=1280
Height=720
FPS=30
Stream = input("F for flask / G for gstream / N for none : ")

if Stream=="F" or Stream=="f":
    streamer = VideoFStreamer(width=Width, height=Height, fps=FPS, stream=Stream)
else:
    streamer = VideoGStreamer(width=Width, height=Height, fps=FPS, stream=Stream)

print("Traitement démarré... ctrl+C pour stopper")

prev_time = time.time()
frame_count = 0
fps=0

try:
    while True:
        ret, frame = streamer.read()
        if not ret:
            break

        #frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)        #conversion niveaux de gris
        #frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)

        # --- DÉBUT DU TRAITEMENT OPENCV ---
        # Exemple simple : Détection de visages ou dessin
        cv2.putText(frame, f"Pi4 - Detection Active - FPS {fps}",
                    (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # Insérez votre modèle de détection ici (YOLO, Haar, etc.)
        # --- FIN DU TRAITEMENT OPENCV ---

        # Envoi vers le pipeline de streaming
        if Stream!="N" or "n":
            streamer.send(frame)

            frame_count += 1
            current_time = time.time()
            if current_time - prev_time >= 1.0:
                print(f"FPS Réels : {frame_count}")
                fps = frame_count
                frame_count = 0
                prev_time = current_time

except KeyboardInterrupt:
    print("\nArrêt du programme...")
    sys.exit(1)

finally:
    streamer.release()
