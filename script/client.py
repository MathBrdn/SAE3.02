# client.py (version robuste, noms FR, docstrings)
import socket
import random

class Client:
    """
    Client récupérant la liste des routeurs auprès du Master
    et envoyant un message simple via un routeur choisi aléatoirement.
    """

    def __init__(self, ip_master="127.0.0.1", port_master=5000):
        self.__ip_master = ip_master
        self.__port_master = port_master

    def get_ip_master(self):
        return self.__ip_master

    def set_ip_master(self, ip):
        self.__ip_master = ip

    def get_port_master(self):
        return self.__port_master

    def set_port_master(self, port):
        self.__port_master = port

    def recuperer_routeurs(self):
        """
        Se connecte au Master et récupère la liste des routeurs.
        Retourne un dictionnaire {ID_routeur: port}.
        Le protocole attendu (par ligne) : "<ID> <PORT> <CLE>"
        Fin du flux : ligne "END"
        """
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.__ip_master, self.__port_master))

        # Indique que l'on est un client
        s.sendall(b"CLIENT\n")

        buffer = ""
        # Lire jusqu'à recevoir la ligne "END"
        while True:
            chunk = s.recv(1024).decode()
            if not chunk:
                # connexion fermée par le serveur
                break
            buffer += chunk
            if "END\n" in buffer:
                break

        s.close()

        # Traiter chaque ligne reçue
        routeurs = {}
        for ligne in buffer.splitlines():
            ligne = ligne.strip()
            if not ligne:
                continue
            if ligne == "END":
                break

            # Utiliser maxsplit=2 pour autoriser la clé à contenir des espaces
            parts = ligne.split(maxsplit=2)
            if len(parts) < 3:
                # Ligne malformée — afficher pour debug et ignorer
                print("DEBUG - ligne routeur malformée (ignorée) :", repr(ligne))
                continue

            id_routeur, port_str, cle = parts
            try:
                port = int(port_str)
            except ValueError:
                print("DEBUG - port invalide pour la ligne (ignorée) :", repr(ligne))
                continue

            routeurs[id_routeur] = port

        return routeurs

    def envoyer_message(self, message="Bonjour !"):
        """
        Envoie un message via un routeur choisi aléatoirement.
        """
        routeurs = self.recuperer_routeurs()
        print("Routeurs disponibles :", routeurs)

        if not routeurs:
            print("Aucun routeur disponible.")
            return

        id_routeur, port = random.choice(list(routeurs.items()))

        contenu = f"127.0.0.1 {port} {message}"

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(("127.0.0.1", port))
        s.sendall(contenu.encode())
        s.close()

        print(f"Message envoyé via {id_routeur}.")

if __name__ == "__main__":
    client = Client()
    client.envoyer_message()
