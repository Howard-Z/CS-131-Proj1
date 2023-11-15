from intbase import *
from brewparse import parse_program
import element
from env_v1 import *
import copy

class Interpreter(InterpreterBase):
    
    #Initialize the base class with the flag for debug
    def __init__(self, console_output=True, inp=None, trace_output=False):
        super().__init__(console_output, inp)
        self.debug = trace_output
        self.bin_ops = {'+', '-', '*', '/','==', '<', '<=', '>', '>=', '!=', '||', '&&'}
        self.un_ops = {'neg', '!'}
        self.arith_ops = {'+', '-', '*', '/'}
        self.val_types = {'int', 'string', 'bool', 'nil'}
        self.bool_expr = {'||', '&&'}

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
        val, status = self.env.get(name)
        if status == False:
            # If you didn't pull a value out of the env
            # Then you must be looking for a function from the execute assignment function
            # This checks if there are multiple functions with the same name
            # so you skip the ambiguity
            func = self.mult_func_check(name)
            if func != None:
                return func
            else:
                super().error(
                    ErrorType.NAME_ERROR,
                    f"Variable {name} has not been defined",
                )
        else:
            return val
    
    # Set a variable
    def set_var(self, name, val, is_param = False, is_ref = False, ref_name = None):
        self.env.set(name, val, is_param, is_ref, ref_name)

    # Parse a single argument
    def parse_single(self, arg):
        # TODO: YOU NEED TO PROCESS LAMBDAs HERE!!!!
        if arg.elem_type in self.bin_ops or arg.elem_type in self.un_ops or arg.elem_type == 'fcall':
                return self.execute_expression(arg)
        elif arg.elem_type == 'var':
            return self.get_var(arg.get('name'))
        else:
            return arg.get('val')

    # Given a list of arguments, process all of them if they can be processed
    def parse_args(self, args):
        parsed = []
        for arg in args:
            parsed.append(self.parse_single(arg))
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
                arg = self.bool_converter(arg)
            output += str(arg)
        super().output(output)
        return
    
    # The implementation of inputi()
    def brew_input(self, args, is_inputi):
        if len(args) > 1:
            super().error(
                ErrorType.NAME_ERROR,
                f"No inputi() function found that takes > 1 parameter",
            )
            return
        if len(args) == 1:
            super().output(args[0])

        user_input = super().get_input()
        if is_inputi:
            return int(user_input)
        return str(user_input)

    # This is to check if multiple functions have the same name
    # because when you assign to a variable it wouldn't know which one
    # if you overloaded it: see section "First Class Functions" --> "Storing Functions in a Variable"
    # first bullet point
    def mult_func_check(self, name):
        ast_temp = self.ast.get('functions')
        counter = 0
        out_func = None
        for ast_func in ast_temp:
            if ast_func.get('name') == name:
                counter += 1
                out_func = ast_func
        if counter > 1:
            super().error(
                ErrorType.NAME_ERROR,
                f"Multiple function {name} has been defined",
            )
        if counter == 1:
            return out_func
        
        super().error(
            ErrorType.NAME_ERROR,
            f"Function {name} has not been defined",
        )

    # get function
    def get_func(self, name):
        ast_temp = self.ast.get('functions')
        for ast_func in ast_temp:
            if ast_func.get('name') == name:
                return ast_func
        func = self.get_var(name)
        return func

    #overload check
    def overload_check(self, name, num_args):
        ast_temp = self.ast.get('functions')
        for ast_func in ast_temp:
            if ast_func.get('name') == name and len(ast_func.get('args')) == num_args:
                return True
        func = self.get_var(name)
        if type(func) == element.Element:
            if func.elem_type == 'func' and len(func.get('args')) == num_args:
                return True
        return False

    
    #function check
    def function_check(self, name):
        ast_func = self.ast.get('functions')
        for func in ast_func:
            if func.get('name') == name:
                return True
        func = self.get_var(name)
        if type(func) == element.Element:
            if func.elem_type == 'func':
                return True
        else:
            super().error(
                ErrorType.TYPE_ERROR,
                f"Function {name} is not a defined function",
            )

    # return var name or none
    def var_or_none(self, expr):
        if expr.elem_type == 'var':
            return expr.get('name')
        return None

    # Function for handling brewin function calls
    def call_function(self, name, args):
        if name == 'print':
            parsed = self.parse_args(args)
            self.brew_print(parsed)
            return None
        elif name == 'inputi' or name == 'inputs':
            parsed = self.parse_args(args)
            thing = name == 'inputi'
            return self.brew_input(parsed, thing)
        elif self.function_check(name):
            self.env.new_block()
            func = None
            if self.overload_check(name, len(args)):
                func = self.get_func(name)
            else:
                super().error(
                ErrorType.NAME_ERROR,
                f"Function {name} has not been defined",
            )
            for i in range(len(args)):
                if func.get('args')[i].elem_type == 'arg':
                    self.set_var(func.get('args')[i].get('name'), self.parse_single(args[i]), True, False)
                else:
                    self.set_var(func.get('args')[i].get('name'), self.parse_single(args[i]), True, True, self.var_or_none(args[i]))
            val = self.execute_function(func)
            self.env.set_ret(False)
            self.env.exit_block()
            return val
            
        else:
            super().error(
                ErrorType.NAME_ERROR,
                f"Function {name} has not been defined",
            )

    # Execute a function node
    def execute_function(self, func):
        output = None
        if self.debug:
            print(self.env.is_ret())
        for statement in func.dict['statements']:
            if not self.env.is_ret():
                output = self.execute_statement(statement)
                if self.env.is_ret():
                    return output
            else:
                self.env.set_ret(False)
                return output
        
    # The subtraction operator
    def subtract(self, op1, op2):
        if self.arith_check(op1, op2):
            return op1 - op2
        else:
            super().error(
                ErrorType.TYPE_ERROR,
                "Incompatible types for arithmetic operation",
            )
    
    # The addition operator
    def add(self, op1, op2):
        if type(op1) == type(op2):
            return op1 + op2
        else:
            super().error(
                ErrorType.TYPE_ERROR,
                "Incompatible types for arithmetic operation",
            )

    # The multiplication operator
    def mult(self, op1, op2):
        if self.arith_check(op1, op2):
            return op1 * op2
        else:
            super().error(
                ErrorType.TYPE_ERROR,
                "Incompatible types for arithmetic operation",
            )

    # The division operator
    def div(self, op1, op2):
        if self.arith_check(op1, op2):
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
        if type(op1) == bool or type(op1) == None:
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


    # Corersion function to bool
    def coerce_to_bool(self, val):
        if type(val) == bool:
            return val
        # assumption made here that if val isn't a bool, it must be an int
        else:
            return val != 0
        

    # Corersion function to bool
    def coerce_to_int(self, val):
        if type(val) == int:
            return val
        # assumption made here that if val isn't an int, it must be an bool
        else:
            return 1 if val else 0

    # Bool-Integer coercion check
    def bool_int_comp_check(self, op1, op2):
        if type(op1) == bool or type(op1) == int:
            if type(op2) == bool or type(op2) == int:
                return True
        return False

    
    # Execute an expression
    def execute_expression(self, expr):
        # handling variables
        if expr.elem_type == 'var':
            return self.get_var(expr.get('name'))
        # handling constants
        if expr.elem_type in self.val_types and expr.elem_type != 'nil':
            return expr.get('val')
        if expr.elem_type == 'nil':
            return None
        # taking care of the binary operations
        if expr.elem_type in self.bin_ops:
            op1, op2 = None, None
            if expr.dict['op1'].elem_type in self.val_types and expr.dict['op1'].elem_type != 'nil':
                op1 = expr.dict['op1'].dict['val']
            elif expr.dict['op1'].elem_type == 'nil':
                op1 = None
            elif expr.dict['op1'].elem_type == 'var':
                op1 = self.get_var(expr.dict['op1'].dict['name'])
            elif expr.get('op1').elem_type == 'fcall':
                op1 = self.call_function(expr.get('op1').get('name'), expr.get('op1').get('args'))
            else:
                op1 = self.execute_expression(expr.dict['op1'])
            
            if expr.dict['op2'].elem_type in self.val_types and expr.dict['op2'].elem_type != 'nil':
                op2 = expr.dict['op2'].dict['val']
            elif expr.dict['op2'].elem_type == 'nil':
                op2 = None
            elif expr.dict['op2'].elem_type == 'var':
                op2 = self.get_var(expr.dict['op2'].dict['name'])
            elif expr.get('op2').elem_type == 'fcall':
                op2 = self.call_function(expr.get('op2').get('name'), expr.get('op2').get('args'))
            else:
                op2 = self.execute_expression(expr.dict['op2'])
            
            operator = None
            e_type = expr.elem_type
            if e_type in self.arith_ops:
                op1 = self.coerce_to_int(op1)
                op2 = self.coerce_to_int(op2)
            if e_type in self.bool_expr:
                op1 = self.coerce_to_bool(op1)
                op2 = self.coerce_to_bool(op2)
            if e_type == '+':
                if self.arith_check(op1, op2) or self.string_check(op1, op2):
                    operator = self.add
                else:
                    super().error(
                        ErrorType.TYPE_ERROR,
                        "Incompatible types for arithmetic addition",
                    )
            elif e_type == '!=':
                if type(op1) != type(op2):
                    if self.bool_int_comp_check(op1, op2):
                        return self.coerce_to_bool(op1) != self.coerce_to_bool(op2)
                    else:
                        return True
                return op1 != op2
            elif e_type == '==':
                if type(op1) != type(op2):
                    if self.bool_int_comp_check(op1, op2):
                        return self.coerce_to_bool(op1) == self.coerce_to_bool(op2)
                    return False
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
            if expr.dict['op1'].elem_type in self.val_types and expr.get('op1') != 'nil':
                op1 = expr.dict['op1'].dict['val']
            elif expr.dict['op1'].elem_type == 'nil':
                op1 = None
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
                if type(op1) == int:
                    op1 = self.coerce_to_bool(op1)
                if type(op1) == bool or type(op1) == None:
                    operator = self.bool_neg
                else:
                    super().error(
                        ErrorType.TYPE_ERROR,
                        "Incompatible types for boolean negation",
                    )
            return operator(op1)
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
        if assn.get('expression').elem_type == 'nil':
            self.set_var(assn.get('name'), None)
            return
        if assn.dict['expression'].elem_type in self.val_types:
            self.set_var(assn.dict['name'], assn.dict['expression'].dict['val'])
            return
        if assn.dict['expression'].elem_type == 'lambda':
            # TODO
            pass

    def loop_conditional(self, conditional):
        output = self.execute_expression(conditional)
        if type(output) != bool and type(output) != int:
            super().error(
                ErrorType.TYPE_ERROR,
                "Not boolean or int expression in conditional check"
            )
            return None
        return output


    # Execute a statement
    def execute_statement(self, statement):
        if statement.elem_type == '=':
            return self.execute_assignment(statement)

        elif statement.elem_type == 'fcall':
            return self.call_function(statement.get('name'), statement.get('args'))
        
        elif statement.elem_type == 'if':
            self.env.new_block()
            output = None
            if self.loop_conditional(statement.get('condition')):
                for true_statement in statement.get('statements'):
                    output = self.execute_statement(true_statement)
                    if self.env.is_ret():
                        self.env.exit_block()
                        return output
            elif statement.get('else_statements') != None:
                for false_statement in statement.get('else_statements'):
                    output = self.execute_statement(false_statement)
                    if self.env.is_ret():
                        self.env.exit_block()
                        return output
            self.env.exit_block()

        elif statement.elem_type == 'while':
            output = None
            self.env.new_block()
            while self.loop_conditional(statement.get('condition')):
                for while_statements in statement.get('statements'):
                    output = self.execute_statement(while_statements)
                    if self.env.is_ret():
                        self.env.exit_block()
                        return output
            self.env.exit_block()
            return None
            
        elif statement.elem_type == 'return':
            output = None
            if statement.get('expression') != None:
                output = self.execute_expression(statement.get('expression'))
                self.env.set_ret(True)
                return output
            else:
                self.env.set_ret(True)
                return None
        return None

def main():
    program = """
func foo(ref f) {
 return f;
}


func main() {
  b = 0;
  f = lambda () { b = b + 1; print(b); };
  f();
  f();
  g = foo(f);
  g();
  g();
  f();
  print(b);
}

"""
    interp = Interpreter()
    interp.run(program)

if __name__ == '__main__':
    #Notes
    # throw an Error when trying to assign functions that have overloads
    # do not capture when assigning functions
    # lambdas do capture however
    # captured variables are deep copied
    # The modifications to the values in the closure are sustained
    main()
