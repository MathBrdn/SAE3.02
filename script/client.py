import socket
import random
import sys
import threading

MASTER_IP = "127.0.0.1"
MASTER_PORT = 5000

class Client:
    def __init__(self, ip, port):
        self.__ip = ip
        self.__port = port

    def ecouter(self):
        s = socket.socket()
        s.bind((self.__ip, self.__port))
        s.listen()
        print(f"[CLIENT {self.__port}] 🟢 en attente...")

        while True:
            c, _ = s.accept()
            msg = c.recv(8192)
            c.close()
            print(f"[CLIENT {self.__port}] 📩 MESSAGE FINAL : {msg.decode()}")

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
            rid, ip, port = l.split()
            routeurs.append((ip, int(port)))

        return routeurs

    def envoyer_message(self, message, ip_dest, port_dest, nb_routeurs=3):
        routeurs = self.recuperer_routeurs()
        chemin = random.sample(routeurs, nb_routeurs)

        payload = message

        # le dernier saut est le client final
        payload = f"ROUTE|{ip_dest}|{port_dest}|{message}"

        # on empile uniquement les routeurs SUIVANTS
        for ip, port in reversed(chemin[1:]):
            payload = f"ROUTE|{ip}|{port}|{payload}"


        s = socket.socket()
        s.connect(chemin[0])
        s.sendall(payload.encode())
        s.close()
        print("[CLIENT] 🟢 message envoyé")


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
