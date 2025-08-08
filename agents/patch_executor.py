import json
import subprocess
from pathlib import Path
import datetime, os
class PatchExecutor:
    def __init__(self, systems_file="data/wsl_targets.json"):
        self.systems = self._load_systems(systems_file)
    
    def _load_systems(self, path):
        with open(Path(path), 'r') as f:
            return json.load(f)["systems"]
    
    def _execute_wsl(self, system, command):
        try:
            result = subprocess.run(
                ["wsl", "-d", "Samsung-Ubuntu", "-u", system["credentials"]["user"], 
                "--", "bash", "-c", command],
                capture_output=True,
                text=True,
                check=True
            )
            return {"success": True, "output": result.stdout}
        except subprocess.CalledProcessError as e:
            return {"success": False, "error": e.stderr}
    
    def _build_docker_command(self, step):
        if step["action"] == "upgrade":
            return (
                f"stop {step['container_name']} && "
                f"rm {step['container_name']} && "
                f"run -d --name {step['container_name']} "
                f"-p {step['ports'][0]} {step['image']}"
            )
        return ""

    # In patch_executor.py, add this method
    def _get_wsl_command(self, system_name, command):
        """Build proper WSL command for target system"""
        system = next(s for s in self.systems if s["name"] == system_name)
        return [
            "wsl", "-d", "Samsung-Ubuntu", "-u", system["credentials"]["user"],
            "bash", "-c", command
        ]

        # Update execute() to use real commands
    

    def execute(self, patch_plan):
        results = {}
        log_file = f"backend/data/execution_logs/{patch_plan['audit_id']}_debug.log"
        os.makedirs(os.path.dirname(log_file), exist_ok=True)

        with open(log_file, "w") as f:
            f.write(f"Started: {datetime.datetime.now()}\n")

            system = next(s for s in self.systems if s["name"] == "Samsung-Ubuntu")
            cmds = ["sudo apt update"]
            for cmd in cmds:
                try:
                    f.write(f"Running: {cmd}\n")
                    process = subprocess.Popen(
                        ["wsl", "-d", "Samsung-Ubuntu", "-u", system["credentials"]["user"], "bash", "-c", cmd],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT, # Redirect stderr to stdout
                        text=True,
                        bufsize=1,
                        universal_newlines=True
                    )

                    # Live output streaming
                    for line in process.stdout:
                        print(line, end='') # Print to server console
                        f.write(line) # Write to log file
                    
                    process.wait() # Wait for the process to complete

                    results[cmd] = {"success": process.returncode == 0, "output": "See console and log for output.", "error": ""}

                except Exception as e:
                    f.write(f"ERROR: {e}\n")
                    results[cmd] = {"success": False, "error": str(e)}

            f.write(f"Finished: {datetime.datetime.now()}\n")
        return results