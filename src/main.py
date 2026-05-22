"""
Точка входа в приложение Python Text Editor.

Запуск:
    python main.py

Требования:
    - Python 3.10+
    - tkinter (входит в стандартную поставку Python)
"""

from editor import TextEditor


def main() -> None:
    """Создать и запустить экземпляр текстового редактора."""
    app = TextEditor()
    app.mainloop()


if __name__ == "__main__":
    main()
