import cv2
from pythonosc import udp_client
import numpy as np

# Configura il client OSC
client = udp_client.SimpleUDPClient("127.0.0.1", 7000)  # Indirizzo IP e porta di HeavyM
print("clien created")
# Inizializza la webcam
cap = cv2.VideoCapture(1)
print("webcam opened")
while True:
    ret, frame = cap.read()
    if not ret:
        break
    
     # Converti il frame in scala di grigi
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # Calcola la luminosità media
    brightness = np.mean(gray)
    
    # Normalizza la luminosità in un range da 0 a 1
    normalized_brightness = brightness / 255.0
    print(normalized_brightness)
    # Invia i dati a HeavyM tramite OSC
    client.send_message("/master/opacity/value", normalized_brightness)
    
    # Visualizza il frame (opzionale)
    cv2.imshow('Frame', frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
