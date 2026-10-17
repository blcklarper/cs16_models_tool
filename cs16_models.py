import json
import shutil
import sys
from pathlib import Path

try:
    from prompt_toolkit import PromptSession
    from prompt_toolkit.application import Application
    from prompt_toolkit.completion import Completer, Completion
    from prompt_toolkit.formatted_text import HTML
    from prompt_toolkit.key_binding import KeyBindings
    from prompt_toolkit.layout import Layout, Window
    from prompt_toolkit.layout.controls import FormattedTextControl
    from prompt_toolkit.styles import Style
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text
except ImportError:
    print("Missing dependencies. Run:  pip install prompt_toolkit rich")
    input("Press Enter to close...")
    sys.exit(1)

APP = Path(__file__).resolve().parent / "data"
INCOMING = APP / "incoming"
BACKUPS = APP / "backups"
SKINPACKS = APP / "skinpacks"
CONFIG = APP / "config.json"
MANIFEST = APP / "manifest.json"

DEFAULT_MODELS_DIR = r"C:\Games\CS 1.6 GoldClient\cstrike\models"
ACCENT = "#d97757"

console = Console()

MASCOT = [" ▐▛███▜▌ ", "▝▜█████▛▘", "  ▘▘ ▝▝  "]

SELECT_STYLE = Style.from_dict({
    "title": "bold",
    "hint": "#888888",
    "cur": ACCENT + " bold",
    "on": ACCENT,
    "off": "#888888",
})

PLAYERS = ["arctic", "gign", "gsg9", "guerilla", "leet", "sas", "terror", "urban", "vip"]

WEAPONS = [
    "ak47", "aug", "awp", "deagle", "elite", "famas", "fiveseven", "flashbang",
    "g3sg1", "galil", "glock18", "hegrenade", "knife", "m249", "m3", "m4a1",
    "mac10", "mp5", "p228", "p90", "scout", "sg550", "sg552", "smokegrenade",
    "tmp", "ump45", "usp", "xm1014", "c4",
]
WORLD_EXTRA = ["backpack", "c4", "kevlar", "assault", "thighpack", "shield"]

GROUPS = {
    "players": ("Player models (CT + T)", [f"player/{p}/{p}.mdl" for p in PLAYERS]
                + [f"player/{p}/{p}T.mdl" for p in PLAYERS]),
    "view":    ("View models  v_*  (weapon in your hands)", [f"v_{w}.mdl" for w in WEAPONS]),
    "third":   ("Third-person  p_*  (weapon held by players)", [f"p_{w}.mdl" for w in WEAPONS if w != "c4"]),
    "world":   ("World models  w_*  (weapon on the ground)",
                [f"w_{w}.mdl" for w in WEAPONS if w != "c4"] + [f"w_{w}.mdl" for w in WORLD_EXTRA]),
}
KNOWN_ROOT = {Path(f).stem.lower() for g in GROUPS.values() for f in g[1] if "/" not in f}


def load_json(path: Path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def save_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


cfg = {"models_dir": DEFAULT_MODELS_DIR}


def models_dir() -> Path:
    return Path(cfg["models_dir"])


def select_multi(title, items, selected=None):
    keys = [k for k, _ in items]
    state = {"i": 0, "sel": set(keys if selected is None else selected)}
    kb = KeyBindings()

    @kb.add("up")
    @kb.add("k")
    def _(event):
        state["i"] = (state["i"] - 1) % len(keys)

    @kb.add("down")
    @kb.add("j")
    def _(event):
        state["i"] = (state["i"] + 1) % len(keys)

    @kb.add("space")
    def _(event):
        k = keys[state["i"]]
        state["sel"] ^= {k}

    @kb.add("a")
    def _(event):
        state["sel"] = set() if len(state["sel"]) == len(keys) else set(keys)

    @kb.add("enter")
    def _(event):
        event.app.exit(result=[k for k in keys if k in state["sel"]])

    @kb.add("escape", eager=True)
    @kb.add("c-c")
    def _(event):
        event.app.exit(result=None)

    def render():
        out = [("class:title", title + "\n"),
               ("class:hint", "space toggle · ↑/↓ move · a all/none · enter confirm · esc cancel\n\n")]
        for n, (k, label) in enumerate(items):
            cur = n == state["i"]
            on = k in state["sel"]
            out.append(("class:cur" if cur else "", "❯ " if cur else "  "))
            out.append(("class:on" if on else "class:off", "[x] " if on else "[ ] "))
            out.append(("class:cur" if cur else "", label + "\n"))
        return out

    app = Application(
        layout=Layout(Window(FormattedTextControl(render, show_cursor=False), dont_extend_height=True)),
        key_bindings=kb,
        style=SELECT_STYLE,
        full_screen=False,
        erase_when_done=True,
    )
    return app.run()


def select_one(title, items):
    state = {"i": 0}
    kb = KeyBindings()

    @kb.add("up")
    @kb.add("k")
    def _(event):
        state["i"] = (state["i"] - 1) % len(items)

    @kb.add("down")
    @kb.add("j")
    def _(event):
        state["i"] = (state["i"] + 1) % len(items)

    @kb.add("enter")
    def _(event):
        event.app.exit(result=items[state["i"]][0])

    @kb.add("escape", eager=True)
    @kb.add("c-c")
    def _(event):
        event.app.exit(result=None)

    def render():
        out = [("class:title", title + "\n"),
               ("class:hint", "↑/↓ move · enter select · esc cancel\n\n")]
        for n, (k, label) in enumerate(items):
            cur = n == state["i"]
            out.append(("class:cur" if cur else "", ("❯ " if cur else "  ") + f"{n + 1}. {label}\n"))
        return out

    app = Application(
        layout=Layout(Window(FormattedTextControl(render, show_cursor=False), dont_extend_height=True)),
        key_bindings=kb,
        style=SELECT_STYLE,
        full_screen=False,
        erase_when_done=True,
    )
    return app.run()


def say(msg: str):
    console.print(Text("● ", style=ACCENT) + Text.from_markup(msg))


def sub(msg: str):
    console.print(Text.from_markup(f"  [dim]⎿[/dim]  {msg}"))


def err(msg: str):
    console.print(Text.from_markup(f"[red]✗[/red] {msg}"))


def rel_for(stem: str):
    stem = stem.lower()
    if stem in PLAYERS:
        return Path("player") / stem / f"{stem}.mdl"
    if stem.endswith("t") and stem[:-1] in PLAYERS:
        return Path("player") / stem[:-1] / f"{stem[:-1]}T.mdl"
    if stem in KNOWN_ROOT:
        return Path(f"{stem}.mdl")
    return None


def ask_target(mdl: Path):
    try:
        answer = console.input(
            f"  [yellow]?[/yellow] {mdl.name} is not a known name. "
            f"Which model should it replace? (e.g. v_ak47, leet, Enter = skip): "
        ).strip().lower()
    except (EOFError, KeyboardInterrupt):
        return None
    if answer.endswith(".mdl"):
        answer = answer[:-4]
    return rel_for(answer) if answer else None


def rel_dest(mdl: Path):
    rel = rel_for(mdl.stem)
    if rel:
        return rel
    if models_dir().exists():
        for hit in models_dir().rglob(mdl.name):
            return hit.relative_to(models_dir())
    return ask_target(mdl)


def backup_and_copy(src: Path, rel: Path):
    dest = models_dir() / rel
    manifest = load_json(MANIFEST, {})
    key = rel.as_posix()
    if key not in manifest:
        if dest.exists():
            b = BACKUPS / rel
            b.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(dest, b)
            manifest[key] = "original"
        else:
            manifest[key] = "new"
        save_json(MANIFEST, manifest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)


def collect(arg: str):
    arg = arg.strip().strip('"').strip("'")
    if not arg or arg.lower() == "all":
        return sorted(INCOMING.glob("*.mdl"))
    p = Path(arg)
    if not p.exists():
        p = INCOMING / arg
        if not p.exists() and not arg.lower().endswith(".mdl"):
            p = INCOMING / f"{arg}.mdl"
    if p.is_dir():
        return sorted(p.rglob("*.mdl"))
    return [p] if p.is_file() and p.suffix.lower() == ".mdl" else []


def cmd_install(arg: str):
    files = collect(arg)
    if not files:
        return err(f"No .mdl files found. Put them in [bold]{INCOMING}[/bold] or give a path.")
    if not models_dir().exists():
        return err(f"Models folder not found: {models_dir()}  (run /path)")
    ok = 0
    for f in files:
        rel = rel_dest(f)
        if rel is None:
            sub(f"[yellow]?[/yellow] {f.name}: unknown model, skipped "
                f"(rename it like the original, e.g. v_ak47.mdl)")
            continue
        backup_and_copy(f, rel)
        sub(f"[green]✓[/green] {f.name}  →  models/{rel.as_posix()}")
        ok += 1
    say(f"Installed [bold]{ok}[/bold]/{len(files)} model(s). Use /restore to undo.")


def cmd_restore(arg: str):
    manifest = load_json(MANIFEST, {})
    if not manifest:
        return say("Nothing to restore.")
    arg = arg.strip().lower()
    keys = list(manifest) if arg in ("", "all") else [k for k in manifest if arg in k.lower()]
    if not keys:
        return err("No installed model matches that.")
    for k in keys:
        dest = models_dir() / k
        if manifest[k] == "original":
            shutil.copy2(BACKUPS / k, dest)
            sub(f"[green]↺[/green] restored {k}")
        else:
            dest.unlink(missing_ok=True)
            sub(f"[green]✗[/green] removed {k} (did not exist originally)")
        manifest.pop(k)
    save_json(MANIFEST, manifest)
    say(f"Restored {len(keys)} file(s).")


def cmd_list(_=""):
    if not models_dir().exists():
        return err(f"Models folder not found: {models_dir()}")
    t = Table(border_style="dim", header_style=ACCENT)
    t.add_column("Group")
    t.add_column("Found in game", justify="right")
    t.add_column("Replaced by you", justify="right")
    manifest = load_json(MANIFEST, {})
    for key, (title, files) in GROUPS.items():
        found = sum((models_dir() / f).exists() for f in files)
        mine = sum(f in manifest for f in files)
        t.add_row(title, f"{found}/{len(files)}", str(mine))
    console.print(t)
    inc = list(INCOMING.glob("*.mdl"))
    sub(f"{len(inc)} file(s) waiting in {INCOMING}")


def pack_dir(name: str) -> Path:
    return SKINPACKS / name


def cmd_skinpack(arg: str):
    parts = arg.split(maxsplit=2)
    action = parts[0].lower() if parts else "list"
    name = parts[1] if len(parts) > 1 else ""

    if action == "list":
        packs = [p for p in SKINPACKS.iterdir() if p.is_dir()] if SKINPACKS.exists() else []
        if not packs:
            return say("No skinpacks yet. Try [bold]/skinpack create <name>[/bold]")
        for p in packs:
            n = len(list(p.rglob("*.mdl")))
            sub(f"[bold]{p.name}[/bold]  ({n} models)")

    elif action == "create":
        if not name:
            return err("Usage: /skinpack create <name>")
        res = select_multi(
            f"Create skinpack [{name}] — which models do you want to copy from your game?",
            [(k, v[0]) for k, v in GROUPS.items()],
        )
        if not res:
            return say("Cancelled.")
        n = 0
        for g in res:
            for f in GROUPS[g][1]:
                src = models_dir() / f
                if src.exists():
                    dst = pack_dir(name) / f
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src, dst)
                    n += 1
        say(f"Skinpack [bold]{name}[/bold] created with {n} models → {pack_dir(name)}")

    elif action == "add":
        if not name:
            return err("Usage: /skinpack add <name> [file|all]")
        files = collect(parts[2] if len(parts) > 2 else "all")
        n = 0
        for f in files:
            rel = rel_dest(f)
            if rel is None:
                sub(f"[yellow]?[/yellow] {f.name}: unknown, skipped")
                continue
            dst = pack_dir(name) / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, dst)
            sub(f"[green]+[/green] {rel.as_posix()}")
            n += 1
        say(f"Added {n} model(s) to [bold]{name}[/bold].")

    elif action == "apply":
        if not pack_dir(name).exists():
            return err("Skinpack not found. Use /skinpack list")
        files = list(pack_dir(name).rglob("*.mdl"))
        for f in files:
            backup_and_copy(f, f.relative_to(pack_dir(name)))
        say(f"Applied skinpack [bold]{name}[/bold] ({len(files)} models). /restore to undo.")

    elif action == "delete":
        if pack_dir(name).exists():
            shutil.rmtree(pack_dir(name))
            say(f"Deleted skinpack {name}.")
        else:
            err("Skinpack not found.")
    else:
        err("Usage: /skinpack [list|create|add|apply|delete] <name>")


def normalize_dir(p: str) -> str:
    path = Path(p.strip().strip('"').strip("'"))
    if (path / "cstrike" / "models").is_dir():
        return str(path / "cstrike" / "models")
    if path.name.lower() == "cstrike" and (path / "models").is_dir():
        return str(path / "models")
    return str(path)


def detect_installs():
    found = []
    patterns = [
        "Games/*/cstrike/models",
        "Games/cstrike/models",
        "*/cstrike/models",
        "Program Files (x86)/Steam/steamapps/common/Half-Life/cstrike/models",
        "Program Files/Steam/steamapps/common/Half-Life/cstrike/models",
        "Steam/steamapps/common/Half-Life/cstrike/models",
    ]
    for letter in "CDEFGHIJKLMNOPQRSTUVWXYZ":
        root = Path(f"{letter}:/")
        try:
            if not root.exists():
                continue
            for pat in patterns:
                for hit in root.glob(pat):
                    if hit.is_dir() and str(hit) not in found:
                        found.append(str(hit))
        except OSError:
            continue
    return found


def browse_dir():
    try:
        import tkinter
        from tkinter import filedialog
        root = tkinter.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        chosen = filedialog.askdirectory(title="Select your cstrike or cstrike/models folder")
        root.destroy()
        return chosen or None
    except Exception:
        err("Folder picker is not available here. Type the path instead.")
        return None


def set_models_dir(p: str):
    cfg["models_dir"] = normalize_dir(p)
    save_json(CONFIG, cfg)
    ok = models_dir().exists()
    say(f"Models folder: [bold]{models_dir()}[/bold] " + ("[green](found)[/green]" if ok else "[red](not found)[/red]"))


def cmd_path(arg: str):
    if arg.strip():
        return set_models_dir(arg)
    detected = detect_installs()
    items = [(f"d:{d}", d) for d in detected]
    items += [("browse", "Browse for a folder…"), ("type", "Type a path…"), ("keep", f"Keep current ({models_dir()})")]
    choice = select_one("Choose your CS 1.6 models folder", items)
    if choice is None or choice == "keep":
        return say(f"Models folder unchanged: [bold]{models_dir()}[/bold]")
    if choice.startswith("d:"):
        return set_models_dir(choice[2:])
    if choice == "browse":
        picked = browse_dir()
        return set_models_dir(picked) if picked else say("Cancelled.")
    try:
        typed = console.input("  [bold]Path:[/bold] ").strip()
    except (EOFError, KeyboardInterrupt):
        typed = ""
    set_models_dir(typed) if typed else say("Cancelled.")


def cmd_help(_=""):
    for c, (_, d) in COMMANDS.items():
        console.print(f"  [{ACCENT}]{c:<24}[/{ACCENT}] [dim]{d}[/dim]")


COMMANDS = {
    "/install [file|folder|all]": (cmd_install, "Install .mdl files (default: everything in incoming/)"),
    "/list": (cmd_list, "Show which default models exist / were replaced"),
    "/restore [name|all]": (cmd_restore, "Put the original models back"),
    "/skinpack list": (cmd_skinpack, "List skinpacks"),
    "/skinpack create <name>": (cmd_skinpack, "Copy the main CS models from the game into a pack"),
    "/skinpack add <name> [file|all]": (cmd_skinpack, "Add incoming .mdl files to a pack"),
    "/skinpack apply <name>": (cmd_skinpack, "Install a pack into the game"),
    "/skinpack delete <name>": (cmd_skinpack, "Delete a pack"),
    "/path [folder]": (cmd_path, "Choose the cstrike/models folder (menu if no folder given)"),
    "/help": (cmd_help, "Show commands"),
    "/exit": (None, "Quit"),
}


class SlashCompleter(Completer):
    def get_completions(self, document, complete_event):
        text = document.text_before_cursor
        if not text.startswith("/"):
            return
        for c, (_, desc) in COMMANDS.items():
            if c.startswith(text):
                insert = c.split(" <")[0].split(" [")[0]
                yield Completion(insert, start_position=-len(text), display=c, display_meta=desc)


def banner():
    grid = Table.grid(padding=(0, 3))
    grid.add_column()
    grid.add_column()
    right = [
        Text.from_markup("[bold]CS 1.6 Model Manager[/bold] [dim]v1.0[/dim]"),
        Text.from_markup(f"[dim]{models_dir()}[/dim]"),
        Text.from_markup("[dim]/help for commands[/dim]"),
    ]
    for m, r in zip(MASCOT, right):
        grid.add_row(Text(m, style=ACCENT), r)
    console.print(Panel(
        grid,
        title=f"[{ACCENT}]✻[/{ACCENT}] Welcome",
        title_align="left",
        border_style=ACCENT,
        padding=(1, 2),
        expand=False,
    ))
    console.print(Text.from_markup(
        "  [dim]Tips: drop .mdl files in [/dim]"
        f"[{ACCENT}]data/incoming[/{ACCENT}][dim] then run /install, or paste a file path.[/dim]\n"
    ))


def main():
    for d in (INCOMING, BACKUPS, SKINPACKS):
        d.mkdir(parents=True, exist_ok=True)
    cfg.update(load_json(CONFIG, {}))
    save_json(CONFIG, cfg)

    console.clear()
    banner()
    if not models_dir().exists():
        err(f"Default folder not found: {models_dir()}  → run /path to choose it")

    style = Style.from_dict({
        "prompt": ACCENT + " bold",
        "bottom-toolbar": "noreverse #888888",
        "completion-menu.completion": "bg:#262626 #cccccc",
        "completion-menu.completion.current": "bg:#d97757 #000000",
        "completion-menu.meta.completion": "bg:#262626 #888888",
        "completion-menu.meta.completion.current": "bg:#d97757 #000000",
    })
    session = PromptSession(completer=SlashCompleter(), complete_while_typing=True, style=style)
    rule = "─" * min(console.width, 100)

    while True:
        try:
            console.print(f"[dim]{rule}[/dim]")
            line = session.prompt(
                HTML("<prompt>&gt; </prompt>"),
                bottom_toolbar=HTML(" / for commands · ctrl+c to quit"),
            ).strip()
            console.print(f"[dim]{rule}[/dim]")
        except (KeyboardInterrupt, EOFError):
            break
        if not line:
            continue
        if line in ("/exit", "/quit", "exit", "quit"):
            break

        if not line.startswith("/"):
            cmd_install(line)
            continue

        word, _, arg = line[1:].partition(" ")
        handler = {
            "install": cmd_install, "list": cmd_list, "restore": cmd_restore,
            "skinpack": cmd_skinpack, "path": cmd_path, "models": cmd_path, "help": cmd_help,
        }.get(word.lower())
        if handler:
            try:
                handler(arg)
            except Exception as e:
                err(f"{type(e).__name__}: {e}")
        else:
            err(f"Unknown command /{word}. Try /help")
    console.print("[dim]bye 👋[/dim]")


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    try:
        main()
    except Exception:
        import traceback
        traceback.print_exc()
        input("\nPress Enter to close...")
