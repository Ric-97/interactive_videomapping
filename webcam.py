import cv2

def main():
    # Inizializzazione della webcam
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Errore nell'apertura della webcam.")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Errore nel leggere il frame dalla webcam.")
            break

        # Mostra il video in una finestra
        cv2.imshow("Webcam Feed", frame)

        # Premere 'q' per uscire
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Rilascia la videocamera e chiude tutte le finestre
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
