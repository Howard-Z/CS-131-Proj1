#This is here just so I can force object pointers
class Box:
    def __init__(self, val):
        self.val = val

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
            if symbol in self.environment[i]:
                return self.environment[i][symbol].val, True
        return None, False
    
    # Gets the data associated a variable name
    def get_obj(self, symbol):
        for i in range(self.curr_scope, -1, -1):
            if symbol in self.environment[i]:
                return self.environment[i][symbol], True
        return None, False

    # deletes the object specified by the symbol
    def del_obj(self, symbol):
        for i in range(self.curr_scope, -1, -1):
            if symbol in self.environment[i]:
                del self.environment[i][symbol]
        return True

    # Sets the data associated with a variable name
    def set(self, symbol, value, is_param, is_ref, ref_name):
        if is_param and not is_ref:
            self.environment[self.curr_scope][symbol] = Box(value)
            return
        elif is_param and is_ref and ref_name != None:
            for i in range(self.curr_scope, -1, -1):
                if ref_name in self.environment[i]:
                    # self.environment[i][symbol] = (Box(value), i)
                    self.environment[self.curr_scope][symbol] = self.environment[i][ref_name]
                    return
        for i in range(self.curr_scope, -1, -1):
            if symbol in self.environment[i]:
                self.environment[i][symbol].val = value
                return
        self.environment[self.curr_scope][symbol] = Box(value)


# about proto inheritance
# of 1 level
# def a method in parent and accessing in child
# shadowing the method
# def a closure in the parent
# access the closure in the child
# the closure should be shared among parent and child
# def a function that uses attributes of the parent object
# let's say s.len and s.width
# create a child that inherits everything, function referes to width and legnth
# but if you change them only in the child
# c.len = 30
# p.proto = c
# p.len = 10
# this should not modify c

# test proto 7 is about accesing prototype from the method of a child

# tests my implementation of this always refers to the object the method is called on

# test shadowing:
# 