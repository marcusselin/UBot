from time import sleep
from pathlib import Path

env_dir = Path(__file__).resolve().parent

with open(env_dir / "status.txt", "w") as f:
    f.write("maintenance")
print("Entering maintenance mode...")
sleep(5)
with open(env_dir / "maintenace.txt", "w") as fm:
    fm.write("1")