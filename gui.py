import customtkinter as ctk
import threading
import sys
import os
from tkinter import filedialog
import locale

# Import auto_editor main entry point
try:
    import auto_editor.__main__ as ae_main
except ImportError:
    ae_main = None

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

# --- Translations ---
TRANSLATIONS = {
    "en": {
        "title": "Auto-Editor GUI",
        "appearance": "Appearance Mode:",
        "file_placeholder": "Select video file...",
        "browse": "Browse",
        "margin": "Margin (sec):",
        "export": "Export Format:",
        "run": "Run Auto-Editor",
        "error_file": "Error: Please select a file first.\n",
        "running": "Running Auto-Editor...\n",
        "finished": "\nProcess finished.\n",
        "error_import": "Error: auto-editor module not found. Please install it via pip.\n",
        "lang_switch": "Switch to Japanese",
    },
    "ja": {
        "title": "Auto-Editor GUI",
        "appearance": "外観モード:",
        "file_placeholder": "動画ファイルを選択...",
        "browse": "参照",
        "margin": "マージン (秒):",
        "export": "出力形式:",
        "run": "Auto-Editorを実行",
        "error_file": "エラー: ファイルを選択してください。\n",
        "running": "Auto-Editorを実行中...\n",
        "finished": "\n処理が完了しました。\n",
        "error_import": "エラー: auto-editorモジュールが見つかりません。pipでインストールしてください。\n",
        "lang_switch": "Switch to English",
    }
}

class OutputRedirector:
    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.encoding = 'utf-8' # Dummy for compatibility

    def write(self, str):
        self.text_widget.configure(state="normal")
        self.text_widget.insert("end", str)
        self.text_widget.see("end")
        self.text_widget.configure(state="disabled")
    
    def flush(self):
        pass

class AutoEditorApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Detect system language
        sys_lang = locale.getdefaultlocale()[0]
        self.lang = "ja" if sys_lang and sys_lang.startswith("ja") else "en"

        self.title(self.tr("title"))
        self.geometry("700x500")

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)

        # --- Sidebar ---
        self.sidebar_frame = ctk.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="Auto-Editor", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.appearance_mode_label = ctk.CTkLabel(self.sidebar_frame, text=self.tr("appearance"), anchor="w")
        self.appearance_mode_label.grid(row=5, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = ctk.CTkOptionMenu(self.sidebar_frame, values=["System", "Light", "Dark"],
                                                               command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=6, column=0, padx=20, pady=(10, 10))
        
        self.lang_button = ctk.CTkButton(self.sidebar_frame, text=self.tr("lang_switch"), command=self.toggle_language)
        self.lang_button.grid(row=7, column=0, padx=20, pady=(10, 20))

        # --- Main Content ---
        
        # File Selection
        self.file_path = ctk.StringVar()
        
        self.file_frame = ctk.CTkFrame(self)
        self.file_frame.grid(row=0, column=1, padx=20, pady=20, sticky="ew")
        self.file_frame.grid_columnconfigure(0, weight=1)

        self.entry_file = ctk.CTkEntry(self.file_frame, textvariable=self.file_path, placeholder_text=self.tr("file_placeholder"))
        self.entry_file.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.btn_browse = ctk.CTkButton(self.file_frame, text=self.tr("browse"), command=self.browse_file)
        self.btn_browse.grid(row=0, column=1, padx=10, pady=10)

        # Options
        self.options_frame = ctk.CTkFrame(self)
        self.options_frame.grid(row=1, column=1, padx=20, pady=(0, 20), sticky="nsew")
        
        # Margin
        self.label_margin = ctk.CTkLabel(self.options_frame, text=self.tr("margin"))
        self.label_margin.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.entry_margin = ctk.CTkEntry(self.options_frame, placeholder_text="0.2")
        self.entry_margin.insert(0, "0.2")
        self.entry_margin.grid(row=0, column=1, padx=10, pady=10, sticky="w")

        # Export Format
        self.label_export = ctk.CTkLabel(self.options_frame, text=self.tr("export"))
        self.label_export.grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.option_export = ctk.CTkOptionMenu(self.options_frame, values=["default", "premiere", "resolve", "final-cut-pro", "shotcut", "kdenlive", "clip-sequence"])
        self.option_export.grid(row=1, column=1, padx=10, pady=10, sticky="w")
        
        self.options_frame.grid_columnconfigure(1, weight=1)

        # Run Button
        self.btn_run = ctk.CTkButton(self, text=self.tr("run"), command=self.run_auto_editor, height=40)
        self.btn_run.grid(row=2, column=1, padx=20, pady=(0, 20), sticky="ew")

        # Output Log
        self.textbox = ctk.CTkTextbox(self, width=250)
        self.textbox.grid(row=3, column=1, padx=20, pady=(0, 20), sticky="nsew")
        self.textbox.configure(state="disabled")
        self.grid_rowconfigure(3, weight=1)

    def tr(self, key):
        return TRANSLATIONS[self.lang].get(key, key)

    def toggle_language(self):
        self.lang = "ja" if self.lang == "en" else "en"
        self.update_ui_text()

    def update_ui_text(self):
        self.title(self.tr("title"))
        self.appearance_mode_label.configure(text=self.tr("appearance"))
        self.entry_file.configure(placeholder_text=self.tr("file_placeholder"))
        self.btn_browse.configure(text=self.tr("browse"))
        self.label_margin.configure(text=self.tr("margin"))
        self.label_export.configure(text=self.tr("export"))
        self.btn_run.configure(text=self.tr("run"))
        self.lang_button.configure(text=self.tr("lang_switch"))

    def change_appearance_mode_event(self, new_appearance_mode: str):
        ctk.set_appearance_mode(new_appearance_mode)

    def browse_file(self):
        filename = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4 *.mov *.mkv *.avi"), ("All files", "*.*")])
        if filename:
            self.file_path.set(filename)

    def run_auto_editor(self):
        file_path = self.file_path.get()
        if not file_path:
            self.log(self.tr("error_file"))
            return

        margin = self.entry_margin.get()
        export_format = self.option_export.get()
        
        args = [file_path]
        
        if margin:
            try:
                float(margin)
                margin += "sec"
            except ValueError:
                pass
            args.extend(["--margin", margin])
        
        if export_format != "default":
             args.extend(["--export", export_format])

        self.log(self.tr("running"))
        self.btn_run.configure(state="disabled")
        
        thread = threading.Thread(target=self.execute_internal, args=(args,))
        thread.start()

    def execute_internal(self, args):
        if ae_main is None:
            self.log(self.tr("error_import"))
            self.btn_run.configure(state="normal")
            return

        # Capture stdout/stderr
        original_stdout = sys.stdout
        original_stderr = sys.stderr
        original_argv = sys.argv

        sys.stdout = OutputRedirector(self.textbox)
        sys.stderr = OutputRedirector(self.textbox)
        sys.argv = ["auto-editor"] + args

        try:
            ae_main.main()
        except SystemExit as e:
            self.log(f"\nExit code: {e.code}\n")
        except Exception as e:
            self.log(f"\nError: {str(e)}\n")
        finally:
            sys.stdout = original_stdout
            sys.stderr = original_stderr
            sys.argv = original_argv
            self.log(self.tr("finished"))
            self.btn_run.configure(state="normal")

    def log(self, message):
        self.textbox.configure(state="normal")
        self.textbox.insert("end", message)
        self.textbox.see("end")
        self.textbox.configure(state="disabled")

if __name__ == "__main__":
    app = AutoEditorApp()
    app.mainloop()
