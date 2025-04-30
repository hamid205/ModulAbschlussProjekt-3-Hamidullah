from PyQt6.QtWidgets import (  # وارد کردن ابزارهای گرافیکی از PyQt6     # Importieren von GUI-Komponenten aus PyQt6
    QWidget, QLabel, QLineEdit, QVBoxLayout, QHBoxLayout,
    QPushButton, QMessageBox, QComboBox, QFormLayout, QApplication, QMainWindow
)
from PyQt6.QtCore import QDateTime, Qt  # وارد کردن ماژول‌های زمان و Qt    # Zeit- und Qt-Module importieren
import datetime  # ماژول زمان پایتون                       # Python-Zeitmodul

class EditADUserWindow(QWidget):  # پنجره ویرایش کاربر Active Directory   # Fenster zum Bearbeiten eines AD-Benutzers
    def __init__(self, caption, userid, db_handler):
        super().__init__()
        self.setWindowTitle(caption)  # تنظیم عنوان پنجره             # Fenstertitel setzen
        self.userid = userid          # ذخیره شناسه کاربر              # Benutzer-ID speichern
        self.db_handler = db_handler  # ذخیره شیء پایگاه داده          # Datenbank-Handler speichern

        # فیلدهای فرم                                              # Formularfelder
        self.firstname = QLineEdit()
        self.firstname.setReadOnly(True)  # فقط خواندنی             # Nur lesbar
        self.lastname = QLineEdit()
        self.lastname.setReadOnly(True)                              # Nur lesbar
        self.phone = QLineEdit()
        self.department = QLineEdit()
        self.street = QLineEdit()
        self.postalcode = QLineEdit()
        self.city = QLineEdit()
        self.kuerzel = QComboBox()  # فیلد کد شهری                  # Kürzel-Feld als ComboBox

        self.status = QComboBox()   # فیلد وضعیت کاربر               # Benutzerstatus            ### User Story 3.1 c)
        self.course = QComboBox()   # فیلد دوره                      # Kursauswahl                ### User Story 3.1 c)
        self.created_label = QLabel()    # برچسب تاریخ ایجاد         # Erstellungsdatum
        self.modified_label = QLabel()   # برچسب آخرین تغییر         # Letzte Änderung

        # چیدمان فرم                                              # Formularlayout
        form_layout = QFormLayout()
        form_layout.addRow("Vorname:", self.firstname)
        form_layout.addRow("Nachname:", self.lastname)
        form_layout.addRow("Telefon:", self.phone)
        form_layout.addRow("Abteilung:", self.department)
        form_layout.addRow("Straße:", self.street)
        form_layout.addRow("PLZ:", self.postalcode)
        form_layout.addRow("Ort:", self.city)
        form_layout.addRow("Kürzel:", self.kuerzel)
        form_layout.addRow("Status:", self.status)
        form_layout.addRow("Kurs:", self.course)
        form_layout.addRow("Erstellt:", self.created_label)
        form_layout.addRow("Letzte Änderung:", self.modified_label)

        # دکمه‌ها                                                 # Schaltflächen
        button_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        cancel_button = QPushButton("Abbrechen")  # دکمه انصراف      # Abbrechen-Button
        ok_button.clicked.connect(self.save_changes)
        cancel_button.clicked.connect(self.close)
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)

        # چیدمان اصلی                                             # Hauptlayout
        main_layout = QVBoxLayout(self)
        main_layout.addLayout(form_layout)
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

        self.load_user_data()  # بارگذاری اطلاعات کاربر           # Benutzerdaten laden

    def to_local_time(self, dt):  # تبدیل زمان UTC به زمان محلی     # UTC-Zeit in lokale Zeit umwandeln
        if isinstance(dt, datetime.datetime):
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=datetime.timezone.utc)
            return dt.astimezone().strftime("%Y-%m-%d %H:%M:%S")
        return str(dt)

    def load_user_data(self):  # بارگذاری داده‌های کاربر از پایگاه داده   # Benutzerdaten aus Datenbank laden  ### User Story 3.1 c)
        query = f"""
            SELECT firstname, lastname, phone, department, street, postalcode, city, city_code,
                   status_id_fk, ou_id_fk, created, modified
            FROM aduser
            WHERE id_pk = {self.userid}
        """
        try:
            result = self.db_handler.get_data(query)
            if result:
                (
                    firstname, lastname, phone, department, street, postalcode, city, city_code,
                    status_id, ou_id, created, modified
                ) = result[0]

                self.firstname.setText(firstname)
                self.lastname.setText(lastname)
                self.phone.setText(phone)
                self.department.setText(department)
                self.street.setText(street)
                self.postalcode.setText(postalcode)
                self.city.setText(city)

                self.created_label.setText(self.to_local_time(created))
                self.modified_label.setText(self.to_local_time(modified))

                # پر کردن فیلد کد شهری                          # Kürzel-Feld mit city_code-Werten füllen
                city_codes = self.db_handler.get_data("SELECT DISTINCT city_code FROM aduser WHERE city_code IS NOT NULL")
                for (code,) in city_codes:
                    if code:
                        self.kuerzel.addItem(code)

                index = self.kuerzel.findText(city_code)  # تنظیم مقدار فعلی         # Aktuellen Wert setzen
                if index >= 0:
                    self.kuerzel.setCurrentIndex(index)

                # پر کردن فیلد وضعیت                         # Statusauswahl füllen
                statuses = self.db_handler.get_data("SELECT id_pk, bezeichnung FROM aduser_status") # Daten aus der Tabelle "aduser_status" holen (ID und Bezeichnung)  ### User Story 3.1 c)
                for sid, name in statuses:                          #Jede Statuszeile (ID und Name) zur ComboBox hinzufügen
                    self.status.addItem(name, sid)
                index = self.status.findData(status_id)   # Den Index in der ComboBox suchen, der zum gegebenen status_id passt
                if index >= 0:                            # Wenn ein gültiger Index gefunden wurde, diesen als aktuellen Eintrag setzen
                    self.status.setCurrentIndex(index)

                # پر کردن فیلد دوره                         # Kurse füllen
                courses = self.db_handler.get_data("SELECT id_pk, name FROM adou") # Daten aus der Tabelle "adou" holen (ID und Name der Organisationseinheit)   ### User Story 3.1 c)
                for cid, name in courses:                                          # Jede Organisationseinheit (ID und Name) zur ComboBox hinzufügen
                    self.course.addItem(name, cid)
                index = self.course.findData(ou_id)                                # Den Index in der ComboBox suchen, der zum gegebenen ou_id passt
                if index >= 0:
                    self.course.setCurrentIndex(index)
            else:
                QMessageBox.warning(self, "Fehler", "Benutzer nicht gefunden.")  # کاربر پیدا نشد
                self.close()
        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"Fehler beim Laden:\n{e}")  # خطا هنگام بارگذاری
            self.close()

    def save_changes(self):  # ذخیره تغییرات کاربر در پایگاه داده  # Änderungen speichern
        try:
            query = """
                UPDATE aduser
                SET phone=%s, department=%s, street=%s, postalcode=%s, city=%s, city_code=%s,
                    status_id_fk=%s, ou_id_fk=%s, modified=NOW()
                WHERE id_pk=%s
            """
            values = (
                self.phone.text(),
                self.department.text(),
                self.street.text(),
                self.postalcode.text(),
                self.city.text(),
                self.kuerzel.currentText(),  # ذخیره کد شهری             # Kürzel speichern
                self.status.currentData(),
                self.course.currentData(),
                self.userid,
            )
            self.db_handler.change_data(query, values)

            QMessageBox.information(self, "Erfolg", "Benutzerdaten gespeichert.")  # داده‌ها ذخیره شدند

            # به‌روزرسانی جدول در پنجره اصلی                 # Hauptfenster aktualisieren
            for widget in QApplication.topLevelWidgets():
                if isinstance(widget, QMainWindow):
                    if hasattr(widget, 'load_ad_users'):
                        widget.load_ad_users()
                    break

            self.close()  # بستن پنجره                        # Fenster schließen

        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"Fehler beim Speichern:\n{e}")  # خطا در ذخیره‌سازی
