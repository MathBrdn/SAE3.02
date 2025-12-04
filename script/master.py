import socket
import threading

class Master:
    """
    Serveur central recevant les déclarations des routeurs et
    fournissant la liste des routeurs aux clients.
    """

    liste_routeurs = {}

    def __init__(self, ip_master="127.0.0.1", port_master=5000):
        self.__ip_master = ip_master
        self.__port_master = port_master

    def get_ip_master(self):
        return self.__ip_master

    def get_port_master(self):
        return self.__port_master

    # --- Ajout d’un routeur ---
    def ajouter_routeur(self, id_routeur, port, cle_publique):
        Master.liste_routeurs[id_routeur] = (port, cle_publique)
        print(f"→ Routeur enregistré : {id_routeur} (port {port})")

    # --- Message ROUTER ---
    def traiter_message_routeur(self, message):
        """
        Format : ROUTER <ID> <CLE> <PORT>
        """
        elements = message.split()
        if len(elements) != 4:
            print("⚠ Message routeur invalide :", elements)
            return

        _, rid, cle, port = elements
        self.ajouter_routeur(rid, int(port), cle)

    # --- Message CLIENT ---
    def traiter_message_client(self, connexion):
        for rid, (port, cle) in Master.liste_routeurs.items():
            ligne = f"{rid} {port} {cle}\n"
            print("MASTER ENVOIE :", repr(ligne))   # debug optionnel
            connexion.sendall(ligne.encode())
        connexion.sendall(b"END\n")



    # --- Boucle serveur ---
    def demarrer(self):
        serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serveur.bind((self.__ip_master, self.__port_master))
        serveur.listen()

        print(f"Master en écoute sur {self.__ip_master}:{self.__port_master}")

        while True:
            connexion, adresse = serveur.accept()
            message = connexion.recv(1024).decode().strip()

            if not message:
                connexion.close()
                continue

            type_message = message.split()[0]

            if type_message == "ROUTER":
                threading.Thread(target=self.traiter_message_routeur, args=(message,)).start()

            elif type_message == "CLIENT":
                self.traiter_message_client(connexion)
                connexion.close()
                continue


            connexion.close()


if __name__ == "__main__":
    Master().demarrer()
