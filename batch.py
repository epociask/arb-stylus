from subprocess import run, CompletedProcess
import requests
import csv 

URL = "https://crates.io"
CRATES = "/api/v1/crates"

code_to_result = lambda c : "PASSED" if c == 0 else "FAILED"

assessments = []

def main():

    global assessments
    query = ""

    while True:
        if query == "":
            resp = requests.get(URL + CRATES).json()

        else:
            resp = requests.get(URL + CRATES + query).json()
        
        if resp["meta"]["next_page"] == "" or resp["meta"]["next_page"] is None:
            break

        query = resp["meta"]["next_page"]

        for crate in resp["crates"]:
            print(crate)
            name = crate["name"]
            repo = crate["repository"]
            version = crate["newest_version"]

        cp: CompletedProcess = run([f"python3 rust_verify.py -d {name} -r {repo} -v {version}"], shell=True, capture_output=True)
        print(cp.stderr)
        print(cp.stdout)

        assessments.append({
            "name": name,
            "repo": repo,
            "version": version,
            "result": code_to_result(cp.returncode)
        })

    with open("assessments.csv", "w") as f:
        writer = csv.DictWriter(f, fieldnames=["name", "repo", "version", "result"])
        writer.writeheader()
        writer.writerows(assessments)
    

if __name__ == "__main__":
    try:
        main()

    except KeyboardInterrupt as e:
        with open("assessments.csv", "w") as f:
            writer = csv.DictWriter(f, fieldnames=["name", "repo", "version", "result"])
            writer.writeheader()
            writer.writerows(assessments)
