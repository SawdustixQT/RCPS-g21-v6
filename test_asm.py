import asm

def test():
    print("\n")
    assert asm.load(13, 508) == b'\x8a\xe6\x0f\x00'
    assert asm.read(934, 14) == b'%\xd3\x01\x00\x0e'
    assert asm.write(13, 6, 7) == b'\xd3\xb6\x03'
    assert asm.bin_op(6, 4) == b'o#'
