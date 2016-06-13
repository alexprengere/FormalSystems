#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import with_statement

import yaml
import re
from itertools import product, repeat, count

from .leplparsing import reg_to_lex, parse
from .OrderedSet import OrderedSet


def generate_wildcards(conditions):
    # Wildcards handling for each rule
    wildcards = {}

    for cond in conditions:
        cond = [e for e in re.split(' is | are |[ \t]+', cond) if e]
        sym, reg = cond[:-1], cond[-1]
        for s in sym:
            wildcards[s.strip()] = reg.strip()

    return wildcards


def iterate_over_wildcard(wildcards):
    for coords in triangle_iteration(start=1, dim=len(wildcards)):
        w_iter = {}
        for name, k in zip(wildcards.keys(), coords):
            # Case .*? non-greedy matching
            reg = wildcards[name].strip('?')
            s, wildcard = reg[:-1], reg[-1]

            if wildcard == '+':
                w_iter[name] = s * k
            elif wildcard == '*':
                w_iter[name] = s * (k - 1)

            else:
                raise Exception('Regex %s not supported.' % reg)

        yield w_iter


def increase_coord(point, i):
    new_point = list(point)
    new_point[i] += 1

    return tuple(new_point)


def triangle_iteration(start, dim, stop=None):
    """
    >>> list(triangle_iteration(1, 1, stop=3))
    [(1,), (2,), (3,)]
    >>> list(triangle_iteration(1, 2, stop=3))
    [(1, 1), (1, 2), (2, 1), (1, 3), (3, 1), (2, 2)]
    >>> list(triangle_iteration(1, 0, stop=3))
    []
    """
    if not dim:
        return

    # Initialization
    point = (start, ) * dim
    frontier = set([point])
    yield point

    c = 1

    while True:
        frontier = set(
            increase_coord(p, i)
            for p in list(frontier)
            for i, _ in enumerate(p)
        )

        for p in frontier:
            yield p

        c += 1
        if stop is not None and c >= stop:
            return


def reg_to_printer(regs, wildcards):
    for i, _ in enumerate(regs):
        # We will modify reg, but regs[i] wont be
        reg = regs[i]
        for s in wildcards:
            reg = reg.replace(s, '%%(%s)s' % s)

        yield reg


def compile_schema(raw_schema):
    raw_schema = raw_schema.split(',')
    conditions, exp = raw_schema[:-1], raw_schema[-1].strip()
    wildcards = generate_wildcards(conditions)
    (regex,), aliases = reg_to_lex((exp,), wildcards)
    (schema,) = tuple(reg_to_printer((exp,), wildcards))

    return wildcards, aliases, regex, schema


def compile_rule(raw_rule):
    rule = raw_rule.split(',')

    conditions = rule[:-1]
    oldts, newts = [r.strip() for r in rule[-1].split(' => ')]
    oldts = [r.strip() for r in oldts.split(' and ')]
    newts = [r.strip() for r in newts.split(' and ')]

    wildcards = generate_wildcards(conditions)

    oldts, aliases = reg_to_lex(oldts, wildcards)
    newts = tuple(reg_to_printer(newts, wildcards))

    return aliases, oldts, newts


def reverse_alias(aliases, alias):
    for s, s_aliases in aliases.iteritems():
        if alias in s_aliases:
            return s

    raise ValueError('Alias %s did not match a symbol in %s' %
                     (alias, aliases))


def check_consistency(aliases, *matches):
    ua_match = {}

    for match in matches:
        for alias, v in match.iteritems():
            sym = reverse_alias(aliases, alias)

            if sym not in ua_match:
                ua_match[sym] = v
            elif ua_match[sym] != v:
                # Aliases should match the same value
                return

    return ua_match


class AxiomsSchema(object):
    def __init__(self, name, s):
        self.name = name
        self.raw_schema = s

        self.wildcards, self.aliases, self.reg, self.schema = compile_schema(s)

    def __str__(self):
        return '(%s) %s' % (self.name, self.raw_schema)

    def _is_axiom(self, theorem):
        for m in parse(self.reg, theorem.string):
            if m is None:
                # No match
                yield
                continue

            yield check_consistency(self.aliases, m)

    def is_axiom(self, theorem, verbose=True):
        for c in self._is_axiom(theorem):
            if c is None:  # No match or inconsistency in aliases
                if verbose:
                    print 'N  %-10s *is not* an axiom [%s]' % \
                        (theorem, self)
            else:
                if verbose:
                    print 'Y  %-10s   *is*   an axiom [%s with %s]' % \
                        (theorem, self, ' and '.join('%s=%s' % (s, c[s]) for s in self.aliases))
                return True
        return False

    def iterate_over_schema(self):
        if not self.wildcards:
            # Simple axiom, no schema
            yield Theorem(self.schema)
        else:
            # Clever iteration over wildcards in schema
            for r in iterate_over_wildcard(self.wildcards):
                yield Theorem(self.schema % r)


class Theorem(object):
    def __init__(self, string, parents=None, p_rule=None):
        # Theorem string expression
        self.string = string
        # Parent iterable
        if parents is None:
            self.parents = ()
        else:
            self.parents = tuple(parents)
        # Producing rule
        if p_rule is None:
            self.p_rule = 'Axiom'
        else:
            self.p_rule = p_rule

    def __str__(self):
        return self.string

    def __hash__(self):
        # For test like: th in set(ths)
        return self.string.__hash__()

    def __eq__(self, other):
        # For test like: th == oth
        return self.string == other.string

    def __len__(self):
        return len(self.string)


class Rule(object):
    def __init__(self, name, s):
        self.name = name
        self.raw_rule = s
        self.aliases, self.oldts, self.newts = compile_rule(s)

    def __str__(self):
        return '(%s) %s' % (self.name, self.raw_rule)

    def produce_one(self, t_ths, verbose=True):
        # Note that the 'yield None' are just there
        # inform the upper function that a producing failed
        # It can be commented for speed (about one third gain)

        # We build a list of list of aliases,
        # for each partial rule for each matching possibility
        match_per_cond = []

        for pr, t in zip(self.oldts, t_ths):
            match_per_cond.append([])

            for m in parse(pr, t.string):
                if m is None:
                    # No match
                    yield
                    continue

                c = check_consistency(self.aliases, m)

                if c is None:
                    # Inconsistency in aliases, non-match
                    yield
                    continue

                match_per_cond[-1].append(m)

        # Cartesian product, we test each possibility of matching
        # in each partial rule
        for t_matches in product(*match_per_cond):
            c = check_consistency(self.aliases, *t_matches)
            if c is None:
                yield
                continue

            for nth in self.newts:
                yield Theorem(nth % c, parents=t_ths, p_rule=self)

    def produce(self, ths, old_ths=None, verbose=True):
        n = len(self.oldts)

        # Iterate over all possibilities of n-tuple
        for t_ths in self.compute_combinations(n, ths, old_ths):
            for nth in self.produce_one(t_ths, verbose):
                if nth is not None:
                    if verbose:
                        self.display_prod(t_ths, nth)
                    yield nth
                else:
                    # Nothing yielded
                    if verbose:
                        self.display_unprod(t_ths)

    def display_prod(self, t_ths, nth):
        print 'P  %-40s  for  %-25s  gives  %s' % \
            (self, ' and '.join(str(t) for t in t_ths), nth)

    def display_unprod(self, t_ths):
        print '.  %-40s  for  %-25s' % \
            (self, ' and '.join(str(t) for t in t_ths))

    @staticmethod
    def compute_combinations(n, ths, old_ths=None):
        if old_ths is None:
            # Here we could just define old_ths as set() and
            # go on, but if ths is OrderedSet, old_ths | ths will fail
            old_ths = ths.__class__()

        # Sub optimal: it should be possible to compute all combinations
        # of ths + old_ths without the combinations of old_ths, in a way
        # that avoids computing all combinations in the first place
        #
        # Note that product will give "same theorem tuple",
        # like (1, 1) as a part of the cartesian product of [1, 2, 3]
        for t_ths in set(product(*repeat(old_ths | ths, n))) - \
                set(product(*repeat(old_ths, n))):

            yield t_ths


def iterator_mix(*iterators):
    """
    Iterating over list of iterators.
    Bit like zip, but zip stops after the
    shortest iterator is empty, abd here
    we go one until all iterators are empty.
    """
    while True:
        one_left = False

        for it in iterators:
            try:
                yield it.next()
            except StopIteration:
                pass
            else:
                one_left = True

        if not one_left:
            break


def extract_from(elem, s):
    if elem not in s:
        return
    list_s = list(s)
    return list_s[list_s.index(elem)]


class FormalSystem(object):
    def __init__(self):
        self.axioms = []
        self.rules = []

    def read_formal_system(self, source):
        with open(source, 'r') as f:
            data = yaml.load(f)

            for i, raw_schema in enumerate(data['axioms'], start=1):
                self.axioms.append(AxiomsSchema(i, raw_schema))

            for i, raw_rule in enumerate(data['rules'], start=1):
                self.rules.append(Rule(i, raw_rule))

    def is_axiom(self, theorem, verbose=True):
        for axiom in self.axioms:
            if axiom.is_axiom(theorem, verbose):
                return True
        return False

    def iterate_over_schema(self, max_iter=None):
        it_list = [ax.iterate_over_schema() for ax in self.axioms]
        n = 0
        # We rotate the schema we pick axioms in
        for el in iterator_mix(*it_list):
            n += 1
            if max_iter is not None and n > max_iter:
                return

            yield el

    def apply_rules(self, ths, old_ths=None, verbose=True):
        for rule in self.rules:
            for newt in rule.produce(ths, old_ths, verbose):
                yield newt

    def _apply_rules_step(self, ths, verbose=True):
        current = OrderedSet(ths)
        yield 1, current

        for i in count(2):
            if verbose:
                print
            current = OrderedSet(self.apply_rules(current, verbose=verbose))
            if verbose:
                print
            yield i, current

    def apply_rules_step(self, ths, step, verbose=True):
        for i, ths in self._apply_rules_step(ths, verbose):
            print 'STEP %s: %s' % (i, '/'.join(str(b) for b in ths))
            if i >= step:
                break

        return ths

    def derivation_step(self, axioms, th, step=10, verbose=True):
        for i, ths in self._apply_rules_step(axioms, verbose):
            print 'STEP %s: %s' % (i, '/'.join(str(b) for b in ths))
            if th in ths or i >= step:
                break

        return self.th_to_derivation(th, extract_from(th, ths), verbose=True)

    def _apply_rules_bucket(self, ths, full=False, verbose=True):
        bucket = OrderedSet()
        old_bucket = OrderedSet()

        for turn, ax in enumerate(ths, start=1):
            if verbose:
                print '[Adding %s to bucket]' % ax
                print

            bucket.add(ax)
            yield turn, bucket

            if verbose:
                print

            # All permutations of bucket + old_bucket will be computed,
            # minus the permutations of old_bucket
            new_bucket = OrderedSet(self.apply_rules(bucket, old_bucket, verbose))

            if full:
                # if this case, old_bucket contains all theorems
                # from the beginning, useful to test permutations
                # for rules with ' and ' of several theorems
                old_bucket = old_bucket | bucket

            bucket = new_bucket

    def apply_rules_bucket_till(self,
                                ths,
                                min_len=None,
                                max_turns=None,
                                full=False,
                                verbose=True):

        if max_turns is None:
            max_turns = float('inf')

        if min_len is None:
            min_len = float('inf')

        # Test if one element has length > min_len
        def has_min_len(t):
            return len(t) >= min_len

        bucket_gen = self._apply_rules_bucket(ths, full, verbose)

        for turn, bucket in bucket_gen:
            print '=== BUCKET %s: %s' % \
                (turn, '/'.join(str(b) for b in bucket))

            # We stop if we processed all axioms shorter than min_len
            # And all their "childs" are longer than min_len after some iteration
            # This way we know we got all theorems with len <= min_len
            if all(map(has_min_len, bucket)) or turn >= max_turns:
                break

        return bucket

    def derivation_asc(self,
                       axioms,
                       th,
                       max_turns=None,
                       full=False,
                       verbose=True):

        if max_turns is None:
            max_turns = float('inf')

        bucket_gen = self._apply_rules_bucket(axioms, full, verbose)

        for turn, bucket in bucket_gen:
            print '=== BUCKET %s: %s' % \
                (turn, '/'.join(str(b) for b in bucket))

            if th in bucket or turn >= max_turns:
                break

        return self.th_to_derivation(th, extract_from(th, bucket), verbose=True)

    @staticmethod
    def th_to_derivation(th, fth, verbose):
        if fth is None:
            if verbose:
                print '\n=== Theorem %s not found' % th
            return

        if verbose:
            print '\n=== Theorem %s found, derivation:' % th

        gen = 0
        report = [(gen, fth)]
        parents = fth.parents

        while True:
            gen += 1

            if not parents:
                f_gen = gen
                break

            for parent in parents:
                report.append([gen, parent])

            parents = [
                pp
                for parent in parents
                for pp in parent.parents
            ]

        report.reverse()

        if verbose:
            for gen, p in report:
                if p.parents:
                    print '[%-2s]  %-40s  for  %-25s  gives  %-20s' % \
                        (f_gen - gen, p.p_rule, ' and '.join(str(t) for t in p.parents), p)
                else:
                    print '[%-2s]  %-40s       %-25s  gives  %-20s' % \
                        (f_gen - gen, p.p_rule, '', p)

        return report


if __name__ == '__main__':
    import doctest
    doctest.testmod()
