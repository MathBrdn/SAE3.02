import socket
import threading

class Master:
    # === Attribut de classe ===
    router_list = {}   # Un seul Master → acceptable

    def __init__(self, master_ip="127.0.0.1", master_port=5000):
        self.__master_ip = master_ip
        self.__master_port = master_port

    # ============================
    # Getters / Setters
    # ============================
    def get_master_ip(self):
        return self.__master_ip

    def get_master_port(self):
        return self.__master_port

    def set_master_ip(self, new_ip):
        self.__master_ip = new_ip

    def set_master_port(self, new_port):
        self.__master_port = new_port

    # ============================
    # Gestion des routeurs
    # ============================
    def add_router(self, router_id, port, public_key):
        Master.router_list[router_id] = (port, public_key)
        print(f"[MASTER] Routeur {router_id} ajouté → port={port}, key={public_key}")

    # ============================
    # Connexions routeur / client
    # ============================

    def handle_router(self, conn):
        data = conn.recv(1024).decode().strip()

        print(f"[MASTER] Message brut reçu du routeur : '{data}'")

        parts = data.split()
        if len(parts) < 3:
            print("[MASTER] ERREUR : message routeur invalide :", parts)
            conn.close()
            return

        router_id = parts[0]
        public_key = parts[1]
        listen_port = int(parts[2])

        self.add_router(router_id, listen_port, public_key)
        conn.close()


    # ============================
    # Boucle principale
    # ============================
    def start(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((self.__master_ip, self.__master_port))
        s.listen()

        print(f"[MASTER] Écoute sur {self.__master_ip}:{self.__master_port}")

        while True:
            conn, addr = s.accept()
            mode = conn.recv(6).decode()

            if mode == "ROUTER":
                threading.Thread(target=self.handle_router, args=(conn,)).start()
            elif mode == "CLIENT":
                threading.Thread(target=self.handle_client, args=(conn,)).start()


if __name__ == "__main__":
    master = Master()
    master.start()
