from subprocess import run, CompletedProcess
from datetime import datetime
from colorama import Fore, Style
from art import *
import argparse

# stylus CLI CMDs
VERIFY: str = "cargo stylus check"

# error msg constants
ERR_DEP_NOT_FOUND: str = "[dependencies] table not found in Cargo.toml"
ERR_NO_NAME: str = "Dependency name not provided"
ERR_NO_VERSION: str = "Dependency version not provided"
ERR_CREATE: str = "Failed to create tmp stylus project"
ERR_CHECK: str = "Dependency verification failed"
ERR_PERM_CHANGE: str = "Failed to change permissions on tmp stylus project"

# get_args returns the CLI args
def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
                    prog='Rust Stylus Dependency Checker',
                    description='Checks a third party Rust dependency for stylus contract compatibility')
    
    parser.add_argument('-d', '--dependency', type=str, help='The name of the dependency to check')
    parser.add_argument('-r', '--repo', type=str, help='The git repo of the dependency to check')
    parser.add_argument('-v', '--version', type=str, help='The version of the dependency to check')

    return parser.parse_args()


# get_dep_declaration returns the Cargo.toml dependency declaration string for the given args
def get_dep_declaration(args: argparse.Namespace) -> str:
    if args.dependency is None or args.dependency.strip() == "":
        raise Exception(ERR_NO_NAME)
    
    if args.version is None or args.version.strip() == "":
        raise Exception(ERR_NO_VERSION)
    
    if args.repo is None or args.repo.strip() == "":
        return args.dependency + " = \"" + args.version + "\""
    
    return args.dependency + " = {version = \"" + args.version + "\", git = \"" + args.repo + "\"}"


def main(file_id: str, args: argparse.Namespace):
    args: argparse.Namespace = get_args()
    path: str = f".temp/{file_id}/"

    # (1) Inject dependency into Cargo.toml
    lines: list[str] = []
    dep_declaration: str = get_dep_declaration(args)
    with open(path + "Cargo.toml", "r") as f:
        lines: list[str] = f.readlines()
        dep_index: int = lines.index("[dependencies]\n")

        if dep_index == -1:
            raise Exception(ERR_DEP_NOT_FOUND)
        
        lines.insert(dep_index + 1, dep_declaration + "\n")

    with open(path + "Cargo.toml", 'w') as f: 
        for line in lines:
            f.write(line)

    # (2) Inject dependency import into Main.rs
    with open(path + "src/main.rs", "r") as f:
        lines = f.readlines()

        # NOTE - this won't work if the example code changes in the future
        lines.insert(25, "use " + args.dependency + "::*;\n")

    with open(path + "src/main.rs", 'w') as f: 
        for line in lines:
            f.write(line)


    # (3) Verify the dependency compiles with stylus
    print(Style.RESET_ALL + "\n\nVerifying dependency compiles with stylus")
    cp: CompletedProcess = run([f"cd .temp/{file_id} && cargo stylus check"], capture_output=True, shell=True)

    if "Stylus checks failed:" in str(cp.stdout):
        print(Fore.RED + "\n\n ====== FAILED ====== \n\n")
        print("Dependency verification failed, please consider using another third party package instead \n\n")
        print(str(cp.stderr))
        raise Exception(ERR_CHECK)

    print(Fore.GREEN + "\n\n ====== PASSED ====== \n\n")
    print(f"Dependency {args.dependency}:{args.version} verified successfully")


# clean_up removes the tmp stylus project
def clean_up(file_id: str):
    cp: CompletedProcess = run(["rm", "-rf", f".temp/{file_id}"], capture_output=True)

    if cp.returncode != 0:
        print("Failed to clean up tmp stylus project")
        print(str(cp.stderr))


if __name__ == "__main__":

    print(Fore.BLUE + "======= Stylus Dependency Checker ======= \n\n")
    print("This tool will check a third party Rust dependency for stylus contract compatibility \n\n")

    file_id: str = datetime.now().strftime("%Y%m%d%H%M%S")
    args: argparse.Namespace = get_args()
    
    cp: CompletedProcess = run(["cargo", "stylus", "new", f".temp/{file_id}"], capture_output=True)
    if cp.returncode != 0:
        print("Failed to create tmp stylus project")
        print(str(cp.stderr))
        exit(1)

    try:
        main(file_id, args)

    except Exception as e:
        print(e)
        exit(1)

    finally:
        print(Style.RESET_ALL + "Cleaning up tmp stylus project")
        clean_up(file_id)

    exit(0)