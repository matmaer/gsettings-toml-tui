from gsettings_toml.tui import GSettings


def main() -> None:
    app = GSettings()
    app.run()


if __name__ == "__main__":
    main()
