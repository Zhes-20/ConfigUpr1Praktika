"""Graphical user interface for the shell emulator using Tkinter."""

import tkinter as tk
from tkinter import font
from typing import Callable, Optional

from src.shell_core import ShellCore


class ShellGui:
    """Tkinter-based GUI window for interactive terminal emulation."""

    def __init__(
        self,
        shell: ShellCore,
        on_exit: Optional[Callable[[], None]] = None,
    ) -> None:
        """Initialize main window, widgets and bind keyboard events."""
        self.shell = shell
        self.on_exit = on_exit
        self.history: list[str] = []
        self.history_index = -1

        self.root = tk.Tk()
        self.root.title(self.shell.get_title())
        self.root.geometry("860x540")
        self.root.minsize(600, 360)
        self.root.configure(bg="#181818")

        self.term_font = font.Font(family="Courier", size=13)
        self._build_widgets()
        self._show_welcome()

    def _build_widgets(self) -> None:
        """Create and place console text display and input frame."""
        input_frame = tk.Frame(self.root, bg="#181818")
        input_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

        self.prompt_label = tk.Label(
            input_frame,
            text=self.shell.get_prompt(),
            bg="#181818",
            fg="#50fa7b",
            font=self.term_font,
        )
        self.prompt_label.pack(side=tk.LEFT)

        self.entry = tk.Entry(
            input_frame,
            bg="#282a36",
            fg="#f8f8f2",
            insertbackground="#ffffff",
            font=self.term_font,
            relief=tk.SOLID,
            borderwidth=1,
        )
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(8, 0))
        self.entry.focus_set()
        self.entry.bind("<Return>", self._handle_return)
        self.entry.bind("<Up>", self._handle_history_up)
        self.entry.bind("<Down>", self._handle_history_down)

        self._build_text_area()

    def _build_text_area(self) -> None:
        """Create scrollable text area for terminal output."""
        text_frame = tk.Frame(self.root, bg="#181818")
        text_frame.pack(
            side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=(10, 0)
        )

        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.text_area = tk.Text(
            text_frame,
            bg="#181818",
            fg="#f8f8f2",
            insertbackground="#ffffff",
            font=self.term_font,
            wrap=tk.WORD,
            yscrollcommand=scrollbar.set,
            relief=tk.FLAT,
            state=tk.DISABLED,
        )
        self.text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.text_area.yview)

    def _show_welcome(self) -> None:
        """Display startup message in console widget."""
        self.write_output(
            "Эмулятор командной строки UNIX (Этап 1: REPL)\n"
            "Доступные команды: ls (заглушка), cd (заглушка), exit\n\n"
        )

    def write_output(self, text: str) -> None:
        """Append text to the console display widget."""
        self.text_area.configure(state=tk.NORMAL)
        self.text_area.insert(tk.END, text)
        self.text_area.see(tk.END)
        self.text_area.configure(state=tk.DISABLED)

    def _update_prompt(self) -> None:
        """Update prompt label to reflect current shell working path."""
        self.prompt_label.configure(text=self.shell.get_prompt())

    def _handle_return(self, _event: tk.Event) -> None:
        """Process entered command line upon pressing Enter."""
        command = self.entry.get()
        self.entry.delete(0, tk.END)
        if command.strip():
            self.history.append(command)
            self.history_index = len(self.history)

        prompt_str = self.shell.get_prompt()
        self.write_output(f"{prompt_str}{command}\n")

        code, out = self.shell.execute_line(command)
        if out:
            self.write_output(f"{out}\n")

        self._update_prompt()
        if self.shell.is_exit:
            self.root.after(300, self.root.destroy)

    def _handle_history_up(self, _event: tk.Event) -> None:
        """Navigate backward in command history."""
        if self.history and self.history_index > 0:
            self.history_index -= 1
            self.entry.delete(0, tk.END)
            self.entry.insert(0, self.history[self.history_index])

    def _handle_history_down(self, _event: tk.Event) -> None:
        """Navigate forward in command history."""
        if self.history and self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.entry.delete(0, tk.END)
            self.entry.insert(0, self.history[self.history_index])
        elif self.history_index >= len(self.history) - 1:
            self.history_index = len(self.history)
            self.entry.delete(0, tk.END)

    def run(self) -> None:
        """Start the Tkinter event loop."""
        self.root.mainloop()
