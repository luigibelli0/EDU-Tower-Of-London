This file describes the expected content of this directory and what files
are added to the release file from `package_release.yml` github action. This
README file is not copied into the release.

# Expected content of this directory (`pack`)
```
screenshot_0.png         (1920x1080)
screenshot_1.png         (1920x1080)
screenshot_2.png         (1920x1080)
screenshot_3.png         (1920x1080)
screenshot_4.png         (1920x1080)
pack_icon.png           (max. 256x256)
panorama.jpg            (max. 450x4000)
keyart.png              (1920x1080)
partner_art.png         (included in template world, always the same)
release_config.json     (includes "pack_creator_name" & "pack_map_name"
```

# Output created by the `package_release.yml` Github action
## `[ZIP]/Content`
```
/Content/world_template/resource_packs/0/
    pack_icon.png            (max. 256x256)  converted from /pack/pack_icon.png
/Content/world_template/behavior_packs/0/
    pack_icon.png            (max. 256x256)  converted from /pack/pack_icon.png

...and the world files like behavior- and resource- packs, level.dat etc.
```

## `[ZIP]/Marketing Art`
```
*_Marketingkeyart.png        (1920x1080)     converted from /pack/keyart.png
*_MarketingScreenshot_0.png    (1920x1080)   converted from /pack/screenshot0.png
*_MarketingScreenshot_1.png    (1920x1080)   converted from /pack/screenshot1.png
*_MarketingScreenshot_2.png    (1920x1080)   converted from /pack/screenshot2.png
*_MarketingScreenshot_3.png    (1920x1080)   converted from /pack/screenshot3.png
*_MarketingScreenshot_4.png    (1920x1080)   converted from /pack/screenshot4.png
*_PartnerArt.png        (1920x1080)          copy of /pack/partner_art.png
```

## `[ZIP]/Store Art`
```
*_packicon.jpg            (max. 256x256)  converted from /pack/pack_icon.png
*_panorama_0.jpg        (max. 450x4000)   converted from /pack/panorama.jpg
*_Thumbnail_0.jpg        (800x450)        converted from /pack/keyart.png
*_Screenshot_0.jpg        (800x450)       converted from /pack/screenshot0.png
*_Screenshot_1.jpg        (800x450)       converted from /pack/screenshot1.png
*_Screenshot_2.jpg        (800x450)       converted from /pack/screenshot2.png
*_Screenshot_3.jpg        (800x450)       converted from /pack/screenshot3.png
*_Screenshot_4.jpg        (800x450)       converted from /pack/screenshot4.png
```

*=name of the world, this can be the full name but usually I abbreviate it,
for example: Dinosaur Arena becomes DA. Example: DA_Marketingkeyart.png
