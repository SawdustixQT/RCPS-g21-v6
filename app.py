import sys
import json
import subprocess
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QHBoxLayout, QPushButton, QTextEdit, QLineEdit,
                               QLabel, QFileDialog, QMessageBox, QFrame, QScrollArea)
from PySide6.QtCore import Qt, Slot
import os
from asm import bin_as_hex
import struct


class UvmApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Not So ASM")
        self.setGeometry(100, 100, 700, 700)
        self.data_to_dump = {}
        self.name = "test"
        self.filename = f"{self.name}.json"
        self.bin_filename = f"{self.name}.bin"
        self.dump = f"{self.name}_dump.json"

        self.init_ui()

    def rename(self, name):
        self.name = name
        self.filename = f"{self.name}.json"
        self.bin_filename = f"{self.name}.bin"
        self.dump = f"{self.name}_dump.json"


    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()

        # Окно для кода программы
        main_layout.addWidget(QLabel("<h2>Основной код программы</h2>"))

        self.editor = QTextEdit()
        self.editor.setPlaceholderText("Введите данные в формате JSON здесь...")

        initial_template = json.dumps({
            "program": {
                "name": "test",
                "architecture": "",
                "description": "",
                "instructions": [
                    {
                        "op": "LOAD",
                        "reg_addr": 13,
                        "const": 508
                    }
                ]
            }
        }, indent=4)
        self.editor.setText(initial_template)
        main_layout.addWidget(self.editor)

        # Панель кнопок
        button_layout = QHBoxLayout()

        save_json_button = QPushButton("Сохранить JSON")
        save_json_button.clicked.connect(self.create_json)
        button_layout.addWidget(save_json_button)

        save_bin_button = QPushButton("Создать BIN файл")
        save_bin_button.clicked.connect(self.create_bin_file)
        button_layout.addWidget(save_bin_button)

        run_button = QPushButton("Запустить программу")
        run_button.setStyleSheet("background-color: lightgreen; height: 30px;")
        run_button.clicked.connect(self.run_asm_py)
        button_layout.addWidget(run_button)

        main_layout.addLayout(button_layout)

        # Разделитель
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(line)

        # Панель для диапазона памяти
        memory_layout = QHBoxLayout()
        memory_layout.addWidget(QLabel("Диапазон памяти для дампа (-r аргумент):"))

        # Поле для начального адреса
        memory_layout.addWidget(QLabel("Старт:"))
        self.memory_start_edit = QLineEdit("0")
        self.memory_start_edit.setMaximumWidth(80)
        self.memory_start_edit.setToolTip("Начальный адрес памяти (десятичное число)")
        memory_layout.addWidget(self.memory_start_edit)

        memory_layout.addWidget(QLabel("Конец:"))
        self.memory_end_edit = QLineEdit("2048")
        self.memory_end_edit.setMaximumWidth(80)
        self.memory_end_edit.setToolTip("Конечный адрес памяти (десятичное число)")
        memory_layout.addWidget(self.memory_end_edit)

        memory_layout.addStretch()  # Добавляем растягивающееся пространство

        main_layout.addLayout(memory_layout)

        # Вывод бинарного файла
        main_layout.addWidget(QLabel("<h2>Шестнадцатеричный дамп бинарного файла</h2>"))

        self.bin_viewer = QTextEdit()
        self.bin_viewer.setReadOnly(True)
        self.bin_viewer.setMaximumHeight(100)  # Ограничиваем высоту до 2-3 строк
        self.bin_viewer.setPlaceholderText("Шестнадцатеричное представление бинарного файла...")
        self.bin_viewer.setStyleSheet("font-family: 'Courier New', monospace; font-size: 10pt;")

        main_layout.addWidget(self.bin_viewer)

        # Разделитель
        line2 = QFrame()
        line2.setFrameShape(QFrame.HLine)
        line2.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(line2)

        main_layout.addWidget(QLabel("<h2>Дамп памяти</h2>"))

        # Вывод дампа
        self.viewer = QTextEdit()
        self.viewer.setReadOnly(True)
        self.viewer.setPlaceholderText(f"Содержимое файла дампа отобразится здесь после сохранения...")
        main_layout.addWidget(self.viewer)

        central_widget.setLayout(main_layout)

        self.load_dump_file()
        # self.load_bin_file()

    @Slot()
    def create_json(self):
        pass

    @Slot()
    def create_bin_file(self):
        """Создает бинарный файл из JSON программы и отображает его шестнадцатеричный дамп."""
        try:
            program_data = json.loads(self.editor.toPlainText())
            name = program_data['program']['name']
            if name == '':
                QMessageBox.critical(self, '', 'Введите название файла')
            else:
                self.rename(name)

                with open(f'{name}.json', "w") as output_file:
                    json.dump(program_data, output_file, ensure_ascii=False, indent=4)
                try:
                    subprocess.run([sys.executable, "asm.py",
                                        "-i", f'{name}.json',
                                        "-o", f'{name}.bin',
                                        "-t", "True"],
                                     capture_output=True,  # захватываем stdout и stderr
                                     text=True,  # возвращаем строки, а не байты
                                     encoding='utf-8'
                                     )
                except subprocess.CalledProcessError as e:
                    QMessageBox.critical(self, "", f"Скрипт завершился с ошибкой: {e.returncode}")
                    QMessageBox.critical(self, "", f"Ошибка: {e.stderr}")

                self.load_bin_file(f'{name}.bin')
        except Exception as e:
            QMessageBox.critical(self, "Ошибка создания BIN", f"Не удалось создать бинарный файл: {e}")

    @Slot()
    def load_bin_file(self, bin_filename):
        """Загружает и отображает шестнадцатеричный дамп бинарного файла."""
        if os.path.exists(bin_filename):
            try:
                with open(bin_filename, 'rb') as f:
                    binary_data = f.read()

                # Формируем шестнадцатеричный дамп
                hex_dump = bin_as_hex(binary_data)
                self.bin_viewer.setText(hex_dump)

            except IOError:
                self.bin_viewer.setText(f"Не удалось прочитать файл {bin_filename}.")
        else:
            self.bin_viewer.setText(f"Бинарный файл пока не создан.")

    @Slot()
    def load_dump_file(self):
        """Загружает содержимое dump-файла в окно просмотра."""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.viewer.setText(content)
            except IOError:
                self.viewer.setText(f"Не удалось прочитать файл {self.filename}.")
        else:
            self.viewer.setText(f"Файл дампа пока не создан.")

    @Slot()
    def run_asm_py(self):
        """Имитирует запуск внешней программы с параметром имени файла."""
        if not os.path.exists(self.filename):
            QMessageBox.warning(self, "Ошибка запуска",
                                f"Файл {self.filename} не найден. Сначала сохраните данные.")
            return

        if not os.path.exists(self.bin_filename):
            QMessageBox.warning(self, "Ошибка запуска",
                                f"Бинарный файл {self.bin_filename} не найден. Сначала создайте бинарный файл.")
            return

        try:
            memory_start = int(self.memory_start_edit.text())
            memory_end = int(self.memory_end_edit.text())

            if memory_start < 0:
                QMessageBox.warning(self, "Ошибка", "Начальный адрес памяти не может быть отрицательным")
                return
            if memory_end <= memory_start:
                QMessageBox.warning(self, "Ошибка", "Конечный адрес памяти должен быть больше начального")
                return

            memory_range = f"{memory_start}-{memory_end}"

        except ValueError:
            QMessageBox.warning(self, "Ошибка", "некорректные значения диапазона памяти")
            return

        subprocess.run(
            [sys.executable, "asm_iter.py",
             "-i", self.bin_filename,
             "-o", self.filename,
             "-r", memory_range],
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        self.load_dump_file()



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = UvmApp()
    window.show()
    sys.exit(app.exec())