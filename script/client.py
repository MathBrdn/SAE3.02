import socket
import random
import sys
import threading
import os

MASTER_IP = "127.0.0.1"
MASTER_PORT = 5000

def xor_bytes(data: bytes, key: bytes) -> bytes:
    return bytes(b ^ key[i % len(key)] for i, b in enumerate(data))

def rsa_chiffrer(m: int, e: int, n: int) -> int:
    return pow(m, e, n)

class Client:
    def __init__(self, ip, port):
        self.__ip = ip
        self.__port = port

    def ecouter(self):
        serveur = socket.socket()
        serveur.bind((self.__ip, self.__port))
        serveur.listen()

        print(f"[CLIENT {self.__port}] 🟢 en attente...")

        while True:
            c, _ = serveur.accept()
            data = c.recv(8192)
            c.close()

            if not data:
                print("[CLIENT] ⚠ paquet vide")
                continue

            print(f"[CLIENT {self.__port}] 📩 paquet reçu ({len(data)} octets)")
            print(f"[CLIENT {self.__port}] ✅ MESSAGE FINAL : {data.decode(errors='ignore')}")


    def recuperer_routeurs(self):
        s = socket.socket()
        s.connect((MASTER_IP, MASTER_PORT))
        s.sendall(b"CLIENT")

        buffer = ""
        while "END\n" not in buffer:
            buffer += s.recv(1024).decode()
        s.close()

        routeurs = []
        for l in buffer.splitlines():
            if l == "END":
                break
            rid, ip, port, e, n = l.split()
            routeurs.append((ip, int(port), int(e), int(n)))

        return routeurs

    def envoyer_message(self, message, ip_dest, port_dest, nb_routeurs=3):
        routeurs = self.recuperer_routeurs()
        chemin = random.sample(routeurs, nb_routeurs)

        payload = message.encode()

        for ip, port, e, n in reversed(chemin):
            cle_xor = os.urandom(16)
            payload = xor_bytes(payload, cle_xor)
            cle_int = int.from_bytes(cle_xor, "big")
            cle_rsa = rsa_chiffrer(cle_int, e, n)
            payload = f"{cle_rsa}|{ip}|{port}|".encode() + payload

        ip0, port0, *_ = chemin[0]
        s = socket.socket()
        s.connect((ip0, port0))
        s.sendall(payload)
        s.close()

        print("[CLIENT] message envoyé")


if __name__ == "__main__":
    port = int(sys.argv[1])
    c = Client("127.0.0.1", port)
    threading.Thread(target=c.ecouter, daemon=True).start()

    if len(sys.argv) > 4 and sys.argv[2] == "send":
        c.envoyer_message(
            " ".join(sys.argv[5:]),
            sys.argv[3],
            int(sys.argv[4])
        )

    while True:
        pass
