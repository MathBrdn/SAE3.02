import socket
import sys

MASTER_IP = "127.0.0.1"
MASTER_PORT = 5000

# ================= CRYPTO =================

def xor_bytes(data: bytes, key: bytes) -> bytes:
    return bytes(b ^ key[i % len(key)] for i, b in enumerate(data))

def rsa_dechiffrer(c: int, d: int, n: int) -> int:
    return pow(c, d, n)

# ================= ROUTEUR =================

class Routeur:
    def __init__(self, rid, ip, port):
        self.__id = rid
        self.__ip = ip
        self.__port = port

        # 🔑 RSA pédagogique (FIXE, autorisé)
        self.__e = 17
        self.__n = 3233        # 61 * 53
        self.__d = 2753        # inverse de e mod phi

    def envoyer_master(self):
        msg = f"ROUTER {self.__id} {self.__ip} {self.__port} {self.__e} {self.__n}"
        s = socket.socket()
        s.connect((MASTER_IP, MASTER_PORT))
        s.sendall(msg.encode())
        s.close()
        print(f"[{self.__id}] déclaré au master")

    def envoyer(self, ip, port, data: bytes):
        s = socket.socket()
        s.connect((ip, port))
        s.sendall(data)
        s.close()

    def ecouter(self):
        serveur = socket.socket()
        serveur.bind(("0.0.0.0", self.__port))
        serveur.listen()

        print(f"[{self.__id}] écoute sur {self.__port}")

        while True:
            c, _ = serveur.accept()
            data = c.recv(8192)
            c.close()

            if not data:
                print(f"[{self.__id}] ⚠ paquet vide")
                continue

            print(f"[{self.__id}] 📥 paquet reçu ({len(data)} octets)")

            # 🔓 Retrait d’UNE couche
            try:
                data = self.dechiffrer(data)
                print(f"[{self.__id}] 🔓 couche retirée")
            except Exception as e:
                print(f"[{self.__id}] ❌ ERREUR déchiffrement : {e}")
                continue

            # ---------- ROUTAGE ----------
            if data.startswith(b"FINAL|"):
                _, ip, port, msg = data.split(b"|", 3)
                print(f"[{self.__id}] 🚀 ENVOI AU CLIENT {ip.decode()}:{port.decode()}")
                self.envoyer(ip.decode(), int(port), msg)

            else:
                ip, port, reste = data.split(b"|", 2)
                print(f"[{self.__id}] ➡ relais vers {ip.decode()}:{port.decode()}")
                self.envoyer(ip.decode(), int(port), reste)


    def demarrer(self):
        self.envoyer_master()
        self.ecouter()


if __name__ == "__main__":
    Routeur(sys.argv[1], "127.0.0.1", int(sys.argv[2])).demarrer()
