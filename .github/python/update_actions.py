"""
This script updates the .github folder from the template world on
this repo to update actions and bug templates.
"""

from pathlib import Path
import json
import shutil
import sys
import copy

try:
    import better_json_tools as bjt
except ImportError:
    print("better_json_tools is not installed. Please install it to use this feature.")
    bjt = None

REPO_NAME = "NULL"
if len(sys.argv) > 1:
    REPO_NAME = sys.argv[1]

TEMPLATE = Path("../Template")
GITHUB_PATH = Path(".github")
SCRIPTS_PATH = Path(".scripts")
VSCODE_PATH = Path(".vscode")
DEBUGGER_FOLDER = Path("debugger")
PACK_FOLDER = Path("pack")
REGOLITH_PATH = Path("regolith")
PRETTIER_IGNORE_PATH = Path(".prettierignore")

def remove_init():
    """
    This makes sure that the init action is deleted. The init
    action should only run on initialisation of a project but
    failed to delete for older projects.
    """
    Path.unlink(GITHUB_PATH / "python/init.py")
    Path.unlink(GITHUB_PATH / "workflows/init.yml")


def main():
    # read release_config.json within the pack
    with open(Path(PACK_FOLDER) / "release_config.json", "r") as f:
        release_config = json.load(f)

    format_version = 0
    # .Github
    if GITHUB_PATH.exists():
        shutil.rmtree(GITHUB_PATH)
    shutil.copytree(TEMPLATE / GITHUB_PATH, GITHUB_PATH)

     # .scripts
    if SCRIPTS_PATH.exists():
        shutil.rmtree(SCRIPTS_PATH)
    shutil.copytree(TEMPLATE / SCRIPTS_PATH, SCRIPTS_PATH)

    # open all ps1 scripts in .scripts and replace TemplateWorld with appropriate world names
    for file in SCRIPTS_PATH.iterdir():
        if file.suffix == ".ps1":
            with file.open("r") as f:
                lines = f.readlines()
            with file.open("w") as f:
                for line in lines:
                    if "bedrock" in file.name:
                        # Use bedrock world name for bedrock scripts
                        new_line = line.replace("TemplateWorld", release_config.get("exported_world_bedrock", release_config.get("exported_world", "WORLD_NAME")))
                    elif "edu" in file.name:
                        # Use edu world name for edu scripts
                        new_line = line.replace("TemplateWorld", release_config.get("exported_world_edu", release_config.get("exported_world", "WORLD_NAME_EDU")))
                    else:
                        # Default behavior for other scripts (fallback to bedrock)
                        new_line = line.replace("TemplateWorld", release_config.get("exported_world_bedrock", release_config.get("exported_world", "WORLD_NAME")))
                    f.write(new_line)

    # debugger/.scripts

    if (DEBUGGER_FOLDER/SCRIPTS_PATH).exists():
        shutil.rmtree(DEBUGGER_FOLDER/SCRIPTS_PATH)
    shutil.copytree(SCRIPTS_PATH, DEBUGGER_FOLDER/SCRIPTS_PATH)

    # update debugger/.scripts files

    # open all files within DEBUGGER_FOLDER/SCRIPTS_PATH and replace the 
    # first line with 'cd ../regolith\n'

    for file in (DEBUGGER_FOLDER/SCRIPTS_PATH).iterdir():
        with file.open("r") as f:
            lines = f.readlines()
        with file.open("w") as f:
            lines[0] = 'cd ../regolith\n'
            f.writelines(lines)

    # .vscode
    if VSCODE_PATH.exists():
        shutil.rmtree(VSCODE_PATH)
    if (DEBUGGER_FOLDER / VSCODE_PATH).exists():
        shutil.rmtree(DEBUGGER_FOLDER / VSCODE_PATH)
    shutil.copytree(TEMPLATE / VSCODE_PATH, VSCODE_PATH)
    shutil.copytree(TEMPLATE / VSCODE_PATH, DEBUGGER_FOLDER/VSCODE_PATH)

    # prettierignore
    if not PRETTIER_IGNORE_PATH.exists():
        shutil.copy(TEMPLATE / PRETTIER_IGNORE_PATH, PRETTIER_IGNORE_PATH)

    # read release_config.json within the pack
    with open(Path(PACK_FOLDER) / "release_config.json", "r") as f:
        release_config = json.load(f)

    # check the format version of the release_config
    if "format_version" in release_config:
        format_version = release_config["format_version"]
    else:
        format_version = 0

    # update to haze if format version is 0
    if format_version == 0 and REPO_NAME != "NULL" and bjt is not None:
        # update the config.json
        data = bjt.load_jsonc(REGOLITH_PATH / "config.json").data

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
                        settings["level_dat_path"] = (
                            f"worlds/{new_world_name}/level.dat"
                        )
                    if "levelname_path" in settings:
                        settings["levelname_path"] = (
                            f"worlds/{new_world_name}/levelname.txt"
                        )

                    # Update the filter item with the new settings
                    filter_item["settings"] = settings
                    break
        else:
            data["regolith"]["profiles"][target_profile] = {
                "export": {
                    "bpPath": "../behavior_packs/0",
                    "readOnly": False,
                    "rpPath": "../resource_packs/0",
                    "target": "exact",
                },
                "filters": [{"profile": "default"}],
            }
        if "default" in data["regolith"]["profiles"]:
            data["regolith"]["profiles"]["default"]["export"] = {
                "target": "development"
            }

        if "debug" in data["regolith"]["profiles"]:
            data["regolith"]["profiles"]["debug"]["export"] = {"target": "development"}

        if not "worlds" in data:
            data["worlds"] = ["./worlds/*"]
        with (REGOLITH_PATH / "config.json").open("w") as f:
            json.dump(data, f, indent="\t")

        # modifying release config
        new_worlds_path = REGOLITH_PATH / "worlds" / REPO_NAME.replace("-", "_")
        new_worlds_path.mkdir(parents=True, exist_ok=True)

        # move files to new world path
        files_to_move = [
            "world_behavior_packs.json",
            "world_resource_packs.json",
            "manifest.json",
            "levelname.txt",
            "level.dat_old",
            "level.dat",
        ]
        for file in files_to_move:
            shutil.move(file, new_worlds_path / file)
        shutil.move("db", new_worlds_path / "db")

        # update the release_config.json
        release_config["format_version"] = 1
        format_version = 1
        if "exported_world" not in release_config:
            release_config["exported_world"] = REPO_NAME.replace("-", "_")
        with (PACK_FOLDER / "release_config.json").open("w") as f:
            json.dump(release_config, f, indent=4)
    if format_version == 1 and REPO_NAME != "NULL" and bjt is not None:
        # update the config.json
        data = bjt.load_jsonc(REGOLITH_PATH / "config.json").data

        data["$schema"] = (
            "https://raw.githubusercontent.com/Bedrock-OSS/regolith-schemas/main/config/v1.4.json"
        )
        data["regolith"]["format_version"] = "1.4.0"
        for profile in data["regolith"]["profiles"]:
            if (
                data["regolith"]["profiles"][profile]["export"]["target"]
                == "development"
            ):
                data["regolith"]["profiles"][profile]["export"]["build"] = "standard"
        with (REGOLITH_PATH / "config.json").open("w") as f:
            json.dump(data, f, indent="\t")

        # update the release_config.json
        release_config["format_version"] = 2
        format_version = 2
        with (PACK_FOLDER / "release_config.json").open("w") as f:
            json.dump(release_config, f, indent=4)
    if format_version == 2 and REPO_NAME != "NULL" and bjt is not None:
        # update the config.json
        data = bjt.load_jsonc(REGOLITH_PATH / "config.json").data

        filter_definitions = data["regolith"]["filterDefinitions"]
        if "cg_containers" in filter_definitions:
            filter_definitions["cg_containers"]["version"] = "1.2.1"
        with (REGOLITH_PATH / "config.json").open("w") as f:
            json.dump(data, f, indent="\t")

        # update the release_config.json
        release_config["format_version"] = 3
        format_version = 3
        with (PACK_FOLDER / "release_config.json").open("w") as f:
            json.dump(release_config, f, indent=4)
    if format_version == 3 and REPO_NAME != "NULL" and bjt is not None:
        content_guide_path = REGOLITH_PATH / "filters_data" / "content_guide_generator" / "TEMPLATE.md"
        content_guide_config_path = GITHUB_PATH / "styling" / "content_guide_config.txt"
        
        # open content_guide_path in read mode
        with content_guide_path.open("r") as f:
            content_guide = f.read()  
        
        # open content_guide_config_path in read mode
        with content_guide_config_path.open("r") as f:
            content_guide_config = f.read()

        # open content_guide_path in write mode and write each line from 
        # content_guide_config to content_guide with a newline character
        # in the beginning of the file and then paste the content of content_guide
        with content_guide_path.open("w") as f:
            f.write(content_guide_config)
            f.write("\n")
            f.write(content_guide)    
        
        # update the release_config.json
        format_version = 4
        release_config["format_version"] = 4
        with (PACK_FOLDER / "release_config.json").open("w") as f:
            json.dump(release_config, f, indent=4)
    if format_version == 4 and REPO_NAME != "NULL" and bjt is not None:
        content_guide_path = REGOLITH_PATH / "filters_data" / "content_guide_generator" / "TEMPLATE.md"
        
        # check if the content_guide_path exists
        if content_guide_path.exists():
            # rename exisiting content_guide_path to OLD_TEMPLATE.md
            content_guide_path.rename(REGOLITH_PATH / "filters_data" / "content_guide_generator" / "OLD_TEMPLATE.md")

        # copy new template
        shutil.copy(TEMPLATE / "regolith/filters_data/content_guide_generator/TEMPLATE.md", REGOLITH_PATH / "filters_data/content_guide_generator/TEMPLATE.md")
        
        # copy images folder
        shutil.copytree(TEMPLATE / "regolith/filters_data/content_guide_generator/images", REGOLITH_PATH / "filters_data/content_guide_generator/images")
        
        # open regolith config
        data = bjt.load_jsonc(REGOLITH_PATH / "config.json").data

        # if the version of the filtersdefinitions of the content_guide_generator is lower then "1.7.3" set it to that version.
        if "content_guide_generator" in data["regolith"]["filterDefinitions"]:
            if data["regolith"]["filterDefinitions"]["content_guide_generator"]["version"] < "1.7.3":
                data["regolith"]["filterDefinitions"]["content_guide_generator"]["version"] = "1.7.3"

        # save the config
        with (REGOLITH_PATH / "config.json").open("w") as f:
            json.dump(data, f, indent="\t")

        # update the release_config.json
        format_version = 5
        release_config["format_version"] = 5
        with (PACK_FOLDER / "release_config.json").open("w") as f:
            json.dump(release_config, f, indent=4)
    if format_version == 5 and REPO_NAME != "NULL" and bjt is not None:
        # open regolith config
        data = bjt.load_jsonc(REGOLITH_PATH / "config.json").data

        # if the version of the filtersdefinitions of the content_guide_generator is lower then "1.7.3" set it to that version.
        if "content_guide_generator" in data["regolith"]["filterDefinitions"]:
            if data["regolith"]["filterDefinitions"]["content_guide_generator"]["version"] < "1.7.5":
                data["regolith"]["filterDefinitions"]["content_guide_generator"]["version"] = "1.7.5"

        # save the config
        with (REGOLITH_PATH / "config.json").open("w") as f:
            json.dump(data, f, indent="\t")

        # update the release_config.json
        format_version = 6
        release_config["format_version"] = 6
        with (PACK_FOLDER / "release_config.json").open("w") as f:
            json.dump(release_config, f, indent=4)
    if format_version == 6 and REPO_NAME != "NULL" and bjt is not None:
        # open regolith config
        data = bjt.load_jsonc(REGOLITH_PATH / "config.json").data

        if "system_template" in data["regolith"]["filterDefinitions"]:
            if data["regolith"]["filterDefinitions"]["system_template"]["version"] < "3.11.0":
                data["regolith"]["filterDefinitions"]["system_template"]["version"] = "3.11.0"

        if "system_template_esbuild" in data["regolith"]["filterDefinitions"]:
            if data["regolith"]["filterDefinitions"]["system_template_esbuild"]["version"] < "2.1.0":
                data["regolith"]["filterDefinitions"]["system_template_esbuild"]["version"] = "2.1.0"

        # get the default profile
        default_profile = data["regolith"]["profiles"]["default"]

        system_template = None
        system_template_esbuild = None

        for filter in default_profile["filters"]:
            if filter["filter"] == "system_template":
                system_template = filter
            elif filter["filter"] == "system_template_esbuild":
                system_template_esbuild = filter

        if system_template is None:
            # adding system template
            system_template = {
                "filter": "system_template",
                "settings": {
                    "log_path": "system_template_log.json",
                    "scope": {
                        "esbuild_path": "data/system_template_esbuild"
                    },
                    "scope_path": "scope.json"
                }
            }
            name_ninja_index = next((i for i, item in enumerate(default_profile["filters"]) if item['filter'] == 'name_ninja'), -1)
            default_profile["filters"].insert(name_ninja_index, system_template)
        else:
            if "scope" not in system_template["settings"]:
                system_template["settings"]["scope"] = {
                    "esbuild_path": "data/system_template_esbuild"
                }

        if system_template_esbuild is None:
            # adding system template esbuild
            system_template_esbuild = {
                "filter": "system_template_esbuild",
                "settings": {
                    "entryPoint": "data/system_template_esbuild/main.ts",
                    "external": [
                        "@minecraft/server"
                    ],
                    "minify": False,
                    "outfile": "`BP/scripts/{path_namespace}/main.js`",
                    "scope_path": "scope.json"
                }
            }
            system_template_index = next((i for i, item in enumerate(default_profile["filters"]) if item['filter'] == 'system_template'), -1)
            default_profile["filters"].insert(system_template_index, system_template_esbuild)


        # duplicate the default profile to a new profile called debugger
        data["regolith"]["profiles"]["debugger"] = copy.deepcopy(default_profile)

        # list of filters that should be removed from the debugger profile
        filters_to_remove = ["texture_list", "content_guide_generator", "cgg_world_settings"]

        # remove the filters from the debugger profile
        for filter_to_remove in filters_to_remove:
            data["regolith"]["profiles"]["debugger"]["filters"] = [filter for filter in data["regolith"]["profiles"]["debugger"]["filters"] if filter["filter"] != filter_to_remove]

        # getting product_key from the release_config file
        product_key = release_config["product_key"].lower()

        # remove the export settings from the debugger profile
        data["regolith"]["profiles"]["debugger"].pop("export", None)

        # set the export settings to this:
        export = {
            "bpPath": "../debugger/bp",
            "readOnly": True,
            "rpPath": "../debugger/rp",
            "target": "exact"
        }
        data["regolith"]["profiles"]["debugger"]["export"] = export

        # get the system template filter from the debugger profile
        system_template = next((filter for filter in data["regolith"]["profiles"]["debugger"]["filters"] if filter["filter"] == "system_template"), None)
        system_template["settings"]["scope"] = {"esbuild_path": f"BP/scripts/shapescape/{product_key}/"}

        system_template_esbuild = next((filter for filter in data["regolith"]["profiles"]["debugger"]["filters"] if filter["filter"] == "system_template_esbuild"), None)
        system_template_esbuild["settings"]["entryPoint"] = f"BP/scripts/shapescape/{product_key}/main.ts"
        system_template_esbuild["settings"]["sourcemap"] = True

        # adding copy filter
        data["regolith"]["filterDefinitions"]["copy_everywhere"] = {
            "url": "github.com/Shapescape-Software/copy-everywhere",
            "version": "1.0.0"
        }

        data["regolith"]["profiles"]["debugger"]["filters"].insert(0, {
            "filter": "copy_everywhere",
            "settings": {
                "values": [
                    {
                        "dest": "BP/scripts/node_modules",
                        "src": "data/node_modules/"
                    },
                    {
                        "dest": "BP/scripts/package-lock.json",
                        "src": "data/package-lock.json"
                    }
                ]
            }
        })

        # save the config
        with (REGOLITH_PATH / "config.json").open("w") as f:
            json.dump(data, f, indent="\t")

        # copy system_template auto_map from template to this project
        shutil.copy(TEMPLATE / "regolith/filters_data/system_template/auto_map.json", REGOLITH_PATH / "filters_data/system_template/auto_map.json")
        # copy gitignore
        shutil.copy(TEMPLATE / ".gitignore", Path(".gitignore"))

        # update the release_config.json
        format_version = 7
        release_config["format_version"] = 7
        with (PACK_FOLDER / "release_config.json").open("w") as f:
            json.dump(release_config, f, indent=4)
    if format_version == 7 and REPO_NAME != "NULL" and bjt is not None:
        # copy gitignore
        shutil.copy(TEMPLATE / ".gitignore", Path(".gitignore"))

        shutil.copy(TEMPLATE / "debugger.code-workspace", Path("debugger.code-workspace"))

        # update the release_config.json
        format_version = 8
        release_config["format_version"] = 8
        with (PACK_FOLDER / "release_config.json").open("w") as f:
            json.dump(release_config, f, indent=4)
    if format_version == 8 and REPO_NAME != "NULL" and bjt is not None:
        # open regolith config
        data = bjt.load_jsonc(REGOLITH_PATH / "config.json").data

        # remove "regolith"[format_version] from the config
        data["regolith"].pop("format_version", None)

        # add "regolith"[formatVersion] to the config and set it to "1.4.0"
        data["regolith"]["formatVersion"] = "1.4.0"

        # save the config
        with (REGOLITH_PATH / "config.json").open("w") as f:
            json.dump(data, f, indent="\t")
        
        # update the release_config.json
        format_version = 9
        release_config["format_version"] = 9
        with (PACK_FOLDER / "release_config.json").open("w") as f:
            json.dump(release_config, f, indent=4)
    if format_version == 9 and REPO_NAME != "NULL" and bjt is not None:
        # Add education UUID fields if they don't exist
        if "edu_creator_uuid" not in release_config:
            release_config["edu_creator_uuid"] = "a423c8e7-21b1-40ea-b0f4-e1cdd048ee1e"
        
        if "edu_world_creator_uuid" not in release_config:
            release_config["edu_world_creator_uuid"] = ""
        
        # update the release_config.json
        format_version = 10
        release_config["format_version"] = 10
        with (PACK_FOLDER / "release_config.json").open("w") as f:
            json.dump(release_config, f, indent=4)
    if format_version == 10 and REPO_NAME != "NULL" and bjt is not None:
        # Add dual world support fields if they don't exist
        if "exported_world_bedrock" not in release_config:
            release_config["exported_world_bedrock"] = release_config.get("exported_world", "WORLD_NAME")
        
        if "exported_world_edu" not in release_config:
            release_config["exported_world_edu"] = release_config.get("exported_world", "WORLD_NAME") + "_EDU"
        
        if "product_name" not in release_config:
            release_config["product_name"] = release_config.get("product_name", "")
        
        if "product_name_edu" not in release_config:
            release_config["product_name_edu"] = release_config.get("product_name", "") + " (Education Edition)"
        
        if "enable_bedrock_pipeline" not in release_config:
            release_config["enable_bedrock_pipeline"] = True
        
        if "enable_edu_pipeline" not in release_config:
            release_config["enable_edu_pipeline"] = False
        
        # update the release_config.json
        format_version = 11
        release_config["format_version"] = 11
        with (PACK_FOLDER / "release_config.json").open("w") as f:
            json.dump(release_config, f, indent=4)
    if format_version == 11 and REPO_NAME != "NULL" and bjt is not None:
        # open regolith config
        data = bjt.load_jsonc(REGOLITH_PATH / "config.json").data

        # Add shapescape_world_settings filter definition if not present
        if "shapescape_world_settings" not in data["regolith"]["filterDefinitions"]:
            data["regolith"]["filterDefinitions"]["shapescape_world_settings"] = {
                "url": "github.com/ShapescapeMC/Shapescape-World-Settings",
                "version": "1.0.1"
            }

        # Replace level_dat_updater with shapescape_world_settings in all profiles
        for profile_name, profile_data in data["regolith"]["profiles"].items():
            if "filters" in profile_data:
                for filter_item in profile_data["filters"]:
                    if isinstance(filter_item, dict) and filter_item.get("filter") == "level_dat_updater":
                        # Simply rename the filter, keep all settings unchanged
                        filter_item["filter"] = "shapescape_world_settings"
                        # Ensure levelname_path is present in settings
                        if "settings" in filter_item and "levelname_path" not in filter_item["settings"]:
                            # Add levelname_path if it's missing
                            level_dat_path = filter_item["settings"].get("level_dat_path", "")
                            if level_dat_path:
                                # Derive levelname_path from level_dat_path
                                levelname_path = level_dat_path.replace("level.dat", "levelname.txt")
                                filter_item["settings"]["levelname_path"] = levelname_path

        # Remove level_dat_updater from filter definitions if it exists
        data["regolith"]["filterDefinitions"].pop("level_dat_updater", None)

        # save the config
        with (REGOLITH_PATH / "config.json").open("w") as f:
            json.dump(data, f, indent="\t")

        # update the release_config.json
        format_version = 12
        release_config["format_version"] = 12
        with (PACK_FOLDER / "release_config.json").open("w") as f:
            json.dump(release_config, f, indent=4)
    
    # Apply packs
    remove_init()


if __name__ == "__main__":
    main()
