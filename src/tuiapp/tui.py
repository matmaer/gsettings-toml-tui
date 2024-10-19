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
            if result.returncode == 0 and result.stdout != "":
                cur_val = result.stdout.strip("'\n ")
                # return str(result.stdout).strip(" \t\n")
                return cur_val
            return "error"
        except subprocess.CalledProcessError as e:
            if e.stdout != "":
                self.rlog(e.stdout)
            elif e.stderr != "":
                self.rlog(e.stderr)
            else:
                self.rlog(e)
            return "error"

    def compare_settings(self) -> None:
        for schema, schema_key in self.desired.items():
            self.rlog(f"[yellow]{schema}[/]")
            # des_val is short for "desired value"
            for schema_key, des_val in schema_key.items():
                gsettings_cmd = f"gsettings get {schema} {schema_key}"
                # cur_val means current (active) value
                cur_val = self.run_gsettings_command(gsettings_cmd)
                # 'gsettings get' sometimes returns types, sometimes not.
                # So, remove types from the output to compare values.
                # to check if ok for 'gsettings set' command and all cases
                to_remove = ["uint32 ", "uint64 ", "int32 ", "int64 "]
                for text in to_remove:
                    cur_val = cur_val.replace(text, "")
                if cur_val != "error":
                    # self.rlog(f"{schema_key}: {cur_val}  {des_val}")
                    if str(des_val) != str(cur_val):
                        to_print = [
                            f"[red]{schema_key} is different[/]",
                            f"current: {cur_val}",
                            f"desired: {des_val}",
                        ]
                        self.rlog("\n".join(to_print))
                    else:
                        self.rlog(f"{schema_key} already has value {des_val}")
                else:
                    self.rlog(f"Error retrieving value for {schema_key}, aborting")
                    break

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

    @on(Button.Pressed, "#clear_richlog")
    def clear_richlog(self):
        self.query_one(RichLog).clear()


def run_tui():
    app = Atui()
    app.run()
