from pathlib import Path
from uuid import uuid4
from urllib.request import urlopen
import re
import json
import sys

REGOLITH_PATH = Path("regolith")
BP_PATH = Path(REGOLITH_PATH / "packs/BP")
RP_PATH = Path(REGOLITH_PATH / "packs/RP")
BP_DOWNLOAD_URL = "https://github.com/Mojang/bedrock-samples/releases/latest"

REPO_NAME = sys.argv[1]
REPO_PATH = sys.argv[2]


def get_latest_version():
    # Gets the lastest stable version of Minecraft
    response = urlopen(BP_DOWNLOAD_URL)
    download_url = response.url
    pattern = re.compile("[0-9]+\\.[0-9]+\\.[0-9]+")
    semver = re.search(pattern, download_url.split("/")[-1])
    return [int(i) for i in semver.group().split(".")]


def apply_packs():
    """
    Applies the resource and behavior packs from the resource_packs and
    behavior_packs folders to the minecraft world by editing the world's
    world_resource_packs.json and world_behavior_packs.json files. The order
    of the packs is alphabetical.
    """
    worlds_path = Path("regolith") / "worlds" / REPO_NAME.replace("-", "_")

    args = [
        (
            worlds_path / "world_resource_packs.json",
            RP_PATH,
        ),
        (
            worlds_path / "world_behavior_packs.json",
            BP_PATH,
        ),
    ]
    for output, pack_folder in args:
        output_data = []
        for manifest in sorted(pack_folder.glob("manifest.json")):
            with manifest.open("r", encoding="utf8") as f:
                manifest_data = json.load(f)
            uuid = manifest_data["header"]["uuid"]
            version = manifest_data["header"]["version"]
            output_data.append({"pack_id": uuid, "version": version})
        with output.open("w", encoding="utf8") as f:
            json.dump(output_data, f, indent="\t")


def main():
    # Main function
    # Get current stable version of MC
    mc_version = get_latest_version()

    # Rename world_folder
    world_folder = Path("./regolith/worlds/world_folder")
    world_folder.rename(world_folder.parent / REPO_NAME.replace("-", "_"))

    # Initialize the project manifest
    project_manifest = (
        Path("regolith") / "worlds" / REPO_NAME.replace("-", "_") / "manifest.json"
    )
    with project_manifest.open("r") as f:
        data = json.load(f)
    data["header"]["uuid"] = str(uuid4())
    data["modules"][0]["uuid"] = str(uuid4())
    data["header"]["base_game_version"] = mc_version
    with project_manifest.open("w") as f:
        json.dump(data, f, indent="\t")

    # Initialize resource pack manifest
    rp_header_uuid = str(uuid4())
    bp_header_uuid = str(uuid4())
    with (RP_PATH / "manifest.json").open("r") as f:
        data = json.load(f)
    data["header"]["uuid"] = rp_header_uuid
    data["header"]["min_engine_version"] = mc_version
    data["modules"][0]["uuid"] = str(uuid4())
    data["dependencies"][0]["uuid"] = bp_header_uuid
    with (RP_PATH / "manifest.json").open("w") as f:
        json.dump(data, f, indent="\t")

    # Initialize behavior pack manifest
    with (BP_PATH / "manifest.json").open("r") as f:
        data = json.load(f)
    data["header"]["uuid"] = bp_header_uuid
    data["header"]["min_engine_version"] = mc_version
    data["modules"][0]["uuid"] = str(uuid4())
    data["modules"][1]["uuid"] = str(uuid4())
    data["dependencies"][0]["uuid"] = rp_header_uuid
    with (BP_PATH / "manifest.json").open("w") as f:
        json.dump(data, f, indent="\t")
    apply_packs()

    # Updating system template scripting_setup manifest UUID's
    with (
        REGOLITH_PATH / "filters_data/system_template/scripting_setup/manifest.json"
    ).open("r") as f:
        data = json.load(f)
        data["modules"][0]["uuid"] = str(uuid4())
    with (
        REGOLITH_PATH / "filters_data/system_template/scripting_setup/manifest.json"
    ).open("w") as f:
        json.dump(data, f, indent="\t")

    # Initialize bp and rp en_US.lang files
    new_lang = ["pack.name=" + REPO_NAME + "\n", "pack.description=By Shapescape"]
    with (BP_PATH / "texts/en_US.lang").open("w") as f:
        for lines in new_lang:
            f.writelines(lines)
    with (RP_PATH / "texts/en_US.lang").open("w") as f:
        for lines in new_lang:
            f.writelines(lines)
    new_lang = [
        "pack.name=" + REPO_NAME + "\n",
        "pack.description=INSERT PACK DESCRIPTION (FOR MARKETPLACE PAGE) HERE",
    ]
    with Path("texts/en_US.lang").open("w") as f:
        for lines in new_lang:
            f.writelines(lines)

    # Initialize regolith config.json
    with (REGOLITH_PATH / "config.json").open("r") as f:
        data = json.load(f)

        # Set the project name
        data["name"] = REPO_NAME

        # Replace the WORLD_PLACEHOLDER in packaging profile.
        target_profile = "packaging"
        target_filter = "level_dat_updater"

        new_world_name = REPO_NAME.replace("-", "_")

        # Check if the target filter exists and replace WORLD_PLACEHOLDER
        if target_profile in data["regolith"]["profiles"]:
            profile = data["regolith"]["profiles"][target_profile]

            for filter_item in profile["filters"]:
                if "filter" in filter_item and filter_item["filter"] == target_filter:
                    # Replace WORLD_PLACEHOLDER in the settings paths
                    settings = filter_item["settings"]
                    if "level_dat_path" in settings:
                        settings["level_dat_path"] = settings["level_dat_path"].replace(
                            "WORLD_PLACEHOLDER", new_world_name
                        )
                    if "levelname_path" in settings:
                        settings["levelname_path"] = settings["levelname_path"].replace(
                            "WORLD_PLACEHOLDER", new_world_name
                        )

                    # Update the filter item with the new settings
                    filter_item["settings"] = settings
                    break

    with (REGOLITH_PATH / "config.json").open("w") as f:
        json.dump(data, f, indent="\t")

    # Initialize readme
    with Path("README.md").open("r") as f:
        data = f.read()
        data = data.replace("# Template-Regolith", "# " + REPO_NAME)

    with Path("README.md").open("w") as f:
        f.write(data)

    # Create code workspaces
    regolith_workspace_path = (
        REPO_NAME.replace(" ", "_") + "-regolith." + "code-workspace"
    )

    with Path(regolith_workspace_path).open("w") as f:
        data = {
            "folders": [{"path": "regolith"}],
            "settings": {},
        }
        json.dump(data, f, indent=4)

    with Path("./pack/release_config.json").open("r") as f:
        # change the product_name to the repo_name
        data = json.load(f)
        data["product_name"] = REPO_NAME.title().replace("-", " ")
        data["product_name_edu"] = REPO_NAME.title().replace("-", " ") + " (Education Edition)"
        data["exported_world_bedrock"] = REPO_NAME.replace("-", "_")
        data["exported_world_edu"] = REPO_NAME.replace("-", "_") + "_EDU"
        first_letters = [
            word[0] for word in REPO_NAME.title().replace("-", " ").split()
        ]
        data["product_key"] = "".join(first_letters)
    with Path("./pack/release_config.json").open("w") as f:
        json.dump(data, f, indent="\t")


if __name__ == "__main__":
    main()
    # Delete the workflow and this script so it won't be used ever again
    Path(".github/workflows/init.yml").unlink()
    Path(".github/python/init.py").unlink()
