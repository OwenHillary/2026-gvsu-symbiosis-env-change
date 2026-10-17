"""
Generate an EXP from a graph file, makes sure all changed spots are chnaged
"""

import argparse
import os
import sys
import json
import re
import shutil
from pathlib import Path

template_dir = Path(__file__).resolve().parent
exp_root = template_dir.parent

hpc_template_dir = template_dir / "HPC"

base_gen_slurm_fpath = hpc_template_dir / "base_gen_slurm.txt"
base_job_info_fpath = hpc_template_dir / "base_job_info.txt"



def get_graph_list(graph_fpath):
    """Read Graph.json and return its graph output IDs."""

    with graph_fpath.open("r", encoding="utf-8") as fp:
        graph_config = json.load(fp)

    graphs = graph_config.get("graphs-to-generate")
    graph_ids = []

    for graph in graphs:
        output_id = graph.get("output_id")
        graph_ids.append(output_id)

    return ",\n".join(
        f"        {json.dumps(graph_id)}"
        for graph_id in graph_ids
    )


def get_formated_graph_list(graph_fpath, prefix):
    """Read Graph.json and return its graph output IDs."""

    with graph_fpath.open("r", encoding="utf-8") as fp:
        graph_config = json.load(fp)

    graphs = graph_config.get("graphs-to-generate")
    graph_ids = []

    for graph in graphs:
        output_id = graph.get("output_id")
        graph_ids.append(output_id)

    return "\n".join(
        f'      {prefix} == "{graph_id}.mat" ~ "{graph_id}",'
        for graph_id in graph_ids
    )


def replace_placeholders(template, replacements):
    """Replace placeholders and reject any that remain."""

    for placeholder, value in replacements.items():
        template = template.replace(placeholder, value)

    return template



def main():
    # Configure command line arguments
    parser = argparse.ArgumentParser(description="Generate new EXP")
    parser.add_argument("--exp_name", type=str, required=True, help="What is the name of this exp")
    parser.add_argument("--graphs", type=str, required=True, help="What graphs are part of this EXP")
    parser.add_argument("--sym_type", type=str, required=True, help="What graphs are part of this EXP")
    parser.add_argument("--seed", type=int, required=True, help="What graphs are part of this EXP")

    args = parser.parse_args()

    # Paths

    exp_dir = exp_root / args.exp_name
    hpc_dir = exp_dir / "hpc"
    graph_fpath = template_dir / args.graphs

    analysis_template_dir = template_dir / "analysis"

    base_r_fpath = analysis_template_dir / "base_R.txt"
    base_run_agg_fpath = analysis_template_dir / "base_run_agg.txt"
    aggregate_fpath = analysis_template_dir / "aggregate.py"

    analysis_dir = exp_dir / "analysis"
        

    # Avoid accidentally writing into an existing experiment.
    if exp_dir.exists():
        parser.error(f"Exp already exists: {exp_dir}")

    # make sure we have a file
    if not graph_fpath.is_file():
        parser.error(f"Graphs not found: {graph_fpath}")

    # Set up are sym type
    if args.sym_type in ("p", "parasite"):
        sym_type = "parasite"
        reward_type = "flat"
    else:
        sym_type = "mutualist"
        reward_type = "diff"

    # Get Graph list
    # Get graph IDs as a Python list
    graph_list = get_graph_list(graph_fpath)
    formated_graph = get_formated_graph_list(graph_fpath, "SPATIAL_STRUCT_MODE")


    r_template = base_r_fpath.read_text(encoding="utf-8")

    r_script = replace_placeholders(r_template, {
        "<<exp_name>>": args.exp_name,
        "<<graph_levels>>": graph_list,
        "<<graph_case>>": formated_graph,
        })

    # Generate the aggregation shell script
    run_agg_template = base_run_agg_fpath.read_text(encoding="utf-8")

    run_agg_script = replace_placeholders(run_agg_template, {
        "<<exp_name>>": args.exp_name,})

    # Make the gen_slurm
    gen_slurm_template = base_gen_slurm_fpath.read_text(encoding="utf-8")
    gen_slurm = replace_placeholders(
        gen_slurm_template,
        {   "<<graph_list>>": graph_list,
            "<<sym_type>>": sym_type,
            "<<reward_type>>": reward_type,},)

    # Make the job Info
    job_info_template = base_job_info_fpath.read_text(encoding="utf-8")

    job_info = replace_placeholders(
        job_info_template,
        {   "<<exp_name>>": args.exp_name,
            "<<running_seed>>": str(args.seed),},)


    # Create output files.
    exp_dir.mkdir()
    hpc_dir.mkdir()
    try:
        # Copy unchanged HPC files and directories.
        static_files = [
            "base_gen_slurm.txt",
            "hillary-run-gen-slurm.sh",
        ]

        for filename in static_files:
            source = hpc_template_dir / filename
            shutil.copy2(source, hpc_dir / filename)

        config_source = hpc_template_dir / "config"
        shutil.copytree(config_source, hpc_dir / "config")

        (hpc_dir / "gen-slurm.py").write_text(gen_slurm, encoding="utf-8")

        (hpc_dir / "job-info.sh").write_text(job_info, encoding="utf-8")

        shutil.copy2(graph_fpath, hpc_dir / "Graph.json")

        # Create the Analysis directory
        analysis_dir.mkdir()

        shutil.copy2(aggregate_fpath, analysis_dir / "aggregate.py")

        (analysis_dir / f"{args.exp_name}.Rmd").write_text(r_script, encoding="utf-8")

        (analysis_dir / "run_agg.sh").write_text(run_agg_script, encoding="utf-8")


        print(f"Created experiment: {exp_dir}")
        print(f"Configured {len(graph_list.splitlines())} graph IDs.")
    
    except Exception:
        # Remove the incomplete experiment if generation fails.
        shutil.rmtree(exp_dir)
        raise

    print(f"Created experiment: {exp_dir}")
    print(f"Symbiont type: {sym_type}")
    print(f"Seed: {args.seed}")

if __name__ == "__main__":
    main()

    
    

