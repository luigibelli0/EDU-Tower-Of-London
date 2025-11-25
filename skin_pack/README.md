This README file is not copied into the release.


Put all contents of a skin pack in here and go to the actions tab in github. There should be a workflow called `Generate Skin Pack` which when you run it will create all files necessary for the skin pack.

Skins need to be named specifically for the action to work.: 

`skin_a.png` if it is an `alex` skin

`skin_s.png` if it is an `steve` skin



If all files are correctly generated/added to this folder it will be recognised by the packaging action as well, meaning it will be packaged correctly into the zip.

If this folder has no other content then this readme, the folder it will be ignored!