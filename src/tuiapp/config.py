import tomllib
from pathlib import Path

CONFIGS_DIR = Path(__file__).resolve().parent / "configs"

TUI_TCSS = CONFIGS_DIR / "tui.tcss"


def get_toml():
    try:
        with open(CONFIGS_DIR / "gsettings.toml", "rb") as f:
            return tomllib.load(f)
    except FileNotFoundError as not_found:
        raise not_found
