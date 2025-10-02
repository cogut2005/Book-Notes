from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit, QComboBox, 
                             QLabel, QTextEdit, QDialogButtonBox, QMessageBox)
from PyQt6.QtCore import Qt

import os


class AddBookDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add New Book/Podcast")
        self.setModal(True)
        self.resize(600, 500)
        
        # Initialize the UI
        self.init_ui()
        
        # Load stylesheet after UI is created
        self.load_stylesheet()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Form layout for book details
        form_layout = QFormLayout()
        
        # Book name field
        self.name_input = QLineEdit()
        self.name_input.setObjectName("name_input")
        self.name_input.setPlaceholderText("Enter the title...")

        self.name_label = QLabel("Name/Title*:")
        self.name_label.setObjectName("name_label")
        self.name_label.setBuddy(self.name_input)
        form_layout.addRow(self.name_label, self.name_input)
        
        # Creator field
        self.creator_input = QLineEdit()
        self.creator_input.setObjectName("creator_input")
        self.creator_input.setPlaceholderText("Enter author/host/creator...")
        self.creator_label = QLabel("Author/Creator*:")
        self.creator_label.setObjectName("creator_label")
        self.creator_label.setBuddy(self.creator_input)
        form_layout.addRow(self.creator_label, self.creator_input)
        
        # Type field
        self.type_combo = QComboBox()
        self.type_combo.setObjectName("type_combo")
        self.type_combo.addItems(["Book", "Podcast", "Audiobook", "Article", "Other"])

        self.type_label = QLabel("Type*:")
        self.type_label.setObjectName("type_label")
        self.type_label.setBuddy(self.type_combo)
        form_layout.addRow(self.type_label, self.type_combo)

        layout.addLayout(form_layout)
        
        # Notes section
        notes_label = QLabel("Initial Notes (Optional):")
        notes_label.setObjectName("notes_label")
        layout.addWidget(notes_label)
        
        self.notes_input = QTextEdit()
        self.notes_input.setObjectName("notes_input")
        self.notes_input.setPlaceholderText("You can start writing your notes here...")
        self.notes_input.setMaximumHeight(200)
        layout.addWidget(self.notes_input)
        
        # Button box
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
    def get_book_data(self):
        """Return the entered book data"""
        return {
            'name': self.name_input.text().strip(),
            'creator': self.creator_input.text().strip(),
            'type': self.type_combo.currentText(),
            'notes': self.notes_input.toPlainText().strip()
        }
        
    def validate_input(self):
        """Validate that required fields are filled"""
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "Missing Information", "Please enter a name/title for the book.")
            self.name_input.setFocus()
            return False
        return True
    
    def load_stylesheet(self):
        """Load the CSS stylesheet"""
        css_path = os.path.join(os.path.dirname(__file__), "add_book.css")
        try:
            with open(css_path, "r") as file:
                self.setStyleSheet(file.read())
        except FileNotFoundError:
            print("Warning: add_book.css not found. Using default styling.")