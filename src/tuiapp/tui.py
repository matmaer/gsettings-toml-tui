import pickle
import subprocess
from pathlib import Path

from textual import on
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, Footer, Header, RichLog

# import tomllib


CONFIGS = Path(__file__).resolve().parent / "configs"
TCSS_PATH = CONFIGS / "tui.tcss"


class Sidebar(Vertical):
    def compose(self) -> ComposeResult:
        yield Button(
            label="All Settings (long time to load first time)",
            id="all_settings",
            tooltip="show or load all current settings",
        )
        yield Button(
            label="Custom Settings",
            id="custom_settings",
        )
        yield Button(
            label="Compare",
            id="compare_settings",
            tooltip="Compare current settings with custom settings",
        )
        yield Button(
            label="Update",
            id="update_settings",
            tooltip="Update settings with 'gsettings set' command",
        )
        yield Button(label="Clear \nRichLog", id="clear_richlog")


class GSettings(App):
    def __init__(self):
        super().__init__()
        self.all_settings_pickle = CONFIGS / "all_settings.pickle"
        if self.all_settings_pickle.exists():
            with open(self.all_settings_pickle, "rb") as pickle_file:
                self.all_settings = pickle.load(pickle_file)
        else:
            self.all_settings = {}

    BINDINGS = [
        ("s", "toggle_sidebar", "Toggle Maximized"),
        ("q", "quit", "Quit"),
    ]
    CSS_PATH = TCSS_PATH

    def rlog(self, to_print: str, highlight=True) -> None:
        rich_log = self.query_one(RichLog)
        if not highlight:
            rich_log.highlight = False
        else:
            rich_log.highlight = True
        self.query_one(RichLog).write(to_print)

    def run_command(self, command: list) -> str:
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                check=True,
                encoding="utf-8",
                timeout=1,
            )
            # always remove leading and trailing spaces, tabs and newlines
            # \' will make sure the result is not returned with both single
            # and double quotes
            result.stdout = result.stdout.strip('\t\n" ')
            return result
        except subprocess.CalledProcessError as e:
            message = f"'{e.cmd}' failed, exit conde {e.returncode}"
            self.rlog(f"[tomato bold]{message}[/]")
            self.rlog(f"[lightpink bold]'{e.stdout}'[/]")
            return "error"

    def list_schemas(self) -> list:
        result = self.run_command(["gsettings", "list-schemas"])
        if result.stdout != "" and result != "error":
            schemas = result.stdout.split("\n")
            for schema in schemas:
                command = ["gsettings", "list-children", schema]
                children = self.run_command(command)
                if children != "":
                    # the schema has children, no keys for settings
                    schemas.remove(schema)
            return schemas
        # return empty list if no schemas can be retrieved
        return []

    def list_keys(self, schema: str) -> list:
        result = self.run_command(["gsettings", "list-keys", schema])
        if result.stdout in ["error", "", [], None]:
            return []
        all_keys = result.stdout.split("\n")
        to_exclude = [
            "window-width",
            "window-maximized",
            "window-height",
            "window-fullscreen",
            "recent-",
            "selected-",
            "recently-",
            "recent-",
            "last-",
        ]
        to_return = []
        for key in all_keys:
            if not any(exclude in key for exclude in to_exclude):
                to_return.append(key)
        return to_return

    def get_value(self, schema: str, key: str) -> str:
        result = self.run_command(["gsettings", "get", schema, key])
        if result != "error":
            return result.stdout
        # return empty string if no value can be retrieved
        return ""

    def get_type_and_range(self, schema: str, key: str) -> str:
        result = self.run_command(["gsettings", "range", schema, key])
        if result.stdout != "error" and result.stdout != "":
            # if ["error", ""] in result.stdout:
            if "\n" in result.stdout:
                type_range_str = result.stdout.replace("\n", ", ")
            else:
                type_range_str = result.stdout
            # make the type more readable
            types_replacements = {
                "enum": "type: enumeration;",
                "flags": "type: lags;",
                "range d": "type; range of double precision floating point;",
                "range i": "type: range of integers;",
                "type ai": "type: array of integers;",
                "type as": "type: array of strings;",
                "type av": "type: array of variants;",
                "type a": "type: array;",
                "type b": "type: boolean;",
                "type d": "type: double precision floating point;",
                "type i": "type: integer;",
                "type s": "type: string",
                "type t": "type: t;",
                "type u": "type: unsigned integer;",
            }
            # construct the range and type string
            for current, new in types_replacements.items():
                if current in type_range_str:
                    type_range_str = type_range_str.replace(current, new)
            return str(type_range_str)
        # return empty string if no type and range can be retrieved
        return ""

    def load_all_settings(self) -> dict:
        # create nested dict with all settings
        settings_dict = {}
        schemas = self.list_schemas()
        for schema in schemas:
            keys = self.list_keys(schema)
            # jump to next schema
            if keys in [[], "", "error", None]:
                continue
            settings_dict[schema] = {}
            for key in keys:
                settings_dict[schema][key] = {}
                current = self.get_value(schema, str(key))
                type_range_str = self.get_type_and_range(schema, key)
                # construct the value range
                values_dict = {
                    "value": current,
                    "type_range": str(type_range_str),
                }
                settings_dict[schema][key] = values_dict
        # with open(self.all_settings_pickle, "wb") as f:
        #     pickle.dump(settings_dict, f)
        return settings_dict

    def write_all_settings(self) -> None:
        # yield LoadingIndicator("loading all settings...") todo
        self.rlog("[cyan underline]All Settings[/]")
        if not self.all_settings_pickle.exists():
            self.all_settings = self.load_all_settings()
        else:
            with open(self.all_settings_pickle, "rb") as pickle_file:
                self.all_settings = pickle.load(pickle_file)
        for schema, keys in self.all_settings.items():
            self.rlog(f"[yellow]{schema}[/]")
            for key, value in keys.items():
                self.rlog(f"  [green]{key}[/]: [bold]{value['value']}[/]")
                type_str = self.all_settings[schema][key]["type_range"]
                type_message = f"[#87CEFA]{type_str}[/]"
                self.rlog(f"    {type_message}", highlight=False)

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal():
            yield Sidebar(id="sidebar")
            yield RichLog(
                highlight=True,
                wrap=False,
                markup=True,
            )
        yield Footer()

    @on(Button.Pressed, "#all_settings")
    def load_all_settings_button(self):
        self.write_all_settings()

    @on(Button.Pressed, "#custom_settings")
    def show_custom(self):
        self.rlog("[cyan underline]Custom Settings[/]")
        self.rlog("[lightblue]to be implemented[/]")

    @on(Button.Pressed, "#compare_settings")
    def compare_settings_button(self):
        self.rlog("[cyan underline]Settings Comparison[/]")
        self.rlog("[lightblue]to be implemented[/]")

    @on(Button.Pressed, "#update_settings")
    def update_settings_button(self):
        self.rlog("[cyan underline]Settings Update[/]")
        self.rlog("[lightblue]to be implemented[/]")

    @on(Button.Pressed, "#clear_richlog")
    def clear_richlog(self):
        self.query_one(RichLog).clear()
        self.rlog("[cyan]RichLog Cleared[/]")

    def action_toggle_sidebar(self):
        self.query_one(Sidebar).toggle_class("-hidden")


def run_tui():
    app = GSettings()
    app.run()
