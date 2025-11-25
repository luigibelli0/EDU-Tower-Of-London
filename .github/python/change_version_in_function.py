from pathlib import Path
import sys

TAG = sys.argv[1]

function_path = Path(
    "./regolith/filters_data/system_template/world_version/world_version.mcfunction"
)

if function_path.exists():
    with open(function_path, "w") as f:
        version = TAG.split(".")
        version = f"{version[0]}.{version[1]}.{version[2]}"
        f.write('tellraw @s {"rawtext":[{"text":"' + version + '"}]}')
else:
    print(f"Not able to find world_version.mcfunction at path {function_path}")
    print("Skipping step.")
