"""
Python Text Editor
==================
Простой текстовый редактор на Python с использованием библиотеки Tkinter.

Автор: Жамолдинов Жасурбек Иброимжонович
Практика: Проектная практика 2026
Университет: Московский Политехнический Университет
"""

import os
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog


class TextEditor(tk.Tk):
    """
    Основной класс текстового редактора.

    Наследует от tk.Tk и инкапсулирует весь интерфейс и логику приложения.
    Поддерживает открытие, редактирование и сохранение текстовых файлов,
    поиск по тексту, смену темы и горячие клавиши.
    """

    # Доступные темы оформления
    THEMES = {
        "dark": {
            "bg": "#1e1e1e",
            "fg": "#d4d4d4",
            "select_bg": "#264f78",
            "insert": "#aeafad",
            "statusbar_bg": "#252526",
            "statusbar_fg": "#858585",
        },
        "light": {
            "bg": "#ffffff",
            "fg": "#1e1e1e",
            "select_bg": "#add8e6",
            "insert": "#000000",
            "statusbar_bg": "#f3f3f3",
            "statusbar_fg": "#555555",
        },
    }

    def __init__(self):
        """Инициализация главного окна и всех компонентов редактора."""
        super().__init__()

        self.title("Python Text Editor")
        self.geometry("950x650")
        self.minsize(600, 400)

        # Состояние приложения
        self.current_file: str | None = None
        self.is_modified: bool = False
        self.current_theme: str = "dark"

        # Построение интерфейса
        self._build_menu()
        self._build_editor()
        self._build_statusbar()
        self._bind_shortcuts()

        # Применить начальную тему
        self._apply_theme()

        # Обработчик закрытия окна
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # ─────────────────────────────────────────────
    # Построение интерфейса
    # ─────────────────────────────────────────────

    def _build_menu(self) -> None:
        """Создание строки меню с разделами Файл, Правка, Вид, О программе."""
        menubar = tk.Menu(self)

        # ── Файл ──
        file_menu = tk.Menu(menubar, tearoff=False)
        file_menu.add_command(label="Новый         Ctrl+N", command=self.new_file)
        file_menu.add_command(label="Открыть...    Ctrl+O", command=self.open_file)
        file_menu.add_separator()
        file_menu.add_command(label="Сохранить     Ctrl+S", command=self.save_file)
        file_menu.add_command(label="Сохранить как... Ctrl+Shift+S", command=self.save_as)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self._on_close)
        menubar.add_cascade(label="Файл", menu=file_menu)

        # ── Правка ──
        edit_menu = tk.Menu(menubar, tearoff=False)
        edit_menu.add_command(label="Отменить     Ctrl+Z", command=self._undo)
        edit_menu.add_command(label="Повторить    Ctrl+Y", command=self._redo)
        edit_menu.add_separator()
        edit_menu.add_command(label="Вырезать     Ctrl+X", command=self._cut)
        edit_menu.add_command(label="Копировать   Ctrl+C", command=self._copy)
        edit_menu.add_command(label="Вставить     Ctrl+V", command=self._paste)
        edit_menu.add_separator()
        edit_menu.add_command(label="Выделить всё  Ctrl+A", command=self._select_all)
        edit_menu.add_separator()
        edit_menu.add_command(label="Найти...     Ctrl+F", command=self.find_text)
        menubar.add_cascade(label="Правка", menu=edit_menu)

        # ── Вид ──
        view_menu = tk.Menu(menubar, tearoff=False)
        view_menu.add_command(label="Тёмная тема",  command=lambda: self._switch_theme("dark"))
        view_menu.add_command(label="Светлая тема", command=lambda: self._switch_theme("light"))
        menubar.add_cascade(label="Вид", menu=view_menu)

        # ── О программе ──
        menubar.add_command(label="О программе", command=self._show_about)

        self.config(menu=menubar)

    def _build_editor(self) -> None:
        """Создание основной текстовой области с вертикальной прокруткой."""
        frame = tk.Frame(self)
        frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(frame, orient=tk.VERTICAL)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.text_area = tk.Text(
            frame,
            font=("Consolas", 12),
            wrap=tk.WORD,
            undo=True,
            autoseparators=True,
            maxundo=-1,
            yscrollcommand=scrollbar.set,
            padx=8,
            pady=6,
        )
        self.text_area.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.text_area.yview)

        # Отслеживать изменения для флага «изменён»
        self.text_area.bind("<<Modified>>", self._on_text_modified)

    def _build_statusbar(self) -> None:
        """Создание строки состояния внизу окна."""
        self.statusbar = tk.Label(
            self,
            text="Готово  |  Строки: 1  |  Слова: 0  |  Символы: 0",
            anchor=tk.W,
            padx=10,
            pady=4,
            font=("Segoe UI", 9),
        )
        self.statusbar.pack(side=tk.BOTTOM, fill=tk.X)

    def _bind_shortcuts(self) -> None:
        """Назначение горячих клавиш."""
        self.bind("<Control-n>", lambda e: self.new_file())
        self.bind("<Control-o>", lambda e: self.open_file())
        self.bind("<Control-s>", lambda e: self.save_file())
        self.bind("<Control-S>", lambda e: self.save_as())
        self.bind("<Control-f>", lambda e: self.find_text())
        self.bind("<Control-a>", lambda e: self._select_all())
        # Обновление строки состояния при каждом нажатии клавиши
        self.text_area.bind("<KeyRelease>", lambda e: self._update_statusbar())

    # ─────────────────────────────────────────────
    # Операции с файлами
    # ─────────────────────────────────────────────

    def new_file(self) -> None:
        """Создать новый пустой документ. При наличии изменений запросить подтверждение."""
        if not self._confirm_discard():
            return
        self.text_area.delete("1.0", tk.END)
        self.current_file = None
        self.is_modified = False
        self.title("Python Text Editor — Новый файл")
        self._update_statusbar()

    def open_file(self) -> None:
        """Открыть файл через диалог выбора файла."""
        if not self._confirm_discard():
            return
        path = filedialog.askopenfilename(
            title="Открыть файл",
            filetypes=[
                ("Текстовые файлы", "*.txt"),
                ("Python файлы", "*.py"),
                ("Markdown файлы", "*.md"),
                ("Все файлы", "*.*"),
            ],
        )
        if path:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                self.text_area.delete("1.0", tk.END)
                self.text_area.insert(tk.END, content)
                self.text_area.edit_reset()  # сбросить историю undo
                self.current_file = path
                self.is_modified = False
                self.title(f"Python Text Editor — {os.path.basename(path)}")
                self._update_statusbar()
            except Exception as exc:
                messagebox.showerror("Ошибка", f"Не удалось открыть файл:\n{exc}")

    def save_file(self) -> None:
        """Сохранить текущий файл. Если файл новый — вызвать «Сохранить как»."""
        if self.current_file:
            self._write_file(self.current_file)
        else:
            self.save_as()

    def save_as(self) -> None:
        """Сохранить файл с новым именем через диалог."""
        path = filedialog.asksaveasfilename(
            title="Сохранить как",
            defaultextension=".txt",
            filetypes=[
                ("Текстовые файлы", "*.txt"),
                ("Python файлы", "*.py"),
                ("Markdown файлы", "*.md"),
                ("Все файлы", "*.*"),
            ],
        )
        if path:
            self.current_file = path
            self._write_file(path)

    def _write_file(self, path: str) -> None:
        """Записать содержимое текстовой области в файл по заданному пути."""
        try:
            content = self.text_area.get("1.0", tk.END)
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            self.is_modified = False
            self.title(f"Python Text Editor — {os.path.basename(path)}")
        except Exception as exc:
            messagebox.showerror("Ошибка", f"Не удалось сохранить файл:\n{exc}")

    # ─────────────────────────────────────────────
    # Операции редактирования
    # ─────────────────────────────────────────────

    def _undo(self) -> None:
        """Отменить последнее действие."""
        try:
            self.text_area.edit_undo()
        except tk.TclError:
            pass  # нечего отменять

    def _redo(self) -> None:
        """Повторить отменённое действие."""
        try:
            self.text_area.edit_redo()
        except tk.TclError:
            pass  # нечего повторять

    def _cut(self) -> None:
        """Вырезать выделенный текст в буфер обмена."""
        self.text_area.event_generate("<<Cut>>")

    def _copy(self) -> None:
        """Копировать выделенный текст в буфер обмена."""
        self.text_area.event_generate("<<Copy>>")

    def _paste(self) -> None:
        """Вставить текст из буфера обмена."""
        self.text_area.event_generate("<<Paste>>")

    def _select_all(self) -> None:
        """Выделить весь текст в документе."""
        self.text_area.tag_add(tk.SEL, "1.0", tk.END)
        self.text_area.mark_set(tk.INSERT, "1.0")
        self.text_area.see(tk.INSERT)

    # ─────────────────────────────────────────────
    # Поиск
    # ─────────────────────────────────────────────

    def find_text(self) -> None:
        """Открыть диалог поиска и подсветить все вхождения в тексте."""
        query = simpledialog.askstring("Поиск", "Найти:", parent=self)
        if not query:
            return

        # Снять предыдущую подсветку
        self.text_area.tag_remove("found", "1.0", tk.END)

        count = 0
        start = "1.0"
        while True:
            pos = self.text_area.search(query, start, stopindex=tk.END, nocase=True)
            if not pos:
                break
            end = f"{pos}+{len(query)}c"
            self.text_area.tag_add("found", pos, end)
            start = end
            count += 1

        if count:
            self.text_area.tag_config("found", background="#ffd43b", foreground="#000000")
            self.statusbar.config(text=f"Найдено: {count} совпадени{'е' if count == 1 else 'я' if 2 <= count <= 4 else 'й'}")
        else:
            messagebox.showinfo("Поиск", f"Текст «{query}» не найден.")

    # ─────────────────────────────────────────────
    # Темы оформления
    # ─────────────────────────────────────────────

    def _switch_theme(self, theme_name: str) -> None:
        """Переключить тему оформления редактора."""
        self.current_theme = theme_name
        self._apply_theme()

    def _apply_theme(self) -> None:
        """Применить текущую тему ко всем виджетам."""
        theme = self.THEMES[self.current_theme]
        self.text_area.config(
            bg=theme["bg"],
            fg=theme["fg"],
            selectbackground=theme["select_bg"],
            insertbackground=theme["insert"],
        )
        self.statusbar.config(
            bg=theme["statusbar_bg"],
            fg=theme["statusbar_fg"],
        )
        self.configure(bg=theme["bg"])

    # ─────────────────────────────────────────────
    # Строка состояния и служебные методы
    # ─────────────────────────────────────────────

    def _update_statusbar(self) -> None:
        """Обновить счётчики строк, слов и символов в строке состояния."""
        content = self.text_area.get("1.0", tk.END)
        lines = int(self.text_area.index(tk.END).split(".")[0]) - 1
        words = len(content.split())
        chars = len(content) - 1  # -1 убирает автоматический символ \n
        self.statusbar.config(
            text=f"  Строки: {lines}  |  Слова: {words}  |  Символы: {chars}"
        )

    def _on_text_modified(self, _event=None) -> None:
        """Обработчик события изменения содержимого текстовой области."""
        if self.text_area.edit_modified():
            self.is_modified = True
            self.text_area.edit_modified(False)
            self._update_statusbar()

    def _confirm_discard(self) -> bool:
        """
        Спросить пользователя о сохранении, если есть несохранённые изменения.

        Returns:
            True  — если можно продолжить (пользователь согласился или изменений нет).
            False — если пользователь отменил операцию.
        """
        if not self.is_modified:
            return True
        answer = messagebox.askyesnocancel(
            "Несохранённые изменения",
            "Документ изменён. Сохранить перед выходом?",
        )
        if answer is None:   # Cancel
            return False
        if answer:           # Yes
            self.save_file()
        return True          # No — продолжить без сохранения

    def _on_close(self) -> None:
        """Обработчик нажатия кнопки закрытия окна."""
        if self._confirm_discard():
            self.destroy()

    def _show_about(self) -> None:
        """Показать диалоговое окно «О программе»."""
        messagebox.showinfo(
            "О программе",
            "Python Text Editor v1.0\n\n"
            "Автор: Жамолдинов Жасурбек Иброимжонович\n"
            "Язык: Python 3.x\n"
            "Библиотека GUI: Tkinter\n\n"
            "Проектная практика 2026\n"
            "Московский Политехнический Университет",
        )
