## AI Contributor Guide – World Template (Bedrock)

Purpose: Enable fast, correct changes to this Minecraft Marketplace world template. Focus edits on source inputs (regolith filters + systems), never on generated output packs.

### Core Architecture

1. Regolith orchestrates a filter pipeline (see `regolith/config.json`). Profiles:
   - default: authoring / rapid iteration
   - debug: default + colorized function name logging
   - debugger: exports to `debugger/` read‑only pack paths + runs extra filters + loopback exemptions
   - packaging: production build (minify, level.dat update) for release automation
2. Content sources live under `regolith/filters_data/` (systems, scripts, scopes, templates). Output behavior & resource packs are written into `packs/BP` & `packs/RP` (or profile export paths). Do not hand‑edit output.
3. Modular systems use the `system_template` filter. Each system folder (e.g. `marketing_banners/`, `warp/`, `world_version/`) contains:
   - `_map.py` (file mapping rules)
   - `_scope.json` (optional per‑system overrides)
   - Content files (`*.mcfunction`, entities, resources, etc.)
4. Scripting pipeline:
   - Author TypeScript in `regolith/filters_data/system_template_esbuild/main.ts` (empty scaffold) or per‑system TS/JS sources.
   - `system_template_esbuild` bundles to `BP/scripts/{path_namespace}/main.js` (sourcemap in non‑packaging profiles, no minify by default).
   - A placeholder namespace `shapescape` is token‑replaced by `text_replacer` using values from `regolith/filters_data/scope.json` (e.g. `colon_namespace`, `path_namespace`). Use those scope variables instead of literal strings when adding new placeholder patterns.

### Key Files & Their Roles

| File                                            | Role                                                                              |
| ----------------------------------------------- | --------------------------------------------------------------------------------- |
| `regolith/config.json`                          | Defines filters & profile order (read before changing pipeline).                  |
| `regolith/filters_data/scope.json`              | Source‑of‑truth namespace variables; update when changing naming.                 |
| `system_template/scripting_setup/manifest.json` | Script module manifest; adjust `dependencies` (e.g. `@minecraft/server` version). |
| `system_template/default_init/init.mcfunction`  | Sets up scoreboards & constants (names rely on namespace replacements).           |
| `.scripts/*.ps1`                                | Developer workflows (tasks call these). Prefer tasks over manual commands.        |

### Developer Workflows (use VS Code Tasks)

- Install deps: runs `.scripts/install_dependencies.ps1` (npm install inside `filters_data`, then `regolith install-all` & update). Run after pulling new filters.
- Build run (default): `.scripts/build.ps1` → `regolith run` (default profile) to local development world.
- Debug run: `.scripts/debug.ps1` → `regolith run` + `regolith run debugger` + loopback exemptions (enables network/script debugging across Minecraft variants).
- Export / Import world (Bedrock): `.scripts/export_bedrock.ps1` / `.scripts/import_bedrock.ps1` via `haze` tool.
- Export / Import Education: same with COM_MOJANG env set (see corresponding scripts).
- Packaging (CI): GitHub Action uses `packaging` profile → minify, update level.dat, produce marketing/store art from `pack/` assets.

### Adding / Modifying Script Code

1. Add or edit a system folder under `system_template/` if logic belongs to a distinct feature area.
2. For system scripts, create a `main.js` (or TS pre‑bundle) plus `subscripts/*.js`; import subscripts in `main.js` (see root README example) and map them in `_map.py` with `on_conflict` set to `append_start` for `main.js`.
3. Keep placeholder namespace tokens (`shapescape_`, `shapescape:`, etc.)—the filter pipeline rewrites them. Hard‑coding final names breaks portability.
4. Sync API module versions: update `@minecraft/server` version in `scripting_setup/manifest.json` (and optionally dev dependency for autocompletion) together.

### Scoreboards & Initialization

`default_init/init.mcfunction` establishes predictable objectives (e.g. `shapescape_tmp`, `shapescape_const`). Reuse them instead of creating parallel objectives; add new constants by extending that file only if shared across multiple systems.

### Naming & Namespaces

Modify `scope.json` if the project namespace changes; the text replacement filters will cascade. Do not manually rename existing paths or prefixes in content files—adjust scope variables instead to avoid partial mismatches.

### Common Pitfalls

- Editing generated pack files → changes discarded next build. Always modify sources under `filters_data`.
- Forgetting `append_start` on system `main.js` merge → breaks multi‑system script aggregation.
- Hard‑coding final namespace strings instead of placeholders → blocks automated rename.
- Updating script API version only in one place → runtime/editor mismatch.

### If You Add New Automation

Document any new filters or tasks here: list profile insertion point, required scope vars, and whether output is deterministic.

Questions / Gaps? Ask for: desired namespace changes, additional filters, or script API version targets before large refactors.
