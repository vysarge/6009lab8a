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
    """
    numbers = set('0123456789')
    def parse_expression(index):
        if (tokens[index] in numbers):
            return int(tokens[index]), index+1
        if (tokens[index] == '('):
            pass
    # start off recursion
    parsed_expression, next_index = parse_expression(0)
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
