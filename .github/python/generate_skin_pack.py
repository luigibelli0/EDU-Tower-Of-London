"""
This script generates a skin pack depending on if a manifest
does not exist and if there are skins in the folder.
"""

from pathlib import Path
import json
from uuid import uuid4

SKINPACK_PATH = Path("skin_pack")

RELEASE_CONFIG_PATH = Path("pack/release_config.json")

# get project name and short from release config
with RELEASE_CONFIG_PATH.open("r") as file:
    data = json.load(file)
    project_name = data["product_name"]
    project_identifier = data["product_key"]


def get_uuids():
    """
    This checks if a manifest.json already exists, if true,
    then it takes the current UUIDs and saves them. If not
    UUID was found, then it will create a new one.
    """
    manifest = SKINPACK_PATH / "manifest.json"
    header_uuid = "null"
    modules_uuid = "null"

    if manifest.exists():
        with manifest.open("r") as f:
            data = json.load(f)
            if data["header"]["uuid"]:
                header_uuid = str(data["header"]["uuid"])
            if data["modules"][0]["uuid"]:
                modules_uuid = str(data["modules"][0]["uuid"])
    if header_uuid == "null":
        header_uuid = str(uuid4())
    if modules_uuid == "null":
        modules_uuid = str(uuid4())
    return header_uuid, modules_uuid


def generate_manifest():
    """
    This makes sure that the init action is deleted. The init
    action should only run on initialisation of a project but
    failed to delete for older projects.
    """
    manifest = SKINPACK_PATH / "manifest.json"
    # get or generate UUID's
    header_uuid, modules_uuid = get_uuids()

    with manifest.open("w") as f:
        content = {}
        header = {}
        module = {}
        header.update({"name": "pack.name"})
        header.update({"version": [1, 0, 0]})
        header.update({"uuid": header_uuid})
        module.update({"type": "skin_pack"})
        module.update({"version": [1, 0, 0]})
        module.update({"uuid": modules_uuid})
        content.update({"header": header})
        content.update({"modules": [module]})
        content.update({"format_version": 1})
        json.dump(content, f, indent=2)


def generate_skins_file():
    # generate skins.json
    with (SKINPACK_PATH / "skins.json").open("w") as f:
        content = {}
        skins = []
        for skin in SKINPACK_PATH.glob("*.png"):
            skin_name = skin.name[: len(skin.name) - 6]
            data = {}
            localisation_name = "skin." + project_identifier + ".SP." + skin_name
            geometry_type = skin.name[len(skin.name) - 5 : len(skin.name) - 4]
            if geometry_type == "s":
                geometry_type = "geometry.humanoid.custom"
            if geometry_type == "a":
                geometry_type = "geometry.humanoid.customSlim"
            data.update({"localization_name": localisation_name})
            data.update({"geometry": geometry_type})
            data.update({"texture": skin.name})
            data.update({"type": "paid"})
            skins.append(data)
        content["skins"] = skins
        content.update({"serialize_name": project_identifier})
        content.update({"localization_name": project_identifier})
        json.dump(content, f, indent=2)


def generate_texts():
    texts_dir = SKINPACK_PATH / "texts/"  # create folder
    p = texts_dir
    p.mkdir(parents=True, exist_ok=True)
    # create languages.json
    with (p / "languages.json").open("w") as f:
        languages = ["en_US"]
        json.dump(languages, f, indent=2)
    # create en_US.lang
    with (p / "en_US.lang").open("w", encoding="utf8") as f:
        new_lang = [
            "skinpack." + project_identifier + "=" + project_name + " Skins" + "\n"
        ]
        for skin in SKINPACK_PATH.glob("*.png"):
            new_lang.append(
                "skin."
                + project_identifier
                + ".SP."
                + skin.name[: len(skin.name) - 6]
                + "="
                + skin.name[: len(skin.name) - 6].title()
                + "\n"
            )
        for lines in new_lang:
            f.writelines(lines)


def main():
    # .Github
    generate_texts()
    generate_skins_file()
    generate_manifest()

    # Apply packs


if __name__ == "__main__":
    main()
