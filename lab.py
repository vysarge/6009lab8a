"""6.009 Lab 8A: carlae Interpreter"""

import sys


class EvaluationError(Exception):
    """Exception to be raised if there is an error during evaluation."""
    pass



def tokenize(source):
    """
    Splits an input string into meaningful tokens (left parens, right parens,
    other whitespace-separated values).  Returns a list of strings.

    Arguments:
        source (str): a string containing the source code of a carlae
                      expression

    >>> tokenize("(cat (dog (tomato)))")
    ['(', 'cat', '(', 'dog', '(', 'tomato', ')', ')', ')']
    >>> tokenize("(+ cat dog) ; comment")
    ['(', '+', 'cat', 'dog', ')']
    """
    whitespace_vals = set(" \n") # whitespace values
    single_vals = set("()")
    curr_token = '' # the current token being processed
    commented = False # whether we are currently in a comment
    found_tokens = [] # list of found tokens.
    for ch in source:
        if (commented): # skip comments
            if (ch == '\n'):
                commented = False # end comments at a carriage return
            continue
        # otherwise
        if (ch == ';'): # set flag to ignore comments
            commented = True
            if (len(curr_token) > 0):
                found_tokens.append(curr_token)
        elif (ch in single_vals): # for ( and )
            if (len(curr_token) > 0):
                found_tokens.append(curr_token)
            found_tokens.append(ch)
            curr_token = ''
        # for whitespace-separated tokens
        elif (ch in whitespace_vals):
            if (len(curr_token) > 0):
                found_tokens.append(curr_token)
                curr_token = ''
        else:
            curr_token += ch

    # catch any dangling tokens
    if (len(curr_token) > 0):
        found_tokens.append(curr_token)

    return found_tokens

def parse(tokens):
    """
    Parses a list of tokens, constructing a representation where:
        * symbols are represented as Python strings
        * numbers are represented as Python ints or floats
        * S-expressions are represented as Python lists

    Arguments:
        tokens (list): a list of strings representing tokens

    >>> parse(['3.5'])
    3.5
    >>> parse(['x'])
    'x'
    >>> parse(['(', 'x', ')'])
    ['x']
    >>> parse(['(', '5', '(', 'x', '3', ')', ')'])
    [5, ['x', 3]]
    >>> parse(['(', '5', '(', 'x', '3', ')', 'm'])
    Traceback (most recent call last):
    ...
    SyntaxError: Unclosed open parenthesis
    >>> parse(['3.45.7'])
    Traceback (most recent call last):
    ...
    SyntaxError: Malformed number input
    >>> parse(['34.-5'])
    Traceback (most recent call last):
    ...
    SyntaxError: Malformed number input
    >>> parse(['(', '+', '2', '(', '-', '3', '4', ')', ')'])
    ['+', 2, ['-', 3, 4]]
    """
    numbers = set('0123456789.-')
    def parse_expression(index):
        if (not tokens[index] == '-' and all([(val in numbers) for val in tokens[index]])): # if a number, return it
            num_parts = tokens[index].split('.')
            if (len(num_parts) == 1): # account for ints as well as floats
                val = int(tokens[index])
            elif ((len(num_parts) == 2) and (len(num_parts[1]) > 0) and (int(num_parts[1])>0)):
                val = float(tokens[index])
            else:
                raise SyntaxError('Malformed number input')
            return val, index+1
        if (tokens[index] not in '()'): # if a variable, return it
            return tokens[index], index+1
        if (tokens[index] == '('): # otherwise, parse expression recursively
            pointer = index+1
            parse_list = []
            # while within the expression, add each token recursively
            while (pointer < len(tokens) and tokens[pointer] != ')'):
                val, pointer = parse_expression(pointer)
                parse_list.append(val)
            if (pointer >= len(tokens)): # if the expression is unclosed, complain
                raise SyntaxError('Unclosed open parenthesis')
            return parse_list, pointer+1 # otherwise return the list of parsed tokens
        raise SyntaxError('Unopened close parenthesis or uncaught error type in parser')
    # start off recursion
    parsed_expression, next_index = parse_expression(0)
    if (next_index != len(tokens)):
        raise SyntaxError('Unopened close parenthesis or uncaught error type in parser')
    return parsed_expression

class CarlaeEnvironment:
    """
    A class to hold an environment
    self.parent is the parent environment (should also be a CarlaeEnvironment)
    self.defs is a dictionary holding the variable and function definitions
    May set values directly or update from a dictionary.
    """
    def __init__(self, parent=None):
        assert parent==None or isinstance(parent, CarlaeEnvironment), \
            'Parent of a CarlaeEnvironment must also be a CarlaeEnvironment'
        self.parent = parent
        self.defs = {}

    def __setitem__(self, key, value):
        """
        Set the value of the given keyword in this environment
        """
        if not isinstance(key, str):
            raise EvaluationError('Invalid variable name: {}'.format(key))
        self.defs[key] = value

    def __getitem__(self, key):
        """
        Return the value of the given keyword in this environment or,
        if not found, in its parent.
        Will raise an EvaluationError if that keyword is not present
        """
        if (key in self.defs.keys()):
            return self.defs[key]
        if (self.parent is None):
            raise EvaluationError('Invalid keyword: {}'.format(key))
        return self.parent[key]

    def update(self, defs_to_add):
        """
        Add all definitions from the given dictionary to the environment
        Will overwrite existing definitions
        """
        assert isinstance(defs_to_add, dict), 'Cannot update from a non-dictionary'
        for key in defs_to_add.keys():
            self.__setitem__(key, defs_to_add[key])

class CarlaeFunction:
    """
    This class describes a function written in Carlae.
    Call to evaluate it on the inputs given.
    """
    def __init__(self, arg_names, expression, env):
        self.arg_names = arg_names
        self.expression = expression
        self.env = env

    def __call__(self, arg_list):
        if (len(arg_list) != len(self.arg_names)):
            raise EvaluationError("Incorrect number of arguments given; {} required".format(len(self.arg_names)))
        return self.func_eval_dict({self.arg_names[i]: arg_list[i] for i in range(len(self.arg_names))})

    def func_eval_dict(self, arg_dict):
        local_env = CarlaeEnvironment(self.env)
        local_env.update(arg_dict)
        return evaluate(self.expression, local_env)

carlae_builtins = {
    '+': sum,
    '-': lambda args: -args[0] if len(args) == 1 else (args[0] - sum(args[1:])),
    '*': lambda args: 1 if len(args)==0 else args[0]*carlae_builtins['*'](args[1:]),
    '/': lambda args: 1/args[0] if len(args)==1 else \
        args[0]/carlae_builtins['*'](args[1:]),
}
# builtin environment: should be the parent of the global environment as well.
builtins_env = CarlaeEnvironment()
builtins_env.update(carlae_builtins)

def evaluate(tree, env=None):
    """
    Evaluate the given syntax tree according to the rules of the carlae
    language.

    Arguments:
        tree (type varies): a fully parsed expression, as the output from the
                            parse function
    >>> evaluate(-3.5)
    -3.5
    >>> evaluate(['+', 3, -4.5])
    -1.5
    """
    # default variables issue
    # those in function line are only evaluated once
    if env is None:
        env = CarlaeEnvironment(builtins_env)

    # for single inputs
    if (not isinstance(tree, list)):
        if (isinstance(tree, str)): # for symbols, find the associated value
            return env[tree]
        else: # otherwise it should be a number
            return tree # so return directly

    # catch possible issues? and ensure a useful error will be raised if necessary
    if (len(tree) == 0):
        raise EvaluationError('Empty expression encountered!')

    # special keyword: define
    if (tree[0] == 'define'):
        if len(tree) != 3:
            raise EvaluationError('Define must be given one name and one expression')

        nameparsed = tree[1]
        funcparsed = tree[2]
        if (isinstance(tree[1], list)): # if in the concise form
            nameparsed = tree[1][0] # convert it to the lambda form for evaluation
            funcparsed = ['lambda', tree[1][1:], tree[2]]
        val = evaluate(funcparsed, env)
        env[nameparsed] = val
        return val

    # special keyword: lambda
    if (tree[0] == 'lambda'):
        if (len(tree) != 3):
            raise EvaluationError('Lambda must be given one set of arguments and one expression')
        func = CarlaeFunction(tree[1], tree[2], env)
        return func
    
    # otherwise, for S-expressions
    # this should be all that is left after evaluating single inputs and special keywords
    func = evaluate(tree[0], env)

    # check functions
    if (not callable(func)):
        raise EvaluationError('Function expected: {}'.format(func))
    # and evaluate
    args = [evaluate(arg, env) for arg in tree[1:]]
    return func(args)

def result_and_env(tree, env=None):
    """
    Test function: wrapper for evaluate that also guarantees returning the environment
    """
    # default variables
    if env is None:
        env = CarlaeEnvironment(builtins_env)

    res = evaluate(tree, env)
    return res, env

if __name__ == '__main__':
    # code in this block will only be executed if lab.py is the main file being
    # run (not when this module is imported)
    pass
    # run doctests-- comment out before submitting!
    # import doctest
    # doctest.testmod()

    #print(carlae_builtins['/']([1, 2, 3, 4, 5]))
    # env = None
    # outval, env = result_and_env(parse(tokenize("(define addN (lambda (n) (lambda (i) (+ i n))))")), env)
    # outval, env = result_and_env(parse(tokenize("(define add7 (addN 7))")), env)
    # outval, env = result_and_env(parse(tokenize("(add7 2)")), env)
    # outval, env = result_and_env(parse(tokenize("(add7 ((addN 3) ((addN 19) 8)))")), env)
    

    # REPL
    val = input("in> ")
    env = None
    while(val != 'QUIT'):
        # tokens = tokenize(val)
        # parsed = parse(tokens)
        # outval, env = result_and_env(parsed, env)
        try:
            tokens = tokenize(val)
            parsed = parse(tokens)
            outval, env = result_and_env(parsed, env)
        except EvaluationError as evalerror:
            print(EvaluationError)
            outval = evalerror
        except SyntaxError as synerror:
            print(SyntaxError)
            outval = synerror
        except Exception as error:
            print("Unknown Error type")
            outval = error
        print("  out> {}".format(outval))        
        val = input("in> ")
        
