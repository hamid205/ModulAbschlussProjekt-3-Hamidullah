# Importiere eigene Module und Bibliotheken
from editaduser_TN import EditADUserWindow  # Fenster zum Bearbeiten eines AD-Users
from database import DatabaseHandler        # Klasse für Datenbankverbindung
from login import LoginDialog               # Fenster für Login-Dialog
import sys
import os
import csv
import shutil
from datetime import datetime

# Importiere PyQt6 Klassen für GUI
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QDockWidget, QToolBar,
    QTableWidget, QTableWidgetItem, QTextEdit, QVBoxLayout, QWidget,
    QMessageBox, QAbstractItemView, QFileDialog
)

# Hauptfenster der Anwendung
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Menüstruktur definieren
        self.mainmenue = {1: "&Datei", 2: "&Active Directory", 4: "&Hilfe"}
        self.menueoptions = {
            11: "Import von CSV", 12: "Transfer nach AD", 13: "Einloggen", 14: "Ausloggen",
            0: "separator", 19: "&Beenden", 21: "Benutzer bearbeiten", 22: "Lösche AD-User",
            23: "Inaktiv AD-User", 41: "&Über", 42: "&Hilfe"
        }
        # Toolbar Buttons definieren
        self.toolbarbuttons = {
            13: "Einloggen", 11: "Import von CSV", 12: "Transfer nach AD",
            0: "separator", 21: "Benutzer bearbeiten", 22: "Lösche AD-User", 23: "Inaktiv AD-User",
            0: "separator", 42: "&Hilfe"
        }
        self.initUI()

    def initUI(self):
        # Fenster-Titel und Icon setzen
        self.setWindowTitle("myAdmin Center")
        self.setWindowIcon(QIcon(".\\images\\logo-zm.png"))

        # Menüleiste aufbauen
        menubar = self.menuBar()
        for menu_id, menu_title in self.mainmenue.items():
            menu = menubar.addMenu(menu_title)
            for action_id, action_title in self.menueoptions.items():
                if action_id == 0:
                    menu.addSeparator()
                elif action_id // 10 == menu_id:
                    action = QAction(action_title, self)
                    action.setProperty("command", (action_id, action_title))
                    action.triggered.connect(self.menue_clicked)
                    menu.addAction(action)

        # Toolbar aufbauen
        toolbar = QToolBar("Hauptwerkzeugleiste")
        self.addToolBar(toolbar)
        for command, caption in self.toolbarbuttons.items():
            if command == 0:
                toolbar.addSeparator()
            else:
                btn = QPushButton()
                icon = ".\\images\\tb_" + str(command) + ".png"
                if os.path.exists(icon):
                    btn.setIcon(QIcon(icon))
                    btn.setIconSize(QSize(32, 32))
                    btn.setToolTip(caption)
                else:
                    btn.setText(caption)
                btn.setProperty("command", (command, caption))
                btn.clicked.connect(self.menue_clicked)
                toolbar.addWidget(btn)

        # Statusleiste anzeigen
        self.statusBar().showMessage("Ausgeloggt")

        # Dock-Widget für Hilfe
        self.dock = QDockWidget("Dock", self)
        self.dock.setWidget(QTextEdit("Zeigt Hilfe"))
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.dock)
        self.dock.setVisible(False)

        # Tabellenansicht für Interessenten
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        central_layout = QVBoxLayout(central_widget)

        self.table_interessenten = QTableWidget()
        self.table_interessenten.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table_interessenten.doubleClicked.connect(self.editaduser)        
        self.table_interessenten.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table_interessenten.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        central_layout.addWidget(self.table_interessenten)

        # Fenstergröße einstellen
        self.resize(800, 600)
        self.show()

    # Öffnet Bearbeitungsfenster für ausgewählten Benutzer
    def editaduser(self):
        selection = self.table_interessenten.selectedItems()
        if selection:
            row = selection[0].row()
            userid = self.table_interessenten.item(row, 0).text()
            self.editaduserwindow = EditADUserWindow(self.menueoptions[21], userid, self.db_handler)
            self.editaduserwindow.setWindowModality(Qt.WindowModality.ApplicationModal)
            self.editaduserwindow.show()
        else:
            QMessageBox.warning(self, "Fehler", "Kein Eintrag ausgewählt!")

    # Löscht einen AD-User aus der Datenbank
    def delete_ad_user(self):
        selection = self.table_interessenten.selectedItems()
        if not selection:
            QMessageBox.warning(self, "Fehler", "Kein Eintrag ausgewählt!")
            return
        row = selection[0].row()
        userid = self.table_interessenten.item(row, 0).text()

        confirm = QMessageBox.question(
            self, "Bestätigung",
            f"Soll der Benutzer mit ID {userid} wirklich gelöscht werden?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.Yes:
            try:
                delete_query = "DELETE FROM aduser WHERE id_pk = %s"
                self.db_handler.change_data(delete_query, (userid,))
                QMessageBox.information(self, "Erfolg", f"Benutzer mit ID {userid} wurde gelöscht.")
                self.load_ad_users()
            except Exception as e:
                QMessageBox.critical(self, "Fehler", f"Fehler beim Löschen:\n{e}")

    # Deaktiviert einen AD-User (Status ändern)
    def deactivate_ad_user(self):
        selection = self.table_interessenten.selectedItems()
        if not selection:
            QMessageBox.warning(self, "Fehler", "Kein Eintrag ausgewählt!")
            return
        row = selection[0].row()
        userid = self.table_interessenten.item(row, 0).text()

        confirm = QMessageBox.question(
            self, "Bestätigung",
            f"Soll der Benutzer mit ID {userid} deaktiviert werden?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.Yes:
            try:
                update_query = "UPDATE aduser SET status_id_fk = 2 WHERE id_pk = %s"
                self.db_handler.change_data(update_query, (userid,))
                QMessageBox.information(self, "Erfolg", f"Benutzer mit ID {userid} wurde deaktiviert.")
                self.load_ad_users()
            except Exception as e:
                QMessageBox.critical(self, "Fehler", f"Fehler beim Deaktivieren:\n{e}")

    # Reagiert auf Menü- oder Toolbar-Klicks
    def menue_clicked(self):
        men = self.sender()
        print(f"Menu {men.property('command')} selected")
        match men.property("command")[0]:
            case 21:
                self.editaduser()
            case 22:
                self.delete_ad_user()
            case 23:
                self.deactivate_ad_user()
            case 12:
                QMessageBox.warning(self, "Fehler", "Transfer nach AD ist deaktiviert!")
            case 42:
                self.menue_help_help()
            case 41:
                self.menue_help_about()
            case 13:
                self.menu_login()
            case 14:
                self.logout_database()
            case 11:
                self.menue_csv_import()

    # Öffnet Login-Dialog und verbindet sich mit Datenbank
    def menu_login(self):
        dlg = LoginDialog(self)
        if dlg.exec():
            self.db_handler = dlg.get_db_handler()
            self.statusBar().showMessage("Eingeloggt")
            self.load_ad_users()

    # Trennt die Verbindung zur Datenbank
    def logout_database(self):
        if self.db_handler:
            self.db_handler.close_connection()
            self.db_handler = None
        self.table_interessenten.clear()
        self.table_interessenten.setRowCount(0)
        self.table_interessenten.setColumnCount(0)
        self.statusBar().showMessage("Ausgeloggt")

    # Lädt Benutzer-Daten aus der Datenbank in die Tabelle
    def load_ad_users(self):
        if not hasattr(self, 'db_handler') or self.db_handler is None:
            QMessageBox.warning(self, "Fehler", "Keine Datenbankverbindung!")
            return
        try:
            query = "SELECT * FROM view_aduser_details"
            results = self.db_handler.get_data(query)
            self.table_interessenten.clear()
            self.table_interessenten.setRowCount(0)
            headers = [desc[0] for desc in self.db_handler.cursor.description]
            self.table_interessenten.setColumnCount(len(headers))
            self.table_interessenten.setHorizontalHeaderLabels(headers)
            for row_num, row_data in enumerate(results):
                self.table_interessenten.insertRow(row_num)
                for col_num, value in enumerate(row_data):
                    self.table_interessenten.setItem(row_num, col_num, QTableWidgetItem(str(value)))
        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"Fehler beim Laden der Daten:\n{e}")

    # CSV-Datei importieren und Benutzer in Datenbank einfügen oder aktualisieren
    def menue_csv_import(self):
        if not hasattr(self, 'db_handler') or self.db_handler is None:
            QMessageBox.warning(self, "Fehler", "Bitte zuerst einloggen!")
            return

        file_path, _ = QFileDialog.getOpenFileName(self, "CSV-Datei auswählen", "", "CSV-Dateien (*.csv)")
        if not file_path:
            return

        try:
            with open(file_path, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    firstname = row.get('firstname', '').strip()
                    lastname = row.get('lastname', '').strip()
                    phone = row.get('phone', '').strip()
                    department = row.get('abteilung', '').strip()
                    street = row.get('street', '').strip()
                    city = row.get('city', '').strip()
                    city_code = row.get('city_code', '').strip()
                    postalcode = row.get('postalcode', '').strip()
                    kurs_id = int(row.get('kurs', 0))
                    status_id = int(row.get('status_id_fk', 0))

                    username = (firstname[0] + lastname).lower() if firstname and lastname else ''
                    email = f"{firstname.lower()}.{lastname.lower()}@M-zukunftsmotor.local" if firstname and lastname else ''

                    if not username:
                        continue

                    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                    check_query = "SELECT id_pk FROM aduser WHERE username = %s"
                    existing = self.db_handler.get_data(check_query, (username,))

                    if existing:
                        # Update bestehender Benutzer
                        update_query = """
                            UPDATE aduser SET firstname=%s, lastname=%s, email=%s, phone=%s,
                                department=%s, street=%s, city=%s, city_code=%s, postalcode=%s,
                                status_id_fk=%s, ou_id_fk=%s, modified=%s
                            WHERE username=%s
                        """
                        values = (firstname, lastname, email, phone, department,
                                  street, city, city_code, postalcode, status_id, kurs_id, current_time, username)
                        self.db_handler.change_data(update_query, values)
                    else:
                        # Neuer Benutzer
                        insert_query = """
                            INSERT INTO aduser (firstname, lastname, username, email, phone, department, street,
                                city, city_code, postalcode, status_id_fk, ou_id_fk)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """
                        values = (firstname, lastname, username, email, phone, department,
                                  street, city, city_code, postalcode, status_id, kurs_id)
                        self.db_handler.insert_data(insert_query, values)

            QMessageBox.information(self, "Erfolg", "CSV-Import abgeschlossen!")
            self.load_ad_users()

        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"Fehler beim Import:\n{e}")

    # Platzhalter für "Über"-Dialog
    def menue_help_about(self):
        print("Missing function!")

    # Hilfe-Fenster anzeigen
    def menue_help_help(self):
        self.dock.setVisible(True)

# Startet die Anwendung
def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())

# Nur ausführen, wenn direkt gestartet
if __name__ == "__main__":
    main()
