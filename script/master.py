import socket

class Master:
    def __init__(self, ip="127.0.0.1", port=5000):
        self.__ip = ip
        self.__port = port
        self.__routeurs = {}  # id -> (ip, port)

    def traiter_routeur(self, message: str):
        """
        ROUTER <ID> <IP> <PORT>
        """
        parts = message.split()
        if len(parts) != 4 or parts[0] != "ROUTER":
            print("[MASTER] Message routeur invalide")
            return

        _, rid, ip, port = parts
        self.__routeurs[rid] = (ip, int(port))
        print(f"[MASTER] Routeur {rid} enregistré ({ip}:{port})")

    def traiter_client(self, connexion):
        for rid, (ip, port) in self.__routeurs.items():
            connexion.sendall(f"{rid} {ip} {port}\n".encode())
        connexion.sendall(b"END\n")

    def demarrer(self):
        s = socket.socket()
        s.bind((self.__ip, self.__port))
        s.listen()
        print(f"[MASTER] Écoute sur {self.__ip}:{self.__port}")

        while True:
            c, _ = s.accept()
            msg = c.recv(4096).decode().strip()

            if msg.startswith("ROUTER"):
                self.traiter_routeur(msg)
            elif msg == "CLIENT":
                self.traiter_client(c)

            c.close()


if __name__ == "__main__":
    Master().demarrer()
