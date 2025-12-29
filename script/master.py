import socket

class Master:
    def __init__(self, ip="127.0.0.1", port=5000):
        self.__ip = ip
        self.__port = port
        self.__routeurs = {}  # id -> (ip, port, e, n)

    def traiter_routeur(self, message: str):
        """
        ROUTER <ID> <IP> <PORT> <E> <N>
        """
        parts = message.split()
        if len(parts) != 6 or parts[0] != "ROUTER":
            print("[MASTER] Message routeur invalide")
            return

        _, rid, ip, port, e, n = parts
        self.__routeurs[rid] = (ip, int(port), int(e), int(n))
        print(f"[MASTER] Routeur {rid} enregistré ({ip}:{port})")

    def traiter_client(self, connexion):
        for rid, (ip, port, e, n) in self.__routeurs.items():
            connexion.sendall(f"{rid} {ip} {port} {e} {n}\n".encode())
        connexion.sendall(b"END\n")

    def demarrer(self):
        s = socket.socket()
        s.bind((self.__ip, self.__port))
        s.listen()

        print(f"[MASTER] Écoute sur {self.__ip}:{self.__port}")

        while True:
            connexion, _ = s.accept()
            message = connexion.recv(4096).decode().strip()

            if not message:
                connexion.close()
                continue

            if message.startswith("ROUTER"):
                self.traiter_routeur(message)

            elif message == "CLIENT":
                self.traiter_client(connexion)

            connexion.close()


if __name__ == "__main__":
    Master().demarrer()
