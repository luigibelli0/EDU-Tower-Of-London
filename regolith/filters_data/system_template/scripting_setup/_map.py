[
    # Manifest Setup
    ## This is merged to the manifest in BP to add the scripting file with the namespaced name.
    {
        "source": "manifest.json",
        "target": "BP/manifest.json",
        "on_conflict": "merge",
        "json_template": True,
    },
]
