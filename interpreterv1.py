from intbase import *
from brewparse import parse_program


class Interpreter(InterpreterBase):
    def __init__(self, console_output=True, inp=None, trace_output=False):
        super().__init__(console_output, inp)
        self.debug = trace_output

    def main_check(self, ast):
        for func in ast.dict['functions']:
            if func.dict['name'] == "main":
                self.main = func
                return True
        super().error(
                ErrorType.NAME_ERROR,
                "No main() function was found",
            )
        
    def get_var(self, name):
        if name not in self.var_to_val:
            super().error(
                ErrorType.NAME_ERROR,
                f"Variable {name} has not been defined",
            )
        else:
            return self.var_to_val[name]
    
    def set_var(self, name, val):
        self.var_to_val[name] = val
        
    def parse_args(self, args):
        parsed = []
        for arg in args:
            if arg.elem_type == '+' or arg.elem_type == '-' or arg.elem_type == 'fcall':
                parsed.append(self.execute_expression(arg))
            elif arg.elem_type == 'var':
                parsed.append(self.get_var(arg.get('name')))
            else:
                parsed.append(arg.get('val'))
        return parsed

    def brew_print(self, args):
        output = ""
        for arg in args:
            output += str(arg)
        super().output(output)
        return
    
    def brew_input(self, args):
        if len(args) > 1:
            super().error(
                ErrorType.NAME_ERROR,
                f"No inputi() function found that takes > 1 parameter",
            )
            return
        elif len(args) == 1:
            super().output(args)
            user_input = int(super().get_input())
            return user_input
        else:
            user_input = int(super().get_input())
            return user_input

    def call_function(self, name, args):
        #THIS IS A BAD WAY TO CALL FUNCTIONS
        #TODO: FIX
        parsed = self.parse_args(args)
        if name == 'print':
            self.brew_print(parsed)
            return
        elif name == 'inputi':
            return self.brew_input(parsed)
        else:
            super().error(
                ErrorType.NAME_ERROR,
                f"Function {name} has not been defined",
            )

    def execute_function(self, func):
        for statement in func.dict['statements']:
            self.execute_statement(statement) 

    def subtract(self, op1, op2):
        if type(op1) == type(op2):
            return op1 - op2
        else:
            super().error(
                ErrorType.TYPE_ERROR,
                "Incompatible types for arithmetic operation",
            )
    
    def add(self, op1, op2):
        if type(op1) == type(op2):
            return op1 + op2
        else:
            super().error(
                ErrorType.TYPE_ERROR,
                "Incompatible types for arithmetic operation",
            )

    def execute_expression(self, expr):
        if expr.elem_type == '+' or expr.elem_type == '-':
            operator = None
            if expr.elem_type == '+':
                operator = self.add
            else:
                operator = self.subtract
            op1, op2 = None, None
            if expr.dict['op1'].elem_type == 'int' or expr.dict['op1'].elem_type == 'string':
                op1 = expr.dict['op1'].dict['val']
            elif expr.dict['op1'].elem_type == 'var':
                op1 = self.get_var(expr.dict['op1'].dict['name'])
            else:
                op1 = self.execute_expression(expr.dict['op1'])
            
            if expr.dict['op2'].elem_type == 'int' or expr.dict['op2'].elem_type == 'string':
                op2 = expr.dict['op2'].dict['val']
            elif expr.dict['op2'].elem_type == 'var':
                op2 = self.get_var(expr.dict['op2'].dict['name'])
            else:
                op2 = self.execute_expression(expr.dict['op2'])
            
            return operator(op1, op2)
        #For some reason this is only going to be the inputi function
        else:
            if expr.get('name') != 'inputi':
                super().error(
                    ErrorType.FAULT_ERROR,
                    "You can't call anything but inputi from an expression",
                )
            #TODO: process args first before passing? not anymore since I have the parse args function?
            return self.call_function(expr.get('name'), expr.get('args'))

            

    def execute_assignment(self, assn):
        if assn.dict['expression'].elem_type == '+' or assn.dict['expression'].elem_type == '-' or assn.dict['expression'].elem_type == 'fcall':
            self.set_var(assn.get('name'), self.execute_expression(assn.dict['expression']))
            return 
        if assn.dict['expression'].elem_type == 'var':
            self.set_var(assn.dict['name'], self.get_var(assn.dict['expression'].dict['name']))
            return
        if assn.dict['expression'].elem_type == 'int' or assn.dict['expression'].elem_type == 'string':
            self.set_var(assn.dict['name'], assn.dict['expression'].dict['val'])
            return


    def execute_statement(self, statement):
        if statement.elem_type == '=':
            return self.execute_assignment(statement)
            #not sure if I should return anything?
        elif statement.elem_type == 'fcall':
            return self.call_function(statement.get('name'), statement.get('args'))

    def run(self, program):
        ast = parse_program(program)
        self.var_to_val = {}
        if not self.main_check(ast):
            return
        #This is only because we have one function called main
        return self.execute_function(self.main)


    
def main():
    program = """func main() {
             x = 4 + inputi("enter a number: ");
             print("The sum is: ", x);
          }"""
    interpreter = Interpreter()
    interpreter.run(program)

if __name__ == '__main__':
    main()