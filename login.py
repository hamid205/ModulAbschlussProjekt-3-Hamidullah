# User Story 1.1  Log-in

from PyQt6.QtWidgets import (  # وارد کردن ابزارهای گرافیکی از PyQt6  # GUI-Komponenten aus PyQt6 importieren
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QComboBox, QPushButton, QMessageBox
)
from database import DatabaseHandler  # وارد کردن کلاس کنترل پایگاه داده  # Import der Datenbank-Verwaltungsklasse

class LoginDialog(QDialog):  # پنجره گفت‌وگو برای ورود به پایگاه داده  # Dialogfenster für die Datenbankanmeldung
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Datenbankanmeldung")  # عنوان پنجره را تنظیم می‌کند  # Fenstertitel setzen
        self.setFixedSize(300, 200)  # اندازه ثابت پنجره  # Feste Fenstergröße

        self.db_handler = None  # کنترل‌کننده پایگاه داده هنوز تعریف نشده  # Datenbank-Handler (noch leer)

        # چیدمان عمودی اصلی پنجره  # Hauptlayout (vertikal)
        layout = QVBoxLayout()

        # انتخاب پایگاه داده  # Datenbankauswahl
        self.db_label = QLabel("Database:")  # برچسب نام پایگاه داده  # Beschriftung für Datenbank
        self.db_select = QComboBox()  # منوی کشویی برای انتخاب پایگاه داده  # Dropdown zur Auswahl der Datenbank
        self.db_select.addItems(["AD", "interessenten_modul3"])  # گزینه‌های موجود  # Verfügbare Optionen
        layout.addWidget(self.db_label)
        layout.addWidget(self.db_select)

        # نام کاربری  # Benutzername
        self.user_label = QLabel("Benutzername:")  # برچسب نام کاربری  # Beschriftung für Benutzername
        self.user_input = QLineEdit()  # فیلد ورودی نام کاربری  # Eingabefeld für Benutzername
        layout.addWidget(self.user_label)
        layout.addWidget(self.user_input)

        # رمز عبور  # Passwort
        self.pass_label = QLabel("Passwort :")  # برچسب رمز عبور  # Beschriftung für Passwort
        self.pass_input = QLineEdit()  # فیلد ورودی رمز عبور  # Eingabefeld für Passwort
        self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)  # نمایش رمز به صورت ستاره  # Passwort verstecken
        layout.addWidget(self.pass_label)
        layout.addWidget(self.pass_input)

        # دکمه‌های تایید و لغو  # OK- und Abbrechen-Schaltflächen
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("OK")
        self.cancel_button = QPushButton("Abbrechen")  # دکمه لغو  # Abbrechen-Schaltfläche
        self.ok_button.clicked.connect(self.try_login)  # اتصال دکمه OK به تابع ورود  # OK-Button mit Login-Funktion verbinden
        self.cancel_button.clicked.connect(self.reject)  # بستن پنجره بدون ورود  # Fenster ohne Anmeldung schließen
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)  # اعمال چیدمان به پنجره  # Layout anwenden

    def try_login(self):  # تلاش برای ورود به پایگاه داده  # Versuch, sich mit der Datenbank zu verbinden
        db = self.db_select.currentText()  # گرفتن نام پایگاه داده انتخاب‌شده  # Ausgewählte Datenbank
        user = self.user_input.text()      # گرفتن نام کاربری  # Benutzername
        password = self.pass_input.text()  # گرفتن رمز عبور  # Passwort

        try:
            self.db_handler = DatabaseHandler(  # ساخت کنترل‌کننده پایگاه داده  # Erstellung des Datenbank-Handlers
                host="mariadb",  # نام سرور (می‌توان تغییر داد)  # Servername (anpassbar)
                user=user,
                password=password,
                database=db
            )
            QMessageBox.information(self, "Erfolg", "Verbindung erfolgreich!")  # موفقیت در اتصال  # Verbindung erfolgreich
            self.accept()  # بستن پنجره با تایید  # Dialog schließen (OK)
        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"Verbindung fehlgeschlagen:\n{e}")  # خطا در اتصال  # Fehler beim Verbinden
            self.db_handler = None  # حذف کنترل‌کننده در صورت خطا  # Handler zurücksetzen

    def get_db_handler(self):  # برگرداندن شیء پایگاه داده  # Rückgabe des Datenbank-Handlers
        return self.db_handler

################################################################################################################################################################################

# کلاس DatabaseHandler برای اتصال به پایگاه داده استفاده می‌شود
# این کلاس اطلاعات اتصال مثل هاست، کاربر، رمز و نام دیتابیس را می‌گیرد
# می‌توان با آن دستورات SQL اجرا کرد (مثل SELECT، INSERT و ...)
# در پایان نیز اتصال را به‌درستی می‌بندد


# Die Klasse DatabaseHandler wird verwendet, um eine Verbindung zur Datenbank herzustellen
# Sie verwendet Host, Benutzername, Passwort und Datenbankname zur Verbindung
# Mit ihr kann man SQL-Befehle wie SELECT, INSERT, UPDATE, DELETE ausführen
# Am Ende wird die Verbindung sicher geschlossen
#################################################################################################################################################################################
