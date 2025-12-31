import socket
import sys
import mysql.connector


class Master:
    def __init__(self, public_ip: str, port: int):
        self.public_ip = public_ip
        self.port = port

        # Connexion MariaDB (locale Ã  la VM master)
        try:
            self.db = mysql.connector.connect(
                host="localhost",
                user="toto",
                password="toto",
                database="SAE302"
            )
            self.cursor = self.db.cursor()
            print("[MASTER] Connexion MariaDB OK")

        except mysql.connector.Error as e:
            print(f"[MASTER] Erreur connexion DB : {e}")
            sys.exit(1)

    # ================= RESET BDD =================
    def reset_database(self):
        try:
            self.cursor.execute("DELETE FROM routeurs")
            self.cursor.execute("DELETE FROM clients")
            self.db.commit()
            print("[MASTER] Base de donnÃ©es rÃ©initialisÃ©e (routeurs + clients)")

        except mysql.connector.Error as e:
            print(f"[MASTER] Erreur reset BDD : {e}")
            sys.exit(1)

    # ================= ROUTEUR =================
    def traiter_routeur(self, message: str):
        """
        Message attendu :
        ROUTER <ID> <PORT>
        """
        parts = message.split()
        if len(parts) != 3 or parts[0] != "ROUTER":
            print("[MASTER] Message routeur invalide")
            return

        _, rid, port = parts

        try:
            self.cursor.execute(
                """
                INSERT INTO routeurs (id_routeur, port, cle_publique)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE port=%s
                """,
                (rid, int(port), "NOPUBKEY", int(port))
            )
            self.db.commit()
            print(f"[MASTER] Routeur {rid} enregistre (port {port})")

        except mysql.connector.Error as e:
            print(f"[MASTER] Erreur DB routeur : {e}")

    # ================= CLIENT =================
    def traiter_client(self, connexion: socket.socket):
        """
        Envoie :
        <ID_ROUTEUR> <IP_MASTER> <PORT>
        """
        try:
            self.cursor.execute(
                "SELECT id_routeur, port FROM routeurs"
            )

            for rid, port in self.cursor.fetchall():
                ligne = f"{rid} {self.public_ip} {port}\n"
                connexion.sendall(ligne.encode())

            connexion.sendall(b"END\n")

        except mysql.connector.Error as e:
            print(f"[MASTER] Erreur DB client : {e}")

    # ================= SERVEUR =================
    def demarrer(self):
        # RESET COMPLET AU DEMARRAGE
        self.reset_database()

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(("0.0.0.0", self.port))
        s.listen()

        print(f"[MASTER] Ecoute sur 0.0.0.0:{self.port}")
        print(f"[MASTER] IP publique annoncee : {self.public_ip}")

        while True:
            connexion, _ = s.accept()

            try:
                message = connexion.recv(4096).decode().strip()

                if not message:
                    connexion.close()
                    continue

                if message.startswith("ROUTER"):
                    self.traiter_routeur(message)

                elif message == "CLIENT":
                    self.traiter_client(connexion)

            except Exception as e:
                print(f"[MASTER] Erreur socket : {e}")

            connexion.close()


# ================= MAIN =================
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage : python3 master.py <IP_PUBLIQUE> <PORT>")
        sys.exit(1)

    ip_publique = sys.argv[1]
    port = int(sys.argv[2])

    Master(ip_publique, port).demarrer()