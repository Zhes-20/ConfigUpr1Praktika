import os
import tkinter as tk
from tkinter import font
from typing import Callable, Optional

from src.shell_core import ShellCore

SCRIPT_STEP_DELAY_MS = 200
EXIT_DELAY_MS = 300


class ShellGui:
    def __init__(
        self,
        shell: ShellCore,
        on_exit: Optional[Callable[[], None]] = None,
    ) -> None:
        self.shell = shell
        self.on_exit = on_exit
        self.history: list[str] = []
        self.history_index = -1
        self.script_lines: list[str] = []

        self.root = tk.Tk()
        self.root.title(self.shell.get_title())
        self.root.geometry("860x540")
        self.root.minsize(600, 360)
        self.root.configure(bg="#181818")

        self.term_font = font.Font(family="Courier", size=13)
        self._build_widgets()
        self._show_welcome_banner()
        self._check_and_run_script()

    def _build_widgets(self) -> None:
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

    def _show_welcome_banner(self) -> None:
        banner = self.shell.config.dump_debug_info()
        self.write_output(f"{banner}\n")
        if self.shell.vfs_error:
            self.write_output(
                f"[ERROR] Ошибка загрузки VFS: {self.shell.vfs_error}\n"
            )
        elif self.shell.config.vfs_path:
            self.write_output("[DEBUG] Загруженная структура VFS:\n")
            for node_line in self.shell.vfs.dump_structure():
                self.write_output(f"  {node_line}\n")
        self.write_output("\nДобро пожаловать в эмулятор!\n\n")

    def _enable_user_input(self) -> None:
        self.entry.configure(state=tk.NORMAL)
        self.entry.focus_set()

    def _check_and_run_script(self) -> None:
        script_path = self.shell.config.script_path
        if not script_path:
            return

        self.entry.configure(state=tk.DISABLED)
        if not os.path.exists(script_path):
            self.write_output(
                f"[ERROR] Стартовый скрипт не найден: {script_path}\n"
            )
            self._enable_user_input()
            return

        try:
            with open(script_path, "r", encoding="utf-8") as file_handle:
                self.script_lines = [
                    line.rstrip("\r\n") for line in file_handle
                ]
            self.root.after(SCRIPT_STEP_DELAY_MS, self._run_next_script_line)
        except OSError as err:
            self.write_output(
                f"[ERROR] Ошибка чтения стартового скрипта: {err}\n"
            )
            self._enable_user_input()

    def _run_next_script_line(self) -> None:
        if not self.script_lines:
            self._enable_user_input()
            return

        line = self.script_lines.pop(0)
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            if stripped.startswith("#"):
                self.write_output(f"{stripped}\n")
            self.root.after(SCRIPT_STEP_DELAY_MS, self._run_next_script_line)
            return

        prompt_str = self.shell.get_prompt()
        self.write_output(f"{prompt_str}{line}\n")
        code, out = self.shell.execute_line(line)
        if out:
            self.write_output(f"{out}\n")

        self._update_prompt()
        if code != 0:
            self.write_output(
                f"[SCRIPT ERROR] Скрипт остановлен из-за ошибки (код {code})\n"
            )
            self._enable_user_input()
            return

        if self.shell.is_exit:
            self.root.after(EXIT_DELAY_MS, self.root.destroy)
            return

        self.root.after(SCRIPT_STEP_DELAY_MS, self._run_next_script_line)

    def write_output(self, text: str) -> None:
        self.text_area.configure(state=tk.NORMAL)
        self.text_area.insert(tk.END, text)
        self.text_area.see(tk.END)
        self.text_area.configure(state=tk.DISABLED)

    def _update_prompt(self) -> None:
        self.prompt_label.configure(text=self.shell.get_prompt())

    def _handle_return(self, _event: tk.Event) -> None:
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
            self.root.after(EXIT_DELAY_MS, self.root.destroy)

    def _handle_history_up(self, _event: tk.Event) -> None:
        if self.history and self.history_index > 0:
            self.history_index -= 1
            self.entry.delete(0, tk.END)
            self.entry.insert(0, self.history[self.history_index])

    def _handle_history_down(self, _event: tk.Event) -> None:
        if self.history and self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.entry.delete(0, tk.END)
            self.entry.insert(0, self.history[self.history_index])
        elif self.history_index >= len(self.history) - 1:
            self.history_index = len(self.history)
            self.entry.delete(0, tk.END)

    def run(self) -> None:
        self.root.mainloop()
