#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse

from formalsystems.formalsystems import FormalSystem, Theorem


def main():
    parser = argparse.ArgumentParser(description='Formal system processor.')

    parser.add_argument('yaml_file',
                        metavar='file',
                        type=str,
                        help='path to YAML definition of the formal system')

    parser.add_argument('-d', '--derivation',
                        dest='theorem',
                        type=Theorem,
                        default=None,
                        help='print theorem derivation')

    parser.add_argument('-s', '--schema',
                        action='store_true',
                        default=None,
                        help='iteration over axioms schema')

    parser.add_argument('-a', '--axiom',
                        dest='axiom',
                        type=Theorem,
                        default=None,
                        help='check axiom definition')

    parser.add_argument('-i', '--iteration',
                        type=int,
                        default=10,
                        help='define max iteration (default 10)')

    parser.add_argument('-q', '--quiet',
                        action='store_true',
                        help='quiet mode')

    args = parser.parse_args()

    fs = FormalSystem()
    fs.read_formal_system(args.yaml_file)

    infinite_axioms = any(ax.wildcards for ax in fs.axioms)
    and_in_rule = any(len(r.oldts) > 1 for r in fs.rules)

    if args.schema is not None:
        print '> Generating axioms schema'
        for ax in fs.iterate_over_schema(max_iter=args.iteration):
            print ax
        return

    if args.axiom is not None:
        fs.is_axiom(args.axiom, verbose=not(args.quiet))
        return

    if infinite_axioms:
        print '> Infinite number of axioms, using bucket algorithm'
    else:
        print '> Finite number of axioms, using step algorithm'

    if and_in_rule:
        print '> Rule with several parents, using recursivity'
    print

    # Main
    if args.theorem is None:
        if infinite_axioms:
            fs.apply_rules_bucket_till(fs.iterate_over_schema(),
                                       min_len=None,  # wont apply
                                       max_turns=args.iteration,
                                       full=and_in_rule,
                                       verbose=not(args.quiet))
        else:
            fs.apply_rules_step(fs.iterate_over_schema(),
                                step=args.iteration,
                                verbose=not(args.quiet))
    else:
        if infinite_axioms:
            fs.derivation_asc(fs.iterate_over_schema(),
                              args.theorem,
                              max_turns=args.iteration,
                              full=and_in_rule,
                              verbose=not(args.quiet))
        else:
            fs.derivation_step(fs.iterate_over_schema(),
                               args.theorem,
                               step=args.iteration,
                               verbose=not(args.quiet))


if __name__ == '__main__':
    main()
