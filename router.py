"""Code du routeur, contient la classe Router.
    Ce module définit un routeur virtuel capable :
    - d’écouter sur une adresse IP et un port,
    - de recevoir des messages,
    - de traiter chaque connexion dans un thread séparé,
    - et de transmettre un message à un autre routeur (fonction prête mais simplifiée).

"""

import socket
import threading

class Router:
    """Classe Router, permet de créer l'objet Router qui fait office de routeur virtuel.
    """
    
    def __init__(self, ip, port):
        """Initialise un routeur avec une IP et un port.
            Parameters
            ----------
            ip : str
                Adresse IP locale du routeur (ex : '127.0.0.1').
            port : int
                Port d’écoute du routeur (ex : 6001).
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
    
    
        
        
        
        