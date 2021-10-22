# -*- coding: utf-8 -*-
"""Find hydrated waters in structure."""
# standard library imports
from pathlib import Path
from typing import List
from typing import Optional
from typing import Tuple


# 3rd-party imports
import numpy as np
import numpy.typing as npt
import pandas as pd
from loguru import logger
from statsdict import Stat

# module imports
from .common import APP
from .common import STATS

# global constants
ATOM_REC: str = "ATOM"
ATOM_START_POS: int = 13
ATOM_STOP_POS: int = 15
ATOMS: Tuple[str, ...] = ("CA",)
B_FACTOR_START: int = 61
B_FACTOR_STOP: int = 65
REC_TYPE_START:int = 0
REC_TYPE_STOP:int = 4
DEFAULT_MIN_LENGTH = 20
DEFAULT_BINS = [80]
DEFAULT_PLDDT_TRUNC = 80
DEFAULT_PLDDT_CRITERION = 80

def bin_labels(bin_type, bins):
    "Create labels for bins of different quantities."
    return [f"pLDDT{n}_{bin_type}" for n in bins]

def extract_b_factors(file_path: Path) -> npt.ArrayLike:
    "Return an array of B factors from a PDB file specified by file_path."
    if not file_path.exists():
        raise ValueError(f"PDB file {file_path} does not exist")
    with file_path.open("rU") as f:
        # parse b_factors out of PDB file
        b_factor_list = [
            float(rec[B_FACTOR_START:B_FACTOR_STOP])
            for rec in f.readlines()
            if (
                (len(rec) > B_FACTOR_STOP)
                and (rec[REC_TYPE_START:REC_TYPE_STOP] == ATOM_REC)
                and (rec[ATOM_START_POS:ATOM_STOP_POS] in ATOMS)
            )
        ]
    return np.array(b_factor_list)

def compute_plddt_stats(file_path,
                        dist_path=None,
                        select_path=None,
                        plddt_trunc=DEFAULT_PLDDT_TRUNC,
                        plddt_criterion=DEFAULT_PLDDT_CRITERION,
                        bins=DEFAULT_BINS,
                        min_length=DEFAULT_MIN_LENGTH):
    "Compute stats on pLDDTs for a PDB file specified by file_path."
    n_bins = len(bins)
    empty_bins = [np.NAN] * n_bins
    plddts = extract_b_factors(file_path)
    n_pts = len(plddts)
    if n_pts >= min_length:
        mean = plddts.mean().round(2)
        median = np.median(plddts).round(2)
        hist = np.histogram(plddts, bins=bins + [100])[0] / n_pts
        cum_hist = np.flip(np.cumsum(np.flip(hist))).round(2)
        trunc_means = empty_bins.copy()
        trunc_medians = empty_bins.copy()
        for i, bin_floor in enumerate(bins):
            obs = plddts[plddts > bin_floor]
            if len(obs):
                trunc_means[i] = obs.mean().round(2)
                trunc_medians[i] = np.median(obs).round(2)
                if ((select_path is not None) and
                        (bin_floor == plddt_trunc) and
                        (trunc_medians[i] >= plddt_criterion)):
                    with select_path.open("a") as f:
                        f.write("".join([f"{file_path.name}\t{val}\n" for val in plddts]))
        if dist_path is not None:
            with dist_path.open("a") as f:
                f.write("".join([f"{val}\n" for val in plddts]))
    else:
        mean = np.NAN
        median = np.NAN
        cum_hist = empty_bins
        trunc_means = empty_bins
        trunc_medians = empty_bins
    return str(file_path), n_pts, mean, median, *cum_hist, *trunc_means, *trunc_medians


@APP.command()
@STATS.auto_save_and_report
def plddt80(pdb_list: Optional[List[Path]]) -> None:
    """Calculate pLDDT80 from AlphaFold model file."""
    results = []
    for file_path in pdb_list:
        results.append(compute_plddt_stats(file_path))
    stats = pd.DataFrame(
        results,
        columns=(
            ["file", "residues_in_pLDDT", "pLDDT_mean", "pLDDT_median"]
            + bin_labels("frac", DEFAULT_BINS)
            + bin_labels("mean", DEFAULT_BINS)
            + bin_labels("median", DEFAULT_BINS)
            ),
        )
    stats_file_path = Path("rafm_stats.tsv")
    logger.info(f"Writing stats to {stats_file_path}")
    stats.to_csv(stats_file_path, sep="\t")
    total_residues = int(stats['residues_in_pLDDT'].sum())
    STATS["total_residues"] = Stat(total_residues)
    select_stats = stats[stats[f"pLDDT{DEFAULT_PLDDT_TRUNC}_median"] >= DEFAULT_PLDDT_CRITERION]
    STATS["selected_residues"] = Stat(int(select_stats['residues_in_pLDDT'].sum()))
    STATS["n"] = Stat(len(pdb_list))