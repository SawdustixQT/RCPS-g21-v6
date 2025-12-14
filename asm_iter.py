import json
import argparse
import os.path
from sys import byteorder


def mask(n):
    return (2 ** n) - 1

CMD_SIZE = {10: 4, 37: 5, 83: 3, 111: 2}

def bin_as_hex(bin_str: bin):
    return  ', '.join(f'{bin(byte)}' for byte in bin_str)

def execute_asm(bytecode, memory_size=1024):
    global CMD_SIZE
    mem_cmd = list(bytecode)
    mem_data = [0] * memory_size
    registers = [0] * 32

    pc = 0
    program_end = len(mem_cmd)
    while pc < program_end:
        opcode = mem_cmd[pc] & mask(7)
        size = CMD_SIZE[opcode]
        cmd = int.from_bytes(mem_cmd[pc:pc + size], byteorder='little')
        # print(opcode, cmd)
        if opcode == 10: # write
            b = (cmd >> 7) & mask(4)
            c = (cmd >> 11) & mask(21)
            registers[b] = c
        elif opcode == 37: # read
            b = (cmd >> 7) & mask(25)
            c = (cmd >> 32) & mask(4)
            registers[c] = mem_data[b]
        elif opcode == 83: # write
            b = (cmd >> 7) & mask(4)
            c = (cmd >> 11) & mask(4)
            d = (cmd >> 15) & mask(5)
            addr = registers[b] + d
            mem_data[addr] = registers[c]
        elif opcode == 111: # <=
            b = (cmd >> 7) & mask(4)
            c = (cmd >> 11) & mask(4)
            addr = registers[b]
            registers[c] = registers[c] <= mem_data[addr]

        size = CMD_SIZE[opcode]
        pc += size
    return mem_data, registers

def mem_validate_args(args):
    if None in (args.i, args.o):
        print("Ошибка при передаче аргументов")
        return args, False
    if ".json" not in args.o:
        print("Файл дампа должен быть формата json")
        return args, False
    return args, True

def dump_memory(output_file, mem, start, end):
    with open(output_file, "w") as file:
        mem_dump = {"dump": []}
        for addr in range(start, end):
            row_dump = {}
            row_dump["address"] = addr
            row_dump["value"] = mem[addr]
            mem_dump['dump'].append(row_dump)

        json.dump(mem_dump, file, ensure_ascii=False, indent=4)


def main():
    parser = argparse.ArgumentParser(description="АСМ Интерпретатор ИКБО-21-22 вариант 6")
    parser.add_argument("-i", help='Путь к бинарному файлу', type=str)
    parser.add_argument("-o", help="Путь к дампу файла", type=str)
    parser.add_argument("-r", help="Диапазон пямяти (в формате start-end)", type=str)
    args = parser.parse_args()
    args, ok = mem_validate_args(args)

    if not ok:
        print("Ошибка при вводе аргументов")
        return

    # Чтение байтовой строки
    with open(args.i, 'rb') as f:
        bytes_list = f.read()

    if args.r is not None:
        start, end = map(int, str(args.r).split('-'))
        mem, reg = execute_asm(bytes_list, memory_size=end-start)
        mem_range = f'[{start}-{end}]'
        dump_memory(args.o, mem, start, end)
    else:
        execute_asm(bytes_list)
        mem_range = ''
    # print([i for i in mem if i != 0])

    print(f"Выполнено. Дамп памяти {mem_range} сохранён в {args.o}")



if __name__ == '__main__':
    main()
