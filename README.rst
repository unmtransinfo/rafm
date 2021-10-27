================================
rafm Reliable AlphaFold Measures
================================
| |PyPI| |Python Version| |Repo| |Downloads| |Dlrate|

| |License| |Tests| |Coverage| |Codacy| |Issues| |Health|

.. |PyPI| image:: https://img.shields.io/pypi/v/rafm.svg
   :target: https://pypi.org/project/rafm/
.. |Python Version| image:: https://img.shields.io/pypi/pyversions/rafm
   :target: https://pypi.org/project/rafm
   :alt: Supported Python Versions
.. |Repo| image:: https://img.shields.io/github/last-commit/unmtransinfo/rafm
    :target: https://github.com/unmtransinfo/rafm
    :alt: GitHub repository
.. |Downloads| image:: https://pepy.tech/badge/rafm
     :target: https://pepy.tech/project/rafm
     :alt: Download stats
.. |Dlrate| image:: https://img.shields.io/pypi/dm/rafm
   :target: https://github.com/unmtransinfo/rafm
   :alt: PYPI download rate
.. |License| image:: https://img.shields.io/badge/License-BSD%203--Clause-blue.svg
    :target: https://github.com/unmtransinfo/rafm/blob/master/LICENSE.txt
    :alt: License terms
.. |Tests| image:: https://github.com/unmtransinfo/rafm/workflows/Tests/badge.svg
   :target: https://github.com/unmtransinfo/rafm/actions?workflow=Tests
   :alt: Tests
.. |Coverage| image:: https://codecov.io/gh/unmtransinfo/rafm/branch/main/graph/badge.svg
    :target: https://codecov.io/gh/unmtransinfo/rafm
    :alt: Codecov.io test coverage
.. |Codacy| image:: https://api.codacy.com/project/badge/Grade/703bc20047ed41bd873901bf596da166
    :target: https://www.codacy.com/gh/unmtransinfo/rafm?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=unmtransinfo/rafm&amp;utm_campaign=Badge_Grade
    :alt: Codacy.io grade
.. |Issues| image:: https://img.shields.io/github/issues/unmtransinfo/rafm.svg
    :target:  https://github.com/unmtransinfo/rafm/issues
    :alt: Issues reported
.. |Read the Docs| image:: https://img.shields.io/readthedocs/rafm/latest.svg?label=Read%20the%20Docs
   :target: https://rafm.readthedocs.io/
   :alt: Read the documentation at https://rafm.readthedocs.io/
.. |Health| image:: https://snyk.io/advisor/python/rafm/badge.svg
  :target: https://snyk.io/advisor/python/rafm
  :alt: Snyk health

.. image:: https://raw.githubusercontent.com/unmtransinfo/rafm/master/docs/_static/calmodulin.png
   :target: https://raw.githubusercontent.com/unmtransinfo/rafm/master/docs/_static/calmodulin.png
   :alt: AlphaFold model and two crystal structures of calmodulin

*rafm* computes per-model measures associated with atomic-level accuracy for
AlphaFold models from *pLDDT* confidence scores.  Outputs are to a
tab-separated file.


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
            The cutoff value on truncated pLDDT for possible utility.
            [default: 91.2]
        * *--min-length INTEGER*
            The minimum sequence length for which to calculate truncated stats.
            [default: 20]
        * *--min-count INTEGER*
            The minimum number of truncated *pLDDT* values for which to
            calculate stats [default: 20]
        * *--lower-bound INTEGER*
            The *pLDDT* value below which stats will not be calculated.
            [default: 80]
        * *--upper-bound INTEGER*
            The *pLDDT* value above which stats will not be calculated.
            [default: 100]
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

* *plddt-plot-dists*
    Plot the distributions on the bounded pLDDT and residues in
    models that pass the selection criteria.

    Input Options:
        * *out-file-type*
            Plot file extension of a type that *matplotlib* understands,
            (e.g., 'jpg', 'pdf') [default: png]
        * *residue-criterion*
            Per-residue cutoff on usability (for plot only).

    Outputs:
        When applied to set of "dark" genomes with no previous PDB entries, the
        distributions of median *pLDDT* scores with a lower bound of 80 and
        per-residue *pLDDT* scores with a minimum of 80 looks like this:

        .. image:: https://raw.githubusercontent.com/unmtransinfo/rafm/master/docs/_static/tdark_dist.png
            :target: https://raw.githubusercontent.com/unmtransinfo/rafm/master/docs/_static/tdark_dist.png
            :alt: Distribution of *pLDDT80* scores and per-residue *pLDDT* scores


Statistical Basis
-----------------
The default parameters were chosen to select for *LDDT* values of greater
than 80 on a set of crystal structures obtained since AlphaFold was trained.
The distributions of *LDDT* scores for the passing and non-passing sets, along
with an (overlapping) set of PDB files at 100% sequence identity over
at least 80% of the sequence looks like this:

.. image:: https://raw.githubusercontent.com/unmtransinfo/rafm/master/docs/_static/lddt_dist.png
   :target: https://raw.githubusercontent.com/unmtransinfo/rafm/master/docs/_static/lddt_dist.png
   :alt: Distribution of high-scoring, low-scoring, and high-similarity structures

The markers on the *x*-axis refer to the size of conformational changes
observed in conformational changes in various protein crystal structures:

* *CALM*
    Between calcum-bound and calcium-free calmodulin
    (depicted in the logo image above).
* *ERK2*
    Between unphosphorylated and doubly-phosphorylated ERK2 kinase.
* *HB*
    Between R- and T-state hemoglobin
* *MB*
    Between carbonmonoxy- and deoxy-myoglobin

The value of *LDDT* >= 80 we selected as the minimum value that was likely to
prove useful for virtual screening.  The per-residue value of *pLDDT* >= 80
was also chosen as the minimum likely to give the correct side-chain rotamers
for a surface defined by contacts between two residues.


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

This project was generated from the
`UNM Translational Informatics Python Cookiecutter`_ template.

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
