import copy
import dis
import sys
from io import BytesIO
from itertools import *

import benchbase
from benchbase import (with_attributes, with_text, onlylib,
                       serialized, children, nochange)

TEXT = "some ASCII text"
UTEXT = u"some klingon: \uF8D2"


############################################################
# Benchmarks
############################################################

class BenchMark(benchbase.TreeBenchMark):

    def bench_create_subelements(self, root):
        global __rewrite__
        SubElement = self.etree.SubElement
        sum = 0
        for r in range(300):
            __rewrite__ = True
            for child in root:
                SubElement(child, '{test}test')
                sum = len(child) + sum
            __rewrite__ = False

        # print(sum)


def writeinst(opc: str, arg: int = 0):
    "Makes life easier in writing python bytecode"
    nb = max(1, -(-arg.bit_length() // 8))
    ab = arg.to_bytes(nb, sys.byteorder)
    ext_arg = dis._all_opmap['EXTENDED_ARG']
    inst = bytearray()
    for i in range(nb - 1):
        inst.append(ext_arg)
        inst.append(ab[i])
    inst.append(dis._all_opmap[opc])
    inst.append(ab[-1])

    return bytes(inst)

def patch(patches):
    code = dis.Bytecode(BenchMark.bench_create_subelements, show_caches=True)
    bytelist = []
    for instr in code:
        name = instr.opname
        arg = instr.arg
        if instr.offset in patches:
            patch = patches[instr.offset]
            name = patch[0]
            if patch[1] is not None:
                arg = patch[1]

        if arg is None:
            arg = 0
        bytelist.append(writeinst(name, arg))

    bytes = b"".join(bytelist)

    orig = BenchMark.bench_create_subelements.__code__
    BenchMark.bench_create_subelements.__code__ = orig.replace(co_code=bytes, co_consts=orig.co_consts, co_names=orig.co_names,
                                                          co_flags=orig.co_flags)

if __name__ == '__main__':
    # print("===== BEFORE PATCH =====")
    # dis.dis(BenchMark.bench_create_subelements, show_caches=True)
    # patch({
    #     86: ("LXML_FOR_ITER", None),
    #     90: ("LXML_STORE_FAST", None),
    #     92: ("NOP", None),
    #     94: ("NOP", None),
    #     96: ("LXML_LOAD_FAST", None),
    #     100: ("LXML_SUBELEMENT", None),
    #     108: ("LXML_POP_TOP", None),
    #     110: ("LXML_LEN", None),
    #     120: ("NOP", None), # will be skipped
    #     122: ("NOP", None),  # will be skipped
    # })
    # print("===== AFTER PATCH =====")
    # dis.dis(BenchMark.bench_create_subelements, show_caches=True)

    benchbase.main(BenchMark)


#  21           0 RESUME                   0
#
#  23           2 LOAD_FAST                0 (self)
#               4 LOAD_ATTR                0 (etree)
#              24 LOAD_ATTR                2 (SubElement)
#              44 STORE_FAST               2 (SubElement)
#
#  24          46 LOAD_CONST               1 (0)
#              48 STORE_FAST               3 (sum)
#
#  25          50 LOAD_GLOBAL              5 (NULL + range)
#              60 LOAD_CONST               2 (100)
#              62 CALL                     1
#              70 GET_ITER
#         >>   72 FOR_ITER                36 (to 148)
#              76 STORE_FAST               4 (r)
#
#  26          78 LOAD_CONST               3 (True)
#              80 STORE_GLOBAL             3 (__rewrite__)
#
#  27          82 LOAD_FAST                1 (root)
#              84 GET_ITER
#         >>   86 FOR_ITER                25 (to 140)
#              90 STORE_FAST               5 (child)
#
#  28          92 PUSH_NULL
#              94 LOAD_FAST                2 (SubElement)
#              96 LOAD_FAST                5 (child)
#              98 LOAD_CONST               4 ('{test}test')
#             100 CALL                     2
#             108 POP_TOP
#
#  29         110 LOAD_GLOBAL              9 (NULL + len)
#             120 LOAD_FAST                5 (child)
#             122 CALL                     1
#             130 LOAD_FAST                3 (sum)
#             132 BINARY_OP                0 (+)
#             136 STORE_FAST               3 (sum)
#             138 JUMP_BACKWARD           27 (to 86)
#
#  27     >>  140 END_FOR
#
#  30         142 LOAD_CONST               5 (False)
#             144 STORE_GLOBAL             3 (__rewrite__)
#             146 JUMP_BACKWARD           38 (to 72)
#
#  25     >>  148 END_FOR
#
#  32         150 LOAD_GLOBAL             11 (NULL + print)
#             160 LOAD_FAST                3 (sum)
#             162 CALL                     1
#             170 POP_TOP
#             172 RETURN_CONST             0 (None)