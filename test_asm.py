from asm import Assembler

def test():
    asm_sequel = Assembler("example.json", output_file_name="example.bin")
    print("\n")
    assert asm_sequel.load_const(10, 13, 508) == b'\x8a\xe6\x0f\x00'
    assert asm_sequel.read_value(37, 934, 14) == b'%\xd3\x01\x00\x0e'
    assert asm_sequel.write_value(83, 13, 6, 7) == b'\xd3\xb6\x03'
    assert asm_sequel.bin_op_leq(111, 6, 4) == b'o#'
