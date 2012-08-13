
=============
FormalSystems
=============

A Python implementation of Douglas Hofstadter formal systems, from his book "Gödel, Escher, Bach".


Formal systems
==============

You may define your own formal systems using a quite simple syntax, close to free text.
Examples for *MIU*, *pg*, *fg* and *NDP* formal systems from the book are implemented in *examples_definition*.

Example
-------

The *MIU* system may be define with:

    axioms:
        - MI

    rules:
        - x is .*, xI => xIU
        - x is .*, Mx => Mxx
        - x is .*, y is .*, xIIIy => xUy
        - x y  .* , xUUy => xy

The underlying syntax is YAML (see raw format). You can define one or several axioms, or even an infinite number of axioms using a schema, as in the *pg* formal system:

    axioms:
        - x is -+, xp-gx-

    rules:
        - x y z are -+, xpygz => xpy-gz-


Syntax
------

Axiom definitions should be formatted like this (*[]* means optinality):

    [def_1, [def_2, ...]] expr

Where:
    - *def_i* are optional definitions of "wildcards", using regular expression syntax, for example:
        - *.** may be anything including the empty string
        - *-+* is a string composed of *-*
      The definitions are written using "char [is] regexp" or "char1 char2 [are] regexp" if different wildcards have the same definition. Note that you will only use *one character* for wildcard definition.
    - *expr* is the axiom expression

Rules for theorem production should be formatted like this: 

    [def_1, [def_2, ...]] cond_1 [and cond_2 [and ...]] => th_1 [and th_2 [and ...]]

Where:
    - *def_i* are the same as before
    - *cond_i* are required theorems, in order to produce new theorems (separated by *and* if several conditions)
    - *th_i* are produced theorems with the rule



Installation
============


Install with:

    `python setup.py install --user`

A script should be put in ~/.local/bin, make sure this path is in your $PATH::

    `export PATH=$PATH:~/.local/bin`


Tests
=====

If installation is successful, run the tests with:

    `% cd tests`
    `% python test_formalsystems.py -v`


Main script
===========

After installation, you should have the main script *FormalSystemsMain.py* deployed somewhere where you *$PATH* points to, under the name *FormalSystems*.
If it is not the case, you can always call the script directly, assuming the dependencies are properly installed (just *pyyaml* and *LEPL*).

Usage of the main script is fully documented in *--help* argument. 

You may generate theorems step by step if the number of axioms is finite, or using a bucket where axioms are thrown and theorems computed iteratively otherwise.

Options are available to display theorem derivation as well.


Python API
==========

Some tests using *doctests*::

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
