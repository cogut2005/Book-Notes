# Personal Note-Taking App

A PyQt6 desktop application for managing books, podcasts, and notes with an integrated local AI assistant.

## Features

### 📚 Book Management
- **Left Panel**: View your collection of books, podcasts, audiobooks, articles, and other items
- **Add Book Button**: Add new items with name, creator, type, rating, and optional initial notes
- **Edit Book Button**: Update existing item metadata at any time
- **Book Types**: Supports Book, Podcast, Audiobook, Article, and Other
- **Ratings**: Store a 0-5 star rating for each item
- **SQLite Database**: All data is persistently stored in a local SQLite database

### 📝 Note Taking
- **Right Panel**: Text editor for writing notes
- **Linked Notes**: Notes are associated with the selected book/podcast
- **Auto-Load**: Notes are automatically loaded when selecting a book
- **Save Functionality**: Save your notes directly to the SQLite database

### 🔍 Search
- **Top Search Bar**: Search through book names, creators, types, and notes content
- **Real-time Results**: Instantly filter your collection
- **Full-text Search**: Search within your notes content

### 🤖 AI Assistant
- **Bottom Panel**: Chat interface with a local AI assistant
- **Question Input**: Ask questions about your notes and library
- **Response Display**: View AI responses in the chat area
- **Local Model Support**: Works with OpenAI-compatible local servers such as LM Studio
- **Auto Detection**: Disables the AI UI gracefully when the local model server is unavailable

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

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Optional: configure local AI endpoint**
   Create a `.env` file in the project root if you want to override the default local model settings:
   ```env
   LOCAL_OPENAI_BASE_URL=http://127.0.0.1:1234/v1
   LOCAL_OPENAI_MODEL=openai/gpt-oss-20b
   LOCAL_OPENAI_API_KEY=not-needed
   ```
   Notes:
   - If you use LM Studio, start its local server before launching the app.
   - If you accidentally set `LOCAL_OPENAI_BASE_URL` without `/v1`, the app now normalizes it automatically.

6. **Run the application:**
   ```bash
   python main.py
   ```

## Project Structure

```
Book Notes/
├── main.py              # Main application file
├── add_book_dialog.py   # Add book dialog class
├── edit_book_dialog.py  # Edit book dialog class
├── add_book.css         # Dialog styling
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
- `rating` (INTEGER DEFAULT 0) - Rating from 0 to 5 stars

## Current Functionality

### ✅ Fully Functional Features:
- **Add Book Dialog**: Single-page popup for adding books with name, creator, type, rating, and initial notes
- **Edit Book Dialog**: Update an item's name, creator, type, and rating
- **Delete Book Feature**: Remove books and all associated notes with confirmation dialog
- **Start Notes Immediately**: Write your first notes directly in the add book dialog
- **Auto-Selection**: Newly added books are automatically selected for immediate note-taking
- **Save Note Button**: Saves your notes to the SQLite database
- **Sorting**: Sort by name, rating, creator, or type
- **Rating Display**: Show star ratings directly in the list
- **Advanced Search**: Case-insensitive search through book names, authors, types, and notes content
- **Real-time Search**: Search results update as you type (with 300ms delay)
- **Clear Search**: Easy-to-use clear button to reset search and show all books
- **Book Selection**: Automatically loads saved notes when selecting a book
- **Smart UI**: Edit and delete buttons are only enabled when a book is selected
- **Data Persistence**: All data is saved to `notes_database.db`
- **Local AI Chat**: Sends your full library context plus your question to a local OpenAI-compatible model

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
- Advanced search functionality
- Export/import features
- Multiple note formats (Markdown, HTML, etc.)

## Future Enhancements

- [ ] Advanced search filters
- [ ] Note export (PDF, Markdown, HTML)
- [ ] Dark mode theme
- [ ] Note categories and tags
- [ ] File attachments
- [ ] Backup and sync features

## Requirements

### Python Packages
- PyQt6
- PyQt6-Qt6
- PyQt6-sip
- requests
- python-dotenv
- openai

### System Requirements
- **RAM**: 256MB minimum
- **Storage**: 50MB for application + space for notes
- **OS**: macOS 10.14+, Windows 10+, or Linux with Qt support

## Troubleshooting

### Common Issues

1. **"ModuleNotFoundError: No module named 'PyQt6'"**
   - Make sure you've activated the virtual environment
   - Install project dependencies with: `pip install -r requirements.txt`

2. **CSS not loading properly**
   - Ensure `mainWindowStyle.css` is in the same directory as `main.py`
   - Check file permissions

3. **Application won't start**
   - Verify Python 3.8+ is installed
   - Check that all dependencies are installed in the virtual environment

4. **AI assistant is disabled**
   - Start your local OpenAI-compatible model server
   - Verify `LOCAL_OPENAI_BASE_URL` points to the correct local endpoint, typically `http://127.0.0.1:1234/v1`
   - Reinstall dependencies if `python-dotenv`, `requests`, or `openai` are missing: `pip install -r requirements.txt`

5. **LM Studio logs show `Unexpected endpoint or method`**
   - This usually means the server is receiving `/models` or `/chat/completions` instead of `/v1/models` or `/v1/chat/completions`
   - Set `LOCAL_OPENAI_BASE_URL=http://127.0.0.1:1234/v1` in `.env`
   - Restart the application after changing `.env`
   - The current code also auto-appends `/v1` when it is missing, but a restart is still required

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

**Note**: The app is fully usable as a local note manager today. The AI assistant depends on a running local OpenAI-compatible model server.
