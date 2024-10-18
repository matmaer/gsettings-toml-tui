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

    def rlog(self, to_print) -> None:
        rlog = self.query_one(RichLog)
        rlog.write(to_print)

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
        self.rlog("Current settings")

    @on(Button.Pressed, "#clear_richlog")
    def clear_richlog(self):
        self.query_one(RichLog).clear()


def run_tui():
    app = Atui()
    app.run()
