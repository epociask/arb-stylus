## Stylus Library Validator

### About
The Stylus Library Validator is a tool that validates if a third party library is compatible with Stylus. It is a command line tool that takes a library as input and outputs an assessment (PASS/FAIL) of the validation process.

Currently this tool only works for rust dependencies. The implementation was also written very quickly and therefore lacks proper testing, documentation, and extensibility. This could be improved in the future. 

### Usage

#### Prerequisites
- [Rust](https://www.rust-lang.org/tools/install)
- [Cargo](https://doc.rust-lang.org/cargo/getting-started/installation.html)
- [Rust-Stylus](https://github.com/OffchainLabs/stylus-sdk-rs)
- [Python3](https://www.python.org/downloads/)

#### Installation
1. Clone this repository
2. Run `pip3 install -r requirements.txt` to install the required python packages

#### Running
Run `python3 rust_verify.py -r "<GIT_REPO>" -d "<DEPENDENCY_NAME> -v "<DEPENDENCY_VERSION>"` to run the stylus package validator. 
    - `<GIT_REPO>` is the git repository of the dependency
    - `<DEPENDENCY_NAME>` is the name of the dependency
    - `<DEPENDENCY_VERSION>` is the version of the dependency


#### Future Work
- Add support for more languages
- Add more tests
- Add more documentation
- Add this PoC as a feature to the Stylus SDK CLIs
- Add batch analysis to provide a report of all valid third party rust dependencies