import sys
import socket
import threading
import random
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit,
    QPushButton, QListWidget, QVBoxLayout
)
from PyQt5.QtCore import Qt


# ================= RSA PÃ‰DAGOGIQUE =================

def pgcd(a, b):
    while b:
        a, b = b, a % b
    return a

def inverse_modulaire(e, phi):
    for d in range(3, phi):
        if (d * e) % phi == 1:
            return d
    raise Exception("Inverse modulaire introuvable")

def nombre_premier():
    while True:
        n = random.randrange(1000, 5000)
        for i in range(2, int(n ** 0.5) + 1):
            if n % i == 0:
                break
        else:
            return n

def generer_cle_rsa():
    p = nombre_premier()
    q = nombre_premier()
    n = p * q
    phi = (p - 1) * (q - 1)
    e = 65537
    d = inverse_modulaire(e, phi)
    return e, d, n


# ================= ROUTEUR =================

class Routeur:
    def __init__(self, rid, ip_vm, port, master_ip, master_port):
        self.rid = rid
        self.ip_vm = ip_vm
        self.port = port
        self.master_ip = master_ip
        self.master_port = master_port

        # \uD83D\uDD10 GÃ©nÃ©ration des clÃ©s RSA
        self.e, self.d, self.n = generer_cle_rsa()

    def envoyer_master(self):
        msg = f"ROUTER {self.rid} {self.ip_vm} {self.port} {self.e} {self.n}"
        s = socket.socket()
        s.connect((self.master_ip, self.master_port))
        s.sendall(msg.encode())
        s.close()

        print(f"[{self.rid}] clÃ© publique envoyÃ©e au master")

    def envoyer(self, ip, port, data):
        s = socket.socket()
        s.connect((ip, port))
        s.sendall(data)
        s.close()

    def ecouter(self):
        s = socket.socket()
        s.bind(("0.0.0.0", self.port))
        s.listen()

        print(f"[{self.rid}] Ã©coute sur {self.ip_vm}:{self.port}")

        while True:
            c, _ = s.accept()
            data = c.recv(8192)
            c.close()

            if not data:
                continue

            try:
                text = data.decode()
                if text.startswith("ROUTE|"):
                    _, ip, port, reste = text.split("|", 3)
                    self.envoyer(ip, int(port), reste.encode())
            except Exception:
                print(f"[{self.rid}] paquet invalide")

    def demarrer(self):
        self.envoyer_master()
        self.ecouter()


# ================= GUI =================

class RouteurGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Routeur SAE302")
        self.setFixedSize(420, 480)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        title = QLabel("CrÃ©ation de routeur")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size:18px; color:#4da6ff;")
        layout.addWidget(title)

        self.rid_input = self.input("ID du routeur")
        self.port_input = self.input("Port du routeur")
        self.ip_vm_input = self.input("IP VM routeurs")
        self.master_ip_input = self.input("IP du master")
        self.master_port_input = self.input("Port du master")

        for w in [
            self.rid_input, self.port_input,
            self.ip_vm_input, self.master_ip_input,
            self.master_port_input
        ]:
            layout.addWidget(w)

        btn = QPushButton("CrÃ©er et dÃ©marrer")
        btn.clicked.connect(self.lancer_routeur)
        btn.setStyleSheet("background-color:#4da6ff; padding:8px;")
        layout.addWidget(btn)

        self.liste = QListWidget()
        layout.addWidget(self.liste)

        self.setLayout(layout)
        self.setStyleSheet("""
            QWidget { background-color:#1e1e1e; color:white; }
            QLineEdit { background:#2a2a2a; color:white; padding:5px; }
        """)

    def input(self, text):
        f = QLineEdit()
        f.setPlaceholderText(text)
        return f

    def lancer_routeur(self):
        try:
            routeur = Routeur(
                self.rid_input.text(),
                self.ip_vm_input.text(),
                int(self.port_input.text()),
                self.master_ip_input.text(),
                int(self.master_port_input.text())
            )

            threading.Thread(
                target=routeur.demarrer,
                daemon=True
            ).start()

            self.liste.addItem(
                f"{routeur.rid} | {routeur.ip_vm}:{routeur.port}"
            )

        except Exception as e:
            self.liste.addItem(f"Erreur : {e}")


# ================= MAIN =================

if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = RouteurGUI()
    gui.show()
    sys.exit(app.exec_())