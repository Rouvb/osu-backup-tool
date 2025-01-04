import os
import shutil
import sys

from PyQt6 import uic
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QMainWindow, QApplication, QFileDialog, QMessageBox

APP_VERSION = "1.1.0"
GITHUB_REPO = "Rouvb/osu-backup-tool"
API_SERVER_URL = f"https://api.github.com/repos/{GITHUB_REPO}"

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

form_class = uic.loadUiType(resource_path("form.ui"))[0]

class BackupThread(QThread):
    finished = pyqtSignal()

    def __init__(self, osu_directory, is_export):
        super().__init__()
        self.osu_directory = osu_directory
        self.is_export = is_export
        self.files = [] # 백업할 디렉토리 또는 파일

    def run(self):
        if self.is_export:
            target_dir = "osu!-backup.zip"
            shutil.make_archive(target_dir.replace(".zip", ""), "zip", self.osu_directory)
        else:
            target_dir = "osu!-backup.zip"
            shutil.unpack_archive(target_dir, self.osu_directory, "zip")
        self.finished.emit()

class BackupTool(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.initUi()
        self.setFixedSize(550, 100)
        self.setWindowIcon(QIcon(resource_path("icon.ico")))
        self.osu_directory = ""

    def initUi(self):
        self.setupUi(self)
        self.pushButton_open_folder.clicked.connect(self.open_osu_folder)
        self.pushButton_export.clicked.connect(self.export_osu)
        self.pushButton_import.clicked.connect(self.import_osu)

    def open_osu_folder(self):
        print("Open osu! Folder")
        self.osu_directory = str(QFileDialog.getExistingDirectory(self, "Select your osu! folder"))
        self.lineEdit.setText(str(self.osu_directory))

    def export_osu(self):
        print("Export", self.osu_directory)
        self.run_backup_thread(is_export=True)

    def import_osu(self):
        print("Import", self.osu_directory)
        self.run_backup_thread(is_export=False)

    def run_backup_thread(self, is_export):
        if self.osu_directory:
            self.thread = BackupThread(self.osu_directory, is_export)
            self.thread.finished.connect(self.on_backup_finished)
            self.thread.start()
        else:
            QMessageBox.warning(self, "Warning", "No osu! folder selected")

    def on_backup_finished(self):
        QMessageBox.information(self, "Success", "Backup finished")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BackupTool()
    window.show()
    app.exec()