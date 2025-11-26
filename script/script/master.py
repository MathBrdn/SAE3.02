"""
Code du master, responsable de :
- gérer les connexions vers les routeurs,
- envoyer des messages,
- orchestrer le routage anonyme (plus tard),
- servir de point d’entrée pour les clients.
"""

import socket
import threading
from router import Router

class Master:
    """
    Classe Master, gère la communication entre les clients et les routeurs.
    """

    def __init__(self, ip, port):
        """
        Initialise un Master.
        Paramètres :
        ip: int -> adresse ip du master
        port: int -> port d'écoute du master
        """
        
        self.__ip = ip
        self.__port = port
        self.__server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #crée la socket server qui va permette d'écouter les connexions errantes
        self.__server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #autorise la réutilisation de la socket.
        self.__running = False
        self.__routers = []

    def __str__(self):
        """Affichage"""
        
        return f"master écoutant sur {self.__ip}:{self.__port}"

    def add_router(self, ip, port):
        """Ajoute un routeur dans la liste."""
        
        self.__routers.append((ip, port))
        print(f"master: Routeur ajouté : {ip}:{port}")

    def create_router(self, ip, port):
        """
        Exemple de la solution 2 :
        Crée un routeur via import DYNAMIQUE.
        """
         
        return Router(ip, port)

    def start_listen(self):
        """Démarre l'écoute du master."""

        self.__server_socket.bind((self.__ip, self.__port))
        self.__server_socket.listen(20) #écoute jusqu'à 20 connexions
        print(f"master: Ecoute sur {self.__ip}:{self.__port}")
        self.__running = True

        while self.__running:
            client_socket, addr = self.__server_socket.accept()
            print(f"master: Client connecté : {addr}")

            thread = threading.Thread(
                target=self.gestion_client,
                args=(client_socket, addr),
                daemon=True
            )
            thread.start()
    
    #inutile pour l'instant car le script client n'est pas finit!
    #def gestion_client(self, client_socket, source):
        #"""Gère un client dans un thread séparé."""
        #print(f"Master: Nouveau client géré : {source}")
        #client_socket.close()

    def send_router(self, routeur_ip, routeur_port, message):
        """Envoie un message à un routeur."""

        print(f"master: Envoi d'un message au routeur {routeur_ip}:{routeur_port}")

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((routeur_ip, routeur_port))
        sock.sendall(message.encode())
        sock.close()


if __name__ == "__main__":
    print("Démarrage du Master")
    master = Master("127.0.0.1", 4000)
    master.add_router("127.0.0.1", 5000)
    master.start_listen()
