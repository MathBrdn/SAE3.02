import socket
import threading

class Master:
    """
    Représente le serveur central chargé de recevoir et enregistrer les routeurs.
    """

    liste_routeurs = {}   # Unique au Master, utilisé pour fournir les routeurs au client

    def __init__(self, ip_master="127.0.0.1", port_master=5000):
        self.__ip_master = ip_master
        self.__port_master = port_master

    # --- Accesseurs ---
    def get_ip_master(self):
        return self.__ip_master

    def get_port_master(self):
        return self.__port_master

    def set_ip_master(self, new_ip):
        self.__ip_master = new_ip

    def set_port_master(self, new_port):
        self.__port_master = new_port

    # --- Gestion des routeurs ---
    def ajouter_routeur(self, id_routeur, port, cle_publique):
        """Ajoute un routeur à la liste disponible pour les clients."""
        Master.liste_routeurs[id_routeur] = (port, cle_publique)
        print(f"→ Routeur enregistré : {id_routeur} (port {port}, clé {cle_publique})")

    # --- Traitement des messages des routeurs ---
    def traiter_message_routeur(self, message):
        """
        Traite le message reçu d'un routeur et l'enregistre.
        Format attendu :
        ROUTER <ID> <CLE> <PORT>
        """
        elements = message.split()

        if len(elements) < 4:
            print("⚠️ Message routeur invalide :", elements)
            return

        id_routeur = elements[1]
        cle_publique = elements[2]
        port_ecoute = int(elements[3])

        self.ajouter_routeur(id_routeur, port_ecoute, cle_publique)

    def demarrer(self):
        """Démarre le Master et écoute les connexions entrantes."""
        serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serveur.bind((self.__ip_master, self.__port_master))
        serveur.listen()

        print(f"Master en écoute sur {self.__ip_master}:{self.__port_master}")

        while True:
            connexion, adresse = serveur.accept()
            donnees = connexion.recv(1024).decode().strip()

            if not donnees:
                connexion.close()
                continue

            premier_mot = donnees.split()[0]

            if premier_mot == "ROUTER":
                threading.Thread(target=self.traiter_message_routeur, args=(donnees,)).start()

            connexion.close()


if __name__ == "__main__":
    master = Master()
    master.demarrer()
