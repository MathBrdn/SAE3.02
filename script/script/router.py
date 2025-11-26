"""
Code du routeur, contient la classe Router.
"""

import socket
import threading


class Router:
    """
    Classe Router, permet de créer un routeur virtuel simple.
    """

    def __init__(self, ip, port):
        """Initialise un routeur avec une IP et un port."""
        self.__ip = ip
        self.__port = port
        self.__server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #crée la socket server qui va permette d'écouter les connexions errantes.
        self.__server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #autorise la réutilisation de la socket.
        self.__running = False

    def __str__(self):
        return f"Routeur écoutant sur {self.__ip}:{self.__port}"

    def connection(self, conn_socket, source):
        """
        Méthode exécutée dans un thread.
        Gère une connexion TCP entrante.
        """

        print(f"ROUTEUR {self.__port}: Connexion établie avec {source}")

        try:
            conn_socket.close() # Fermeture propre de la socket.
        except Exception as e:
            print(f"ERREUR ROUTEUR: Impossible de fermer la connexion : {e}")

    def start_listen(self):
        """Démarre l'écoute du routeur (bind + listen + accept en boucle)."""

        try:
            self.__server_socket.bind((self.__ip, self.__port))
            self.__server_socket.listen(20)
            print(f"router {self.__port}: Ecoute sur {self.__ip}:{self.__port}")
        except Exception as e:
            print(f"ERREUR ROUTEUR: Impossible de démarrer l'écoute : {e}")
            return

        self.__running = True

        # Acceptation de connexions en boucle
        while self.__running:
            try:
                conn_socket, source = self.__server_socket.accept()
            except Exception as e:
                print(f"ERREUR ROUTEUR: Erreur lors de accept() : {e}")
                continue

            # Thread de gestion de connexion
            try:
                thread = threading.Thread(
                    target=self.connection,
                    args=(conn_socket, source),
                    daemon=True
                )
                thread.start()
            except Exception as e:
                print(f"ERREUR ROUTEUR: Impossible de lancer un thread : {e}")


if __name__ == "__main__":
    print("Démarrage du routeur...")
    routeur = Router("127.0.0.1", 5000)
    routeur.start_listen()
