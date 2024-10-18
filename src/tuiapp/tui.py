import subprocess

from textual import on
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, Footer, RichLog

from .config import TUI_TCSS, get_toml


class Sidebar(Vertical):
    def compose(self) -> ComposeResult:
        yield Button(label="DESIRED SETTINGS", id="show_toml")
        yield Button(label="CURRENT SETTINGS", id="show_current")
        yield Button(label="CLEAR RICHLOG", id="clear_richlog")


class Atui(App):
    BINDINGS = [
        ("s", "toggle_sidebar", "Toggle Sidebar"),
        ("q", "quit", "Quit"),
    ]
    CSS_PATH = TUI_TCSS

    def rlog(self, to_print: str) -> None:
        self.query_one(RichLog).write(to_print)

    def bash_run(self, commands: list) -> None:
        for command in commands:
            try:
                pretty_cmd = f"[bold]$_ [/][cyan]{command}[/]"
                result = subprocess.run(
                    command,
                    capture_output=True,
                    check=True,
                    encoding="utf-8",
                    shell=True,
                    timeout=2,
                )
                pretty_exit = f"([green]exit code {result.returncode}[/])"
                if result.returncode == 0 and result.stdout == "":
                    self.rlog(f"{pretty_cmd} [green](success)[/]")
                elif result.stdout != "":
                    self.rlog(f"{pretty_cmd} {pretty_exit}")
                    self.rlog(result.stdout)
                else:
                    to_print = f"{pretty_cmd} [red]{pretty_exit}[/]"
                    self.rlog(f"[yellow]{to_print}[/]")
                    if result.stdout != "":
                        self.rlog(result.stdout)
                    if result.stderr != "":
                        self.rlog(result.stderr)
            except subprocess.CalledProcessError as e:
                if e.stdout != "":
                    self.rlog(e.stdout)
                elif e.stderr != "":
                    self.rlog(e.stderr)
                else:
                    self.rlog(e)

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
        self.rlog(get_toml())

    @on(Button.Pressed, "#show_current")
    def show_current_settings(self):
        self.bash_run(["gsettings list-recursively"])

    @on(Button.Pressed, "#clear_richlog")
    def clear_richlog(self):
        self.query_one(RichLog).clear()


def run_tui():
    app = Atui()
    app.run()
