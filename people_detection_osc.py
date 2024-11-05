import cv2
import numpy as np
from pythonosc import udp_client

# Carica il classificatore a cascata per il rilevamento delle teste
head_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Configurazione del client OSC
client = udp_client.SimpleUDPClient("127.0.0.1", 7000)  # Assicurati che l'indirizzo IP e la porta siano corretti per HeavyM

def detect_heads(frame):
    """Rilevazione delle teste in un frame."""
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    heads = head_cascade.detectMultiScale(gray_frame, 1.1, 4)
    return len(heads) > 0  # Ritorna True se rileva teste, False altrimenti

def divide_frame(frame, rows=4, cols=4):
    """Divide il frame in riquadri definiti da righe e colonne."""
    height, width = frame.shape[:2]
    step_x, step_y = width // cols, height // rows

    quadrants = []
    for i in range(rows):
        for j in range(cols):
            x_start = j * step_x
            y_start = i * step_y
            x_end = (j + 1) * step_x
            y_end = (i + 1) * step_y
            quadrant = frame[y_start:y_end, x_start:x_end]
            quadrants.append((quadrant, i * cols + j))  # Aggiungi il riquadro e l'indice del quadrante
    return quadrants

def send_osc_message(row):
    """Invia il messaggio OSC appropriato in base alla riga."""
    messages = [
        "/sequences/seq1/play",
        "/sequences/seq2/play",
        "/sequences/seq3/play",
        "/sequences/seq4/play"
    ]
    print(messages[row])
    client.send_message(messages[row], 1)  # Invia 1 come argomento

def main():
    cap = cv2.VideoCapture(1)  # Utilizza la cam esterna (1) per il video input

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # # Converti il frame in scala di grigi
        # gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # # Calcola la luminosità media
        # brightness = np.mean(gray)
        
        # # Normalizza la luminosità in un range da 0 a 1
        # normalized_brightness = (brightness/ 255.0)
        # if normalized_brightness < 0.70:
        #     normalized_brightness =  normalized_brightness + 0.30
        # print(normalized_brightness)
        # # Invia i dati a HeavyM tramite OSC
        # client.send_message("/master/opacity/value", normalized_brightness)

        # Divide il frame in 16 riquadri
        quadrants = divide_frame(frame)

        head_detected = [False] * 4  # Una flag per ogni riga

        for quadrant, index in quadrants:
            # Rileva teste nel riquadro
            is_head_detected = detect_heads(quadrant)
            
            if is_head_detected:
                head_detected[index // 4] = True  # Setta la flag per la riga corrispondente
            
            # Disegna i riquadri sul frame originale con indicazione di rilevamento
            height, width = frame.shape[:2]
            step_x, step_y = width // 4, height // 4
            x_start = (index % 4) * step_x
            y_start = (index // 4) * step_y

            color = (0, 255, 0) if is_head_detected else (0, 0, 255)  # Verde se rilevata, rosso se no
            cv2.rectangle(frame, (x_start, y_start), (x_start + step_x, y_start + step_y), color, 2)
            cv2.putText(frame, f"Q{index}: {'Head' if is_head_detected else 'No'}", 
                        (x_start + 10, y_start + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

        # Invia messaggi OSC per le righe in cui è stata rilevata una testa
        for row, detected in enumerate(head_detected):
            if detected:
                print(f"detected head in row:{row}")
                send_osc_message(row)

        # Mostra il video con i riquadri
        cv2.imshow("Head Detection with Quadrants", frame)

        # Break loop on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()