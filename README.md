# Regolith Scripting Template
Guide for using the template, and general scripting information.

## How to use this template
Simply use this as your world template as all required features are setup for use. There is no additional setup needed to make this work with scripting. 

## Getting vs-code autocomplete
You can get autocompletion for your VS-code for the different modules of scripting. This is not required, but useful. You can find the versions of the different modules on npmjs.com for example for @minecraft/server the version and their commands can be found here: https://www.npmjs.com/package/@minecraft/server?activeTab=versions 
Requires Node.js

### Scripting information
Scripting in currently in a state of flux, and things are/have been changing very often. This section will change almost weekly. 

Make sure to have the correct version of each module inside the BP/manifest.json like this

``` json
    {
        "module_name": "@minecraft/server",
        "version": "1.3.0"
    }
```

One of the better locations to learn whats inside of the scripting API is the module article on learn.microsoft.com (https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/minecraft-server). 
You can also look at the bedrock wiki, however this information may be out of date (https://wiki.bedrock.dev/scripting/starting-scripts.html)

## Using Scripting within System Template
The repository is set up in a way that we have an empty main.js file in the behavior pack.

In your system you need to have at least two files. A main.js and the subscript that you want to write. You can have multiple script files as well. It is recommened to have your subscript be named after your system, so make it easier to understand the compiled files.

In the main.js of the system you need to import your subscript.
```js
import "./subscripts/custom_random_tick.js";
```

It is recommened to have all the subscript files in a subscript directory, to make them easier to find within a system. Then your _map.py file could look like this.

```py
[
    {
        "source": "main.js",
        "target": AUTO,
        "on_conflict": "append_start"
    },
    {
        "source": "subscripts/*.js",
        "target": AUTO,
        "on_conflict": "stop"
    }
]
```

Important is that you have you merge your main.js file with the `"on_conflict": "append_start"`. This will ensure that this works well with other systems using scripting.