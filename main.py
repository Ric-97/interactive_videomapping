import cv2

# Inizializzazione del rilevatore HOG con un classificatore pre-addestrato per persone
hog = cv2.HOGDescriptor()
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

def detect_people(frame):
    """Rilevazione delle persone in un frame."""
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # Conversione in scala di grigi
    boxes, _ = hog.detectMultiScale(gray_frame, winStride=(8, 8), padding=(8, 8), scale=1.05)
    return len(boxes) > 0  # Ritorna True se rileva persone, False altrimenti

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

def main():
    cap = cv2.VideoCapture(1)  # Utilizza la cam esterna (1) per il video input

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Divide il frame in 16 riquadri
        quadrants = divide_frame(frame)

        for quadrant, index in quadrants:
            # Rileva persone nel riquadro
            is_person_detected = detect_people(quadrant)
            
            # Disegna i riquadri sul frame originale con indicazione di rilevamento
            height, width = frame.shape[:2]
            step_x, step_y = width // 4, height // 4
            x_start = (index % 4) * step_x
            y_start = (index // 4) * step_y

            color = (0, 255, 0) if is_person_detected else (0, 0, 255)  # Verde se rilevata, rosso se no
            cv2.rectangle(frame, (x_start, y_start), (x_start + step_x, y_start + step_y), color, 2)
            cv2.putText(frame, f"Q{index}: {'Pres' if is_person_detected else 'Ass'}", 
                        (x_start + 10, y_start + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

        # Mostra il video con i riquadri
        cv2.imshow("People Detection with Quadrants", frame)

        # Break loop on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
