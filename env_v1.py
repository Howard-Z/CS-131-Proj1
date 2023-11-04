# The EnvironmentManager class keeps a mapping between each variable (aka symbol)
# in a brewin program and the value of that variable - the value that's passed in can be
# anything you like. In our implementation we pass in a Value object which holds a type
# and a value (e.g., Int, 10).
class EnvironmentManager:
    def __init__(self):
        self.environment = [{}]
        self.curr_scope = 0
        self.ret = False

    #Entering a new scope so add a new dict
    def new_block(self):
        self.curr_scope += 1
        self.environment.append({})

    #exiting a scope so delete the new dict
    def exit_block(self):
        del self.environment[self.curr_scope]
        self.curr_scope -= 1

    #are we currently in return mode
    def is_ret(self):
        return self.ret
    
    #Setting the return mode
    def set_ret(self, flag):
        self.ret = flag
        
    # Gets the data associated a variable name
    def get(self, symbol):
        for i in range(self.curr_scope, -1, -1):
            if symbol in self.environment[i] and self.environment[i][symbol][1] <= self.curr_scope:
                return self.environment[i][symbol][0], True
        return None, False

    # Sets the data associated with a variable name
    def set(self, symbol, value, is_param):
        if is_param:
            self.environment[self.curr_scope][symbol] = (value, self.curr_scope)
        for i in range(self.curr_scope, -1, -1):
            if symbol in self.environment[i] and self.environment[i][symbol][1] <= self.curr_scope:
                self.environment[i][symbol] = (value, i)
                return
        self.environment[self.curr_scope][symbol] = (value, self.curr_scope)

