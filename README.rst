=======================
FormalSystems |travis|_
=======================

.. _travis : https://travis-ci.org/alexprengere/FormalSystems
.. |travis| image:: https://api.travis-ci.org/alexprengere/FormalSystems.png

This is a Python implementation of *Douglas Hofstadter* formal systems, from his book *Gödel, Escher, Bach: An Eternal Golden Braid* (commonly *GEB*).

In fact, you may define your *own formal systems* using a quite simple syntax, close to free text.
Examples for *MIU*, *pg*, *fg* and *NDP* formal systems from the book are implemented in directory *definitions*.

A main Python script gives you possibilities to play with the formal system, including:

- axiom schema support (iteration, decision procedure)
- theorem step by step generation (using different algorithms)
- theorem derivation


------------------------
Formal system definition
------------------------

Examples
========

The *MIU* system may be define with:

.. code-block:: yaml

    axioms:
        - MI

    rules:
        - x is .*, xI => xIU
        - x is .*, Mx => Mxx
        - x is .*, y is .*, xIIIy => xUy
        - x y  .* , xUUy => xy

The underlying syntax is YAML (see raw format). You can define one or several axioms, or even an infinite number of axioms using a schema, as in the *pg* formal system:

.. code-block:: yaml

    axioms:
        - x is -+, xp-gx-

    rules:
        - x y z are -+, xpygz => xpy-gz-


Syntax
======

Axiom definitions should be formatted like this (``[]`` means this is optional):

.. code-block:: bash

 [def_1, [def_2, ...]] expr

Where:

- ``def_i`` is an optional definition of *wildcard*, using a regular expression, for example:

  - ".*" may be anything including the empty string
  - "-+" is a string composed of "-"

The definitions are written using ``char [is] regexp`` or ``char1 char2 [are] regexp`` if different wildcards have the same definition. Note that you should use only *one character* for wildcard definition.

- ``expr`` is the axiom expression

Rules for theorem production should be formatted like this:

.. code-block:: bash

 [def_1, [def_2, ...]] cond_1 [and cond_2 [and ...]] => th_1 [and th_2 [and ...]]

Where:

- ``def_i`` is the same as before
- ``cond_i`` is a required theorem, in order to produce new theorems (separated by *and* if several conditions)
- ``th_i`` is a produced theorems with the rule

------------
Installation
------------

Install with:

.. code-block:: bash

 $ python setup.py install --user

A script should be put in ``~/.local/bin``, make sure this path is in your ``$PATH``:

.. code-block:: bash

 $ export PATH=$PATH:~/.local/bin

-----
Tests
-----

If installation is successful, run the tests with:

.. code-block:: bash

 $ cd tests
 $ python test_formalsystems.py -v

-----------
Main script
-----------

After installation, you should have the main script ``FormalSystemsMain.py`` deployed somewhere where you ``$PATH`` points to, under the name ``FormalSystems``.
If it is not the case, you can always execute the script directly, assuming the dependencies are properly installed (just *pyyaml* and *LEPL*).

Usage of the main script is fully documented in ``--help`` argument.

You may generate theorems step by step if the number of axioms is finite:

.. code-block:: bash

 $ FormalSystems definitions/MIU.yaml --iteration 3 
 > Finite number of axioms, using step algorithm

 STEP 1: MI

 P  (1) x is .*, xI => xIU                    for  MI                         gives  MIU
 P  (2) x is .*, Mx => Mxx                    for  MI                         gives  MII
 .  (3) x is .*, y is .*, xIIIy => xUy        for  MI                       
 .  (4) x y  .* , xUUy => xy                  for  MI                       

 STEP 2: MIU/MII

 P  (1) x is .*, xI => xIU                    for  MII                        gives  MIIU
 .  (1) x is .*, xI => xIU                    for  MIU                      
 P  (2) x is .*, Mx => Mxx                    for  MII                        gives  MIIII
 P  (2) x is .*, Mx => Mxx                    for  MIU                        gives  MIUIU
 .  (3) x is .*, y is .*, xIIIy => xUy        for  MII                      
 .  (3) x is .*, y is .*, xIIIy => xUy        for  MIU                      
 .  (4) x y  .* , xUUy => xy                  for  MII                      
 .  (4) x y  .* , xUUy => xy                  for  MIU                      

 STEP 3: MIIU/MIIII/MIUIU

Or using a bucket where axioms are thrown and theorems computed iteratively if the number of axioms is infinite:

.. code-block:: bash

 $ FormalSystems definitions/pg.yaml --iteration 4
 > Infinite number of axioms, using bucket algorithm

 [Adding -p-g-- to bucket]

 === BUCKET 1: -p-g--

 P  (1) x y z are -+, xpygz => xpy-gz-        for  -p-g--                     gives  -p--g---
 [Adding --p-g--- to bucket]

 === BUCKET 2: -p--g---/--p-g---

 P  (1) x y z are -+, xpygz => xpy-gz-        for  -p--g---                   gives  -p---g----
 P  (1) x y z are -+, xpygz => xpy-gz-        for  --p-g---                   gives  --p--g----
 [Adding ---p-g---- to bucket]

 === BUCKET 3: -p---g----/--p--g----/---p-g----

 P  (1) x y z are -+, xpygz => xpy-gz-        for  -p---g----                 gives  -p----g-----
 P  (1) x y z are -+, xpygz => xpy-gz-        for  ---p-g----                 gives  ---p--g-----
 P  (1) x y z are -+, xpygz => xpy-gz-        for  --p--g----                 gives  --p---g-----
 [Adding ----p-g----- to bucket]

 === BUCKET 4: -p----g-----/---p--g-----/--p---g-----/----p-g-----

Options are available to display theorem derivation as well:

.. code-block:: bash

 $ FormalSystems definitions/NDP.yaml --quiet --derivation P-----
 > Infinite number of axioms, using bucket algorithm
 > Rule with several parents, using recursivity

 === BUCKET 1: --NDP-
 === BUCKET 2: --NDP---/-SD--/P--
 === BUCKET 3: --NDP-----/---SD--/---NDP--
 === BUCKET 4: --NDP-------/---NDP-----/-----SD--/P---/---NDP-
 === BUCKET 5: --NDP---------/---NDP--------/---NDP----/-------SD--/-----SD---/-SD---/----NDP---
 === BUCKET 6: ---NDP-----------/----NDP-------/---NDP-------/--NDP-----------/---------SD--/----NDP-
 === BUCKET 7: ----NDP-----------/----NDP-----/---NDP----------/---NDP--------------/--NDP-------------/-----------SD--/-------SD---/-SD----/----NDP--
 === BUCKET 8: ----NDP---------/----NDP---------------/---NDP-------------/---NDP-----------------/--NDP---------------/----NDP------/-------------SD--/-------SD----/-----SD----/-----------SD---/-----NDP-
 === BUCKET 9: --NDP-----------------/-----NDP------/----NDP-------------/---NDP--------------------/---NDP----------------/----NDP----------/----NDP-------------------/---------------SD--/-SD-----/-------------SD---/-----------SD----/P-----/-----NDP--

 === Theorem P----- found, derivation:
 [1 ]  Axiom                                                                     gives  --NDP-              
 [2 ]  (1) x y are -+, xNDPy => xNDPxy           for  --NDP-                     gives  --NDP---            
 [3 ]  Axiom                                                                     gives  ---NDP--            
 [3 ]  (1) x y are -+, xNDPy => xNDPxy           for  --NDP---                   gives  --NDP-----          
 [4 ]  Axiom                                                                     gives  ----NDP-            
 [4 ]  (1) x y are -+, xNDPy => xNDPxy           for  ---NDP--                   gives  ---NDP-----         
 [4 ]  (2) z is -+, --NDPz => zSD--              for  --NDP-----                 gives  -----SD--           
 [5 ]  (1) x y are -+, xNDPy => xNDPxy           for  ----NDP-                   gives  ----NDP-----        
 [5 ]  (3) x z are -+, zSDx and x-NDPz => zSDx-  for  -----SD-- and ---NDP-----  gives  -----SD---          
 [6 ]  (3) x z are -+, zSDx and x-NDPz => zSDx-  for  -----SD--- and ----NDP-----  gives  -----SD----         
 [7 ]  (4) z is -+, z-SDz => Pz-                 for  -----SD----                gives  P-----


----------
Python API
----------

Some tests using *doctests*:

.. code-block:: python

 >>> from formalsystems.formalsystems import FormalSystem, Theorem

MIU formal system:

.. code-block:: python

 >>> fs = FormalSystem()
 >>> fs.read_formal_system('./definitions/MIU.yaml')
 >>> r = fs.apply_rules_step(fs.iterate_over_schema(), step=4, verbose=False)
 STEP 1: MI
 STEP 2: MIU/MII
 STEP 3: MIIU/MIIII/MIUIU
 STEP 4: MIIIIU/MIIIIIIII/MIIUIIU/MIUIUIUIU/MIU/MUI
 >>> print [str(a) for a in fs.iterate_over_schema()]
 ['MI']

pg formal system:

.. code-block:: python

 >>> fs = FormalSystem()
 >>> fs.read_formal_system('./definitions/pg.yaml')
 >>> r = fs.apply_rules_bucket_till(fs.iterate_over_schema(), max_turns=4, verbose=False)
 === BUCKET 1: -p-g--
 === BUCKET 2: -p--g---/--p-g---
 === BUCKET 3: -p---g----/--p--g----/---p-g----
 === BUCKET 4: -p----g-----/---p--g-----/--p---g-----/----p-g-----
 >>> r = fs.apply_rules_bucket_till(fs.iterate_over_schema(), min_len=9, verbose=False)
 === BUCKET 1: -p-g--
 === BUCKET 2: -p--g---/--p-g---
 === BUCKET 3: -p---g----/--p--g----/---p-g----

NDP formal system:

.. code-block:: python

 >>> fs = FormalSystem()
 >>> fs.read_formal_system('./definitions/NDP.yaml')
 >>> r = fs.apply_rules_bucket_till(fs.iterate_over_schema(), max_turns=2, full=True, verbose=False)
 === BUCKET 1: --NDP-
 === BUCKET 2: --NDP---/-SD--/P--

Successful derivation:

.. code-block:: python

 >>> fs = FormalSystem()
 >>> fs.read_formal_system('./definitions/NDP.yaml')
 >>> r = fs.derivation_asc(fs.iterate_over_schema(), Theorem('P-----'), full=True, max_turns=10)
 <BLANKLINE>
 ...
 === Theorem P----- found, derivation:
 ...

Failed derivation:

.. code-block:: python

 >>> fs = FormalSystem()
 >>> fs.read_formal_system('./definitions/MIU.yaml')
 >>> r = fs.derivation_step(fs.iterate_over_schema(), Theorem('MIUIU'), step=5)
 <BLANKLINE>
 ...
 === Theorem MIUIU found, derivation:
 ...
 >>> r = fs.derivation_step(fs.iterate_over_schema(), Theorem('MU'), step=5)
 <BLANKLINE>
 ...
 === Theorem MU not found

