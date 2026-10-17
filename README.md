# CS 1.6 Model Manager

A terminal app, styled like Claude Code, for managing `.mdl` models in Counter-Strike 1.6.

Drop in a model and it is installed in the right place inside `cstrike/models`, with a backup of the original. You can also build **skinpacks**, which are folders with the main CS models that you can apply or share.

## Features

- Installs `.mdl` files into the correct folder automatically (weapons, player models and player texture files)
- Backs up the original file the first time it is replaced, and restores it on demand
- Creates skinpacks from your current game files or from new `.mdl` files
- Applies a skinpack to the game in one command
- Claude Code style interface: slash commands, autocomplete, orange accent and arrow-key menus
- Finds your CS 1.6 folder automatically, or lets you browse for it

## Requirements

- Python 3.8 or newer
- Windows, macOS or Linux (made for a Windows CS 1.6 install)
- Two packages: `prompt_toolkit` and `rich`

## Installation

```
py -m pip install prompt_toolkit rich
```

If `py` is not recognized, use `python -m pip install prompt_toolkit rich`. If Python is not installed, get it from [python.org](https://www.python.org/downloads/) and tick **Add python.exe to PATH** in the installer.

## Usage

Open `cmd` or PowerShell in the folder with `cs16_models.py` and run:

```
py cs16_models.py
```

Use a real terminal. The app will not work in the output panel of an editor.

### Quick start

1. Run `/path` and choose your CS 1.6 `models` folder. This is only needed once, and it is saved.
2. Put your `.mdl` files in `data/incoming/`.
3. Run `/install`.
4. Start the game.

You can also paste or drag a `.mdl` file or a folder into the prompt to install it straight away.

## Commands

| Command | What it does |
|---|---|
| `/install [file\|folder\|all]` | Installs `.mdl` files. With no argument it installs everything in `data/incoming/` |
| `/list` | Shows how many default models exist in your game and how many you replaced |
| `/restore [name\|all]` | Puts the original models back. A name filters by path, for example `/restore ak47` |
| `/skinpack list` | Lists your skinpacks |
| `/skinpack create <name>` | Opens a menu to choose which groups of models to copy from the game into a new pack |
| `/skinpack add <name> [file\|all]` | Adds `.mdl` files from `data/incoming/` to a pack |
| `/skinpack apply <name>` | Installs a skinpack into the game, with backups |
| `/skinpack delete <name>` | Deletes a skinpack |
| `/path [folder]` | Chooses the `cstrike/models` folder. With no argument it opens a menu. `/models` does the same |
| `/clear` | Clears the screen |
| `/help` | Lists all commands |
| `/exit` | Quits (`/quit`, `exit` and `quit` also work) |

Type `/` to see autocomplete with descriptions.

In menus, use the arrow keys (or `j` / `k`) to move and `enter` to confirm. In the skinpack menu, `space` toggles an item, `a` toggles all or none, and `esc` cancels.

## How models are placed

The destination is chosen from the file name:

| File name | Installed to |
|---|---|
| `leet.mdl`, `gign.mdl`, `sas.mdl`, ... | `models/player/<name>/<name>.mdl` |
| `leetT.mdl`, `gsg9T.mdl`, ... | `models/player/<name>/<name>T.mdl` (texture file) |
| `v_ak47.mdl`, `p_awp.mdl`, `w_usp.mdl`, ... | `models/<name>.mdl` |
| Any other name | Replaces a file with the same name if one exists in `models/`, otherwise the app asks which model to replace |

Known player models: `arctic`, `gign`, `gsg9`, `guerilla`, `leet`, `sas`, `terror`, `urban`, `vip`.

Weapon prefixes:

- `v_` is the view model, the weapon in your hands
- `p_` is the third-person model, the weapon held by players
- `w_` is the world model, the weapon on the ground

If your file has a custom name like `ak47_gold.mdl`, the app asks which model it should replace. Answer with a name like `v_ak47` or `leet`.

## Backups and restore

- The first time a file is replaced, the original is copied to `data/backups/`.
- If a file did not exist before, it is recorded as new and deleted on restore.
- Installing over a file again does not overwrite the saved original.
- `/restore all` puts everything back as it was. Skinpacks go through the same backup system, so they can be undone too.

## Skinpacks

A skinpack is a folder in `data/skinpacks/<name>/` that mirrors the game's `models` folder, so you can zip it and share it.

`/skinpack create` lets you choose from these groups:

- Player models (CT and T, including texture files)
- View models (`v_*`)
- Third-person models (`p_*`)
- World models (`w_*`)

Only files that exist in your game folder are copied.

## Folder layout

```
cs16_models.py
README.md
data/
├── incoming/      put your .mdl files here
├── backups/       original files, saved on first replace
├── skinpacks/     your skinpacks
├── config.json    saved models folder
└── manifest.json  tracks what you replaced
```

The `data/` folder is created automatically next to the script.

## Troubleshooting

| Problem | Fix |
|---|---|
| `'pip' is not recognized` | Use `py -m pip install prompt_toolkit rich` or reinstall Python with **Add to PATH** ticked |
| The window closes instantly | Run it from `cmd` or PowerShell so you can read the error |
| `Models folder not found` | Run `/path` and choose the folder again |
| A file is skipped as "unknown" | Rename it like the original (for example `v_ak47.mdl`) or answer the prompt when it asks |
| Nothing changes in game | Restart the game, and check that the model in the game folder is not overridden by a server or a custom map |

## Notes

- Only `.mdl` files are handled. Sounds, sprites and other files are not touched.
- Close the game before installing if you want the new models to load on the next start.
- Models are copied as they are. The app does not check whether a `.mdl` file is valid.
