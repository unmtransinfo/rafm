================================
rafm Reliable AlphaFold Measures
================================

|PyPI| |Status| |Python Version| |License|

|Read the Docs| |Tests| |Codecov|

|pre-commit| |Black|

.. |PyPI| image:: https://img.shields.io/pypi/v/rafm.svg
   :target: https://pypi.org/project/rafm/
   :alt: PyPI
.. |Status| image:: https://img.shields.io/pypi/status/rafm.svg
   :target: https://pypi.org/project/rafm/
   :alt: Status
.. |Python Version| image:: https://img.shields.io/pypi/pyversions/rafm
   :target: https://pypi.org/project/rafm
   :alt: Python Version
.. |License| image:: https://img.shields.io/pypi/l/rafm
   :target: https://opensource.org/licenses/MIT
   :alt: License
.. |Read the Docs| image:: https://img.shields.io/readthedocs/rafm/latest.svg?label=Read%20the%20Docs
   :target: https://rafm.readthedocs.io/
   :alt: Read the documentation at https://rafm.readthedocs.io/
.. |Tests| image:: https://github.com/unmtransinfo/rafm/workflows/Tests/badge.svg
   :target: https://github.com/unmtransinfo/rafm/actions?workflow=Tests
   :alt: Tests
.. |Codecov| image:: https://codecov.io/gh/unmtransinfo/rafm/branch/main/graph/badge.svg
   :target: https://codecov.io/gh/unmtransinfo/rafm
   :alt: Codecov
.. |pre-commit| image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white
   :target: https://github.com/pre-commit/pre-commit
   :alt: pre-commit
.. |Black| image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/psf/black
   :alt: Black

.. image:: https://raw.githubusercontent.com/unmtransinfo/rafm/master/docs/_static/calmodulin.png
   :target: https://raw.githubusercontent.com/unmtransinfo/rafm/master/docs/_static/calmodulin.png
   :alt: AlphaFold model and two crystal structures of calmodulin

*rafm* computes per-model measures associated with atomic-level accuracy for
AlphaFold models from *pLDDT* confidence scores.  Outputs are to a tab-separated
file.


Installation
------------

You can install *rafm* via pip_ from PyPI_:

.. code:: console

   $ pip install rafm


Usage
-----
*rafm --help* lists all commands. Current commands are:

* *plddt-stats*
    Calculate stats on bounded pLDDTs from list of AlphaFold model files.
    in PDB format.

    Options:

        * *--criterion FLOAT*
            The cutoff value on truncated pLDDT for possible utility. [default: 91.2]
        * *--min-length INTEGER*
            The minimum sequence length for which to calculate truncated stats.
            [default: 20]
        * *--min-count INTEGER*
            The minimum number of truncated *pLDDT* values for which to calculate stats.
            [default: 20]
        * *--lower-bound INTEGER*
            The *pLDDT* value below which stats will not be calculated. [default: 80]
        * *--upper-bound INTEGER*
            The *pLDDT* value above which stats will not be calculated. [default: 100]
        * *--file-stem TEXT*
            Output file name stem. [default: rafm]

    Output columns (where *NN* is the bounds specifier, default: 80):

        * *residues_in_pLDDT*
            The number of residues in the AlphaFold model.
        * *pLDDT_mean*
            The mean value of pLDDT over all residues.
        * *pLDDT_median*
            The median value of pLDDT over all residues.
        * *pLDDTNN_count*
            The number of residues within bounds.
        * *pLDDTNN_frac*
            The fraction of pLDDT values within bounds, if the
            count is greater than the minimum.
        * *pLDDTNNN_mean*
            The mean of pLDDT values within bounds, if the
            count is greater than the minimum.
        * *pLDDTNN_median*
            The median of pLDDT values within bounds, if the
            count is greater than the minimum.
        * *LDDT_expect*
            The expectation value of global *LDDT* over the
            residues with *LDDT* within bounds.  Only
            produced if default bounds are used.
        * *passing*
            True if the model passed the criterion, False
            otherwise.  Only produced if default bounds are
            used.
        * *file*
            The path to the model file.

* *plddt-select-residues*
    Writes a tab-separated file of residues from passing models,
    using an input file of values selected by *plddt-stats*.
    Input options are the same as *plddt-stats*.

    Output columns:

        * *file*
            Path to the model file.
        * *residue*
            Residue number, starting from 0 and numbered
            sequentially.  Note that *all* residues will be
            written, regardless of bounds set.
        * *pLDDT*
            pLDDT value for that residue.

Statistical Basis
-----------------
The default parameters were chosen to select for *LDDT* values of greater
than 80 on a set of crystal structures obtained since AlphaFold was trained.  The
distributions of *LDDT* scores for the passing and non-passing sets, along
with an (overlapping) set of PDB files at 100% sequence identity over
at least 80% of the sequence looks like this:

.. image:: https://raw.githubusercontent.com/unmtransinfo/rafm/master/docs/_static/lddt_dist.png
   :target: https://raw.githubusercontent.com/unmtransinfo/rafm/master/docs/_static/lddt_dist.png
   :alt: Distribution of high-scoring, low-scoring, and high-similarity structures

When applied to set of "dark" genomes with no previous PDB entries, the distributions of
median *pLDDT* scores with a lower bound of 80 and per-residue *pLDDT* scores looks like
this:
.. image:: https://raw.githubusercontent.com/unmtransinfo/rafm/master/docs/_static/tdark_dist.png
   :target: https://raw.githubusercontent.com/unmtransinfo/rafm/master/docs/_static/tdark_dist.png
   :alt: Distribution of *pLDDT80* scores and per-residue *pLDDT* scores


Contributing
------------

Contributions are very welcome.
To learn more, see the `Contributor Guide`_.


License
-------

Distributed under the terms of the `MIT license`_,
*rafm* is free and open source software.


Issues
------

If you encounter any problems,
please `file an issue`_ along with a detailed description.


Credits
-------

This project was generated from the `UNM Translational Informatics Python Cookiecutter`_ template.

*rafm* was written by Joel Berendzen and Jessica Binder.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _MIT license: https://opensource.org/licenses/MIT
.. _PyPI: https://pypi.org/
.. _UNM Translational Informatics Python Cookiecutter: https://github.com/unmtransinfo/cookiecutter-unmtransinfo-python
.. _file an issue: https://github.com/unmtransinfo/rafm/issues
.. _pip: https://pip.pypa.io/
.. github-only
.. _Contributor Guide: CONTRIBUTING.rst
.. _Usage: https://rafm.readthedocs.io/en/latest/usage.html
