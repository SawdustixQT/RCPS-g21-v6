import json
import argparse
from fontTools.varLib.instancer import parseArgs

def test():
    assert load(13, 508) == b'\x8a\xe6\x0f\x00'
    assert read(934, 14) == b'%\xd3\x01\x00\x0e'
    assert write(13, 6, 7) == b'\xd3\xb6\x03'
    assert bin_op(6, 4) == b'o#'
    print("Тестирование успешно пройдено")

def fields(value: int, start: int, end: int):
    mask = (2 ** (end - start + 1) - 1)
    return (value & mask) << start

def load(b: int, c: int):
    loaded_value = 0
    loaded_value |= 10
    loaded_value |= fields(b, 7, 10)
    loaded_value |= fields(c, 11, 31)
    return loaded_value.to_bytes(length=4, byteorder="little")

def read(b: int, c: int):
    cmd = 0
    cmd |= 37
    cmd |= fields(b, 7, 31)
    cmd |= fields(c, 32, 35)
    return cmd.to_bytes(length=5, byteorder="little")

def write(b: int, c: int, d: int):
    cmd = 0
    cmd |= 83
    cmd |= fields(b, 7, 10)
    cmd |= fields(c, 11, 14)
    cmd |= fields(d, 15, 20)
    return cmd.to_bytes(length=3, byteorder="little")

def bin_op(b, c):  # Бинарная операция "<="
    cmd = 0
    cmd |= 111
    cmd |= fields(b, 7, 10)
    cmd |= fields(c, 11, 14)
    return cmd.to_bytes(length=2, byteorder="little")

def validate_args(args):
    if args.i is None:
        print("Необходим входной файл программы")
        return args, False
    if args.o == "program.bin":
        return args, True
    if args.t is None:
        args.t = False
        return args, True
    return args, True

def asm_read_file(input_file_name):
    try:
        with open(input_file_name, "r") as file:
            # print("РЕЖИМ ТЕСТИРОВАНИЯ")
            data = json.load(file)
            file.close()
            # print(f"Представление json файла в виде словаря:\n{data}")
            return data['program']['instructions']
    except FileNotFoundError:
        print("Файл не найден")

def asm(cmd: dict):
    op = cmd['op']
    vals = cmd['values']
    return eval(op)(*vals)

def write_bin(program):
    # print(program)
    program_bin = b""
    for cmd in program:
        program_bin += asm(cmd)
    return program_bin

def main():
    parser = argparse.ArgumentParser(description="АСМ ИКБО-21-22 вариант 6")
    parser.add_argument("-i", help='Путь к входному файлу', type=str)
    parser.add_argument("-o", help="Путь выходного файла", type=str)
    parser.add_argument("-t", help="Режим тестирования (True)", type=bool, default=False)
    args = parser.parse_args()
    args, _ok = validate_args(args)
    if args.t:
        test()
        return
    program = asm_read_file(args.i)
    program_bin = write_bin(program)
    with open(args.o, "wb") as file:
        file.write(program_bin)
        file.close()
    print(f'Инструкции программы: {program}')
    print(f'Бинарный файл программы: {program_bin}')


main()


