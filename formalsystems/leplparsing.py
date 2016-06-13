#!/usr/bin/python
# -*- coding: utf-8 -*-

import operator
from collections import defaultdict

from lepl import *  # noqa
import lepl


def reg_to_lex(conditions, wildcards):
    """Transform a regular expression into a LEPL object.

    Replace the wildcards in the conditions by LEPL elements,
    like xM will be replaced by Any() & 'M'.
    In case of multiple same wildcards (like xMx), aliases
    are created to allow the regexp to compile, like
    Any() > 'x_0' & 'M' & Any() > 'x_1', and we chech that the matched values
    for all aliases like x_0, x_1 are the same.
    """
    aliases = defaultdict(set)
    n_conds = []

    # All conditions
    for i, _ in enumerate(conditions):
        n_cond = []

        for char in conditions[i]:
            if char in wildcards:
                alias = '%s_%s' % (char, len(aliases[char]))
                aliases[char].add(alias)
                n_cond.append(make_token(alias, reg=wildcards[char]))
            else:
                n_cond.append(~Literal(char))

        n_cond.append(Eos())
        n_conds.append(reduce(operator.and_, n_cond) > make_dict)

    return tuple(n_conds), aliases


# FIX: LEPL does not seem to be able
# to return empty string matches,
# so filtering matches through a custom
# function like this seems to fix the problem
def join(args):
    return ''.join(args)

def make_token(alias, reg):
    if reg[-1] in '*+':
        s, wildcard = reg[:-1], reg[-1]
        if wildcard == '+':
            rep = 1
        else:  # wildcard is *
            rep = 0
        if s == '.':
            return (Any()[rep:, ...] > join) > alias
        return (Literal(s)[rep:, ...] > join) > alias

    return Literal(reg) > alias


def parse(reg, theorem):
    try:
        # reg.parse_all has this grammar
        # [[{}], [{}], ...]
        for l in reg.parse_string_all(theorem):
            for m in l:
                yield m

    except lepl.stream.maxdepth.FullFirstMatchException:
        # Uncomment to see fail matches
        yield
