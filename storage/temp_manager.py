import os
import time
import threading

TEMP_DIR = "/tmp/nitropix"
MAX_AGE = 48 * 60 * 60  # 48 horas


def cleanup_old_files():

    if not os.path.exists(TEMP_DIR):
        return

    now = time.time()

    for filename in os.listdir(TEMP_DIR):

        path = os.path.join(TEMP_DIR, filename)

        if not os.path.isfile(path):
            continue

        file_age = now - os.path.getmtime(path)

        if file_age > MAX_AGE:
            try:
                os.remove(path)
                print(f"[CLEANUP] Eliminado: {filename}")
            except Exception as e:
                print(f"[CLEANUP ERROR] {e}")


def cleanup_loop():
    while True:
        cleanup_old_files()
        time.sleep(3600)  # revisa cada 1 hora


def start_cleanup_worker():
    thread = threading.Thread(target=cleanup_loop, daemon=True)
    thread.start()