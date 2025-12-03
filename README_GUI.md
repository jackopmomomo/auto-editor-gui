# Auto-Editor GUI

A modern GUI wrapper for [Auto-Editor](https://github.com/WyattBlue/auto-editor), built with Python and CustomTkinter.

## Features

-   **User-Friendly Interface**: Easy to use GUI for common Auto-Editor tasks.
-   **Multi-language Support**: English and Japanese support.
-   **Portable**: Can be built into a standalone executable that works without Python installed.
-   **Cross-Platform**: Works on Windows, macOS, and Linux (requires building on the target OS).

## Installation

1.  Clone the repository.
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

Run the script directly:
```bash
python gui.py
```

## Building Standalone Executable

To build a standalone executable (EXE) that includes Auto-Editor:

```bash
pyinstaller --noconfirm --onefile --windowed --collect-all customtkinter --collect-all auto_editor gui.py
```

The executable will be located in the `dist` folder.
