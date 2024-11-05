import cv2
import time
from pythonosc import udp_client
import numpy as np
from PIL import Image
import os
from datetime import datetime

def create_gif(frames, output_path):
    """Converte una lista di frame in una GIF."""
    pil_frames = [Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)) for frame in frames]
    pil_frames[0].save(
        output_path,
        save_all=True,
        append_images=pil_frames[1:],
        duration=100,
        loop=0
    )

class MotionDetector:
    def __init__(self):
        self.frame_history = []
        self.history_size = 5
        self.detection_counter = 0
        self.movement_threshold = 3000
        self.confirmation_threshold = 3
        self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(
            history=100,
            varThreshold=50,
            detectShadows=False
        )
        self.current_contour_area = 0  # Per visualizzare l'area corrente
        self.status = "IN ATTESA"  # Stato corrente del sistema

    def preprocess_frame(self, frame):
        """Preprocessa il frame per migliorare la rilevazione in condizioni di scarsa illuminazione."""
        lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
        cl = clahe.apply(l)
        enhanced = cv2.merge((cl,a,b))
        enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)
        return cv2.GaussianBlur(enhanced, (21, 21), 0)

    def detect_motion(self, frame):
        """Rileva e analizza il movimento nel frame."""
        processed = self.preprocess_frame(frame)
        fg_mask = self.bg_subtractor.apply(processed)
        
        kernel = np.ones((5,5), np.uint8)
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, kernel)
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, kernel)
        
        contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        significant_motion = False
        self.current_contour_area = 0
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > self.current_contour_area:
                self.current_contour_area = area
            if area > self.movement_threshold:
                significant_motion = True
                cv2.drawContours(frame, [contour], -1, (0, 255, 0), 2)  # Disegna i contorni rilevanti
        
        if significant_motion:
            self.detection_counter += 1
            self.status = f"RILEVAMENTO IN CORSO ({self.detection_counter}/{self.confirmation_threshold})"
        else:
            self.detection_counter = max(0, self.detection_counter - 1)
            if self.detection_counter == 0:
                self.status = "IN ATTESA"
        
        return self.detection_counter >= self.confirmation_threshold

def add_status_overlay(frame, detector, is_acquiring):
    """Aggiunge overlay con informazioni sullo stato del sistema."""
    # Crea una copia del frame per non modificare l'originale
    display_frame = frame.copy()
    
    # Aggiunge rettangolo semi-trasparente per lo sfondo del testo
    overlay = display_frame.copy()
    cv2.rectangle(overlay, (10, 10), (400, 120), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.4, display_frame, 0.6, 0, display_frame)
    
    # Font e colori
    font = cv2.FONT_HERSHEY_SIMPLEX
    white = (255, 255, 255)
    
    # Testi da visualizzare
    texts = [
        f"STATO: {detector.status if not is_acquiring else 'ACQUISIZIONE IN CORSO'}",
        f"Area movimento: {int(detector.current_contour_area)}",
        f"Soglia movimento: {detector.movement_threshold}",
        f"Counter: {detector.detection_counter}/{detector.confirmation_threshold}"
    ]
    
    # Posiziona i testi
    y = 40
    for text in texts:
        cv2.putText(display_frame, text, (20, y), font, 0.6, white, 2)
        y += 25
    
    return display_frame

def main():
    # Inizializzazione client OSC
    osc_client = udp_client.SimpleUDPClient("127.0.0.1", 8000)
    
    # Inizializzazione della webcam1
    cap1 = cv2.VideoCapture(0)
    cap1.set(cv2.CAP_PROP_EXPOSURE, -2)
    cap1.set(cv2.CAP_PROP_GAIN, 1)
    
    # Crea finestra con dimensioni fisse
    window_name = 'Rilevamento Movimento'
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, 800, 600)
    
    motion_detector = MotionDetector()
    
    output_folder = "captured_gifs"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    print("Sistema avviato. Premi 'q' per uscire.")
    
    is_acquiring = False
    
    while True:
        ret1, frame1 = cap1.read()
        if not ret1:
            print("Errore nella lettura dalla webcam1")
            break
        
        if not is_acquiring:
            person_detected = motion_detector.detect_motion(frame1)
            
            if person_detected:
                print("Persona rilevata con certezza!")
                is_acquiring = True
                motion_detector.status = "ACQUISIZIONE IN CORSO"
                
                osc_client.send_message("/sequences/seq2/play", 1)
                
                print("Attendi 4 secondi...")
                time.sleep(4)
                
                cap2 = cv2.VideoCapture(0)
                frames = []
                start_time = time.time()
                
                while time.time() - start_time < 4:
                    ret2, frame2 = cap2.read()
                    if ret2:
                        frames.append(frame2)
                
                cap2.release()
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                gif_path = os.path.join(output_folder, f"captured_{timestamp}.gif")
                create_gif(frames, gif_path)
                print(f"GIF salvata: {gif_path}")
                
                osc_client.send_message("/sequences/seq1/play", 1)
                
                motion_detector.detection_counter = 0
                print("Attendi 5 secondi prima del prossimo rilevamento...")
                time.sleep(5)
                
                is_acquiring = False
                motion_detector.status = "IN ATTESA"
        
        # Aggiunge overlay e mostra il frame
        display_frame = add_status_overlay(frame1, motion_detector, is_acquiring)
        cv2.imshow(window_name, display_frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap1.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()