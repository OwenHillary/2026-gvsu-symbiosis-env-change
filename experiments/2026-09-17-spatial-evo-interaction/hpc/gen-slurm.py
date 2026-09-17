'''
Generate slurm job submission scripts - one per condition
'''

import argparse
import os
import sys
import pathlib
from pyvarco import CombinationCollector

# Add scripts directory to path, import utilities from scripts directory.
sys.path.append(
    os.path.join(
        pathlib.Path(os.path.dirname(os.path.abspath(__file__))).parents[2],
        "scripts"
    )
)
import utilities as utils

# Default configuration values
default_seed_offset = 1000
default_account = None
default_num_replicates = 30
default_job_time_request = "8:00:00"
default_job_mem_request = "4G"

executable = "symbulation_sgp"

base_slurm_script_fpath = "./base_slurm_script.txt"

# Create combos
combos = CombinationCollector()

# Parameters that do not change across treatments for this experiment.
fixed_parameters = {
    # -- General parameters --
    "DATA_INT": "100",
    "PRINT_INTERVAL": "100",
    "UPDATES": "200000",
    "WORLD_WIDTH": "100",
    "WORLD_HEIGHT": "100",
    "INIT_POP_SIZE": "-1",
    "HOST_AGE_MAX": "-1",
    "SYM_AGE_MAX": "-1",
    # -- SGP mode general --
    "CYCLES_PER_UPDATE": "16",
    "SGP_MUT_PER_BIT_RATE": "0.005",
    "FIND_NEIGHBOR_HOST_ATTEMPTS": "5",
    "TASK_PROFILE_MODE": "self-all",
    "HOST_PROGRAM_PATH": "nand-program-100.json",
    "SYM_PROGRAM_PATH": "nand-program-100.json",
    "TASK_IO_BANK_SIZE": "50000",
    "TASK_IO_UNIQUE_OUTPUT": "1",
    # -- Task environment + reproduction --
    "TASK_ENV_CFG_PATH": "env-diff-rewards.json",
    "HORIZ_TRANS": "1",
    "SYM_VERT_TRANS_RES": "0",
    "OUSTING": "1",
    "VT_TASK_MATCH": "0",
    "HOST_MIN_CYCLES_BEFORE_REPRO": "0",
    "SYM_MIN_CYCLES_BEFORE_REPRO": "0",
    "HOST_REPRO_RES": "256",
    "SYM_HORIZ_TRANS_RES": "128",
    # -- Host-endosymbiont interactions --
    "ENABLE_STRESS": "0",
    "ENABLE_NUTRIENT": "0",
    "ENABLE_HEALTH": "1",
    "PARASITE_BASE_CYCLE_PROP": "0.5",
    "HEALTH_INTERACTION_CHANCE": "1.0",
    "TASK_PROFILE_COMPATIBILITY_MODE": "task-any-match",
    "HORIZONTAL_TRANSMISSION_COMPATIBILITY_MODE": "task-profile-strictly-stronger-match",
    # -- Evolvable interaction value --
    "HOST_INT": "-2",
    "SYM_INT": "-2",
    "MUTATION_SIZE": "0.02",
    "MUTATION_RATE": "1"
}

special_decorators = [
    "__COPY_OVER",
    "__DYNAMIC"
]
combos.register_var("symbiont__COPY_OVER")
combos.register_var("cycle_prop__COPY_OVER")
combos.register_var("interaction_multiplier__COPY_OVER")
combos.register_var("task_credit__COPY_OVER")
combos.register_var("EVENTS_CFG_PATH")
combos.register_var("spatial_structure__DYNAMIC")
combos.register_var("VERTICAL_TRANSMISSION")

combos.add_val(
    "symbiont__COPY_OVER",
    [
        "-START_MOI 1 -HEALTH_TYPE interaction-value"
    ]
)

combos.add_val(
    "VERTICAL_TRANSMISSION",
    ["0.0", "0.1", "0.2", "0.3", "0.4", "0.5", "0.6", "0.7", "0.8", "0.9", "1.0"]
)

combos.add_val(
    "cycle_prop__COPY_OVER",
    ["-PARASITE_CYCLE_LOSS_PROP 0.75 -MUTUALIST_CYCLE_GAIN_PROP 0.75"]
)

combos.add_val(
    "interaction_multiplier__COPY_OVER",
    [
        "-MUTUALIST_CYCLE_DONATE_MULTIPLIER 4 -PARASITE_CYCLE_STEAL_MULTIPLIER 4",
    ]
)

combos.add_val(
    "task_credit__COPY_OVER",
    [
        "-HOST_ONLY_FIRST_TASK_CREDIT 1 -SYM_ONLY_FIRST_TASK_CREDIT 1"
    ]
)

combos.add_val(
    "EVENTS_CFG_PATH",
    [
        "events-constant.json"
    ]
)

combos.add_val(
    "spatial_structure__DYNAMIC",
    [
        "toroidal-lattice_100x100",
        "toroidal-lattice_50x200",
        "toroidal-lattice_20x500",
        "toroidal-lattice_10x1000",
        "toroidal-lattice_4x2500",
        "toroidal-lattice_2x5000",
        "cycle",
        "well-mixed"
    ]
)


def main():
    # Configure command line arguments
    parser = argparse.ArgumentParser(description="Generate SLURM submission scripts.")
    parser.add_argument("--data_dir", type=str, help="Where is the base output directory for each run?")
    parser.add_argument("--config_dir", type=str, help="Where is the configuration directory for experiment?")
    parser.add_argument("--replicates", type=int, default=default_num_replicates, help="How many replicates should we run of each condition?")
    parser.add_argument("--job_dir", type=str, default=None, help="Where to output these job files? If none, put in 'jobs' directory inside of the data_dir")
    parser.add_argument("--seed_offset", type=int, default=default_seed_offset, help="Value to offset random number seeds by")
    parser.add_argument("--hpc_account", type=str, default=default_account, help="Value to use for the slurm ACCOUNT")
    parser.add_argument("--time_request", type=str, default=default_job_time_request, help="How long to request for each job on hpc?")
    parser.add_argument("--mem", type=str, default=default_job_mem_request, help="How much memory to request for each job?")
    parser.add_argument("--runs_per_subdir", type=int, default=-1, help="How many replicates to clump into job subdirectories")
    parser.add_argument("--repo_dir", type=str, help="Where is the repository for this experiment?")
    parser.add_argument("--hpc_env_file", type=str, default=None, help="Bash script that loads correct hpc modules")
    parser.add_argument("--spatial_structs_dir", type=str, help="Which directory contains spatial structures to be used?")


    args = parser.parse_args()

    # Load in the base slurm file
    base_slurm_script = ""
    with open(base_slurm_script_fpath, "r") as fp:
        base_slurm_script = fp.read()

    # Get list of all combinations to run
    combo_list = combos.get_combos()
    for c in combo_list:
        print(c)

    # Calculate how many total jobs we have, and what the last id will be
    num_jobs = args.replicates * len(combo_list)

    # Echo chosen options
    print(f'Generating {num_jobs} jobs across {len(combo_list)} slurm files!')
    print(f' - Data directory: {args.data_dir}')
    print(f' - Config directory: {args.config_dir}')
    print(f' - Repository directory: {args.repo_dir}')
    print(f' - Spatial structs directory: {args.spatial_structs_dir}')
    print(f' - Job directory: {args.job_dir}')
    print(f' - Replicates: {args.replicates}')
    print(f' - Account: {args.hpc_account}')
    print(f' - Time Request: {args.time_request}')
    print(f' - Memory: {args.mem}')
    print(f' - Seed offset: {args.seed_offset}')

    # If no job_dir provided, default to data_dir/jobs
    if args.job_dir == None:
        args.job_dir = os.path.join(args.data_dir, "jobs")

    # Create a job file for each condition
    cur_job_id = 0
    cond_i = 0
    cur_subdir_run_cnt = 0
    cur_run_subdir_id = 0

    # Localize some commandline args for convenience ( less typing :) )
    config_dir = args.config_dir
    data_dir = args.data_dir
    job_dir = args.job_dir
    repo_dir = args.repo_dir
    spatial_structs_dir = args.spatial_structs_dir


    # Identify relevant/available spatial structure files
    spatial_structs = combos.get_vals("spatial_structure__DYNAMIC")
    # Only allow .mat files.
    # IMPORTANT: If multiple graph files for a single condition, they must:
    #  - each end with _ID.mat where ID is a value [0:number of replicates)
    #  - all be in matrix format
    # No spatial structure files for well-mixed condition.
    struct_files = {
        spatial_struct: [
            filename
            for filename in os.listdir(spatial_structs_dir)
            if filename.startswith(spatial_struct) and (".mat" in filename)
        ]
        for spatial_struct in spatial_structs if spatial_struct != "well-mixed"
    }

    # Sort any lists of file names on _<number>
    for spatial_struct in struct_files:
        if len(struct_files[spatial_struct]) > 1:
            struct_files[spatial_struct].sort(key = lambda x : int(x.split(".")[0].split("_")[-1]))
            # If more files than replicates, use only first N files
            if args.replicates < len(struct_files[spatial_struct]):
                struct_files[spatial_struct] = struct_files[spatial_struct][:args.replicates]
            elif args.replicates > len(struct_files[spatial_struct]):
                print(f"Too few spatial structure files for requested number of replicates for {spatial_struct}")
                exit(-1)

    # -- Generate slurm script for each condition --
    for condition_info in combo_list:
        # print(condition_info)
        # Calc current seed (all runs should have a unique random seed).
        cur_seed = args.seed_offset + (cur_job_id * args.replicates)
        filename_prefix = f'RUN_C{cond_i}'
        file_str = base_slurm_script
        file_str = file_str.replace("<<TIME_REQUEST>>", args.time_request)
        file_str = file_str.replace("<<ARRAY_ID_RANGE>>", f"1-{args.replicates}")
        file_str = file_str.replace("<<MEMORY_REQUEST>>", args.mem)
        file_str = file_str.replace("<<JOB_NAME>>", f"C{cond_i}")
        file_str = file_str.replace("<<CONFIG_DIR>>", config_dir)
        file_str = file_str.replace("<<REPO_DIR>>", repo_dir)
        file_str = file_str.replace("<<EXEC>>", executable)
        file_str = file_str.replace("<<JOB_SEED_OFFSET>>", str(cur_seed))
        file_str = file_str.replace("<<SPATIAL_STRUCT_DIR>>", spatial_structs_dir)
        if args.hpc_account is None:
            file_str = file_str.replace("<<HPC_ACCOUNT_INFO>>", "")
        else:
            file_str = file_str.replace("<<HPC_ACCOUNT_INFO>>", f"#SBATCH --account {args.hpc_account}")

        if args.hpc_env_file is None:
            file_str = file_str.replace("<<SETUP_HPC_ENV>>", "")
        else:
            file_str = file_str.replace("<<SETUP_HPC_ENV>>", f"source {args.hpc_env_file}")

        # Configure run directory
        run_dir = os.path.join(data_dir, f"{filename_prefix}_"+"${SEED}")
        file_str = file_str.replace("<<RUN_DIR>>", run_dir)

        # -- Build command line parameters --
        # Start by adding in fixed parameters
        cmd_line_params = {param:fixed_parameters[param] for param in fixed_parameters}
        cmd_line_params["SEED"] = "${SEED}"
        # Then, add condition-specific parameters (starting with non-__COPY_OVER params)
        for param in condition_info:
            if any([dec in param for dec in special_decorators]):
                continue
            cmd_line_params[param] = condition_info[param]

        # Spatial structure configuration
        cond_spatial_struct = condition_info["spatial_structure__DYNAMIC"]
        need_to_load_struct_file = False
        if cond_spatial_struct == "well-mixed":
            # Configure spatial structure as well-mixed using symbulation parameters
            cmd_line_params["SPATIAL_STRUCT_MODE"] = "well-mixed"
            cmd_line_params["SPATIAL_STRUCT_LOAD_MODE"] = "matrix"
            cmd_line_params["SPATIAL_STRUCT_CFG_PATH"] = "none"
        else:
            need_to_load_struct_file = True
            # Load spatial structure file
            cmd_line_params["SPATIAL_STRUCT_MODE"] = "load"
            cmd_line_params["SPATIAL_STRUCT_LOAD_MODE"] = "matrix"
            # Identify which spatial structure file to load
            cond_struct_files = struct_files[cond_spatial_struct]
            if len(cond_struct_files) <= 1:
                # Just one graph file for entire condition, use that.
                cmd_line_params["SPATIAL_STRUCT_CFG_PATH"] = f"{cond_spatial_struct}.mat"
            else:
                # Multiple one graph file per replicate.
                graph_name_prefix = "_".join(cond_struct_files[-1].split("_")[:-1])
                # Check that all replicates will have a graph file as expected
                for i in range(len(cond_struct_files)):
                    run_id = i
                    run_seed = cur_seed + i
                    graph_filename = cond_struct_files[i]
                    expected_graph_name = f"{graph_name_prefix}_{run_id}"
                    if graph_filename != expected_graph_name:
                        print(f"Unexpected graph name for condition: {condition_info}")
                        print(f"  Expected: {expected_graph_name}")
                        print(f"  Found: {graph_filename}")
                # Set graph file name
                cmd_line_params["SPATIAL_STRUCT_CFG_PATH"] = f"{cond_spatial_struct}_" + "${RUN_ID}.mat"

        # Build command line parameter string (including any 'copy_over' parameters)
        params = list(cmd_line_params.keys())
        params.sort()
        set_params = [f"-{param} {cmd_line_params[param]}" for param in params]
        copy_params = [condition_info[key] for key in condition_info if "__COPY_OVER" in key]
        run_param_str = " ".join(set_params + copy_params)

        run_cmds = []
        run_cmds.append(f'RUN_PARAMS="{run_param_str}"')
        run_cmds.append('echo "./${EXEC} ${RUN_PARAMS}" > cmd.log')
        run_cmds.append('./${EXEC} ${RUN_PARAMS} > run.log')
        run_cmds_str = "\n".join(run_cmds)

        file_str = file_str.replace("<<RUN_CMDS>>", run_cmds_str)

        # -- Build run configuration copy commands --
        config_cp_cmds = []
        config_cp_cmds.append("cp ${CONFIG_DIR}/*.cfg .")
        config_cp_cmds.append("cp ${CONFIG_DIR}/*.json .")
        # Only copy a spatial structure file into run directory if needed
        if need_to_load_struct_file:
            config_cp_cmds.append("cp ${GRAPHS_DIR}/" + cmd_line_params["SPATIAL_STRUCT_CFG_PATH"] + " .")
        config_cp_cmds_str = "\n".join(config_cp_cmds)
        file_str = file_str.replace("<<CONFIG_CP_CMDS>>", config_cp_cmds_str)

        # -- Write job submission file --
        cur_job_dir = job_dir if args.runs_per_subdir == -1 else os.path.join(job_dir, f"job-set-{cur_run_subdir_id}")
        utils.mkdir_p(cur_job_dir)
        with open(os.path.join(cur_job_dir, f'{filename_prefix}.sb'), 'w') as fp:
            fp.write(file_str)

        # Update condition id and current job id
        cur_job_id += 1
        cond_i += 1
        cur_subdir_run_cnt += args.replicates
        if cur_subdir_run_cnt > (args.runs_per_subdir - args.replicates):
            cur_subdir_run_cnt = 0
            cur_run_subdir_id += 1

if __name__ == "__main__":
    main()