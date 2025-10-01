
def load_const(a: int, b:int, c:int):
    loaded_value = 0
    loaded_value |= a
    loaded_value |= (b << 7)
    loaded_value |= (c << 11)
    return loaded_value.to_bytes(length=4, byteorder="little")

def read_value(a: int, b: int, c: int):
    cmd = 0
    cmd |= a
    cmd |= (b << 7)
    cmd |= (c << 32)
    return cmd.to_bytes(length=5, byteorder="little")


def write_value(a: int, b: int, c: int, d: int):
    cmd = 0
    cmd |= a
    cmd |= b << 7
    cmd |= c << 11
    cmd |= d << 15
    return cmd.to_bytes(length=3, byteorder="little")


def bin_op_leq(a, b, c):
    cmd = 0
    cmd |= a
    cmd |= b << 7
    cmd |= c << 11
    return cmd.to_bytes(length=2, byteorder="little")

print(load_const(10, 13, 508))
print(list(read_value(37, 934, 14)))
print(write_value(83, 13, 6, 7))
print(list(bin_op_leq(111, 6, 4)))
"specifications"