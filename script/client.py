import socket
import threading
import random

MASTER_IP = "127.0.0.1"
MASTER_PORT = 5000

class Client:

    def __init__(self, ip_local, port_local):
        self.ip = ip_local
        self.port = port_local

    def ecouter(self):
        serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serv.bind((self.ip, self.port))
        serv.listen()

        print(f"[CLIENT {self.ip}:{self.port}] En attente du message final...")

        while True:
            conn, addr = serv.accept()
            data = conn.recv(4096).decode()
            conn.close()
            print(f"[CLIENT {self.port}] Message reçu : {data}")

    def recuperer_routeurs(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((MASTER_IP, MASTER_PORT))
        s.sendall(b"CLIENT")

        buffer = s.recv(4096).decode()
        s.close()

        routeurs = {}
        for ligne in buffer.splitlines():
            ligne = ligne.strip()
            if ligne == "END":
                break

            rid, ip, port, cle = ligne.split()
            routeurs[rid] = (ip, int(port))

        return routeurs

    def envoyer_message(self, message, ip_dest, port_dest):
        routeurs = self.recuperer_routeurs()

        if not routeurs:
            print("Aucun routeur disponible.")
            return

        rid, (rip, rport) = random.choice(list(routeurs.items()))
        print(f"[CLIENT] Envoi via {rid} ({rip}:{rport})")

        contenu = f"{ip_dest} {port_dest} {message}"

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((rip, rport))
        s.sendall(contenu.encode())
        s.close()


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 3:
        print("Usage : python client.py <PORT_LOCAL>")
        exit(1)

    ip_local = "127.0.0.1"
    port_local = int(sys.argv[1])

    client = Client(ip_local, port_local)

    threading.Thread(target=client.ecouter).start()

    # Exemple d’envoi local :
    # client.envoyer_message("Salut !", "127.0.0.1", 7002)
