# Personal Note-Taking App

A modern PyQt6 desktop application for taking notes on books, podcasts, and audiobooks with an integrated AI assistant.

## Features

### 📚 Book Management
- **Left Panel**: View your collection of books, podcasts, and audiobooks
- **Add Book Button**: Add new items to your collection with name, creator, and type
- **Book Types**: Supports Books, Podcasts, Audiobooks, Articles, and Other
- **SQLite Database**: All data is persistently stored in a local SQLite database

### 📝 Note Taking
- **Right Panel**: Rich text editor for writing notes
- **Linked Notes**: Notes are associated with the selected book/podcast
- **Auto-Load**: Notes are automatically loaded when selecting a book
- **Save Functionality**: Save your notes directly to the SQLite database

### 🔍 Search
- **Top Search Bar**: Search through book names, creators, types, and notes content
- **Real-time Results**: Instantly filter your collection
- **Full-text Search**: Search within your notes content

### 🤖 AI Assistant
- **Bottom Panel**: Chat interface with AI assistant
- **Question Input**: Ask questions about your notes
- **Response Display**: View AI responses in the chat area
- **Placeholder**: Currently prints questions to console

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- macOS, Windows, or Linux

### Installation Steps

1. **Clone or download the project files to your desired directory**

2. **Navigate to the project directory:**
   ```bash
   cd "/path/to/Book Notes"
   ```

3. **Create and activate a virtual environment:**
   ```bash
   # Create virtual environment
   python3 -m venv venv
   
   # Activate on macOS/Linux
   source venv/bin/activate
   
   # Activate on Windows
   venv\Scripts\activate
   ```

4. **Install PyQt6:**
   ```bash
   pip install PyQt6
   ```

5. **Run the application:**
   ```bash
   python main.py
   ```

## Project Structure

```
Book Notes/
├── main.py              # Main application file
├── add_book_dialog.py   # Add book dialog class
├── mainWindowStyle.css  # CSS styling for modern UI
├── notes_database.db    # SQLite database (created automatically)
├── venv/                # Virtual environment (created during setup)
└── README.md            # This file
```

## Usage

1. **Launch the application** by running `python main.py`
2. **Select a book** from the left panel to start taking notes
3. **Write your notes** in the right panel editor
4. **Search** for books or content using the top search bar
5. **Ask the AI** questions about your notes using the bottom panel

## Database Schema

The application uses SQLite database with the following table structure:

**books** table:
- `id` (INTEGER PRIMARY KEY) - Auto-incrementing unique identifier
- `name` (TEXT NOT NULL) - Book/podcast/audiobook title
- `creator` (TEXT) - Author, host, or creator name (optional)
- `type` (TEXT NOT NULL) - Type: Book, Podcast, Audiobook, Article, or Other
- `notes` (TEXT DEFAULT '') - Your personal notes for this item

## Current Functionality

### ✅ Fully Functional Features:
- **Add Book Dialog**: Single-page popup for adding books with name, creator, type, and initial notes
- **Delete Book Feature**: Remove books and all associated notes with confirmation dialog
- **Start Notes Immediately**: Write your first notes directly in the add book dialog
- **Auto-Selection**: Newly added books are automatically selected for immediate note-taking
- **Save Note Button**: Saves your notes to the SQLite database
- **Advanced Search**: Case-insensitive search through book names, authors, types, and notes content
- **Real-time Search**: Search results update as you type (with 300ms delay)
- **Clear Search**: Easy-to-use clear button to reset search and show all books
- **Book Selection**: Automatically loads saved notes when selecting a book
- **Smart UI**: Delete button is only enabled when a book is selected
- **Data Persistence**: All data is saved to `notes_database.db`

### 🔄 Placeholder Features:
- **Ask AI Button**: Prints questions and adds them to the chat display (ready for AI integration)

## Database File

The SQLite database file `notes_database.db` is created automatically in the application directory. This file contains all your books and notes data.

## User Interface

### Layout Features
- **Resizable panels** using QSplitter
- **Modern styling** with custom CSS
- **Responsive design** that adapts to window resizing
- **Intuitive navigation** with keyboard shortcuts (Enter key support)

### Styling
- Clean, modern interface with rounded corners
- Color-coded buttons for different functions
- Hover effects and visual feedback
- Custom scrollbars and selection highlighting

## Development Notes

### Architecture
- Built with PyQt6 for cross-platform compatibility
- Object-oriented design with MainWindow class
- Modular UI components for easy maintenance
- Separate CSS file for styling

### Extensibility
The application is designed to be easily extended with:
- Database integration for persistent storage
- Real AI assistant integration
- Advanced search functionality
- Export/import features
- Multiple note formats (Markdown, HTML, etc.)

## Future Enhancements

- [ ] Database integration (SQLite)
- [ ] Real AI assistant (OpenAI API integration)
- [ ] Advanced search with filtering
- [ ] Note export (PDF, Markdown, HTML)
- [ ] Dark mode theme
- [ ] Note categories and tags
- [ ] File attachments
- [ ] Backup and sync features

## Requirements

### Python Packages
- PyQt6 (>=6.0.0)

### System Requirements
- **RAM**: 256MB minimum
- **Storage**: 50MB for application + space for notes
- **OS**: macOS 10.14+, Windows 10+, or Linux with Qt support

## Troubleshooting

### Common Issues

1. **"ModuleNotFoundError: No module named 'PyQt6'"**
   - Make sure you've activated the virtual environment
   - Install PyQt6 with: `pip install PyQt6`

2. **CSS not loading properly**
   - Ensure `styles.css` is in the same directory as `main.py`
   - Check file permissions

3. **Application won't start**
   - Verify Python 3.8+ is installed
   - Check that all dependencies are installed in the virtual environment

## License

This project is created as a demonstration application. Feel free to use and modify as needed.

## Contributing

To contribute to this project:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

---

**Note**: This is a skeleton application with placeholder functionality. All button actions currently print to the console and are ready for integration with real backend services.