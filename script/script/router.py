import sys
import socket
import threading
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QGroupBox, QTextEdit, QMessageBox
)
from PyQt5.QtCore import pyqtSignal


class RouterGUI(QWidget):

    log_signal = pyqtSignal(str)   # \uD83D\uDD25 SIGNAL THREAD-SAFE

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Routeur SAE302")
        self.setMinimumWidth(700)

        self.router_id = None
        self.router_ip = None
        self.router_port = None
        self.master_ip = None
        self.master_port = None

        self.init_ui()
        self.apply_style()

        # Connexion signal â†’ slot GUI
        self.log_signal.connect(self.append_log)

    # ================= UI =================

    def init_ui(self):
        layout = QVBoxLayout()
        layout.addWidget(self.config_box())
        layout.addWidget(self.log_box())
        self.setLayout(layout)

    def apply_style(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e2e;
                color: #e0e0e0;
                font-size: 12px;
            }
            QLineEdit {
                background-color: #2b2b3c;
                border: 1px solid #444;
                padding: 4px;
            }
            QPushButton {
                background-color: #3b5bdb;
                border: none;
                padding: 6px;
            }
            QPushButton:hover {
                background-color: #5c7cfa;
            }
            QTextEdit {
                background-color: #111;
                border: 1px solid #333;
            }
            QGroupBox {
                border: 1px solid #444;
                margin-top: 10px;
            }
        """)

    # ================= CONFIG =================

    def config_box(self):
        box = QGroupBox("Configuration routeur")
        layout = QHBoxLayout()

        self.id_input = QLineEdit()
        self.ip_input = QLineEdit()
        self.port_input = QLineEdit()
        self.master_ip_input = QLineEdit()
        self.master_port_input = QLineEdit()

        btn = QPushButton("DÃ©marrer routeur")
        btn.clicked.connect(self.demarrer_routeur)

        layout.addWidget(QLabel("ID"))
        layout.addWidget(self.id_input)
        layout.addWidget(QLabel("IP routeur"))
        layout.addWidget(self.ip_input)
        layout.addWidget(QLabel("Port"))
        layout.addWidget(self.port_input)
        layout.addWidget(QLabel("Master IP"))
        layout.addWidget(self.master_ip_input)
        layout.addWidget(QLabel("Master Port"))
        layout.addWidget(self.master_port_input)
        layout.addWidget(btn)

        box.setLayout(layout)
        return box

    # ================= LOG =================

    def log_box(self):
        box = QGroupBox("Logs")
        layout = QVBoxLayout()

        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)

        layout.addWidget(self.log_area)
        box.setLayout(layout)
        return box

    def append_log(self, text):
        self.log_area.append(text)

    def log(self, text):
        print(text)
        self.log_signal.emit(text)

    # ================= ROUTEUR =================

    def demarrer_routeur(self):
        try:
            self.router_id = self.id_input.text()
            self.router_ip = self.ip_input.text()
            self.router_port = int(self.port_input.text())
            self.master_ip = self.master_ip_input.text()
            self.master_port = int(self.master_port_input.text())

            threading.Thread(target=self.declarer_master, daemon=True).start()
            threading.Thread(target=self.ecouter, daemon=True).start()

            QMessageBox.information(self, "Routeur", "Routeur dÃ©marrÃ©")

        except Exception as e:
            QMessageBox.critical(self, "Erreur", str(e))

    def declarer_master(self):
        try:
            msg = f"ROUTER {self.router_id} {self.router_ip} {self.router_port} 0 0"
            s = socket.socket()
            s.connect((self.master_ip, self.master_port))
            s.sendall(msg.encode())
            s.close()

            self.log(f"[MASTER] DÃ©claration envoyÃ©e : {msg}")

        except Exception as e:
            self.log(f"[ERREUR MASTER] {e}")

    def ecouter(self):
        s = socket.socket()
        s.bind(("0.0.0.0", self.router_port))
        s.listen()

        self.log(f"[ECOUTE] En Ã©coute sur {self.router_ip}:{self.router_port}")

        while True:
            conn, addr = s.accept()
            data = conn.recv(8192)
            conn.close()

            if not data:
                continue

            raw = data.decode(errors="ignore")

            self.log("----- PAQUET REÃ‡U -----")
            self.log(f"[BRUT] {raw}")

            if not raw.startswith("ROUTE|"):
                self.log("[IGNORÃ‰] Format invalide")
                continue

            try:
                _, ip, port, payload = raw.split("|", 3)

                self.log(f"[ROUTAGE] Prochain saut -> {ip}:{port}")
                self.log(f"[PAYLOAD] {payload}")

                s2 = socket.socket()
                s2.connect((ip, int(port)))
                s2.sendall(payload.encode())
                s2.close()

                self.log("[OK] Paquet transmis")

            except Exception as e:
                self.log(f"[ERREUR ROUTAGE] {e}")


# ================= MAIN =================

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RouterGUI()
    window.show()
    sys.exit(app.exec_())
