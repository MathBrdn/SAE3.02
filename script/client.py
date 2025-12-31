import socket
import random
import sys
import threading


class Client:
    def __init__(self, client_ip, client_port, master_ip, master_port):
        self.client_ip = client_ip
        self.client_port = client_port
        self.master_ip = master_ip
        self.master_port = master_port

    # ---------- ÉCOUTE ----------
    def ecouter(self):
        s = socket.socket()
        s.bind((self.client_ip, self.client_port))
        s.listen()

        print(f"[CLIENT {self.client_ip}:{self.client_port}] en attente...")

        while True:
            c, _ = s.accept()
            data = c.recv(8192)
            c.close()

            if not data:
                continue

            print(f"[CLIENT {self.client_port}] MESSAGE FINAL : {data.decode(errors='ignore')}")

    # ---------- MASTER ----------
    def recuperer_routeurs(self):
        s = socket.socket()
        s.connect((self.master_ip, self.master_port))
        s.sendall(b"CLIENT")

        buffer = ""
        while "END\n" not in buffer:
            buffer += s.recv(1024).decode()
        s.close()

        routeurs = []
        for line in buffer.splitlines():
            if line == "END":
                break
            rid, ip, port = line.split()
            routeurs.append((rid, ip, int(port)))

        return routeurs

    # ---------- ENVOI ----------
    def envoyer_message(self, message, dest_ip, dest_port, nb_routeurs):
        routeurs = self.recuperer_routeurs()

        if len(routeurs) < nb_routeurs:
            print("[CLIENT] Pas assez de routeurs disponibles")
            return

        chemin = random.sample(routeurs, nb_routeurs)

        print("[CLIENT] Chemin choisi :")
        for rid, ip, port in chemin:
            print(f"   - {rid} ({ip}:{port})")

        # Dernière étape : client destinataire
        payload = f"ROUTE|{dest_ip}|{dest_port}|{message}"

        # Empilement des routeurs (sauf le premier)
        for _, ip, port in reversed(chemin[1:]):
            payload = f"ROUTE|{ip}|{port}|{payload}"

        # Envoi au premier routeur
        _, ip0, port0 = chemin[0]

        try:
            s = socket.socket()
            s.connect((ip0, port0))
            s.sendall(payload.encode())
            s.close()
            print("[CLIENT] message envoyé")

        except Exception as e:
            print(f"[CLIENT] erreur envoi vers {ip0}:{port0} -> {e}")


# ================= MAIN =================

if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("Usage :")
        print("  python client.py <CLIENT_IP> <CLIENT_PORT> <MASTER_IP> <MASTER_PORT>")
        print("  python client.py <CLIENT_IP> <CLIENT_PORT> <MASTER_IP> <MASTER_PORT> send <DEST_IP> <DEST_PORT> \"MESSAGE\" <NB_ROUTEURS>")
        sys.exit(1)

    client_ip = sys.argv[1]
    client_port = int(sys.argv[2])
    master_ip = sys.argv[3]
    master_port = int(sys.argv[4])

    client = Client(client_ip, client_port, master_ip, master_port)

    # Thread écoute
    threading.Thread(target=client.ecouter, daemon=True).start()

    # Envoi optionnel
    if len(sys.argv) > 5 and sys.argv[5] == "send":
        if len(sys.argv) < 10:
            print("Arguments manquants pour l'envoi")
            sys.exit(1)

        dest_ip = sys.argv[6]
        dest_port = int(sys.argv[7])
        message = sys.argv[8]
        nb_routeurs = int(sys.argv[9])

        client.envoyer_message(message, dest_ip, dest_port, nb_routeurs)

    # Boucle infinie
    while True:
        pass
