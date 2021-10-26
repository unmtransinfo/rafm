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
from . import NAME
from . import VERSION
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
DEFAULT_MIN_COUNT = 20
DEFAULT_PLDDT_LOWER_BOUND = 80
DEFAULT_PLDDT_UPPER_BOUND = 100
DEFAULT_PLDDT_CRITERION = 91.2
MODULE_NAME = __name__.split(".")[0]
EMPTY_PATH = Path()

def bin_labels(bin_type, lower_bound):
    "Create labels for bins of different quantities."
    return f"pLDDT{lower_bound}_{bin_type}"

def extract_b_factors(file_path: Path) -> List[float]:
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
    return b_factor_list


def compute_plddt_stats(file_path,
                        lower_bound=DEFAULT_PLDDT_LOWER_BOUND,
                        min_count=DEFAULT_MIN_COUNT,
                        min_length=DEFAULT_MIN_LENGTH,
                        upper_bound=DEFAULT_PLDDT_UPPER_BOUND,
                        ):
    "Compute stats on pLDDTs for a PDB file specified by file_path."
    plddts = np.array(extract_b_factors(file_path))
    n_pts = len(plddts)
    mean = np.NAN
    median = np.NAN
    n_trunc_obs = np.NAN
    trunc_mean = np.NAN
    trunc_median = np.NAN
    trunc_frac = np.NAN
    if n_pts >= min_length:
        mean = plddts.mean().round(2)
        median = np.median(plddts).round(2)
        obs = plddts[plddts >= lower_bound]
        n_trunc_obs = len(obs)
        if len(obs) >= min_count:
            trunc_mean = obs.mean().round(2)
            trunc_median = np.median(obs).round(2)
            trunc_frac = round(n_trunc_obs/n_pts, 2)
    return n_pts, mean, median, n_trunc_obs, trunc_frac, trunc_mean, trunc_median, str(file_path)


@APP.command()
@STATS.auto_save_and_report
def plddt_truncate(
        pdb_list: Optional[List[Path]],
        criterion: Optional[float] = DEFAULT_PLDDT_CRITERION,
        min_length: Optional[int] = DEFAULT_MIN_LENGTH,
        min_count: Optional[int] = DEFAULT_MIN_COUNT,
        lower_bound: Optional[int] = DEFAULT_PLDDT_LOWER_BOUND,
        upper_bound: Optional[int] = DEFAULT_PLDDT_UPPER_BOUND,
        file_stem: Optional[str]=MODULE_NAME,
    ) -> None:
    """Calculate pLDDT80 from AlphaFold model file."""
    results = []
    criterion_label = bin_labels("median", lower_bound)
    stats_file_path = Path(f"{file_stem}_plddt_stats.tsv")
    n_models_in = len(pdb_list)
    STATS["models_in"] = Stat(n_models_in, desc="models read in")
    STATS["min_length"] = Stat(min_length, desc="minimum sequence length")
    STATS["min_count"] = Stat(min_length, desc="minimum # of selected residues")
    STATS["plddt_lower_bound"] = Stat(lower_bound, desc="minimum bound per-residue")
    STATS["plddt_upper_bound"] = Stat(upper_bound, desc="maximum bound per-residue")
    STATS["plddt_criterion"] = Stat(criterion, desc="minimum bounded median for selection")
    for file_path in pdb_list:
        results.append(compute_plddt_stats(file_path,
                                           lower_bound=lower_bound,
                                           min_count=min_count,
                                           min_length=min_length,
                                           upper_bound=upper_bound,
                                           ))
    stats = pd.DataFrame(
        results,
        columns=(
            [
             "residues_in_pLDDT",
             "pLDDT_mean",
             "pLDDT_median",
             bin_labels("count", lower_bound),
             bin_labels("frac", lower_bound),
             bin_labels("mean", lower_bound),
             criterion_label,
             "file"
             ]
        ),
    )
    logger.info(f"Writing stats to {stats_file_path}")
    stats.sort_values(by=criterion_label, inplace=True, ascending=False)
    stats = stats.reset_index()
    del stats["index"]
    passing = [False] * len(stats)
    for row_no, row in stats.iterrows():
        val = row[criterion_label]
        if pd.notnull(val) and (val >= criterion):
            passing[row_no] = True
    stats[f"{NAME}-{VERSION}"] = passing
    stats.to_csv(stats_file_path, sep="\t")
    total_residues = int(stats['residues_in_pLDDT'].sum())
    STATS["total_residues"] = Stat(total_residues,  desc="number of residues in all models")
    selected_stats = stats[stats[f"pLDDT{DEFAULT_PLDDT_LOWER_BOUND}_median"] >= criterion]
    n_models_selected = len(selected_stats)
    frac_models_selected = round(n_models_selected * 100./n_models_in, 0)
    STATS["models_selected"] = Stat(n_models_selected, desc=f"models passing {criterion_label}>={criterion}")
    STATS["model_selection_pct"] = Stat(frac_models_selected, desc="fraction of models passing, %")
    selected_residues = int(selected_stats['residues_in_pLDDT'].sum())
    STATS["selected_residues"] = Stat(selected_residues, desc="residues in passing models")


@APP.command()
@STATS.auto_save_and_report
def plddt_select_residues(
        criterion: Optional[float] = DEFAULT_PLDDT_CRITERION,
        min_length: Optional[int] = DEFAULT_MIN_LENGTH,
        min_count: Optional[int] = DEFAULT_MIN_COUNT,
        lower_bound: Optional[int] = DEFAULT_PLDDT_LOWER_BOUND,
        upper_bound: Optional[int] = DEFAULT_PLDDT_UPPER_BOUND,
        file_stem: Optional[str]=MODULE_NAME,
    ) -> None:
    stats_file_path = Path(f"{file_stem}_plddt_stats.tsv")
    stats = pd.read_csv(stats_file_path, sep="\t")
    criterion_label = bin_labels("median", lower_bound)
    count_label = bin_labels("count", lower_bound)
    plddt_list = []
    residue_list = []
    file_list = []
    for row_num, row in stats.iterrows():
        if (
            (row['residues_in_pLDDT'] >= min_length) and
            (row[criterion_label] >= criterion) and
            (row[count_label] >= min_count)
        ):
            plddts = extract_b_factors(Path(row["file"]))
            n_res = len(plddts)
            plddt_list += (plddts)
            residue_list += [i for i in range(n_res)]
            file_list += [row["file"]] * n_res
    df = pd.DataFrame({"UniProt": file_list,
                       "residue": residue_list,
                       "pLDDT": plddt_list})
    out_file_path = Path(f"{file_stem}_plddt{lower_bound}_{criterion}.tsv")
    logger.info(f"Writing residue file {out_file_path}")
    df.to_csv(out_file_path, sep="\t")
