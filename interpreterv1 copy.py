from intbase import *
from brewparse import parse_program
from env_v1 import *
import copy

class Interpreter(InterpreterBase):
    
    #Initialize the base class with the flag for debug
    def __init__(self, console_output=True, inp=None, trace_output=False):
        super().__init__(console_output, inp)
        self.debug = trace_output
        self.bin_ops = {'+', '-', '*', '/','==', '<', '<=', '>', '>=', '!=', '||', '&&'}
        self.un_ops = {'neg', '!'}
        self.val_types = {'int', 'string', 'bool', 'nil'}

    # Run a program
    def run(self, program):
        self.ast = parse_program(program)
        self.env = EnvironmentManager()
        self.var_to_val = {}
        if not self.main_check(self.ast):
            return
        #This is only because we have one function called main
        return self.execute_function(self.main)

    # Given an AST:
    # Check if the main function exists
    def main_check(self, ast):
        for func in ast.dict['functions']:
            if func.dict['name'] == "main":
                self.main = func
                return True
        super().error(
                ErrorType.NAME_ERROR,
                "No main() function was found",
            )
        
    # Get the value of a variable if it exists
    def get_var(self, name):
        if name not in self.var_to_val:
            super().error(
                ErrorType.NAME_ERROR,
                f"Variable {name} has not been defined",
            )
        else:
            return self.var_to_val[name]
    
    # Set a variable
    def set_var(self, name, val):
        self.var_to_val[name] = val
        
    # Given a list of arguments, process all of them if they can be processed
    def parse_args(self, args):
        parsed = []
        for arg in args:
            if arg.elem_type in self.bin_ops or arg.elem_type in self.un_ops or arg.elem_type == 'fcall':
                parsed.append(self.execute_expression(arg))
            elif arg.elem_type == 'var':
                parsed.append(self.get_var(arg.get('name')))
            else:
                parsed.append(arg.get('val'))
        return parsed

    #The bool converter because casing
    def bool_converter(self, thing):
        if thing:
            return "true"
        return "false"

    # The implementation of the print() function
    def brew_print(self, args):
        output = ""
        for arg in args:
            if(type(arg) == bool):
                arg = self.bool_convert(arg)
            output += str(arg)
        super().output(output)
        return
    
    # The implementation of inputi()
    def brew_input(self, args):
        if len(args) > 1:
            super().error(
                ErrorType.NAME_ERROR,
                f"No inputi() function found that takes > 1 parameter",
            )
            return
        elif len(args) == 1:
            super().output(args[0])
            user_input = int(super().get_input())
            return user_input
        else:
            user_input = int(super().get_input())
            return user_input

    #overload check
    def overload_check(self, name, num_args):
        ast_temp = self.ast.get('functions')
        for ast_func in ast_temp:
            if ast_func.get('name') == name and len(ast_func.get('args')) == num_args:
                return ast_func
        super().error(
            ErrorType.NAME_ERROR,
            f"Function {name} has not been defined",
        )
    
    #function check
    def function_check(self, name):
        ast_func = self.ast.get('functions')
        for func in ast_func:
            if func.get('name') == name:
                return True
        return False

    # Function for handling brewin function calls
    def call_function(self, name, args):
        parsed = self.parse_args(args)
        if name == 'print':
            self.brew_print(parsed)
            return
        elif name == 'inputi':
            return self.brew_input(parsed)
        elif self.function_check(name):
            func = self.overload_check(name, len(args))
            #should add the arguments to the master list of vars here
            for i in range(len(args)):
                self.set_var(func.get('args')[i].get('name'), parsed[i])
            #TODO FUNCTION THINGS HERE AND SCOPING
            self.execute_function(func)
            pass
        else:
            super().error(
                ErrorType.NAME_ERROR,
                f"Function {name} has not been defined",
            )

    # Execute a function node
    def execute_function(self, func):
        for statement in func.dict['statements']:
            self.execute_statement(statement) 

    # The subtraction operator
    def subtract(self, op1, op2):
        self.arith_check(op1, op2)
        if type(op1) == type(op2):
            return op1 - op2
        else:
            super().error(
                ErrorType.TYPE_ERROR,
                "Incompatible types for arithmetic operation",
            )
    
    # The addition operator
    def add(self, op1, op2):
        self.arith_check(op1, op2)
        if type(op1) == type(op2):
            return op1 + op2
        else:
            super().error(
                ErrorType.TYPE_ERROR,
                "Incompatible types for arithmetic operation",
            )

    # The multiplication operator
    def mult(self, op1, op2):
        self.arith_check(op1, op2)
        if type(op1) == type(op2):
            return op1 * op2
        else:
            super().error(
                ErrorType.TYPE_ERROR,
                "Incompatible types for arithmetic operation",
            )

    # The division operator
    def div(self, op1, op2):
        self.arith_check(op1, op2)
        if type(op1) == type(op2):
            return op1 // op2
        else:
            super().error(
                ErrorType.TYPE_ERROR,
                "Incompatible types for arithmetic operation",
            )
    
    # The arithmetic type check
    def arith_check(self, op1, op2):
        if type(op1) == int and type(op2) == int:
            return True
        else:
            return False
    
    # The unary negation operator
    def arith_neg(self, op1):
        if type(op1) == int:
            return op1 * -1
        else:
            super().error(
                ErrorType.TYPE_ERROR,
                "Incompatible types for arithmetic operation",
            )

    #The boolean negation
    def bool_neg(self, op1):
        if type(op1) == bool:
            return not op1
        else:
            super().error(
                ErrorType.TYPE_ERROR,
                "Incompatible types for logical operation",
            )
    
    #The string type checker
    def string_check(self, op1, op2):
        if type(op1) == str and type(op2) == str:
            return True
        else:
            return False

    # The bool checker
    def bool_checker(self, op1, op2):
        if type(op1) == bool and type(op2) == bool:
            return True
        else:
            return False
        
    # or operator
    def lor(self, op1, op2):
        if self.bool_checker(op1, op2):
            return op1 or op2
        else:
            super().error(
                ErrorType.TYPE_ERROR,
                "Incompatible types for boolean operation",
            )

    # and operator
    def land(self, op1, op2):
        if self.bool_checker(op1, op2):
            return op1 and op2
        else:
            super().error(
                ErrorType.TYPE_ERROR,
                "Incompatible types for boolean operation",
            )

    # The < operator
    def less_than(self, op1, op2):
        if self.arith_check(op1, op2):
            return op1 < op2
        else:
            super().error(
                ErrorType.TYPE_ERROR,
                "Incompatible types for arithmetic comparison",
            )
    
    # The > operator
    def greater_than(self, op1, op2):
        if self.arith_check(op1, op2):
            return op1 > op2
        else:
            super().error(
                ErrorType.TYPE_ERROR,
                "Incompatible types for arithmetic comparison",
            )

    # The <= operator
    def leq(self, op1, op2):
        if self.arith_check(op1, op2):
            return op1 <= op2
        else:
            super().error(
                ErrorType.TYPE_ERROR,
                "Incompatible types for arithmetic comparison",
            )

    # The >= operator
    def geq(self, op1, op2):
        if self.arith_check(op1, op2):
            return op1 >= op2
        else:
            super().error(
                ErrorType.TYPE_ERROR,
                "Incompatible types for arithmetic comparison",
            )



    
    # Execute an expression
    def execute_expression(self, expr):
        # handling variables
        if expr.elem_type == 'var':
            return self.get_var(expr.get('name'))
        # handling constants
        if expr.elem_type in self.val_types:
            return expr.get('val')
        # taking care of the binary operations
        if expr.elem_type in self.bin_ops:
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
            
            operator = None
            e_type = expr.elem_type
            if e_type == '+':
                if self.arith_check(op1, op2) or self.string_check(op1, op2):
                    operator = self.add
                else:
                    super().error(
                        ErrorType.TYPE_ERROR,
                        "Incompatible types for arithmetic addition",
                    )
            elif e_type == '!=':
                #weirdness here
                return op1 != op2
            elif e_type == '==':
                #weirdness here
                return op1 == op2
            elif e_type == '-':
                operator = self.subtract
            elif e_type == '*':
                operator = self.mult
            elif e_type == '/':
                operator = self.div
            elif e_type == '||':
                operator = self.lor
            elif e_type == '&&':
                operator = self.land
            elif e_type == '<':
                operator = self.less_than
            elif e_type == '>':
                operator = self.greater_than
            elif e_type == '<=':
                operator = self.leq
            elif e_type == '>=':
                operator = self.geq
            return operator(op1, op2)
        
        #taking care of the unary operations
        elif expr.elem_type in self.un_ops:
            op1 = None
            if expr.dict['op1'].elem_type == 'int' or expr.dict['op1'].elem_type == 'string':
                op1 = expr.dict['op1'].dict['val']
            elif expr.dict['op1'].elem_type == 'var':
                op1 = self.get_var(expr.dict['op1'].dict['name'])
            else:
                op1 = self.execute_expression(expr.dict['op1'])
            
            operator = None
            e_type = expr.elem_type
            if e_type == 'neg':
                if type(op1) == int:
                    operator = self.arith_neg
                else:
                    super().error(
                        ErrorType.TYPE_ERROR,
                        "Incompatible types for arithmetic negation",
                    )
            elif e_type == '!':
                if type(op1) == bool:
                    operator - self.bool_neg
            return operator(op1)
        #Function calls
        else:
            return self.call_function(expr.get('name'), expr.get('args'))

            
    # Execute an assignemnt operator
    def execute_assignment(self, assn):
        if assn.dict['expression'].elem_type in self.bin_ops or assn.dict['expression'].elem_type in self.un_ops or assn.dict['expression'].elem_type == 'fcall':
            self.set_var(assn.get('name'), self.execute_expression(assn.dict['expression']))
            return 
        if assn.dict['expression'].elem_type == 'var':
            self.set_var(assn.dict['name'], self.get_var(assn.dict['expression'].dict['name']))
            return
        if assn.dict['expression'].elem_type == 'int' or assn.dict['expression'].elem_type == 'string':
            self.set_var(assn.dict['name'], assn.dict['expression'].dict['val'])
            return

    # Execute a statement
    def execute_statement(self, statement):
        if statement.elem_type == '=':
            return self.execute_assignment(statement)
            #not sure if I should return anything?

        elif statement.elem_type == 'fcall':
            return self.call_function(statement.get('name'), statement.get('args'))
        
        elif statement.elem_type == 'if':
            if self.execute_expression(statement.get('condition')):
                for true_statement in statement.get('statements'):
                    self.execute_statement(true_statement)
            else:
                for false_statement in statement.get('else_statements'):
                    self.execute_statement(false_statement)

        elif statement.elem_type == 'while':
            while self.execute_expression(statement.get('condition')):
                for while_statements in statement.get('statements'):
                    self.execute_statement(while_statements)
            
        elif statement.elem_type == 'return':
            return self.execute_expression(statement.get('expression'))
        



    
def main():
    program = """func main() {
  foo(5);
}

func foo(a) {
  print(a);
}"""
    interpreter = Interpreter(trace_output= False)
    interpreter.run(program)

if __name__ == '__main__':
    main()