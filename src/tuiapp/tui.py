import subprocess

from textual import on
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, Footer, RichLog

from .config import TUI_TCSS, get_toml


class Sidebar(Vertical):
    def compose(self) -> ComposeResult:
        yield Button(
            label="Desired Settings",
            id="show_toml",
        )
        yield Button(
            label="Compare Settings",
            id="compare_settings",
        )
        yield Button(
            label="Update Settings",
            id="update_settings",
        )
        yield Button(label="Clear RichLog", id="clear_richlog")


class Atui(App):
    BINDINGS = [
        ("s", "toggle_sidebar", "Toggle Maximized"),
        ("q", "quit", "Quit"),
    ]
    CSS_PATH = TUI_TCSS

    def __init__(self):
        super().__init__()
        self.desired = get_toml()

    def rlog(self, to_print: str) -> None:
        self.query_one(RichLog).write(to_print)

    def run_gsettings_command(self, command: str) -> str:
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                check=True,
                encoding="utf-8",
                shell=True,
                timeout=1,
            )
            if result.returncode == 0:
                if "gsettings get" in command:
                    return result.stdout
                if "gsettings set" in command:
                    # gsettings set returns nothing on success
                    return "success"
            return "error"
        except subprocess.CalledProcessError as e:
            if e.stdout != "":
                self.rlog(e.stdout)
            if e.stderr != "":
                self.rlog(e.stderr)
            else:
                self.rlog(e)
            return "error"

    def update_setting(self, schema: str, schema_key: str, value: str) -> None:
        gsettings_cmd = f"gsettings set {schema} {schema_key} {value}"
        result = self.run_gsettings_command(gsettings_cmd)
        return result

    def get_current_value(self, schema: str, schema_key: str) -> str:
        gsettings_cmd = f"gsettings get {schema} {schema_key}"
        current_value = self.run_gsettings_command(gsettings_cmd)
        # trim from both ends: single quotes, newlines and spaces
        current_value = current_value.strip("'\n ")
        # 'gsettings get' sometimes returns types, sometimes not.
        # So, remove types from the output to compare values.
        # to check if ok for 'gsettings set' command and all cases
        to_remove = ["uint32 ", "uint64 ", "int32 ", "int64 "]
        for text in to_remove:
            current_value = current_value.replace(text, "")
        return current_value

    def compare_settings(self) -> None:
        for schema, schema_key in self.desired.items():
            self.rlog(f"[yellow]{schema}[/]")
            for schema_key, des_val in schema_key.items():
                cur_val = self.get_current_value(schema, schema_key)
                if cur_val == "error":
                    self.rlog(f"Error getting {schema} {schema_key} value, skipping")
                else:
                    if str(des_val) == str(cur_val):
                        self.rlog(f"{schema_key} already has value {des_val}, skipping")
                    else:
                        to_print = [
                            f"[red]{schema_key} is different[/]",
                            f"current: {cur_val}",
                            f"desired: {des_val}",
                        ]
                        self.rlog("\n".join(to_print))

    def compose(self) -> ComposeResult:
        with Horizontal():
            yield Sidebar(id="sidebar")
            yield RichLog(
                highlight=True,
                wrap=False,
                markup=True,
            )
        yield Footer()

    def action_toggle_sidebar(self):
        self.query_one(Sidebar).toggle_class("-hidden")

    @on(Button.Pressed, "#show_toml")
    def show_toml_settings(self):
        self.rlog(self.desired)

    @on(Button.Pressed, "#compare_settings")
    def compare_settings_button(self):
        self.compare_settings()

    @on(Button.Pressed, "#update_settings")
    def update_settings_button(self):
        pass

    @on(Button.Pressed, "#clear_richlog")
    def clear_richlog(self):
        self.query_one(RichLog).clear()


def run_tui():
    app = Atui()
    app.run()
