import socket
import random
import sys

MASTER_IP = "127.0.0.1"
MASTER_PORT = 5000

class Routeur:

    def __init__(self, id_routeur, ip_local, port_ecoute):
        self.id = id_routeur
        self.ip = ip_local
        self.port = port_ecoute
        self.cle_publique = self.generer_cle()

    def generer_cle(self, longueur=20):
        return ''.join(str(random.randint(0, 1)) for _ in range(longueur))

    def dechiffrer(self, texte):
        return ''.join(chr(ord(c) ^ 1) for c in texte)

    def envoyer_au_master(self):
        msg = f"ROUTER {self.id} {self.ip} {self.cle_publique} {self.port}"
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((MASTER_IP, MASTER_PORT))
        s.sendall(msg.encode())
        s.close()
        print(f"[{self.id}] Déclaré au Master.")

    def ecouter(self):
        serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serv.bind((self.ip, self.port))
        serv.listen()

        print(f"[{self.id}] Écoute sur {self.ip}:{self.port}")

        while True:
            conn, addr = serv.accept()
            data = conn.recv(4096).decode().strip()
            conn.close()

            if not data:
                continue

            print(f"[{self.id}] Reçu : {repr(data)}")

            parts = data.split(" ", 2)
            if len(parts) < 3:
                print(f"[{self.id}] Format invalide :", parts)
                continue

            ip_next, port_next, contenu = parts
            contenu_dechiffre = self.dechiffrer(contenu)

            out = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            out.connect((ip_next, int(port_next)))
            out.sendall(contenu_dechiffre.encode())
            out.close()

            print(f"[{self.id}] Transmis à {ip_next}:{port_next}")

    def demarrer(self):
        self.envoyer_au_master()
        self.ecouter()


if __name__ == "__main__":

    if len(sys.argv) != 3:
        print("Usage : python router.py <ID> <PORT>")
        exit(1)

    rid = sys.argv[1]
    port_local = int(sys.argv[2])

    r = Routeur(rid, "127.0.0.1", port_local)
    r.demarrer()
