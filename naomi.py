import os.path
import sys
from enum import Enum
from pathlib import Path
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, \
    QSizePolicy, QDesktopWidget, QFileDialog, QHBoxLayout, QMessageBox
from PIL import Image
from pptx_tools.utils import save_pptx_as_png
import comtypes.stream
class FileType(Enum):
    file=0
    folder=1
#  pyinstaller --onefile --noconsole --icon=.\Untitled.ico .\naomi.py

def pptx_to_tiff(output_direc, pptx_file):
    save_pptx_as_png(output_direc, pptx_file)
    for slide in Path(output_direc).iterdir():
        image = Image.open(slide)
        tiff_image = image.convert("L")
        # Save as TIFF
        tiff_image_path = os.path.join(output_direc, f"{slide.stem}.tiff")
        tiff_image.save(tiff_image_path, format="TIFF", dpi=(600, 600))
        # tiff_image.show()

class PPtxWindow(QMainWindow):
    def __init__(self, window_title: str, shape: tuple[int] = (800, 200)):
        super().__init__()

        self.central_widget = QWidget()
        self.layout = QVBoxLayout()
        self.setWindowTitle(window_title)
        self.setGeometry(0, 0, *shape)
        self.center()
        self.central_widget.setLayout(self.layout)

        self.pptx_edit = self.create_file_widget('Select PPTX File', 'PPTX File',FileType.file)
        self.output_edit = self.create_file_widget('Select Output Folder', 'Output Folder',FileType.folder)
        self.finish = QPushButton('Finished!')
        self.finish.setSizePolicy(self.finish.sizePolicy().Fixed, self.finish.sizePolicy().Fixed)
        self.finish.clicked.connect(self.finish_button_press)

        self.layout.addWidget(self.finish, alignment=Qt.AlignCenter)
        self.setCentralWidget(self.central_widget)
        self.show()

    def create_file_widget(self, button_label, edit_label,file_folder:FileType):
        file_layout = QHBoxLayout()
        container = QWidget()
        container.setLayout(file_layout)
        line_edit = QLineEdit()
        line_edit.setPlaceholderText(edit_label)
        button = QPushButton(button_label)
        button.clicked.connect(lambda: self.open_file_dialog(line_edit,file_folder))
        file_layout.addWidget(line_edit)
        file_layout.addWidget(button)
        self.layout.addWidget(container)
        return line_edit

    def show_error_popup(self,error:str):
        # Create and configure error popup
        error_dialog = QMessageBox()
        error_dialog.setIcon(QMessageBox.Critical)
        error_dialog.setText("An error occurred!")
        error_dialog.setInformativeText(error)
        error_dialog.setWindowTitle("Error")
        error_dialog.setStandardButtons(QMessageBox.Ok)
        error_dialog.exec_()
    def finish_button_press(self):
        try:
            output_folder = Path(self.output_edit.text()).joinpath(Path(self.pptx_edit.text()).stem)
            pptx_to_tiff(output_folder, self.pptx_edit.text())
        except Exception as e:
            self.show_error_popup(e.__str__())

    def open_file_dialog(self, line_edit: QLineEdit,file_folder:FileType):
        if file_folder==FileType.file:
            selected, _ = QFileDialog.getOpenFileName(self, "Open File", "", "All Files (*);;Text Files (*.txt)")
        else:
            selected=QFileDialog.getExistingDirectory(self, 'label')
        line_edit.setText(selected)

    def center(self):
        # Get the geometry of the screen
        screen_geometry = QDesktopWidget().screenGeometry()
        # Get the geometry of the window
        window_geometry = self.frameGeometry()
        # Calculate the center point of the screen
        screen_center = screen_geometry.center()
        # Move the window's geometry center to the screen's center point
        window_geometry.moveCenter(screen_center)
        # Move the top-left corner of the window to the calculated top-left position
        self.move(window_geometry.topLeft())


def run_app():
    app = QApplication(sys.argv)
    main_window = PPtxWindow('PoopooPeepee')
    sys.exit(app.exec_())


if __name__ == '__main__':
    run_app()
