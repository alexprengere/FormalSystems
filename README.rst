
============
INSTALLATION
============

Install with::
    python setup.py install --user

A script should be put in ~/.local/bin, make sure this path is in your $PATH::
    export PATH=$PATH:~/.local/bin

Test::
    >>> from pprint import pprint
    >>> from formalsystems.formalsystems import FormalSystem, Theorem

MIU formal system::
    >>> fs = FormalSystem()
    >>> fs.read_formal_system('../examples_definition/MIU.yaml')
    >>> axioms = list(fs.iterate_over_schema())
    >>> print ' - '.join(str(a) for a in axioms)
    MI
    >>> r = fs.apply_rules_step(axioms, step=4, verbose=False)
    >>> for th in r:
    ...     print th
    MIIIIU
    MIIIIIIII
    MIIUIIU
    MIUIUIUIU
    MIU
    MUI

pg formal system::
    >>> fs = FormalSystem()
    >>> fs.read_formal_system('../examples_definition/pg.yaml')
    >>> r = fs.apply_rules_bucket_till(fs.iterate_over_schema(), max_turns=4, verbose=False)
    >>> for th in r:
    ...     print th
    -p----g-----
    ---p--g-----
    --p---g-----
    ----p-g-----
    >>> r = fs.apply_rules_bucket_till(fs.iterate_over_schema(), min_len=9, verbose=False)
    >>> for th in r:
    ...     print th
    -p---g----
    --p--g----
    ---p-g----

P formal system::
    >>> fs = FormalSystem()
    >>> fs.read_formal_system('../examples_definition/P.yaml')
    >>> r = fs.apply_rules_bucket_till(fs.iterate_over_schema(), max_turns=2, full=True, verbose=False)
    >>> for th in r:
    ...     print th
    --NDP---
    -SD--
    P--

Derivations::
    >>> fs = FormalSystem()
    >>> fs.read_formal_system('../examples_definition/P.yaml')
    >>> r = fs.derivation_asc(fs.iterate_over_schema(), Theorem('P-----'), full=True, max_turns=10, verbose=True)
    <BLANKLINE>
    ...
    === Theorem P----- found, derivation:
    ...

 Derivations::
    >>> fs = FormalSystem()
    >>> fs.read_formal_system('../examples_definition/MIU.yaml')
    >>> r = fs.derivation_step(fs.iterate_over_schema(), Theorem('MIUIU'), step=5, verbose=True)
    <BLANKLINE>
    ...
    === Theorem MIUIU found, derivation:
    ...
    >>> r = fs.derivation_step(fs.iterate_over_schema(), Theorem('MU'), step=5, verbose=True)
    <BLANKLINE>
    ...
    === Theorem MU not found
