# The EnvironmentManager class keeps a mapping between each variable (aka symbol)
# in a brewin program and the value of that variable - the value that's passed in can be
# anything you like. In our implementation we pass in a Value object which holds a type
# and a value (e.g., Int, 10).
class EnvironmentManager:
    def __init__(self):
        self.environment = {}
        self.curr_scope = 0

    
    def new_block(self):
        self.curr_scope += 1

    def exit_block(self):
        for var in self.environment:
            if var[1] >= self.curr_scope:
                del self.environment[var]
        self.curr_scope -= 1


    # Gets the data associated a variable name
    def get(self, symbol):
        if symbol in self.environment:
            return self.environment[symbol][0]
        return None

    # Sets the data associated with a variable name
    def set(self, symbol, value):
        self.environment[symbol] = (value, self.curr_scope)
