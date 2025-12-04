import socket
import threading
import random
import sys
from master import Master


class Routeur:
    """
    Représente un routeur du réseau : il se déclare au Master et relaye les messages.
    """

    def __init__(self, id_routeur, port_ecoute, master: Master):
        self.__id_routeur = id_routeur
        self.__port_ecoute = port_ecoute
        self.__master = master
        self.__cle_publique = self.generer_cle_publique()

    # --- Accesseurs ---
    def get_id(self):
        return self.__id_routeur

    def get_cle_publique(self):
        return self.__cle_publique

    def get_port_ecoute(self):
        return self.__port_ecoute

    # --- Génération de clé ---
    def generer_cle_publique(self, longueur=20):
        """Génère une clé publique binaire aléatoire."""
        return ''.join(str(random.randint(0, 1)) for _ in range(longueur))

    # --- Déchiffrement simple ---
    def dechiffrer_couche(self, texte):
        """Déchiffrement XOR très simple."""
        return ''.join(chr(ord(c) ^ 1) for c in texte)

    # --- Déclaration au Master ---
    def envoyer_infos_master(self):
        """Envoie ID, clé publique et port d'écoute au Master."""
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.__master.get_ip_master(), self.__master.get_port_master()))

        message = f"ROUTER {self.__id_routeur} {self.__cle_publique} {self.__port_ecoute}"
        s.send(message.encode())
        s.close()

        print(f"{self.__id_routeur} → Déclaré au Master")

    # --- Boucle d'écoute ---
    def ecouter(self):
        """Attend les messages entrants et les relaie au prochain routeur."""
        serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serveur.bind(("0.0.0.0", self.__port_ecoute))
        serveur.listen()

        print(f"{self.__id_routeur} écoute sur le port {self.__port_ecoute}")

        while True:
            connexion, adresse = serveur.accept()
            donnees = connexion.recv(4096).decode().strip()
            connexion.close()

            if not donnees:
                print(f"{self.__id_routeur} ⚠ Message vide reçu (ignoré)")
                continue

            print(f"{self.__id_routeur} ← Message reçu : {repr(donnees)}")

            # Vérification du format (doit être : <IP> <PORT> <MESSAGE>)
            parties = donnees.split(" ", 2)
            if len(parties) < 3:
                print(f"{self.__id_routeur} ⚠ Format invalide (ignoré) :", parties)
                continue

            ip_suivante, port_suivant, contenu = parties
            contenu_dechiffre = self.dechiffrer_couche(contenu)

            sortie = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sortie.connect((ip_suivante, int(port_suivant)))
            sortie.send(contenu_dechiffre.encode())
            sortie.close()

            print(f"{self.__id_routeur} → Transmis vers {ip_suivante}:{port_suivant}")

    # --- Lancement du routeur ---
    def demarrer(self):
        """Déclare le routeur au Master puis lance la boucle d'écoute."""
        self.envoyer_infos_master()
        self.ecouter()


# =====================================================================
#     EXÉCUTION DIRECTE (en dehors de la classe ! important !)
# =====================================================================
if __name__ == "__main__":
    master = Master()

    PORTS = {"R1": 6001, "R2": 6002, "R3": 6003}

    # Exemple : python router.py R2
    if len(sys.argv) == 2:
        id_routeur = sys.argv[1]

        if id_routeur not in PORTS:
            print("Routeurs valides : R1, R2, R3")
            exit(1)

        Routeur(id_routeur, PORTS[id_routeur], master).demarrer()

    # Démarrage groupé des trois routeurs
    elif len(sys.argv) == 1:
        print("Démarrage des trois routeurs…")

        for id_routeur, port in PORTS.items():
            threading.Thread(
                target=Routeur(id_routeur, port, master).demarrer
            ).start()

    else:
        print("Usage :")
        print("  python router.py R3")
        print("  python router.py")
