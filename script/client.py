import socket
import random

class Client:
    def __init__(self, master_ip="127.0.0.1", master_port=5000):
        self.__master_ip = master_ip
        self.__master_port = master_port

    # ============================
    # Getters / Setters
    # ============================
    def get_master_ip(self):
        return self.__master_ip

    def set_master_ip(self, ip):
        self.__master_ip = ip

    def get_master_port(self):
        return self.__master_port

    def set_master_port(self, port):
        self.__master_port = port

    # ============================
    # Récupération des routeurs
    # ============================
    def get_routeurs(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.__master_ip, self.__master_port))
        s.send("CLIENT".encode())

        routers = {}
        while True:
            line = s.recv(1024).decode()
            if not line or line.startswith("END"):
                break
            rid, port, key = line.strip().split()
            routers[rid] = int(port)

        s.close()
        return routers

    # ============================
    # Envoi simple (pas de chiffrement)
    # ============================
    def send_message(self, message="Bonjour B !"):
        routers = self.get_routeurs()
        print("[CLIENT] Routeurs disponibles :", routers)

        if len(routers) < 1:
            print("[CLIENT] Aucun routeur disponible.")
            return

        # Choix d'un routeur
        rid, port = random.choice(list(routers.items()))

        payload = f"127.0.0.1 {port} {message}"

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(("127.0.0.1", port))
        s.send(payload.encode())
        s.close()

        print(f"[CLIENT] Message envoyé via {rid}.")


if __name__ == "__main__":
    c = Client()
    c.send_message()
