import socket
import sys

MASTER_IP = "127.0.0.1"
MASTER_PORT = 5000

class Routeur:
    def __init__(self, rid, port):
        self.__id = rid
        self.__port = port

    def envoyer_master(self):
        msg = f"ROUTER {self.__id} 127.0.0.1 {self.__port}"
        s = socket.socket()
        s.connect((MASTER_IP, MASTER_PORT))
        s.sendall(msg.encode())
        s.close()
        print(f"[{self.__id}] déclaré au master")

    def envoyer(self, ip, port, data):
        s = socket.socket()
        s.connect((ip, port))
        s.sendall(data)
        s.close()

    def ecouter(self):
        s = socket.socket()
        s.bind(("0.0.0.0", self.__port))
        s.listen()
        print(f"[{self.__id}] écoute sur {self.__port}")

        while True:
            c, _ = s.accept()
            data = c.recv(8192)
            c.close()

            if not data:
                continue

            text = data.decode(errors="ignore")

            # ---------- ROUTAGE ----------
            if text.startswith("ROUTE|"):
                try:
                    _, ip, port, reste = text.split("|", 3)
                    print(f"[{self.__id}] ➡ vers {ip}:{port}")
                    self.envoyer(ip, int(port), reste.encode())
                except Exception:
                    print(f"[{self.__id}] ❌ paquet invalide")
            else:
                # sécurité : ne rien faire si paquet inattendu
                print(f"[{self.__id}] ⚠ paquet ignoré")


    def demarrer(self):
        self.envoyer_master()
        self.ecouter()


if __name__ == "__main__":
    Routeur(sys.argv[1], int(sys.argv[2])).demarrer()
