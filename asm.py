import json
import argparse
import os.path


def bin_as_hex(bin_str: bin):
    return  ', '.join(f'0x{byte:02X}' for byte in bin_str)

def test(program, program_bin):
    print(f'Результат ассемблирования в байтовом формате: {bin_as_hex(program_bin)}')
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
    if ".bin" in args.o:
        return args, True
    if args.t is None:
        args.t = False
        return args, True
    return args, True

def asm_read_file(input_file_name):
    try:
        with open(input_file_name, "r") as file:
            data = json.load(file)
            file.close()
            return data['program']['instructions']
    except FileNotFoundError:
        print("Файл не найден")
        raise FileNotFoundError("Файл не найден")

def asm(commands: list):
    """ Внутреннее представление """
    res = []
    for cmd in commands:
        op = cmd['op']
        if op == 'LOAD':
            res.append((10, cmd['reg_addr'], cmd['const']))
        elif op == "READ":
            res.append((37, cmd['mem_addr'], cmd['reg_addr']))
        elif op == "WRITE":
            res.append((83, cmd['base_reg_addr'], cmd['reg_addr'], cmd['offset']))
        elif op == "BIN_OP":
            res.append((111, cmd['base_reg_addr'], cmd['acc_reg_addr']))
    return res

def encode(not_so_bytes: tuple):
    op = not_so_bytes[0]
    vals = not_so_bytes[1:]
    match op:
        case 10:
            return load(*vals)
        case 37:
            return read(*vals)
        case 83:
            return write(*vals)
        case 111:
            return bin_op(*vals)


def assemble(ir):
    """ Преобразование программы в двоичное представление """
    val = bytearray()
    for en in ir:
        val.extend(encode(en))
    return val

def main():
    parser = argparse.ArgumentParser(description="АСМ ИКБО-21-22 вариант 6")
    parser.add_argument("-i", help='Путь к входному файлу', type=str)
    parser.add_argument("-o", help="Путь выходного файла", type=str)
    parser.add_argument("-t", help="Режим тестирования (True)", type=bool, default=False)
    args = parser.parse_args()
    args, _ok = validate_args(args)

    program = asm_read_file(args.i)

    asm_program = asm(program)
    program_bin = assemble(asm_program)

    # Запись ассемблирования в двоичный выходной файл
    with open(args.o, "wb") as file:
        file.write(program_bin)
        file.close()

    if args.t:
        test(program, program_bin)
    print(f'Инструкции программы: {program}')
    # Размер двоичного файла в байтах
    print(f'Размер бинарного файла программы: {os.path.getsize(args.o)} байт')

if __name__ == '__main__':
    main()

