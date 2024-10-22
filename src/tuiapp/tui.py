import subprocess

from textual import on
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, Footer, Header, RichLog

from .config import TUI_TCSS, get_toml


class Sidebar(Vertical):
    def compose(self) -> ComposeResult:
        yield Button(
            label="Generate",
            id="gen_toml",
            tooltip="Generate toml file with current settings",
        )
        yield Button(
            label="Customize",
            id="custom_toml",
            tooltip="create or show customized settings toml file",
        )
        yield Button(
            label="Compare",
            id="compare_settings",
            tooltip="Compare current settings with custom settings",
        )
        yield Button(
            label="Update",
            id="update_settings",
            tooltip="Update settings with 'gsettings set' to match the custom toml file",
        )
        yield Button(label="Clear \nRichLog", id="clear_richlog")


class GSettings(App):
    BINDINGS = [
        ("s", "toggle_sidebar", "Toggle Maximized"),
        ("q", "quit", "Quit"),
    ]
    CSS_PATH = TUI_TCSS

    def __init__(self):
        super().__init__()
        self.desired = get_toml()
        # list of dicts with schema, key, old value and new value
        self.updates = []

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
                if "gsettings set" in command and result.stdout == "":
                    # gsettings set returns nothing on success
                    return "success"
                return result.stdout
            return "error"
        except subprocess.CalledProcessError as e:
            if e.stdout != "":
                self.rlog(e.stdout)
            if e.stderr != "":
                self.rlog(e.stderr)
            else:
                self.rlog(e)
            return "error"

    def create_current_settings_toml(self) -> None:
        schemas = self.run_gsettings_command("gsettings list-schemas")
        return schemas

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

    def update_settings(self) -> None:
        self.rlog("[cyan underline]Settings Update[/]")
        # self.rlog("No changes to update, run 'Compare Settings' first")
        if len(self.updates) == 0:
            self.rlog("Nothing to do, run 'Compare Settings' to check.")
        else:
            for update in self.updates:
                schema = update["schema"]
                key = update["key"]
                old_value = update["old_value"]
                new_value = update["new_value"]
                command = f'gsettings set {schema} {key} "{new_value}"'
                result = self.run_gsettings_command(command)
                if result == "success":
                    to_print = [
                        f"  [yellow]{schema}[/] [green bold]UPDATED[/]",
                        f"    [green]{key}: [/]{new_value} (old value: {old_value})",
                    ]
                    self.rlog("\n".join(to_print))
                else:
                    self.rlog(f"Error running '{command}'")
            self.updates = []
        self.rlog("")

    def compare_settings(self) -> list:
        self.rlog("[cyan underline]Settings Comparison[/]")
        for schema, keys in self.desired.items():
            changes_needed_for_schema = False
            # self.rlog(f"[yellow]{schema}[/]")
            for key, des_val in keys.items():
                cur_val = self.get_current_value(schema, key)
                if cur_val == "error":
                    self.rlog(f"Error getting {schema} {key} value, skipping")
                else:
                    if str(des_val) != str(cur_val):
                        to_print = [
                            f"[yellow]{schema}[/][red] TO UPDATE[/]",
                            f"  [green]{key}:[/] {cur_val}",
                            f"    [bold]desired: {des_val}[/]",
                        ]
                        self.rlog("\n".join(to_print))
                        self.updates += [
                            {
                                "schema": schema,
                                "key": key,
                                "old_value": cur_val,
                                "new_value": des_val,
                            }
                        ]
                        changes_needed_for_schema = True
            if not changes_needed_for_schema:
                self.rlog(f"[yellow]{schema}[/]: [green]no changes needed[/]")
        self.rlog("")

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

    def action_toggle_sidebar(self):
        self.query_one(Sidebar).toggle_class("-hidden")

    @on(Button.Pressed, "#gen_toml")
    def generate_toml_settings(self):
        self.rlog("[cyan underline]Generate Toml file: to do[/]")
        self.rlog("")

    @on(Button.Pressed, "#custom_toml")
    def show_toml_button(self):
        self.rlog("[cyan underline]Desired Settings[/]")
        self.rlog(self.desired)
        self.rlog("")

    @on(Button.Pressed, "#compare_settings")
    def compare_settings_button(self):
        self.compare_settings()

    @on(Button.Pressed, "#update_settings")
    def update_settings_button(self):
        self.update_settings()

    @on(Button.Pressed, "#clear_richlog")
    def clear_richlog(self):
        self.query_one(RichLog).clear()


def run_tui():
    app = GSettings()
    app.run()
