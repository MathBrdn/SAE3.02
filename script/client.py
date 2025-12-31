import sys
import socket
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QListWidget, QVBoxLayout, QHBoxLayout,
    QMessageBox, QGroupBox, QTextEdit
)
from PyQt5.QtCore import Qt
import threading


class ClientGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Client SAE302")
        self.setMinimumWidth(500)

        self.client_ip = None
        self.client_port = None
        self.master_ip = None
        self.master_port = None

        # chaque routeur = dict {id, ip, port, e, n}
        self.routeurs = []

        self.init_ui()
        self.apply_style()

    # ================= UI =================

    def init_ui(self):
        layout = QVBoxLayout()

        layout.addWidget(self.client_box())
        layout.addWidget(self.master_box())
        layout.addWidget(self.routeur_box())
        layout.addWidget(self.send_box())

        self.setLayout(layout)

    def apply_style(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                color: #dcdcdc;
                font-size: 12px;
            }
            QLineEdit, QTextEdit {
                background-color: #2b2b2b;
                border: 1px solid #3c3c3c;
                padding: 4px;
            }
            QPushButton {
                background-color: #2d6a4f;
                border: none;
                padding: 6px;
            }
            QPushButton:hover {
                background-color: #40916c;
            }
            QGroupBox {
                border: 1px solid #3c3c3c;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 4px 0 4px;
            }
        """)

    # ================= CLIENT =================

    def client_box(self):
        box = QGroupBox("Client")
        layout = QHBoxLayout()

        self.client_ip_input = QLineEdit()
        self.client_port_input = QLineEdit()

        btn = QPushButton("CrÃ©er client")
        btn.clicked.connect(self.creer_client)

        layout.addWidget(QLabel("IP"))
        layout.addWidget(self.client_ip_input)
        layout.addWidget(QLabel("Port"))
        layout.addWidget(self.client_port_input)
        layout.addWidget(btn)

        box.setLayout(layout)
        return box

    def creer_client(self):
        try:
            self.client_ip = self.client_ip_input.text()
            self.client_port = int(self.client_port_input.text())

            threading.Thread(target=self.ecouter, daemon=True).start()

            QMessageBox.information(self, "Client", "Client crÃ©Ã© et en Ã©coute")

        except Exception as e:
            QMessageBox.critical(self, "Erreur", str(e))

    def ecouter(self):
        s = socket.socket()
        s.bind((self.client_ip, self.client_port))
        s.listen()

        while True:
            c, _ = s.accept()
            data = c.recv(8192)
            c.close()
            QMessageBox.information(self, "Message reÃ§u", data.decode(errors="ignore"))

    # ================= MASTER =================

    def master_box(self):
        box = QGroupBox("Master")
        layout = QHBoxLayout()

        self.master_ip_input = QLineEdit()
        self.master_port_input = QLineEdit()

        btn = QPushButton("Connexion master")
        btn.clicked.connect(self.connecter_master)

        layout.addWidget(QLabel("IP"))
        layout.addWidget(self.master_ip_input)
        layout.addWidget(QLabel("Port"))
        layout.addWidget(self.master_port_input)
        layout.addWidget(btn)

        box.setLayout(layout)
        return box

    def connecter_master(self):
        try:
            self.master_ip = self.master_ip_input.text()
            self.master_port = int(self.master_port_input.text())

            self.recuperer_routeurs()
            QMessageBox.information(self, "Master", "ConnectÃ© au master")

        except Exception as e:
            QMessageBox.critical(self, "Erreur", str(e))

    # ================= ROUTEURS =================

    def routeur_box(self):
        box = QGroupBox("Routeurs disponibles")
        layout = QVBoxLayout()

        self.routeur_list = QListWidget()
        self.routeur_list.setSelectionMode(QListWidget.MultiSelection)

        layout.addWidget(self.routeur_list)
        box.setLayout(layout)
        return box

    def recuperer_routeurs(self):
        self.routeur_list.clear()
        self.routeurs.clear()

        s = socket.socket()
        s.connect((self.master_ip, self.master_port))
        s.sendall(b"CLIENT")

        buffer = ""
        while "END\n" not in buffer:
            buffer += s.recv(1024).decode()

        s.close()

        for line in buffer.splitlines():
            if line == "END":
                break

            # FORMAT ATTENDU : ID IP PORT E N
            rid, ip, port, e, n = line.split()

            self.routeurs.append({
                "id": rid,
                "ip": ip,
                "port": int(port),
                "e": int(e),
                "n": int(n)
            })

            self.routeur_list.addItem(f"{rid} ({ip}:{port})")

    # ================= ENVOI =================

    def send_box(self):
        box = QGroupBox("Envoi message")
        layout = QVBoxLayout()

        dest_layout = QHBoxLayout()
        self.dest_ip_input = QLineEdit()
        self.dest_port_input = QLineEdit()

        dest_layout.addWidget(QLabel("Dest IP"))
        dest_layout.addWidget(self.dest_ip_input)
        dest_layout.addWidget(QLabel("Dest Port"))
        dest_layout.addWidget(self.dest_port_input)

        self.message_input = QTextEdit()
        btn = QPushButton("Envoyer")
        btn.clicked.connect(self.envoyer_message)

        layout.addLayout(dest_layout)
        layout.addWidget(QLabel("Message"))
        layout.addWidget(self.message_input)
        layout.addWidget(btn)

        box.setLayout(layout)
        return box

    def envoyer_message(self):
        selection = self.routeur_list.selectedItems()
        if len(selection) < 3:
            QMessageBox.warning(self, "Erreur", "SÃ©lectionnez au moins 3 routeurs")
            return

        dest_ip = self.dest_ip_input.text()
        dest_port = int(self.dest_port_input.text())
        message = self.message_input.toPlainText()

        indices = [self.routeur_list.row(item) for item in selection]
        chemin = [self.routeurs[i] for i in indices]

        payload = f"ROUTE|{dest_ip}|{dest_port}|{message}"

        for r in reversed(chemin[1:]):
            payload = f"ROUTE|{r['ip']}|{r['port']}|{payload}"

        first = chemin[0]
        s = socket.socket()
        s.connect((first["ip"], first["port"]))
        s.sendall(payload.encode())
        s.close()

        QMessageBox.information(self, "Envoi", "Message envoyÃ©")


# ================= MAIN =================

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ClientGUI()
    window.show()
    sys.exit(app.exec_())