import sys
import socket
import threading
import mysql.connector
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QListWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QMessageBox
)
from PyQt5.QtCore import Qt


class MasterGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Master SAE302")
        self.setMinimumWidth(500)

        self.server_socket = None
        self.running = False

        self.init_ui()
        self.apply_style()

    # ================= UI =================

    def init_ui(self):
        layout = QVBoxLayout()

        layout.addWidget(self.master_box())
        layout.addWidget(self.routeur_box())

        self.setLayout(layout)

    def apply_style(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #1b1b1b;
                color: #e0e0e0;
                font-size: 12px;
            }
            QLineEdit {
                background-color: #2a2a2a;
                border: 1px solid #4a4a4a;
                padding: 4px;
            }
            QPushButton {
                background-color: #7a1f1f;
                border: none;
                padding: 6px;
            }
            QPushButton:hover {
                background-color: #a83232;
            }
            QGroupBox {
                border: 1px solid #4a4a4a;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 4px 0 4px;
            }
        """)

    # ================= MASTER =================

    def master_box(self):
        box = QGroupBox("Configuration Master")
        layout = QHBoxLayout()

        self.ip_input = QLineEdit()
        self.port_input = QLineEdit()

        self.start_btn = QPushButton("DÃ©marrer")
        self.start_btn.clicked.connect(self.demarrer_master)

        layout.addWidget(QLabel("IP"))
        layout.addWidget(self.ip_input)
        layout.addWidget(QLabel("Port"))
        layout.addWidget(self.port_input)
        layout.addWidget(self.start_btn)

        box.setLayout(layout)
        return box

    def demarrer_master(self):
        try:
            ip = self.ip_input.text()
            port = int(self.port_input.text())

            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.bind(("0.0.0.0", port))
            self.server_socket.listen()

            self.public_ip = ip
            self.port = port
            self.running = True

            threading.Thread(target=self.ecouter, daemon=True).start()

            QMessageBox.information(self, "Master", "Master dÃ©marrÃ©")

        except Exception as e:
            QMessageBox.critical(self, "Erreur", str(e))

    # ================= ROUTEURS =================

    def routeur_box(self):
        box = QGroupBox("Routeurs dÃ©clarÃ©s")
        layout = QVBoxLayout()

        self.routeur_list = QListWidget()
        layout.addWidget(self.routeur_list)

        box.setLayout(layout)
        return box

    def ajouter_routeur(self, rid, ip, port):
        self.routeur_list.addItem(f"{rid} - {ip}:{port}")

    # ================= SOCKET =================

    def ecouter(self):
        try:
            db = mysql.connector.connect(
                host="localhost",
                user="toto",
                password="toto",
                database="SAE302"
            )
            cursor = db.cursor()

        except mysql.connector.Error as e:
            QMessageBox.critical(self, "DB", str(e))
            return

        while self.running:
            conn, addr = self.server_socket.accept()
            try:
                msg = conn.recv(4096).decode().strip()

                if msg.startswith("ROUTER"):
                    # ROUTER ID IP PORT E N
                    parts = msg.split()
                    if len(parts) != 6:
                        conn.close()
                        continue

                    _, rid, ip_r, port, e, n = parts

                    cursor.execute(
                        """
                        INSERT INTO routeurs (id_routeur, ip_routeur, port, cle_publique)
                        VALUES (%s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE
                        ip_routeur=%s, port=%s, cle_publique=%s
                        """,
                        (rid, ip_r, int(port), f"{e}:{n}",
                         ip_r, int(port), f"{e}:{n}")
                    )
                    db.commit()

                    self.ajouter_routeur(rid, ip_r, port)

                elif msg == "CLIENT":
                    cursor.execute("SELECT id_routeur, ip_routeur, port, cle_publique FROM routeurs")
                    for rid, ip_r, port, cle in cursor.fetchall():
                        e, n = cle.split(":")
                        conn.sendall(f"{rid} {ip_r} {port} {e} {n}\n".encode())
                    conn.sendall(b"END\n")

            except Exception:
                pass

            conn.close()


# ================= MAIN =================

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MasterGUI()
    window.show()
    sys.exit(app.exec_())
