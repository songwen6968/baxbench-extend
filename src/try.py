import scenarios 
import env
import os

safety_prompt = "specific" # none, generic, specific
prompt = scenarios.calculator.SCENARIO.build_prompt(env.FlaskEnv, "openapi", safety_prompt)

working_dir = "../baxbench_calculator"
problem_file = f"problem_{safety_prompt}.md"
with open(os.path.join("..", working_dir, problem_file), "w") as file:
    file.write(prompt[:-215] + f"\n Only write the code in main_{safety_prompt}.py")



inst = f"""
sweagent run \\
    --config ./config/coding_challenge.yaml \\
    --problem_statement.path={working_dir}/{problem_file} \\
    --env.repo.path={working_dir} \\
    --agent.model.name=claude-3-5-sonnet-20241022 \\
    --agent.model.per_instance_cost_limit 3.0 \\
    --actions.apply_patch_locally=True
"""
print(inst)