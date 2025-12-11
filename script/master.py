import socket
import threading

class Master:
    """
    Serveur central qui reçoit les déclarations des routeurs
    et fournit la liste des routeurs aux clients.
    """

    routeurs = {}  # {ID : (IP, PORT, CLE)}

    def __init__(self, ip="127.0.0.1", port=5000):
        self.ip = ip
        self.port = port

    def ajouter_routeur(self, rid, ip, port, cle):
        Master.routeurs[rid] = (ip, port, cle)
        print(f"[MASTER] Routeur enregistré : {rid} - {ip}:{port}")

    def traiter_message_routeur(self, message):
        """
        Format attendu : ROUTER <ID> <IP> <CLE> <PORT>
        """
        elem = message.split()
        if len(elem) != 5:
            print("[MASTER] ERREUR message routeur:", elem)
            return

        _, rid, ip, cle, port = elem
        self.ajouter_routeur(rid, ip, int(port), cle)

    def traiter_message_client(self, conn):
        """
        Envoie tous les routeurs :
        <ID> <IP> <PORT> <CLE>\n
        Puis END
        """
        for rid, (ip, port, cle) in Master.routeurs.items():
            ligne = f"{rid} {ip} {port} {cle}\n"
            conn.sendall(ligne.encode())
        conn.sendall(b"END\n")

    def demarrer(self):
        serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serveur.bind((self.ip, self.port))
        serveur.listen()

        print(f"[MASTER] Écoute sur {self.ip}:{self.port}")

        while True:
            conn, addr = serveur.accept()
            data = conn.recv(1024).decode().strip()

            if not data:
                conn.close()
                continue

            type_msg = data.split()[0]

            if type_msg == "ROUTER":
                self.traiter_message_routeur(data)

            elif type_msg == "CLIENT":
                self.traiter_message_client(conn)

            conn.close()


if __name__ == "__main__":
    Master().demarrer()
