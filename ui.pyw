import sys
from PyQt5.QtWidgets import QApplication, QDialog
from PyQt5.QtCore import Qt, QEvent, QThread, pyqtSignal, pyqtSlot
from PyQt5.uic import loadUi
from main import generate


class AutomationThread(QThread):
    # Define custom signals to communicate with the main thread
    finished = pyqtSignal()
    log_updated = pyqtSignal(str)  # Custom signal to send log messages

    def __init__(self):
        super(AutomationThread, self).__init__()

        self.progress = 0
        self.total_steps = 100  # You can adjust this value based on the total steps in start_automation

    def run(self):
        # Call the start_automation function with progress_callback_text
        def progress_error(text):
            dialog.update_text_label(text)

        # start
        generate(dialog.password, dialog.user, progress_error)
        # Emit the finished signal to indicate the completion
        self.finished.emit()


class MyDialog(QDialog):
    def __init__(self):
        super(MyDialog, self).__init__()
        self.password = ''
        self.user = ''

        # Load the UI from the XML file
        loadUi("./UI/layout.ui", self)

        # Set the fixed size of the window
        self.setFixedSize(402, 226)

        self.pushButton_User.clicked.connect(self.on_push_button_user_clicked)
        self.pushButton_Pass.clicked.connect(self.on_push_button_pass_clicked)

        # Install the event filter for the QLineEdit widgets
        self.lineEdit_User.installEventFilter(self)
        self.lineEdit_Pass.installEventFilter(self)

        # Dictionary to map each widget with its corresponding button and the next widget in line
        self.widget_button_map = {
            self.lineEdit_User: (self.pushButton_User, self.lineEdit_Pass),
            self.lineEdit_Pass: (self.pushButton_Pass, None)
        }

    def on_push_button_pass_clicked(self):
        self.password = self.lineEdit_Pass.text()  # Use .text() to get QLineEdit input
        self.lineEdit_Pass.setEnabled(False)
        self.pushButton_Pass.setEnabled(False)

        # Create the AutomationThread and start it
        self.automation_thread = AutomationThread()

        # Start the automation thread
        self.automation_thread.start()

    def on_push_button_user_clicked(self):
        self.user = self.lineEdit_User.text()  # Use .text() to get QLineEdit input
        self.lineEdit_Pass.setEnabled(True)
        self.pushButton_Pass.setEnabled(True)
        self.lineEdit_User.setEnabled(False)
        self.pushButton_User.setEnabled(False)

    def wrong_credentials(self):
        self.update_text_label('Provided User / Password is incorrect, provide correct credentials.')

    @pyqtSlot(str)
    def update_text_label(self, text):
        self.TextLabel.setText(text)
        self.lineEdit_Pass.setEnabled(True)
        self.pushButton_Pass.setEnabled(True)
        self.lineEdit_User.setEnabled(True)
        self.pushButton_User.setEnabled(True)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.KeyPress and obj in [self.lineEdit_User, self.lineEdit_Pass]:
            if event.key() in [Qt.Key_Return, Qt.Key_Enter]:
                # Get the corresponding button and next widget
                button, next_widget = self.widget_button_map[obj]

                # Click the appropriate button
                button.click()

                # Move the focus to the next widget in line if available
                if next_widget:
                    next_widget.setFocus()

                return True

        return super().eventFilter(obj, event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    dialog = MyDialog()
    dialog.show()
    sys.exit(app.exec_())


