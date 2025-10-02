import sys
import os
import sqlite3
import requests
import json
import threading
import re
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QSplitter, QListWidget, QTextEdit, 
                             QLineEdit, QPushButton, QTextBrowser, QListWidgetItem,
                             QLabel, QMessageBox, QInputDialog, QDialog)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal
from add_book_dialog import AddBookDialog
from edit_book_dialog import EditBookDialog
from dotenv import load_dotenv
from openai import OpenAI



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db_path = os.path.join(os.path.dirname(__file__), "notes_database.db")
        
        # Initialize DeepSeek client
        self.local_client = OpenAI(
            base_url="http://127.0.0.1:1234/v1",  
            api_key="not-needed"                  
        )
        self.system_message = "You are a helpful assistant that analyzes a user's book collection and notes. You will be provided with the complete database of books, authors, types, and notes. Answer questions based on this data, provide insights, recommendations, or summaries as requested. If the answer cannot be found in the provided data, say so clearly."
        
        self.init_database()
        self.init_ui()
        self.setup_connections()
        self.load_stylesheet()
        self.load_books_from_database()
        
        # Initialize search timer for delayed search
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self.perform_delayed_search)
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Personal Note-Taking App")
        self.setGeometry(100, 100, 1200, 800)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        
        # Create the main components
        self.create_search_bar(main_layout)
        self.create_content_area(main_layout)
        self.create_ai_chat_area(main_layout)
        
    def create_search_bar(self, parent_layout):
        """Create the top search bar"""
        search_layout = QHBoxLayout()
        
        search_label = QLabel("Search:")
        search_label.setObjectName("search-label")
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search books, podcasts, or notes...")
        self.search_input.setObjectName("search-input")
        
        self.search_button = QPushButton("Search")
        self.search_button.setObjectName("search-button")
        
        self.clear_search_button = QPushButton("Clear")
        self.clear_search_button.setObjectName("clear-search-button")
        
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_button)
        search_layout.addWidget(self.clear_search_button)
        
        parent_layout.addLayout(search_layout)
        
    def create_content_area(self, parent_layout):
        """Create the main content area with left and right panels"""
        # Create horizontal splitter for main content
        content_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel - Book list
        left_panel = self.create_left_panel()
        content_splitter.addWidget(left_panel)
        
        # Right panel - Notes editor
        right_panel = self.create_right_panel()
        content_splitter.addWidget(right_panel)
        
        # Set splitter proportions (1:2 ratio)
        content_splitter.setStretchFactor(0, 1)
        content_splitter.setStretchFactor(1, 2)
        
        parent_layout.addWidget(content_splitter)
        
    def create_left_panel(self):
        """Create the left panel with book list"""
        left_widget = QWidget()
        left_widget.setObjectName("left-panel")
        left_layout = QVBoxLayout(left_widget)
        
        # Title for the book list
        books_label = QLabel("Books & Podcasts")
        books_label.setObjectName("panel-title")
        left_layout.addWidget(books_label)
        
        # Sort controls
        sort_layout = QHBoxLayout()
        sort_label = QLabel("Sort by:")
        sort_label.setObjectName("sort-label")
        sort_layout.addWidget(sort_label)
        
        from PyQt6.QtWidgets import QComboBox
        self.sort_combo = QComboBox()
        self.sort_combo.setObjectName("sort-combo")
        self.sort_combo.addItems([
            "Name (A-Z)", 
            "Name (Z-A)", 
            "Rating (High to Low)", 
            "Rating (Low to High)",
            "Author (A-Z)",
            "Type"
        ])
        sort_layout.addWidget(self.sort_combo)
        left_layout.addLayout(sort_layout)
        
        # Book list widget
        self.book_list = QListWidget()
        self.book_list.setObjectName("book-list")
        
        left_layout.addWidget(self.book_list)
        
        # Button container for Add and Delete buttons
        button_layout = QHBoxLayout()
        
        # Add Book button
        self.add_book_button = QPushButton("Add Book")
        self.add_book_button.setObjectName("add-book-button")
        button_layout.addWidget(self.add_book_button)
        
        # Edit Book button
        self.edit_book_button = QPushButton("Edit Book")
        self.edit_book_button.setObjectName("edit-book-button")
        self.edit_book_button.setEnabled(False)  # Initially disabled
        button_layout.addWidget(self.edit_book_button)
        
        # Delete Book button
        self.delete_book_button = QPushButton("Delete Book")
        self.delete_book_button.setObjectName("delete-book-button")
        self.delete_book_button.setEnabled(False)  # Initially disabled
        button_layout.addWidget(self.delete_book_button)
        
        left_layout.addLayout(button_layout)
        
        return left_widget
        
    def create_right_panel(self):
        """Create the right panel with notes editor"""
        right_widget = QWidget()
        right_widget.setObjectName("right-panel")
        right_layout = QVBoxLayout(right_widget)
        
        # Title for the notes area
        notes_label = QLabel("Notes")
        notes_label.setObjectName("panel-title")
        right_layout.addWidget(notes_label)
        
        # Notes text editor
        self.notes_editor = QTextEdit()
        self.notes_editor.setObjectName("notes-editor")
        self.notes_editor.setPlaceholderText("Select a book from the left panel to start taking notes...")
        right_layout.addWidget(self.notes_editor)
        
        # Save Note button
        self.save_note_button = QPushButton("Save Note")
        self.save_note_button.setObjectName("save-note-button")
        right_layout.addWidget(self.save_note_button)
        
        return right_widget
        
    def create_ai_chat_area(self, parent_layout):
        """Create the bottom AI chat area"""
        ai_widget = QWidget()
        ai_widget.setObjectName("ai-panel")
        ai_layout = QVBoxLayout(ai_widget)
        
        # AI chat title
        ai_label = QLabel("AI Assistant")
        ai_label.setObjectName("panel-title")
        ai_layout.addWidget(ai_label)
        
        # AI response browser
        self.ai_response_browser = QTextBrowser()
        self.ai_response_browser.setObjectName("ai-response-browser")
        self.ai_response_browser.setMaximumHeight(150)
        self.ai_response_browser.append("AI Assistant: Hello! I'm here to help you with your notes. Ask me anything!")
        ai_layout.addWidget(self.ai_response_browser)
        
        # Input area for AI questions
        ai_input_layout = QHBoxLayout()
        
        self.ai_question_input = QLineEdit()
        self.ai_question_input.setObjectName("ai-question-input")
        self.ai_question_input.setPlaceholderText("Ask the AI assistant about your notes...")
        
        self.ask_ai_button = QPushButton("Ask AI")
        self.ask_ai_button.setObjectName("ask-ai-button")
        
        ai_input_layout.addWidget(self.ai_question_input)
        ai_input_layout.addWidget(self.ask_ai_button)
        
        ai_layout.addLayout(ai_input_layout)
        
        parent_layout.addWidget(ai_widget)
        

            
    def setup_connections(self):
        """Connect buttons to their respective slot methods"""
        self.search_button.clicked.connect(self.on_search_clicked)
        self.clear_search_button.clicked.connect(self.on_clear_search_clicked)
        self.add_book_button.clicked.connect(self.on_add_book_clicked)
        self.edit_book_button.clicked.connect(self.on_edit_book_clicked)
        self.delete_book_button.clicked.connect(self.on_delete_book_clicked)
        self.save_note_button.clicked.connect(self.on_save_note_clicked)
        self.ask_ai_button.clicked.connect(self.on_ask_ai_clicked)
        self.book_list.itemSelectionChanged.connect(self.on_book_selection_changed)
        
        # Allow Enter key to trigger search and AI question
        self.search_input.returnPressed.connect(self.on_search_clicked)
        self.ai_question_input.returnPressed.connect(self.on_ask_ai_clicked)
        
        # Real-time search as user types (with small delay)
        self.search_input.textChanged.connect(self.on_search_text_changed)
        
        # Sort functionality
        self.sort_combo.currentTextChanged.connect(self.on_sort_changed)
        
    def load_stylesheet(self):
        """Load the CSS stylesheet"""
        css_path = os.path.join(os.path.dirname(__file__), "mainWindowStyle.css")
        try:
            with open(css_path, "r") as file:
                self.setStyleSheet(file.read())
        except FileNotFoundError:
            print("Warning: mainWindowStyle.css not found. Using default styling.")
            
    def init_database(self):
        """Initialize SQLite database and create table if it doesn't exist"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create table with columns: name, creator, type, notes, rating
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS books (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    creator TEXT,
                    type TEXT NOT NULL,
                    notes TEXT DEFAULT '',
                    rating INTEGER DEFAULT 0 CHECK (rating >= 0 AND rating <= 5)
                )
            ''')
            
            # Add rating column to existing tables if it doesn't exist
            cursor.execute("PRAGMA table_info(books)")
            columns = [column[1] for column in cursor.fetchall()]
            if 'rating' not in columns:
                cursor.execute('ALTER TABLE books ADD COLUMN rating INTEGER DEFAULT 0 CHECK (rating >= 0 AND rating <= 5)')
                print("Added rating column to existing books table")
            
            conn.commit()
            conn.close()
            print(f"Database initialized successfully at: {self.db_path}")
            
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            QMessageBox.critical(self, "Database Error", f"Failed to initialize database: {e}")
    
    def add_book_to_database(self, name, creator, book_type, initial_notes='', rating=0):
        """Add a new book to the database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO books (name, creator, type, notes, rating)
                VALUES (?, ?, ?, ?, ?)
            ''', (name, creator, book_type, initial_notes, rating))
            
            book_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return book_id
            
        except sqlite3.Error as e:
            print(f"Error adding book: {e}")
            QMessageBox.critical(self, "Database Error", f"Failed to add book: {e}")
            return None
    
    def rating_to_stars(self, rating):
        """Convert numeric rating to star display"""
        if rating == 0:
            return "☆☆☆☆☆"
        filled_stars = "⭐" * rating
        empty_stars = "☆" * (5 - rating)
        return filled_stars + empty_stars
    
    def on_sort_changed(self, sort_text):
        """Handle sort selection change"""
        self.load_books_from_database(sort_by=sort_text)
    
    def load_books_from_database(self, sort_by="Name (A-Z)"):
        """Load all books from database and populate the list widget"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Determine ORDER BY clause based on sort_by parameter
            if sort_by == "Name (A-Z)":
                order_clause = "ORDER BY name ASC"
            elif sort_by == "Name (Z-A)":
                order_clause = "ORDER BY name DESC"
            elif sort_by == "Rating (High to Low)":
                order_clause = "ORDER BY rating DESC, name ASC"
            elif sort_by == "Rating (Low to High)":
                order_clause = "ORDER BY rating ASC, name ASC"
            elif sort_by == "Author (A-Z)":
                order_clause = "ORDER BY creator ASC, name ASC"
            elif sort_by == "Type":
                order_clause = "ORDER BY type ASC, name ASC"
            else:
                order_clause = "ORDER BY name ASC"
            
            cursor.execute(f'SELECT id, name, creator, type, notes, rating FROM books {order_clause}')
            books = cursor.fetchall()
            
            self.book_list.clear()
            
            # Reset the panel title to default
            books_label = self.findChild(QLabel, "panel-title")
            if books_label:
                books_label.setText("Books & Podcasts")
            
            for book_id, name, creator, book_type, notes, rating in books:
                display_text = f"{name}"
                if creator:
                    display_text += f" by {creator}"
                display_text += f" ({book_type})"
                
                # Add rating display
                stars = self.rating_to_stars(rating or 0)
                display_text += f" {stars}"
                
                item = QListWidgetItem(display_text)
                item.setData(Qt.ItemDataRole.UserRole, {
                    "id": book_id,
                    "name": name,
                    "creator": creator,
                    "type": book_type,
                    "notes": notes,
                    "rating": rating or 0
                })
                self.book_list.addItem(item)
                
            conn.close()
            print(f"Loaded {len(books)} books from database")
            
        except sqlite3.Error as e:
            print(f"Error loading books: {e}")
            QMessageBox.critical(self, "Database Error", f"Failed to load books: {e}")
    
    def get_book_notes(self, book_id):
        """Get notes for a specific book"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT notes FROM books WHERE id = ?', (book_id,))
            result = cursor.fetchone()
            
            conn.close()
            
            return result[0] if result else ""
            
        except sqlite3.Error as e:
            print(f"Error getting notes: {e}")
            return ""
    
    def save_book_notes(self, book_id, notes):
        """Save notes for a specific book"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('UPDATE books SET notes = ? WHERE id = ?', (notes, book_id))
            
            conn.commit()
            conn.close()
            
            return True
            
        except sqlite3.Error as e:
            print(f"Error saving notes: {e}")
            QMessageBox.critical(self, "Database Error", f"Failed to save notes: {e}")
            return False
    
    def delete_book_from_database(self, book_id):
        """Delete a book from the database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM books WHERE id = ?', (book_id,))
            
            conn.commit()
            conn.close()
            
            return True
            
        except sqlite3.Error as e:
            print(f"Error deleting book: {e}")
            QMessageBox.critical(self, "Database Error", f"Failed to delete book: {e}")
            return False
    
    def search_books(self, search_term):
        """Search books by name, creator, type, or notes (case-insensitive) and show complete info"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Convert search term to lowercase for case-insensitive search
            search_pattern = f"%{search_term.lower()}%"
            
            # Include notes and rating in the SELECT to show complete information
            cursor.execute('''
                SELECT id, name, creator, type, notes, rating FROM books 
                WHERE LOWER(name) LIKE ? 
                   OR LOWER(creator) LIKE ? 
                   OR LOWER(type) LIKE ? 
                   OR LOWER(notes) LIKE ?
                ORDER BY 
                    CASE 
                        WHEN LOWER(name) LIKE ? THEN 1
                        WHEN LOWER(creator) LIKE ? THEN 2
                        WHEN LOWER(type) LIKE ? THEN 3
                        ELSE 4
                    END,
                    name
            ''', (search_pattern, search_pattern, search_pattern, search_pattern,
                  search_pattern, search_pattern, search_pattern))

            books = cursor.fetchall()

            self.book_list.clear()

            # Update the panel title to show search status
            books_label = self.findChild(QLabel, "panel-title")
            if books_label:
                books_label.setText(f"Search Results for '{search_term}' ({len(books)} found)")

            for book_id, name, creator, book_type, notes, rating in books:
                # Create enhanced display text with more information
                display_text = f"📖 {name}"
                if creator:
                    display_text += f"\n👤 by {creator}"
                display_text += f"\n🏷️ {book_type}"
                
                # Add rating display
                stars = self.rating_to_stars(rating or 0)
                display_text += f"\n⭐ {stars}"
                
                # Add notes preview if notes contain the search term
                if notes and search_term.lower() in notes.lower():
                    # Find the context around the search term
                    notes_preview = self.get_notes_preview(notes, search_term)
                    display_text += f"\n📝 Notes: {notes_preview}"
                elif notes and len(notes.strip()) > 0:
                    # Show a short preview of notes even if search term not in notes
                    short_notes = notes[:50] + "..." if len(notes) > 50 else notes
                    display_text += f"\n📝 Notes: {short_notes}"
                
                item = QListWidgetItem(display_text)
                item.setData(Qt.ItemDataRole.UserRole, {
                    "id": book_id,
                    "name": name,
                    "creator": creator,
                    "type": book_type,
                    "notes": notes,
                    "rating": rating or 0
                })
                self.book_list.addItem(item)
            
            conn.close()
            print(f"Search results: Found {len(books)} books matching '{search_term}' (case-insensitive)")
            
            # Show detailed results summary
            if len(books) == 0:
                QMessageBox.information(self, "Search Results", f"No books found matching '{search_term}'.\n\nSearch includes book names, authors, types, and notes content.")
                # Clear AI chat area when no results
                self.ai_response_browser.clear()
                self.ai_response_browser.append("AI Assistant: No search results found. Try different search terms.")
            else:
                # Auto-select first result and show its complete notes
                if books:
                    self.book_list.setCurrentRow(0)
                
                # Show search summary in AI chat area
                self.show_search_summary(search_term, books)
            
        except sqlite3.Error as e:
            print(f"Error searching books: {e}")
            QMessageBox.critical(self, "Database Error", f"Failed to search: {e}")
    
    def get_notes_preview(self, notes, search_term):
        """Get a preview of notes around the search term"""
        notes_lower = notes.lower()
        search_lower = search_term.lower()
        
        # Find the position of the search term
        pos = notes_lower.find(search_lower)
        if pos == -1:
            return notes[:100] + "..." if len(notes) > 100 else notes
        
        # Get context around the search term (50 characters before and after)
        start = max(0, pos - 50)
        end = min(len(notes), pos + len(search_term) + 50)
        
        preview = notes[start:end]
        
        # Add ellipsis if we're not at the beginning/end
        if start > 0:
            preview = "..." + preview
        if end < len(notes):
            preview = preview + "..."
            
        # Highlight the search term (using ** for emphasis)
        preview = preview.replace(search_term, f"**{search_term}**")
        preview = preview.replace(search_term.upper(), f"**{search_term.upper()}**")
        preview = preview.replace(search_term.lower(), f"**{search_term.lower()}**")
        preview = preview.replace(search_term.capitalize(), f"**{search_term.capitalize()}**")
        
        return preview
    
    def select_book_by_id(self, book_id):
        """Select a book in the list by its database ID"""
        for i in range(self.book_list.count()):
            item = self.book_list.item(i)
            item_data = item.data(Qt.ItemDataRole.UserRole)
            if item_data and item_data.get('id') == book_id:
                self.book_list.setCurrentItem(item)
                break
    
    def show_search_summary(self, search_term, books):
        """Show a comprehensive search summary in the AI chat area"""
        self.ai_response_browser.clear()
        self.ai_response_browser.append(f"🔍 Search Results for '{search_term}'")
        self.ai_response_browser.append(f"Found {len(books)} matching books:")
        
        for i, (book_id, name, creator, book_type, notes, rating) in enumerate(books[:3], 1):  # Show first 3 results
            self.ai_response_browser.append(f"\n{i}. 📖 {name}")
            if creator:
                self.ai_response_browser.append(f"   👤 Author: {creator}")
            self.ai_response_browser.append(f"   🏷️ Type: {book_type}")
            
            # Check where the search term was found
            found_in = []
            search_lower = search_term.lower()
            if search_lower in name.lower():
                found_in.append("title")
            if creator and search_lower in creator.lower():
                found_in.append("author")
            if search_lower in book_type.lower():
                found_in.append("type")
            if notes and search_lower in notes.lower():
                found_in.append("notes")
            
            if found_in:
                self.ai_response_browser.append(f"   ✓ Found in: {', '.join(found_in)}")
            
            if notes and len(notes.strip()) > 0:
                notes_preview = notes[:100] + "..." if len(notes) > 100 else notes
                self.ai_response_browser.append(f"   📝 Notes: {notes_preview}")
        
        if len(books) > 3:
            self.ai_response_browser.append(f"\n... and {len(books) - 3} more results.")
        
        self.ai_response_browser.append(f"\n💡 Click on any book to see complete notes and details.")
            
    # Placeholder slot methods
    def on_search_clicked(self):
        """Handle search button click"""
        search_term = self.search_input.text().strip()
        if search_term:
            print(f"Search clicked: '{search_term}' (case-insensitive)")
            self.search_books(search_term)
        else:
            print("Search clicked: Empty search term - showing all books")
            self.load_books_from_database()  # Show all books if no search term
            self.search_input.setPlaceholderText("Search books, podcasts, or notes...")
    
    def on_search_text_changed(self):
        """Handle real-time search as user types"""
        # Stop the previous timer
        self.search_timer.stop()
        
        # Start a new timer with 300ms delay to avoid too many searches
        self.search_timer.start(300)
    
    def perform_delayed_search(self):
        """Perform the actual search after the timer delay"""
        search_term = self.search_input.text().strip()
        if search_term:
            print(f"Real-time search: '{search_term}'")
            self.search_books(search_term)
        else:
            # If search field is empty, show all books
            self.load_books_from_database()
    
    def on_clear_search_clicked(self):
        """Handle clear search button click"""
        self.search_input.clear()
        self.load_books_from_database()
        print("Search cleared - showing all books")
            
    def on_add_book_clicked(self):
        """Handle add book button click"""
        dialog = AddBookDialog(self)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            if dialog.validate_input():
                book_data = dialog.get_book_data()
                
                # Add to database
                book_id = self.add_book_to_database(
                    book_data['name'], 
                    book_data['creator'], 
                    book_data['type'],
                    book_data['notes'],
                    book_data['rating']
                )
                
                if book_id:
                    self.load_books_from_database()
                    print(f"Added book: '{book_data['name']}' by '{book_data['creator']}' ({book_data['type']}) with ID {book_id}")
                    
                    # Auto-select the newly added book
                    self.select_book_by_id(book_id)
                    
                    QMessageBox.information(self, "Success", f"Book '{book_data['name']}' added successfully!")
                    
                    # If notes were added, show them in the editor
                    if book_data['notes']:
                        self.notes_editor.setPlainText(book_data['notes'])
    
    def on_delete_book_clicked(self):
        """Handle delete book button click"""
        selected_items = self.book_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "Please select a book to delete!")
            return
            
        selected_book = selected_items[0].data(Qt.ItemDataRole.UserRole)
        book_name = selected_book['name']
        
        # Confirmation dialog
        reply = QMessageBox.question(
            self, 
            "Delete Book", 
            f"Are you sure you want to delete '{book_name}' and all its notes?\n\nThis action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.delete_book_from_database(selected_book['id']):
                print(f"Deleted book: '{book_name}' (ID: {selected_book['id']})")
                
                # Refresh the book list
                self.load_books_from_database()
                
                # Clear notes editor
                self.notes_editor.clear()
                self.notes_editor.setPlaceholderText("Select a book from the left panel to start taking notes...")
                
                QMessageBox.information(self, "Success", f"Book '{book_name}' deleted successfully!")
            else:
                QMessageBox.critical(self, "Error", "Failed to delete the book!")
        
    def on_save_note_clicked(self):
        """Handle save note button click"""
        selected_items = self.book_list.selectedItems()
        if selected_items:
            selected_book = selected_items[0].data(Qt.ItemDataRole.UserRole)
            note_content = self.notes_editor.toPlainText()
            
            if self.save_book_notes(selected_book['id'], note_content):
                print(f"Save Note clicked: Saved note for '{selected_book['name']}'")
                print(f"Note content length: {len(note_content)} characters")
                QMessageBox.information(self, "Success", "Notes saved successfully!")
            else:
                QMessageBox.warning(self, "Error", "Failed to save notes!")
        else:
            print("Save Note clicked: No book selected")
            QMessageBox.warning(self, "Warning", "Please select a book first!")
            
    def get_all_database_content(self):
        """Get all books and notes from database as formatted text context"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT id, name, creator, type, notes, rating FROM books ORDER BY name")
            books = cursor.fetchall()
            conn.close()
            
            if not books:
                return "No books found in the database."
            
            context = "Here is all the content from the user's book collection:\n\n"
            
            for book_id, name, creator, book_type, notes, rating in books:
                context += f"Book #{book_id}:\n"
                context += f"Title: {name}\n"
                if creator:
                    context += f"Author/Creator: {creator}\n"
                if book_type:
                    context += f"Type: {book_type}\n"
                if rating > 0:
                    stars = "⭐" * rating + "☆" * (5 - rating)
                    context += f"Rating: {stars} ({rating}/5 stars)\n"
                else:
                    context += f"Rating: Not rated\n"
                if notes:
                    context += f"Notes: {notes}\n"
                else:
                    context += "Notes: (No notes yet)\n"
                context += "\n" + "-"*50 + "\n\n"
            
            return context
            
        except Exception as e:
            return f"Error retrieving database content: {str(e)}"
    
    def clean_output(self, text: str) -> str:
        """Remove <think> ... </think> blocks if they exist"""
        return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()
    
    def message_local(self, prompt: str) -> str:
        """Send message to local AI model with database context"""
        try:
            # Get all database content as context
            database_context = self.get_all_database_content()
            
            # Combine the database context with the user's question
            full_prompt = f"{database_context}\n\nUser Question: {prompt}\n\nPlease answer the question based on the book collection data above. If there is no relevant information, please provide informative answers based on your own knowladge. Assume that all the content in the database has been read by the user."
            
            messages = [
                {"role": "system", "content": self.system_message},
                {"role": "user", "content": full_prompt}
            ]
            completion = self.local_client.chat.completions.create(
                model="deepseek-r1-distill-qwen-14b",
                messages=messages,
            )
            return self.clean_output(completion.choices[0].message.content)
        except Exception as e:
            return f"Error connecting to local model: {str(e)}"
    
    def on_ask_ai_clicked(self):
        """Handle ask AI button click with real AI integration"""
        question = self.ai_question_input.text().strip()
        if question:
            print(f"Ask AI clicked: '{question}'")
            # Add the question to the AI response browser
            self.ai_response_browser.append(f"You: {question}")
            
            # Get AI response with database context
            response = self.message_local(question)
            self.ai_response_browser.append(f"AI: {response}")
            
            self.ai_question_input.clear()
        else:
            print("Ask AI clicked: No question entered")
            
    def on_book_selection_changed(self):
        """Handle book selection change"""
        selected_items = self.book_list.selectedItems()
        if selected_items:
            selected_book = selected_items[0].data(Qt.ItemDataRole.UserRole)
            print(f"Book selected: '{selected_book['name']}' ({selected_book['type']})")
            
            # Enable edit and delete buttons
            self.edit_book_button.setEnabled(True)
            self.delete_book_button.setEnabled(True)
            
            # Load existing notes - use cached notes if available, otherwise fetch from database
            if 'notes' in selected_book and selected_book['notes'] is not None:
                existing_notes = selected_book['notes']
            else:
                existing_notes = self.get_book_notes(selected_book['id'])
            
            self.notes_editor.setPlainText(existing_notes)
            
            # Update notes editor placeholder
            self.notes_editor.setPlaceholderText(f"Write your notes for '{selected_book['name']}' here...")
            
            # Show book details in console for search results
            search_term = self.search_input.text().strip()
            if search_term and existing_notes:
                print(f"Complete book information:")
                print(f"  Title: {selected_book['name']}")
                print(f"  Author: {selected_book.get('creator', 'Unknown')}")
                print(f"  Type: {selected_book['type']}")
                print(f"  Notes length: {len(existing_notes)} characters")
                if search_term.lower() in existing_notes.lower():
                    print(f"  ✓ Search term '{search_term}' found in notes")
        else:
            # Disable edit and delete buttons when no book is selected
            self.edit_book_button.setEnabled(False)
            self.delete_book_button.setEnabled(False)
            self.notes_editor.clear()
            self.notes_editor.setPlaceholderText("Select a book from the left panel to start taking notes...")
    
    def on_edit_book_clicked(self):
        """Handle edit book button click"""
        selected_items = self.book_list.selectedItems()
        if selected_items:
            selected_book = selected_items[0].data(Qt.ItemDataRole.UserRole)
            
            # Create and show edit dialog
            dialog = EditBookDialog(selected_book, self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                if dialog.validate_input():
                    book_data = dialog.get_book_data()
                    
                    # Update in database
                    if self.update_book_in_database(book_data):
                        # Refresh the book list to show updated information
                        current_sort = self.sort_combo.currentText()
                        self.load_books_from_database(sort_by=current_sort)
                        
                        print(f"Updated book: '{book_data['name']}' by '{book_data['creator']}' ({book_data['type']}) - Rating: {book_data['rating']} stars")
                        
                        # Reselect the updated book if possible
                        for i in range(self.book_list.count()):
                            item = self.book_list.item(i)
                            item_data = item.data(Qt.ItemDataRole.UserRole)
                            if item_data and item_data.get('id') == book_data['id']:
                                self.book_list.setCurrentItem(item)
                                break
        else:
            QMessageBox.warning(self, "Warning", "Please select a book to edit!")
    
    def update_book_in_database(self, book_data):
        """Update an existing book in the database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE books 
                SET name = ?, creator = ?, type = ?, rating = ?
                WHERE id = ?
            ''', (book_data['name'], book_data['creator'], book_data['type'], 
                  book_data['rating'], book_data['id']))
            
            if cursor.rowcount > 0:
                conn.commit()
                conn.close()
                QMessageBox.information(self, "Success", "Book updated successfully!")
                return True
            else:
                conn.close()
                QMessageBox.warning(self, "Error", "Book not found in database!")
                return False
                
        except sqlite3.Error as e:
            print(f"Error updating book: {e}")
            QMessageBox.critical(self, "Database Error", f"Failed to update book: {e}")
            return False


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Personal Note-Taking App")
    app.setApplicationVersion("1.0")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())