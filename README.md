# Py-Drop (formerly EdgeDrop)

Py-Drop is a sleek, minimal, and fully native Python-based clipboard manager and drop shelf for Windows. It acts as a sliding edge-activated shelf that intelligently stores and organizes everything you copy or drag into it. 

*(Inspired by the original Edge-Drop concept, rebuilt from the ground up in Python and PyQt6 for maximum performance and native Windows integration).*

Whether it's text, images, files, or folders, Py-Drop helps you keep your temporary files and clipboard items organized without cluttering your desktop.

## ✨ Features

- **Edge Activation:** Hover your mouse at the edge of your screen (left or right) to reveal the shelf automatically.
- **Drag & Drop Workflow:** Seamlessly drag items from other applications into Py-Drop, or drag items out of Py-Drop to drop them into other applications (like WhatsApp, Word, VSCode, etc).
- **Clipboard Monitoring:** Automatically captures what you copy, intelligently categorizing it (Colors, URLs, Text, Files, and Images).
- **Stacking:** Keep your shelf clean! You can drag items on top of each other to "Stack" them into a group. To unstack, simply open the group and drag the item outside.
- **Translucent & Frameless UI:** Beautifully crafted with PyQt6, featuring a modern dark theme and an optional translucent background blur.
- **Global Hotkey:** Don't want to use edge hover? Call Py-Drop instantly using a customizable global hotkey (default: `Ctrl+Alt+V`).
- **Data Persistence:** Your items are saved locally in the `data/` directory and will persist across reboots.

## 🚀 Installation & Usage

Py-Drop uses no external heavyweight dependencies other than PyQt6.

### Prerequisites
- Windows 10/11
- Python 3.9+

### Setup

1. Clone this repository or download the folder.
2. Install the required PyQt6 library:
   ```bash
   pip install PyQt6
   ```
3. Run the application:
   ```bash
   python main.py
   ```

## ⚙️ Configuration

You can tweak the behavior of Py-Drop directly within the app by clicking the **Settings** (gear) icon in the header:
- **Enable Sound Haptics:** Play subtle sound effects on dragging, copying, and deleting.
- **Translucent Background:** Toggle the acrylic blur effect.
- **Edge Side:** Choose whether the shelf slides out from the left or right edge of your screen.
- **Trigger Width:** Adjust how sensitive the edge activation is (in pixels).
- **Shelf Width:** Adjust the visual width of the shelf.
- **Global Hotkey:** Click and record your custom hotkey combination.

## 🛠️ Tech Stack

- **Python 3**
- **PyQt6** for the graphical interface and drag-and-drop orchestration.
- **ctypes / user32** for the low-level Windows global hotkey hooks and cursor edge detection.

## 📂 Architecture

- `src/ui/shelf.py`: Handles the main UI, animations, drop zones, and component rendering.
- `src/core/clipboard.py`: Monitors the system clipboard for new items.
- `src/core/cursor.py`: Tracks mouse position to trigger edge activations.
- `src/core/storage.py`: Manages saving and loading the items from disk.
- `src/core/hotkey.py`: Manages the global Windows hotkey hook.

## 📝 License
This project is licensed under the GPL-3.0 License. See the [LICENSE](LICENSE) file for more details.
