import mysql.connector  # وارد کردن ماژول اتصال به پایگاه داده MySQL/MariaDB  # MySQL/MariaDB-Bibliothek importieren

class DatabaseHandler:  # کلاس کنترل پایگاه داده               # Datenbank-Verwaltungsklasse
    def __init__(self, host, user, password, database):
        # اتصال به پایگاه داده                               # Verbindung zur Datenbank herstellen
        self.connection = mysql.connector.connect(
            host=host,              # آدرس سرور پایگاه داده           # Datenbank-Host
            user=user,              # نام کاربری                     # Benutzername
            password=password,      # رمز عبور                       # Passwort
            database=database       # نام پایگاه داده                 # Datenbankname
        )
        # ایجاد کرسر برای اجرای دستورات SQL                # Cursor erstellen, um SQL-Abfragen auszuführen
        self.cursor = self.connection.cursor()

    def __del__(self):
        # بستن اتصال به پایگاه داده هنگام حذف شیء           # Verbindung beim Löschen des Objekts schließen
        self.connection.close()

    def close_connection(self):
        # بستن اتصال به پایگاه داده به‌صورت دستی             # Verbindung zur Datenbank manuell schließen
        self.connection.close()

    def get_data(self, query):
        # اجرای کوئری SELECT یا مشابه آن                   # SQL-Abfrage (z.B. SELECT) ausführen
        self.cursor.execute(query)
        # دریافت نتایج (در صورت وجود)                        # Ergebnisse abrufen (falls vorhanden)
        result = self.cursor.fetchall()
        return result

    def insert_data(self, query, insert_data):
        # درج داده‌ها در پایگاه داده                        # Daten in die Datenbank einfügen
        self.cursor.execute(query, insert_data)
        # تأیید تغییرات (commit)                             # Änderungen bestätigen (commit)
        self.connection.commit()

    def change_data(self, query, change_data):
        # تغییر یا حذف داده‌ها در پایگاه داده               # Datensätze ändern oder löschen
        self.cursor.execute(query, change_data)
        # تأیید تغییرات (commit)                             # Änderungen bestätigen (commit)
        self.connection.commit()
