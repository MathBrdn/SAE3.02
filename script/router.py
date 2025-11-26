"""
Code du routeur, contient la classe Router.
Ce module définit un routeur virtuel capable :
- d’écouter sur une adresse IP et un port,
- de recevoir des messages,
- de traiter chaque connexion dans un thread séparé,
- et de transmettre un message à un autre routeur (fonction prête mais simplifiée).

"""

import socket
import threading

class Router:
    """
        Classe Router, permet de créer l'objet Router qui fait office de routeur virtuel.
    """
    
    def __init__(self, ip, port):
        """
            Initialise un routeur avec une IP et un port.
            Parameters
            ----------
            ip : str
                Adresse IP locale du routeur.
            port : int
                Port d’écoute du routeur.
        """
        
        self.__ip = ip 
        self.__port = port
        self.__server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.__running = False
    
    def __str__(self):
        """
        """
        
        return f"message"
    
    def connection(self, conn_socket, source):
        """
        Méthode exécutée dans un thread.
        Elle établit une connexion TCP entre le routeur et un client/master.

        Ici, aucune lecture de message :
        on se contente de reconnaître qu'une connexion a été établie.

        Parameters
        ----------
        conn_socket : socket.socket
            La socket dédiée à la connexion TCP établie.
        source : tuple
            Adresse (IP, port) du client/master.
        """

        print(f"[ROUTEUR {self.__port}] Connexion établie avec {source}")

        # Ici, on ne lit pas les données (pas de recv)
        # On pourrait ajouter la logique de traitement plus tard.

        # Fermeture de la connexion TCP
        conn_socket.close()
        
        #try:
            #conn_socket, source = self.__server_socket.accept()
        #except Exception as e:
            #print(f"[ERREUR ROUTEUR] Erreur lors de accept() : {e}")
            #continue
        
    def start_listen(self):
        """
        Démarre l'écoute du routeur sur l'adresse IP et le port configurés.

        Cette méthode :
        - attache la socket à (IP, port) via bind()
        - passe la socket en mode écoute via listen()
        - accepte les connexions entrantes avec accept()
        - crée un thread pour gérer chaque connexion
        """

        # Attache la socket à l'IP et au port du routeur
        self.__server_socket.bind((self.__ip, self.__port))

        # Active l'écoute. Le routeur peut gérer jusqu'à 5 connexions en file d'attente
        self.__server_socket.listen(5)

        print(f"[ROUTEUR {self.__port}] En écoute sur {self.__ip}:{self.__port}")

        self.__running = True

        # Boucle d'écoute continue
        while self.__running:
            # Acceptation d'une connexion entrante
            conn_socket, source = self.__server_socket.accept()

            # Création d'un thread pour gérer cette connexion
            thread = threading.Thread(
                target=self.connection,
                args=(conn_socket, source),
                daemon=True
            )
            thread.start()
        try:
            self.__server_socket.bind((self.__ip, self.__port))
            self.__server_socket.listen(5)
            print(f"[ROUTEUR {self.__port}] En écoute sur {self.__ip}:{self.__port}")
        except Exception as e:
            print(f"[ERREUR ROUTEUR] Impossible de démarrer l'écoute : {e}")
            return

    if __name__ == '__main__':
                
        
        
        
        