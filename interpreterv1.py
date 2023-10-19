from intbase import *
from brewparse import parse_program


class Interpreter(InterpreterBase):
    def __init__(self, console_output=True, inp=None, trace_output=False):
        super().__init__(console_output, inp)

        self.debug = trace_output

    def run(self, program):
        ast = parse_program(program)
        self.var_to_val = {}
        root_node = ast.functions[0]
    

