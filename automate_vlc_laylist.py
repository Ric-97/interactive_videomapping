import os
import time

def update_playlist(folder_path, playlist_path):
    """Aggiorna la playlist VLC in formato M3U con tutti i file GIF nella cartella"""
    # Trova tutti i file GIF nella cartella
    gif_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.gif')]
    
    # Crea la playlist M3U
    with open(playlist_path, 'w', encoding='utf-8') as playlist:
        # Scrivi l'header M3U
        playlist.write('#EXTM3U\n')
        
        # Aggiungi ogni file GIF
        for gif in gif_files:
            file_path = os.path.abspath(os.path.join(folder_path, gif))
            # Aggiungi informazioni sul file
            playlist.write(f'#EXTINF:-1,{gif}\n')
            # Aggiungi il percorso del file
            playlist.write(f'{file_path}\n')
    
    print(f"Playlist aggiornata: {playlist_path}")
    print(f"Numero di GIF nella playlist: {len(gif_files)}")

def monitor_folder(folder_path, playlist_path, check_interval=30):
    """Monitora la cartella e aggiorna la playlist ogni intervallo specificato"""
    print(f"Avvio monitoraggio della cartella: {folder_path}")
    print(f"La playlist verrà salvata in: {playlist_path}")
    print(f"Intervallo di controllo: {check_interval} secondi")
    
    try:
        while True:
            update_playlist(folder_path, playlist_path)
            time.sleep(check_interval)
    except KeyboardInterrupt:
        print("\nMonitoraggio interrotto")

if __name__ == "__main__":
    # Configura questi percorsi
    FOLDER_TO_WATCH = 'C:/Users/riccardoruta/Documents/progetti/OpenCV_Party/captured_gifs'
    PLAYLIST_PATH = "playlist.m3u"  # Modifica questo
    
    monitor_folder(FOLDER_TO_WATCH, PLAYLIST_PATH)