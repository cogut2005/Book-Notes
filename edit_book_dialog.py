from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit, QComboBox, 
                             QLabel, QTextEdit, QDialogButtonBox, QMessageBox)
from PyQt6.QtCore import Qt

import os


class EditBookDialog(QDialog):
    def __init__(self, book_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Book/Podcast")
        self.setModal(True)
        self.resize(600, 500)
        
        # Store the original book data
        self.original_book_data = book_data
        
        # Initialize the UI
        self.init_ui()
        
        # Load the existing book data into the form
        self.load_book_data()
        
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
        
        # Rating field
        self.rating_combo = QComboBox()
        self.rating_combo.setObjectName("rating_combo")
        self.rating_combo.addItems(["⭐⭐⭐⭐⭐ (5 stars)", "⭐⭐⭐⭐☆ (4 stars)", "⭐⭐⭐☆☆ (3 stars)", 
                                   "⭐⭐☆☆☆ (2 stars)", "⭐☆☆☆☆ (1 star)", "☆☆☆☆☆ (Not rated)"])
        
        self.rating_label = QLabel("Rating:")
        self.rating_label.setObjectName("rating_label")
        self.rating_label.setBuddy(self.rating_combo)
        form_layout.addRow(self.rating_label, self.rating_combo)

        layout.addLayout(form_layout)
        
        # Notes section (read-only in edit mode)
        notes_label = QLabel("Notes (view/edit in main window):")
        notes_label.setObjectName("notes_label")
        layout.addWidget(notes_label)
        
        self.notes_display = QTextEdit()
        self.notes_display.setObjectName("notes_display")
        self.notes_display.setReadOnly(True)
        self.notes_display.setMaximumHeight(150)
        layout.addWidget(self.notes_display)
        
        # Button box
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
    def load_book_data(self):
        """Load the existing book data into the form fields"""
        # Set name
        self.name_input.setText(self.original_book_data.get('name', ''))
        
        # Set creator
        self.creator_input.setText(self.original_book_data.get('creator', ''))
        
        # Set type
        book_type = self.original_book_data.get('type', 'Book')
        type_index = self.type_combo.findText(book_type)
        if type_index >= 0:
            self.type_combo.setCurrentIndex(type_index)
        
        # Set rating
        rating = self.original_book_data.get('rating', 0)
        if rating == 0:
            rating_index = 5  # "Not rated"
        else:
            rating_index = 5 - rating  # Convert 5-star to index (5->0, 4->1, etc.)
        self.rating_combo.setCurrentIndex(rating_index)
        
        # Display notes (read-only)
        notes = self.original_book_data.get('notes', '')
        if notes:
            self.notes_display.setPlainText(notes)
        else:
            self.notes_display.setPlainText("(No notes yet)")
        
    def get_book_data(self):
        """Return the updated book data"""
        # Convert rating index to rating value (5-star system)
        rating_index = self.rating_combo.currentIndex()
        rating_value = 5 - rating_index if rating_index < 5 else 0  # 0 for "Not rated"
        
        return {
            'id': self.original_book_data['id'],  # Keep the original ID
            'name': self.name_input.text().strip(),
            'creator': self.creator_input.text().strip(),
            'type': self.type_combo.currentText(),
            'notes': self.original_book_data.get('notes', ''),  # Keep original notes
            'rating': rating_value
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