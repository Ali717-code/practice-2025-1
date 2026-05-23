# Вариативная часть: Python Text Editor

## Тема задания

**Python: Create a Simple Python Text Editor**  
Источник: [Build Your Own X — codecrafters-io/build-your-own-x](https://github.com/codecrafters-io/build-your-own-x)

---

## Пошаговое руководство по созданию редактора

### Шаг 1. Создание главного окна

Первый шаг — создать основной класс, наследующий от `tk.Tk`, и настроить главное окно:

```python
import tkinter as tk

class TextEditor(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Python Text Editor")
        self.geometry("950x650")
        self.current_file = None
        self.is_modified = False
```

**Что происходит:**
- `super().__init__()` — создаёт главное окно приложения
- `geometry("950x650")` — задаёт начальный размер окна в пикселях
- Атрибуты `current_file` и `is_modified` хранят состояние документа

---

### Шаг 2. Добавление текстовой области

Центральный элемент редактора — виджет `Text` с полосой прокрутки:

```python
def _build_editor(self):
    frame = tk.Frame(self)
    frame.pack(fill=tk.BOTH, expand=True)

    scrollbar = tk.Scrollbar(frame, orient=tk.VERTICAL)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    self.text_area = tk.Text(
        frame,
        font=("Consolas", 12),
        wrap=tk.WORD,
        undo=True,          # включить историю отмены
        autoseparators=True,
        yscrollcommand=scrollbar.set,
    )
    self.text_area.pack(fill=tk.BOTH, expand=True)
    scrollbar.config(command=self.text_area.yview)
```

**Ключевые параметры `tk.Text`:**
| Параметр | Значение | Назначение |
|----------|----------|-----------|
| `undo=True` | True | Включает историю Ctrl+Z |
| `wrap=tk.WORD` | WORD | Перенос по словам |
| `font` | ("Consolas", 12) | Моноширинный шрифт |

---

### Шаг 3. Меню приложения

Строка меню создаётся через класс `tk.Menu`:

```python
def _build_menu(self):
    menubar = tk.Menu(self)

    # Меню "Файл"
    file_menu = tk.Menu(menubar, tearoff=False)
    file_menu.add_command(label="Открыть...  Ctrl+O", command=self.open_file)
    file_menu.add_command(label="Сохранить   Ctrl+S", command=self.save_file)
    file_menu.add_separator()
    file_menu.add_command(label="Выход", command=self._on_close)
    menubar.add_cascade(label="Файл", menu=file_menu)

    self.config(menu=menubar)
```

---

### Шаг 4. Работа с файлами

Открытие файла через стандартный диалог:

```python
from tkinter import filedialog

def open_file(self):
    path = filedialog.askopenfilename(
        filetypes=[("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")]
    )
    if path:
        with open(path, "r", encoding="utf-8") as f:
            self.text_area.delete("1.0", tk.END)
            self.text_area.insert(tk.END, f.read())
        self.current_file = path
```

**Формат индексов в `tk.Text`:**
- `"1.0"` — строка 1, символ 0 (начало документа)
- `tk.END` — конец документа
- `"insert"` — текущая позиция курсора

---

### Шаг 5. Функция поиска с подсветкой

Поиск использует теги виджета `Text` для подсветки:

```python
def find_text(self):
    from tkinter import simpledialog
    query = simpledialog.askstring("Поиск", "Найти:")
    if not query:
        return

    # Убрать старую подсветку
    self.text_area.tag_remove("found", "1.0", tk.END)

    # Найти и подсветить все вхождения
    start = "1.0"
    while True:
        pos = self.text_area.search(query, start, stopindex=tk.END, nocase=True)
        if not pos:
            break
        end = f"{pos}+{len(query)}c"
        self.text_area.tag_add("found", pos, end)
        start = end

    # Настроить цвет подсветки
    self.text_area.tag_config("found", background="#ffd43b", foreground="#000")
```

---

### Шаг 6. Смена темы

Темы хранятся в словаре и применяются через `configure()`:

```python
THEMES = {
    "dark":  {"bg": "#1e1e1e", "fg": "#d4d4d4", "insert": "#aeafad"},
    "light": {"bg": "#ffffff", "fg": "#1e1e1e", "insert": "#000000"},
}

def _apply_theme(self):
    theme = self.THEMES[self.current_theme]
    self.text_area.config(
        bg=theme["bg"],
        fg=theme["fg"],
        insertbackground=theme["insert"],
    )
```

---

### Шаг 7. Строка состояния

Нижняя панель обновляется при каждом нажатии клавиши:

```python
def _build_statusbar(self):
    self.statusbar = tk.Label(self, anchor=tk.W, padx=10, pady=4)
    self.statusbar.pack(side=tk.BOTTOM, fill=tk.X)

def _update_statusbar(self):
    content = self.text_area.get("1.0", tk.END)
    lines = int(self.text_area.index(tk.END).split(".")[0]) - 1
    words = len(content.split())
    chars = len(content) - 1
    self.statusbar.config(
        text=f"  Строки: {lines}  |  Слова: {words}  |  Символы: {chars}"
    )
```

---

### Шаг 8. Горячие клавиши

```python
def _bind_shortcuts(self):
    self.bind("<Control-n>", lambda e: self.new_file())
    self.bind("<Control-o>", lambda e: self.open_file())
    self.bind("<Control-s>", lambda e: self.save_file())
    self.bind("<Control-f>", lambda e: self.find_text())
    self.text_area.bind("<KeyRelease>", lambda e: self._update_statusbar())
```

---

### Шаг 9. Запуск приложения

```python
# main.py
from editor import TextEditor

if __name__ == "__main__":
    app = TextEditor()
    app.mainloop()  # главный цикл событий
```

---

## Архитектурная схема

```
┌─────────────────────────────────────────────────────────┐
│                    TextEditor (tk.Tk)                   │
├──────────────┬──────────────┬──────────────┬────────────┤
│   _build_    │   _build_    │   _build_    │  _bind_    │
│   menu()     │   editor()   │  statusbar() │ shortcuts()│
├──────────────┴──────────────┴──────────────┴────────────┤
│                    Файловые операции                     │
│  new_file()  open_file()  save_file()  save_as()        │
├─────────────────────────────────────────────────────────┤
│                   Редактирование                         │
│  _undo()  _redo()  _cut()  _copy()  _paste()            │
├─────────────────────────────────────────────────────────┤
│                    Поиск / Темы                          │
│  find_text()   _apply_theme()   _switch_theme()         │
└─────────────────────────────────────────────────────────┘

Состояние приложения:
  current_file: str | None  ← путь к открытому файлу
  is_modified: bool          ← есть ли несохранённые изменения
  current_theme: str         ← "dark" или "light"
```

---

## Внешние ресурсы по теме

| Ресурс | Описание | Ссылка |
|--------|----------|--------|
| Документация Tkinter | Официальная документация Python | https://docs.python.org/3/library/tkinter.html |
| Tkinter Text Widget | Подробное описание виджета Text | https://docs.python.org/3/library/tkinter.ttk.html |
| Real Python: Tkinter | Полный учебный курс | https://realpython.com/python-gui-tkinter/ |
| Build Your Own X | Коллекция проектов | https://github.com/codecrafters-io/build-your-own-x |
| doka.guide | Справочник по веб-технологиям | https://doka.guide/ |

---

## Результат работы

После выполнения всех шагов получается текстовый редактор со следующими характеристиками:

- **Строк кода:** ~300 (editor.py) + ~15 (main.py)
- **Зависимости:** только стандартная библиотека Python (0 pip install)
- **Платформы:** Windows, macOS, Linux
- **Python:** 3.10+

### Описание работающего приложения

При запуске `python main.py` открывается окно редактора с:
- Тёмной темой оформления (фон `#1e1e1e`, текст `#d4d4d4`)
- Шрифтом Consolas 12pt в текстовой области
- Строкой меню: Файл | Правка | Вид | О программе
- Строкой состояния внизу с счётчиками

Фотографии интерфейса приложения размещены в папке `site/images/`.

---

## Ссылка на исходный код в репозитории

**GitHub:** https://github.com/Ali717-code/practice-2025-1/tree/master/src

Документация к коду: [src/README.md](../src/README.md)
