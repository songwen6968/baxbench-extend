from scenarios import all_scenarios
from env import all_envs
from env.python import FlaskEnv
import os
import json
import pathlib
import subprocess
import shutil

def esc(s: str) -> str:
    return s.replace("/", "-")

envs = [FlaskEnv]
scenarios = all_scenarios
model="us.anthropic.claude-3-5-sonnet-20241022-v2:0"
temperature=0.1
spec_type = "openapi"
safety_prompt = "generic" # none, generic, specific
batch_size = 1
results_dir = pathlib.Path("results")
sweagent_dir = pathlib.Path("../SWE-agent")

def build_prompt(env, scenario, spec_type, safety_prompt):
    sys_prompt = "This is a backend software development task. "
    # before_prompt = "IMPORTANT! DO NOT create README.md. Only make changes in main.py, do not add other files. " \
    # "IMPORTANT! Use insert command instead of edit to add content to a file. "
    # "IMPORTANT! Ignore extra lines issue in all files." 
    prompt = scenario.build_prompt(env, spec_type, safety_prompt)
    # after_prompt = " If you are testing code, no need to really start the server. Test suites should be in a seperate file. " 
    additional_prompt = """IMPORTANT! Use insert command instead of edit to add content to a file.
    """
    return sys_prompt + additional_prompt + prompt

def generate_problem_statement(env, scenario, batch_size):
    save_dir = (
        results_dir
        / esc(model)
        / esc(scenario.id)
        / esc(env.id)
        / f"temp{float(temperature)}-{esc(spec_type)}-{esc(safety_prompt)}"
    )
    try:
        save_dir.mkdir(parents=True, exist_ok=False)
    except:
        shutil.rmtree(save_dir)
        save_dir.mkdir(parents=True, exist_ok=False)

    code_dirs = []
    prompt = build_prompt(env, scenario, spec_type, safety_prompt)
    for sample in range(batch_size):
        code_dir = save_dir / f"sample{sample}" / "code"
        code_dir.mkdir(parents=True, exist_ok=True)
        problem_file_path = code_dir / "problem_statement.md"
        with open(problem_file_path, "w") as f:
            f.write(prompt)
        code_dirs.append(code_dir)
    return code_dirs

def make_git_code_dirs(all_code_dirs):
    def init_and_commit_repo(dir, commit_msg="start"):
        subprocess.run(["git", "-C", str(dir), "init"], check=True)
        with open(dir / ".gitignore", "w") as f:
            f.write("*\n!main.py\n!.gitignore")
        subprocess.run(["git", "-C", str(dir), "add", "."], check=True)
        subprocess.run(["git", "-C", str(dir), "commit", "-m", commit_msg], check=True)    
    for d in all_code_dirs:
        try:
            init_and_commit_repo(d)
        except subprocess.CalledProcessError as e:
            print(f"Failed to init and commit for {d}: {e}")

def send_code_dirs(output_dir, all_code_dirs):
    make_git_code_dirs(all_code_dirs)
    all_code_dirs = [str("../baxbench" / d) for d in all_code_dirs]
    output_file_path = output_dir / "baxbench_dirs.json"
    if output_file_path.exists():
        with open(output_file_path, "r") as f:
            cur_dirs = json.load(f)
    else:
        cur_dirs = {}
    cur_dirs[model] = all_code_dirs
    with open(output_dir / "baxbench_dirs.json", "w") as f:
        json.dump(cur_dirs, f)

def main():
    all_code_dirs = []
    for env in envs:
        for scenario in scenarios:
            all_code_dirs += generate_problem_statement(env, scenario, batch_size=1)
    send_code_dirs(sweagent_dir, all_code_dirs)

if __name__ == "__main__":
    main()