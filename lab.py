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
    """
    numbers = set('0123456789.-')
    def parse_expression(index):
        if (all([(val in numbers) for val in tokens[index]])): # if a number, return it
            num_parts = tokens[index].split('.')
            if (len(num_parts) == 1): # account for ints as well as floats
                val = int(tokens[index])
            elif ((len(num_parts) == 2) and (int(num_parts[1])>0)):
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


carlae_builtins = {
    '+': sum,
    '-': lambda args: -args[0] if len(args) == 1 else (args[0] - sum(args[1:])),
}


def evaluate(tree):
    """
    Evaluate the given syntax tree according to the rules of the carlae
    language.

    Arguments:
        tree (type varies): a fully parsed expression, as the output from the
                            parse function
    """
    raise NotImplementedError


if __name__ == '__main__':
    # code in this block will only be executed if lab.py is the main file being
    # run (not when this module is imported)
    pass
    # run doctests-- comment out before submitting!
    import doctest
    doctest.testmod()
