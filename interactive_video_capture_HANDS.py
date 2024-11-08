import cv2
import time
from pythonosc import udp_client
import numpy as np
from PIL import Image
import os
from datetime import datetime
import mediapipe as mp
from tqdm import tqdm

# setup parameters
camera_1 = 0 # for hands recognition
camera_2 = 0 # for capture the GIF
ip_address = "127.0.0.1"
port =  8000

def create_gif(frames, output_path):
    """Converte una lista di frame in una GIF ad alta qualità."""
    pil_frames = []
    print("Converting frames to GIF...")
    for frame in tqdm(frames, desc="Processing frames"):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_frame = Image.fromarray(frame)
        pil_frame = pil_frame.quantize(method=2, colors=256, dither=Image.Dither.NONE)
        pil_frames.append(pil_frame)

    print("Saving GIF...")
    pil_frames[0].save(
        output_path,
        save_all=True,
        append_images=pil_frames[1:],
        optimize=False,
        duration=1000/30,
        loop=0,
        quality=100,
        disposal=2
    )

class HandDetector:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )
        self.mp_draw = mp.solutions.drawing_utils
        self.status = "IN ATTESA"
        self.open_hand_start_time = None
        self.required_duration = 2.0
        self.is_hand_open = False
        self.current_duration = 0.0
        self.last_detected_hand = None

    def calculate_finger_angle(self, p1, p2, p3):
        """Calcola l'angolo tra tre punti."""
        v1 = np.array([p1.x - p2.x, p1.y - p2.y])
        v2 = np.array([p3.x - p2.x, p3.y - p2.y])
        
        cosine = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
        angle = np.arccos(np.clip(cosine, -1.0, 1.0))
        return np.degrees(angle)

    def is_finger_extended(self, landmarks, tip_id, pip_id, mcp_id):
        """Verifica se un dito è esteso usando l'angolo tra le articolazioni."""
        tip = landmarks.landmark[tip_id]
        pip = landmarks.landmark[pip_id]
        mcp = landmarks.landmark[mcp_id]
        
        angle = self.calculate_finger_angle(tip, pip, mcp)
        return angle > 160  # Il dito è considerato esteso se l'angolo è maggiore di 160 gradi
    
    def is_thumb_extended(self, landmarks, handedness):
        """Verifica se il pollice è esteso, considerando l'orientamento della mano."""
        thumb_tip = landmarks.landmark[self.mp_hands.HandLandmark.THUMB_TIP]
        thumb_ip = landmarks.landmark[self.mp_hands.HandLandmark.THUMB_IP]
        thumb_mcp = landmarks.landmark[self.mp_hands.HandLandmark.THUMB_MCP]
        wrist = landmarks.landmark[self.mp_hands.HandLandmark.WRIST]
        
        # Calcola la direzione del pollice rispetto al polso
        thumb_direction = thumb_tip.x - wrist.x
        
        # Verifica l'angolo di estensione
        angle = self.calculate_finger_angle(thumb_tip, thumb_ip, thumb_mcp)
        is_extended = angle > 135
        
        # Adatta la logica in base all'orientamento della mano
        if handedness == 'Right':
            return is_extended and thumb_direction < 0
        else:  # Left hand
            return is_extended and thumb_direction > 0

    def is_hand_fully_open(self, hand_landmarks, handedness):
        """Verifica se la mano è completamente aperta, supportando entrambe le orientazioni."""
        # Definizione delle dita e dei loro punti di riferimento
        fingers = [
            (self.mp_hands.HandLandmark.INDEX_FINGER_TIP, 
             self.mp_hands.HandLandmark.INDEX_FINGER_PIP,
             self.mp_hands.HandLandmark.INDEX_FINGER_MCP),
            (self.mp_hands.HandLandmark.MIDDLE_FINGER_TIP,
             self.mp_hands.HandLandmark.MIDDLE_FINGER_PIP,
             self.mp_hands.HandLandmark.MIDDLE_FINGER_MCP),
            (self.mp_hands.HandLandmark.RING_FINGER_TIP,
             self.mp_hands.HandLandmark.RING_FINGER_PIP,
             self.mp_hands.HandLandmark.RING_FINGER_MCP),
            (self.mp_hands.HandLandmark.PINKY_TIP,
             self.mp_hands.HandLandmark.PINKY_PIP,
             self.mp_hands.HandLandmark.PINKY_MCP)
        ]
        
        # Verifica il pollice
        thumb_extended = self.is_thumb_extended(hand_landmarks, handedness)
        if not thumb_extended:
            return False
            
        # Verifica le altre dita
        for tip_id, pip_id, mcp_id in fingers:
            if not self.is_finger_extended(hand_landmarks, tip_id, pip_id, mcp_id):
                return False
                
        return True

    def detect_open_hand(self, frame):
        """Rileva la presenza di una mano aperta e traccia il tempo."""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)
        
        if results.multi_hand_landmarks:
            for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
                # Ottiene l'orientamento della mano (destra/sinistra)
                hand_type = handedness.classification[0].label
                
                self.mp_draw.draw_landmarks(
                    frame, 
                    hand_landmarks, 
                    self.mp_hands.HAND_CONNECTIONS,
                    self.mp_draw.DrawingSpec(color=(0,255,0), thickness=2, circle_radius=2),
                    self.mp_draw.DrawingSpec(color=(0,0,255), thickness=2)
                )
                
                current_hand_open = self.is_hand_fully_open(hand_landmarks, hand_type)
                
                if current_hand_open:
                    self.last_detected_hand = hand_type
                    if not self.is_hand_open:
                        self.open_hand_start_time = time.time()
                        self.is_hand_open = True
                    
                    self.current_duration = time.time() - self.open_hand_start_time
                    self.status = f"MANO {hand_type.upper()} APERTA: {self.current_duration:.1f}s/{self.required_duration}s"
                    
                    if self.current_duration >= self.required_duration:
                        return True
                else:
                    self.is_hand_open = False
                    self.open_hand_start_time = None
                    self.current_duration = 0.0
                    self.status = "IN ATTESA"
        else:
            self.is_hand_open = False
            self.open_hand_start_time = None
            self.current_duration = 0.0
            self.status = "IN ATTESA"
            
        return False

def add_status_overlay(frame, detector, is_acquiring):
    """Aggiunge overlay con informazioni sullo stato del sistema."""
    display_frame = frame.copy()
    
    overlay = display_frame.copy()
    cv2.rectangle(overlay, (10, 10), (400, 140), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.4, display_frame, 0.6, 0, display_frame)
    
    font = cv2.FONT_HERSHEY_SIMPLEX
    white = (255, 255, 255)
    
    texts = [
        f"STATO: {detector.status if not is_acquiring else 'ACQUISIZIONE IN CORSO'}",
        "Mostra la mano aperta per 2 secondi",
        f"Tempo: {detector.current_duration:.1f}s" if detector.current_duration > 0 else "In attesa della mano...",
        f"Ultima mano rilevata: {detector.last_detected_hand if detector.last_detected_hand else 'Nessuna'}"
    ]
    
    y = 40
    for text in texts:
        cv2.putText(display_frame, text, (20, y), font, 0.6, white, 2)
        y += 25
    
    return display_frame

def init_camera():
    """Inizializza e configura la webcam."""
    cap = cv2.VideoCapture(camera_1)
    cap.set(cv2.CAP_PROP_EXPOSURE, -2)
    cap.set(cv2.CAP_PROP_GAIN, 1)
    return cap

def main():
    print("Inizializzazione del sistema...")
    osc_client = udp_client.SimpleUDPClient(ip_address,port)
    
    print("Apertura della webcam principale...")
    cap1 = init_camera()
    osc_client.send_message("/sequences/Seq 1/play", 1)
    
    window_name = 'Rilevamento Mano Aperta'
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, 800, 600)
    
    hand_detector = HandDetector()
    
    output_folder = "captured_gifs"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    print("Sistema avviato. Premi 'q' per uscire.")
    print("In attesa del rilevamento della mano...")
    
    
    is_acquiring = False
    
    while True:
        if cap1 is None or not cap1.isOpened():
            print("Riapertura della webcam principale...")
            cap1 = init_camera()
            osc_client.send_message("/sequences/Seq 1/play", 1)
            if not cap1.isOpened():
                print("Errore nella riapertura della webcam")
                break
                
        ret1, frame1 = cap1.read()
        if not ret1:
            print("Errore nella lettura dalla webcam1")
            cap1.release()
            cap1 = None
            continue
        
        if not is_acquiring:
            trigger_activated = hand_detector.detect_open_hand(frame1)
            
            if trigger_activated:
                print(f"\nMano {hand_detector.last_detected_hand} aperta rilevata per 2 secondi!")
                is_acquiring = True
                hand_detector.status = "ACQUISIZIONE IN CORSO"
                
                osc_client.send_message("/sequences/Seq 2/play", 1)
                
                # print("Attesa iniziale...")
                # for _ in tqdm(range(40), desc="Preparazione acquisizione", unit="decisec"):
                #     time.sleep(0.1)

                print("Rilascio camera 1...")
                cap1.release()
                cap1 = None

                print("Apertura camera 2...")
                cap2 = cv2.VideoCapture(camera_2)
                osc_client.send_message("/sequences/Seq 3/play", 1)

                frames = []
                start_time = time.time()
                print("Registrazione frames...")
                
                with tqdm(total=40, desc="Acquisizione frames", unit="frame") as pbar:
                    while time.time() - start_time < 4:
                        ret2, frame2 = cap2.read()
                        if ret2:
                            frames.append(frame2)
                            pbar.update(1)
                
                cap2.release()
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                gif_path = os.path.join(output_folder, f"captured_{timestamp}.gif")
                osc_client.send_message("/sequences/Seq 4/play", 1)
                create_gif(frames, gif_path)
                print(f"GIF salvata: {gif_path}")
                
                
                # print("Attesa prima del prossimo rilevamento...")
                # for _ in tqdm(range(50), desc="Cooldown", unit="decisec"):
                #     time.sleep(0.1)
                
                is_acquiring = False
                hand_detector.status = "IN ATTESA"
                hand_detector.current_duration = 0.0
                print("\nIn attesa del rilevamento della mano...")
        
        display_frame = add_status_overlay(frame1, hand_detector, is_acquiring)
        cv2.imshow(window_name, display_frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    if cap1 is not None:
        cap1.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()