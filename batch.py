from subprocess import run, CompletedProcess
from multiprocessing import Pool, Lock
import os
import pandas as pd
import csv

URL: str = "https://crates.io"
CRATES: str = "/api/v1/crates"

code_to_result = lambda c : "PASSED" if c == 0 else "FAILED"

def get_error_type(error: str) -> str:
    if "could not compile" in error:
        return "COMPILATION"
    
    if "program predeployment check failed when checking against ARB_WASM_ADDRESS" in error:
        return "VERIFICATION"
    
    if "failed to build project to WASM:" in error:
        return "BUILD"
    
    return "UNKNOWN"


def find_data_dir() -> str:
    l: list[str] = os.listdir(".data")
    if len(l) == 0:
        raise FileNotFoundError("No data directory found in .data. Please run `make fetch_data` to download the crate registry data.")

    l = sorted(l, reverse=False)
    return l[0]


def run_process(name: str, version: str) -> object:
    print(f"Running rust_verify.py for {name} {version}...")
    cp: CompletedProcess = run([f"python3 rust_verify.py -d {name} -v {version}"], shell=True, capture_output=True)
    print(cp.stderr)
    print(cp.stdout)

    return {
        "name": name,
        "version": version,
        "result": code_to_result(cp.returncode)
    }

    

def main():

    data_dir: str = find_data_dir()
    print(f"Using {data_dir} dump for performing batch analysis.")

    print("\n Loading version and crates dataframes...")
    version_df: pd.DataFrame = pd.read_csv(f".data/{data_dir}/data/versions.csv")
    crates_df: pd.DataFrame = pd.read_csv(f".data/{data_dir}/data/crates.csv")

    assessments: list[object] = []
    # Filter out crates with less than 1000 downloads
    
    ## versions
    ## crate_id,num
    
    ## crates
    ## name,id

    joined_df: pd.DataFrame = version_df.join(crates_df, on="crate_id", how="inner", lsuffix="_version", rsuffix="_crate")
    print(joined_df.columns)

    # Remove unnecessary columns
    joined_df.drop(columns=["crate_size","created_at_version","features","license","links","published_by","updated_at_crate", "updated_at_version","yanked"], inplace=True)

    print(joined_df.head())

    # Filter out crates with less than 1000 downloads
    joined_df = joined_df[joined_df["downloads_crate"] >= 1000]

    print(joined_df.head())

    with Pool(8) as pool:
        # Run rust_verify.py in parallel
        pool_args: list[tuple] = []
        for _, row in joined_df.iterrows():
            pool_args.append((row["name"], row["num"]))
        
        print("0th item", pool_args[0])

        results = pool.starmap_async(run_process, pool_args)
        
        for result in results.get():
            assessments.append(result)

        # Iterate over rows and run rust_verify.py

        with open("assessments.csv", "w") as f:
            writer = csv.DictWriter(f, fieldnames=["name", "repo", "version", "result"])
            writer.writeheader()
            writer.writerows(assessments)
    

if __name__ == "__main__":
    main()

