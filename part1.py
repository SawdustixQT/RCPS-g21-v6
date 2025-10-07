import json

class Assembler:
    def __init__(self, input_file_name: str, output_file_name: str, is_test = False):
        self.input_file_name = input_file_name.strip('"')
        self.output_file = output_file_name
        self.is_test = is_test
        self.data = ""

    def read_json(self):
        try:
            with open(self.input_file_name, "r") as file:
                print("РЕЖИМ ТЕСТИРОВАНИЯ")
                self.data = json.load(file)
                file.close()
                print(f"Представление json файла в виде словаря:\n{self.data}")
        except FileNotFoundError:
            print("Файл не найден")

    def test(self):
        if self.is_test:
            print(self.load_const(10, 13, 508))
            print(self.read_value(37, 934, 14))
            print(self.write_value(83, 13, 6, 7))
            print(self.bin_op_leq(111, 6, 4))

    def fields(self, value: int, start: int, end: int):
        mask = (2 ** (end - start + 1) - 1)
        return (value & mask) << start

    def load_const(self, a: int, b: int, c: int):
        loaded_value = 0
        loaded_value |= self.fields(a, 0, 6)
        loaded_value |= self.fields(b, 7, 10)
        loaded_value |= self.fields(c, 11, 31)
        return loaded_value.to_bytes(length=4, byteorder="little")

    def read_value(self, a: int, b: int, c: int):
        cmd = 0
        cmd |= self.fields(a, 0, 6)
        cmd |= self.fields(b, 7, 31)
        cmd |= self.fields(c, 32, 35)
        return cmd.to_bytes(length=5, byteorder="little")

    def write_value(self, a: int, b: int, c: int, d: int):
        cmd = 0
        cmd |= self.fields(a, 0, 6)
        cmd |= self.fields(b, 7, 10)
        cmd |= self.fields(c, 11, 14)
        cmd |= self.fields(d, 15, 20)
        return cmd.to_bytes(length=3, byteorder="little")

    def bin_op_leq(self, a, b, c):  # Бинарная операция "<="
        cmd = 0
        cmd |= self.fields(a, 0, 6)
        cmd |= self.fields(b, 7, 10)
        cmd |= self.fields(c, 11, 14)
        return cmd.to_bytes(length=2, byteorder="little")


if __name__ == '__main__':
    inp_file = input("Введите путь к исходному файлу с текстом программы: ")
    output_file = input("Введите путь к двоичному файлу-результату: ")
    should_test = input("Собираетесь тестировать? (Да - Напишите что нибудь, Нет - ничего не пишите и нажмите enter): ")
    asm = Assembler(inp_file, output_file, bool(should_test))
    asm.read_json()

