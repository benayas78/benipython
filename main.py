import sys
import os
import shutil
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

try:
    from PIL import Image, ImageTk
except Exception:
    message = (
        "Pillow is required to run this program.\n\n"
        "Install it with:\n\n    pip install pillow\n\n"
        "Then restart this app."
    )
    # If tkinter not yet initialized, create a small dialog
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror("Missing Dependency", message)
    sys.exit(1)


APP_TITLE = "CHATAPP BENAYAS COMMUNITY CHATAPP"
DESCRIPTION = (
    "Connect with your friends and community instantly. "
    "Download the ChatApp setup for Windows and start chatting today!"
)

HERE = Path(__file__).parent.resolve()
BACKGROUND_FILENAME = HERE / "beni1.jpg"
SETUP_FILENAME = HERE / "ChatAppSetup.exe"


class ChatAppInstallerGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        # Fix minimum size
        self.minsize(640, 420)

        # Remove default window icon on some systems; keep it simple
        # self.iconbitmap('icon.ico')  # optional

        # Build UI
        self._create_widgets()
        self._place_widgets()
        self._style_widgets()
        self.bind("<Configure>", self._on_resize)

    def _create_widgets(self):
        # Canvas to draw background image
        self.canvas = tk.Canvas(self, highlightthickness=0)
        self.bg_image = None  # will hold PhotoImage
        # Overlay frame for text/buttons (transparent background simulated)
        self.overlay = tk.Frame(self.canvas, bg="", padx=20, pady=20)

        # Title label
        self.title_label = tk.Label(
            self.overlay,
            text=APP_TITLE,
            font=("Segoe UI", 22, "bold"),
            fg="white",
            bg="",  # background will be transparent by using the canvas
            wraplength=900,
            justify="center",
        )

        # Description label
        self.desc_label = tk.Label(
            self.overlay,
            text=DESCRIPTION,
            font=("Segoe UI", 12),
            fg="white",
            bg="",
            wraplength=900,
            justify="center",
        )

        # Download button (ttk style)
        self.download_btn = ttk.Button(
            self.overlay, text="Download Setup", command=self._on_download
        )

    def _place_widgets(self):
        self.canvas.pack(fill="both", expand=True)
        # create window on the canvas to hold overlay frame
        self.canvas_window = self.canvas.create_window(
            0, 0, anchor="nw", window=self.overlay
        )
        # pack contents inside overlay
        self.title_label.pack(pady=(20, 10))
        self.desc_label.pack(pady=(0, 20))
        self.download_btn.pack(pady=(0, 20))

        # Footer
        footer_text = "\u00A9 2025 BENAYAS LEULSEGED. All Rights Reserved."
        self.footer_label = tk.Label(
            self.canvas, text=footer_text, font=("Segoe UI", 9), fg="#f0f0f0", bg=""
        )
        self.footer_window = self.canvas.create_window(
            10, 10, anchor="sw", window=self.footer_label
        )

        # initial load of background
        self._load_background_image()

    def _style_widgets(self):
        style = ttk.Style(self)
        # On some platforms the default theme doesn't accept customizations; try 'clam' as fallback
        try:
            style.theme_use("clam")
        except Exception:
            pass

        style.configure(
            "TButton",
            font=("Segoe UI", 12, "bold"),
            padding=(10, 8),
        )

    def _load_background_image(self):
        if not BACKGROUND_FILENAME.exists():
            # Fill with a neutral color and warn
            self.canvas.configure(bg="#2b2b2b")
            messagebox.showwarning(
                "Background not found",
                f"Background image not found:\n{BACKGROUND_FILENAME}\n\n"
                "Place beni1.jpg beside this script to show the background.",
            )
            return

        # Load original image (do not create PhotoImage until we know desired size)
        self._orig_pil_bg = Image.open(BACKGROUND_FILENAME).convert("RGBA")
        self._update_background_photoimage()

    def _update_background_photoimage(self):
        # Determine size of the canvas to scale image
        w = max(self.winfo_width(), 640)
        h = max(self.winfo_height(), 420)
        # maintain aspect ratio, cover-style (like background-size: cover)
        img = self._orig_pil_bg
        img_ratio = img.width / img.height
        target_ratio = w / h

        if img_ratio > target_ratio:
            # image is wider relative to target -> fit height, crop width
            scale = h / img.height
        else:
            # fit width, crop height
            scale = w / img.width

        new_size = (int(img.width * scale), int(img.height * scale))
        resized = img.resize(new_size, Image.LANCZOS)

        # center-crop to (w, h)
        left = (resized.width - w) // 2
        top = (resized.height - h) // 2
        cropped = resized.crop((left, top, left + w, top + h))

        self.bg_image = ImageTk.PhotoImage(cropped)
        # set canvas background
        self.canvas.create_image(0, 0, image=self.bg_image, anchor="nw")
        # move overlay window to center
        self.canvas.coords(self.canvas_window, w // 2, h // 2)
        self.canvas.itemconfig(self.canvas_window, anchor="center")
        # footer bottom-left
        self.canvas.coords(self.footer_window, 12, h - 12)
        self.canvas.itemconfig(self.footer_window, anchor="sw")

    def _on_resize(self, event):
        # update background on resize (throttle not implemented — small windows are fine)
        if hasattr(self, "_orig_pil_bg"):
            self._update_background_photoimage()

        # update overlay width to be a fraction of window width for good wraplength
        overlay_width = min(max(self.winfo_width() - 80, 300), 1000)
        self.overlay.configure(width=overlay_width)
        self.title_label.configure(wraplength=overlay_width - 40)
        self.desc_label.configure(wraplength=overlay_width - 60)

    def _on_download(self):
        # Check setup file exists
        if not SETUP_FILENAME.exists():
            messagebox.showerror(
                "Setup Missing",
                f"Could not find the setup file:\n{SETUP_FILENAME}\n\n"
                "Make sure ChatAppSetup.exe is in the same folder as this script.",
            )
            return

        # Ask where to save
        initial_name = "ChatAppSetup.exe"
        save_path = filedialog.asksaveasfilename(
            defaultextension=".exe",
            filetypes=[("Windows Executable", "*.exe"), ("All Files", "*.*")],
            initialfile=initial_name,
            title="Save ChatApp Setup As",
        )
        if not save_path:
            return  # user cancelled

        try:
            # copy the file
            shutil.copy2(SETUP_FILENAME, save_path)
        except Exception as e:
            messagebox.showerror("Copy Failed", f"Failed to copy the setup:\n{e}")
            return

        messagebox.showinfo(
            "Download Complete", f"ChatApp setup has been saved to:\n{save_path}"
        )


def main():
    app = ChatAppInstallerGUI()
    # center on screen
    app.update_idletasks()
    w = app.winfo_width()
    h = app.winfo_height()
    screen_w = app.winfo_screenwidth()
    screen_h = app.winfo_screenheight()
    x = (screen_w // 2) - (w // 2)
    y = (screen_h // 2) - (h // 2)
    app.geometry(f"{max(w,800)}x{max(h,520)}+{x}+{y}")
    app.mainloop()


if __name__ == "__main__":
    main()

