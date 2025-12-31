import sys
import socket
import threading
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit,
    QPushButton, QListWidget, QVBoxLayout,
    QHBoxLayout, QMessageBox
)
from PyQt5.QtCore import Qt


MASTER_IP = "192.168.178.3"   # à adapter si besoin
MASTER_PORT = 5000


# ================= ROUTEUR LOGIQUE =================

class Routeur:
    def __init__(self, rid, port):
        self.rid = rid
        self.port = port

    def envoyer_master(self):
        try:
            s = socket.socket()
            s.connect((MASTER_IP, MASTER_PORT))
            s.sendall(f"ROUTER {self.rid} {self.port}".encode())
            s.close()
        except Exception as e:
            print(f"[{self.rid}] Erreur connexion master : {e}")

    def ecouter(self):
        s = socket.socket()
        s.bind(("0.0.0.0", self.port))
        s.listen()
        print(f"[{self.rid}] Routeur actif sur port {self.port}")

        while True:
            c, _ = s.accept()
            data = c.recv(8192)
            c.close()

            if not data:
                continue

            text = data.decode(errors="ignore")

            if text.startswith("ROUTE|"):
                try:
                    _, ip, port, reste = text.split("|", 3)
                    print(f"[{self.rid}] Relais vers {ip}:{port}")
                    self.envoyer(ip, int(port), reste)
                except Exception:
                    print(f"[{self.rid}] Paquet invalide")

    def envoyer(self, ip, port, payload):
        try:
            s = socket.socket()
            s.connect((ip, port))
            s.sendall(payload.encode())
            s.close()
        except Exception as e:
            print(f"[{self.rid}] Erreur envoi : {e}")

    def demarrer(self):
        self.envoyer_master()
        self.ecouter()


# ================= THREAD ROUTEUR =================

def lancer_routeur(rid, port):
    r = Routeur(rid, port)
    r.demarrer()


# ================= INTERFACE GRAPHIQUE =================

class RouterGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestionnaire de routeurs")
        self.setFixedSize(420, 400)

        self.init_ui()

    def init_ui(self):
        # Styles
        self.setStyleSheet("""
            QWidget {
                background-color: #f4f7fb;
                font-size: 14px;
            }
            QLabel {
                color: #1f3c88;
                font-weight: bold;
            }
            QPushButton {
                background-color: #1f6feb;
                color: white;
                padding: 8px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #1558c0;
            }
            QListWidget {
                background-color: white;
                border-radius: 6px;
            }
        """)

        # Widgets
        title = QLabel("Création de routeur")
        title.setAlignment(Qt.AlignCenter)

        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText("ID du routeur (ex: R1)")

        self.port_input = QLineEdit()
        self.port_input.setPlaceholderText("Port d'écoute (ex: 6001)")

        btn = QPushButton("Créer le routeur")
        btn.clicked.connect(self.creer_routeur)

        self.liste = QListWidget()

        # Layouts
        layout = QVBoxLayout()
        layout.addWidget(title)
        layout.addSpacing(10)
        layout.addWidget(self.id_input)
        layout.addWidget(self.port_input)
        layout.addWidget(btn)
        layout.addSpacing(15)
        layout.addWidget(QLabel("Routeurs actifs :"))
        layout.addWidget(self.liste)

        self.setLayout(layout)

    def creer_routeur(self):
        rid = self.id_input.text().strip()
        port_text = self.port_input.text().strip()

        if not rid or not port_text:
            QMessageBox.warning(self, "Erreur", "ID et port sont obligatoires")
            return

        try:
            port = int(port_text)
        except ValueError:
            QMessageBox.warning(self, "Erreur", "Port invalide")
            return

        # Lancer le routeur dans un thread
        t = threading.Thread(
            target=lancer_routeur,
            args=(rid, port),
            daemon=True
        )
        t.start()

        self.liste.addItem(f"{rid} - port {port}")
        self.id_input.clear()
        self.port_input.clear()


# ================= MAIN =================

if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = RouterGUI()
    gui.show()
    sys.exit(app.exec_())
