from textual import on
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical

from textual.widgets import Button, Footer, RichLog

from .config import TUI_TCSS


class Sidebar(Vertical):
    def compose(self) -> ComposeResult:
        yield Button(label="SHOW ENVIRONMENT", id="show_env")
        yield Button(label="UPDATE SETTINGS", id="update_gsettings")
        yield Button(label="CLEAR RICHLOG", id="clear_richlog")


class Atui(App):
    BINDINGS = [
        ("s", "toggle_sidebar", "Toggle Sidebar"),
        ("q", "quit", "Quit"),
    ]
    CSS_PATH = TUI_TCSS

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

    @on(Button.Pressed, "#show_env")
    def show_environment(self):
        self.query_one(RichLog).write("environment info here")

    @on(Button.Pressed, "#clear_richlog")
    def clear_richlog(self):
        self.query_one(RichLog).clear()


def run_tui():
    app = Atui()
    app.run()
