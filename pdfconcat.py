from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QFileDialog,
    QMessageBox,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QListWidget,
    QWidget,
    QLabel,
    QLineEdit,
    QGroupBox,
)
from PySide6.QtGui import QDropEvent, QDragEnterEvent, QIcon, QPixmap

import sys
import os
import datetime
import getpass
import pikepdf

import rc_static

APP_NAME = "PDF Concatenator 2000 Pro"
DEFAULT_OUTPUT_NAME = "Concatenated Document"
DEFAULT_EXTENSION = ".pdf"
DEFAULT_OUTPUT_DIR = "Documents"


class PDFConcatenatorApp(QMainWindow):
    # TODO use QRC for static files
    style0 = (
        "background-color: white; background-image: url(':/backdrop.png'); background-repeat: none; "
        "background-attachment: fixed; background-position: center"
    )
    style1 = "background-color: white"

    # get user's home directory path
    home_directory = os.path.expanduser("~")

    export_file_name = DEFAULT_OUTPUT_NAME

    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME)

        # file list and operations
        self.files = []
        self.init_ui()
        self.setAcceptDrops(True)  # Enable drag-and-drop for external files

        # set the application icon
        icon = QIcon(QPixmap(":/icon.png"))
        self.setWindowIcon(icon)

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        central_layout = QVBoxLayout()

        file_frame = QGroupBox("File List", flat=False)

        file_layout = QVBoxLayout()

        # File list display
        self.file_list = QListWidget()
        self.file_list.setStyleSheet(self.style0)
        self.file_list.setSelectionMode(QListWidget.SingleSelection)
        self.file_list.setDragDropMode(QListWidget.InternalMove)  # Enable reordering
        self.file_list.model().rowsMoved.connect(
            self.update_file_order
        )  # Sync file list
        self.file_list.itemSelectionChanged.connect(self.update_action_buttons)
        file_layout.addWidget(self.file_list)

        # Buttons for managing files
        button_layout = QHBoxLayout()

        self.btn_add = QPushButton("+ Add")
        self.btn_add.clicked.connect(self.add_files)
        self.btn_add.setToolTip("Add file(s)")
        self.btn_add.setWhatsThis("Add one or more files to the list.")
        button_layout.addWidget(self.btn_add)

        self.btn_rm = QPushButton("- Remove")
        self.btn_rm.clicked.connect(self.remove_selected)
        self.btn_rm.setEnabled(False)
        self.btn_rm.setToolTip("Remove selected file")
        self.btn_add.setWhatsThis("Delete a file from the list.")
        button_layout.addWidget(self.btn_rm)

        self.btn_up = QPushButton("▲ Up")
        self.btn_up.clicked.connect(self.move_up)
        self.btn_up.setEnabled(False)
        self.btn_up.setToolTip("Move selected file up")
        self.btn_add.setWhatsThis("Move the currently selected file up in the list.")
        button_layout.addWidget(self.btn_up)

        self.btn_down = QPushButton("▼ Down")
        self.btn_down.clicked.connect(self.move_down)
        self.btn_down.setEnabled(False)
        self.btn_down.setToolTip("Move selected file down")
        self.btn_add.setWhatsThis("Move the currently selected file down in the list.")
        button_layout.addWidget(self.btn_down)

        file_layout.addLayout(button_layout)

        export_frame = QGroupBox("Export Settings", flat=False)

        # Output file name and save button
        output_layout = QHBoxLayout()

        self.output_name = QLineEdit(self.export_file_name)
        output_layout.addWidget(QLabel("Document Title:"))
        output_layout.addWidget(self.output_name)

        self.btn_save = QPushButton(
            "Concatenate my PDFs!",
        )
        self.btn_save.clicked.connect(self.save_pdf)
        self.btn_save.setDefault(True)
        self.btn_save.setAutoDefault(True)

        file_frame.setLayout(file_layout)
        central_layout.addWidget(file_frame)

        export_frame.setLayout(output_layout)
        central_layout.addWidget(export_frame)

        central_layout.addWidget(self.btn_save)

        central_widget.setLayout(central_layout)

    def update_action_buttons(self):
        # Enable/disable buttons based on selection and file list
        selected = self.file_list.currentRow()
        total_files = len(self.files)

        self.btn_rm.setEnabled(selected >= 0)
        self.btn_up.setEnabled(selected > 0)
        self.btn_down.setEnabled(selected < total_files - 1)

    def update_file_order(
        self, source_row, source_parent, destination_row, destination_parent
    ):
        # Update the order of files when items are reordered in the list
        moved_item = self.files.pop(source_row)
        self.files.insert(destination_row, moved_item)

    def add_files(self):
        # Add files via QFileDialog
        file_paths, _ = QFileDialog.getOpenFileNames(
            self, "Select PDF Files", "", "PDF Files (*.pdf)"
        )

        file_paths.sort()

        if file_paths:
            self.files.extend(file_paths)
            self.refresh_file_list()

    def remove_selected(self):
        # Remove selected file
        selected = self.file_list.currentRow()
        if selected >= 0:
            del self.files[selected]
            self.refresh_file_list()

    def move_up(self):
        # Move selected file up
        selected = self.file_list.currentRow()
        if selected > 0:
            self.files[selected], self.files[selected - 1] = (
                self.files[selected - 1],
                self.files[selected],
            )
            self.refresh_file_list()
            self.file_list.setCurrentRow(selected - 1)

    def move_down(self):
        # Move selected file down
        selected = self.file_list.currentRow()
        if selected < len(self.files) - 1:
            self.files[selected], self.files[selected + 1] = (
                self.files[selected + 1],
                self.files[selected],
            )
            self.refresh_file_list()
            self.file_list.setCurrentRow(selected + 1)

    def refresh_file_list(self):
        # Refresh the QListWidget to match self.files
        self.file_list.clear()
        self.file_list.addItems(self.files)
        if len(self.files) > 0:
            self.file_list.setStyleSheet(self.style1)
        else:
            self.file_list.setStyleSheet(self.style0)
        self.update_action_buttons()

    def save_pdf(self):
        # Concatenate PDFs and save the output file
        output_file, _ = QFileDialog.getSaveFileName(
            self,
            "Save Output PDF",
            self.output_name.text().replace(" ", "_"),
            "PDF Files (*.pdf)",
        )
        if not output_file:
            return

        try:
            with pikepdf.Pdf.new() as pdf_output:
                current_date = datetime.date.today().strftime("D:%Y%m%d%H%M%S")
                current_user = getpass.getuser().title()

                pdf_output.docinfo["/Creator"] = APP_NAME
                pdf_output.docinfo["/Title"] = output_file.replace("_", " ").title()
                pdf_output.docinfo["/CreationDate"] = current_date
                pdf_output.docinfo["/ModDate"] = current_date
                pdf_output.docinfo["/Author"] = current_user

                for file in self.files:
                    with pikepdf.Pdf.open(file) as pdf:
                        pdf_output.pages.extend(pdf.pages)

                if not output_file.endswith(DEFAULT_EXTENSION):
                    output_file += DEFAULT_EXTENSION

                pdf_output.save(output_file)

            QMessageBox.information(self, "Success", f"PDF saved as {output_file}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save PDF: {e}")

    def dragEnterEvent(self, event: QDragEnterEvent):
        # Accept drag if it contains URLs (files)
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dragMoveEvent(self, event: QDragEnterEvent):
        # Accept drag move events
        event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        # Handle dropped files
        urls = event.mimeData().urls()
        for url in urls:
            file_path = url.toLocalFile()
            if file_path.endswith(".pdf"):
                self.files.append(file_path)
        self.refresh_file_list()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PDFConcatenatorApp()
    window.setFixedSize(400, 480)
    window.show()
    sys.exit(app.exec())
