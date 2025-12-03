import socket
import threading
import random

class Router:
    def __init__(self, router_id, listen_port, master: object):
        self.__id = router_id
        self.__listen_port = listen_port
        self.__master = master  # Agrégation
        self.__public_key = self.generate_public_key()

    # ============================
    # Getters / Setters
    # ============================
    def get_id(self):
        return self.__id

    def get_public_key(self):
        return self.__public_key

    def get_listen_port(self):
        return self.__listen_port

    # ============================
    # Clé publique
    # ============================
    def generate_public_key(self, length=20):
        return ''.join(str(random.randint(0, 1)) for _ in range(length))

    # ============================
    # Chiffrement simple bidon
    # ============================
    def decrypt_layer(self, text):
        return ''.join(chr(ord(c) ^ 1) for c in text)

    # ============================
    # Enregistrement auprès du Master
    # ============================
    def register_master(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.__master.get_master_ip(), self.__master.get_master_port()))

        msg = f"{self.__id} {self.__public_key} {self.__listen_port}"
        s.send(msg.encode())
        s.close()

        print(f"[ROUTER {self.__id}] Enregistré au Master.")

    # ============================
    # Écoute des messages
    # ============================
    def listen(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(("0.0.0.0", self.__listen_port))
        s.listen()

        print(f"[ROUTER {self.__id}] Écoute sur {self.__listen_port}")

        while True:
            conn, addr = s.accept()
            data = conn.recv(4096).decode()
            conn.close()

            print(f"[ROUTER {self.__id}] Reçu : {data}")

            parts = data.split(" ", 2)
            next_ip = parts[0]
            next_port = int(parts[1])
            payload = parts[2]

            decrypted = self.decrypt_layer(payload)

            out = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            out.connect((next_ip, next_port))
            out.send(decrypted.encode())
            out.close()

            print(f"[ROUTER {self.__id}] Forward vers {next_ip}:{next_port}")

    # ============================
    # Démarrage
    # ============================
    def start(self):
        self.register_master()
        self.listen()


if __name__ == "__main__":
    from master import Master
    master = Master()
    r1 = Router("R1", 6001, master)
    r1.start()
    r2 = Router("R2", 6002, master)
    r2.start()
    r3 = Router("R3", 6003, master)
    r3.start()