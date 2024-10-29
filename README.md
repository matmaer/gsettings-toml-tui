# gsettings-toml-tui

This repository is now archived.
During the build research, I found out about the Gio and PyGObject python packages, which are also available in PyPi.

No need to call "gsettings" with subprocess.  Obviously, it's a better way to use the Python repositories from Gnome.

Also, the app will be inproved based on the Textual demo's.

The new repository can be found here: [GnomeSettingsTomlTui](https://github.com/matmaer/GnomeSettingsTomlTui)

---
### **Original Readme:**

Terminal app with modern terminal user interface, to set a batch of [Gnome](https://www.gnome.org/) user settings in the dconf database.

The desired settings are created after editing the generated config file for all settings. Both contain the setting-schemas with keys and values. Values types and ranges are visualized.

Gnome is [available](https://www.gnome.org/getting-gnome/) for most major Linux distributions.

Changing these settings is normally done in the Gnome GUI by the user.  On some occasions, for example to configure a newly created user or to verify your current settings against your custom config; you could save some time as opposed to doing this "manually" in the Gnome GUI.

Build with [Textual](https://github.com/Textualize/textual), which is part of probably the best Rapid Application Development framework for Python at present time. It's lean, stable and user friendly, at least from my experience. See also [textual.textualize.io](https://textual.textualize.io/).

The main purpose of this project is learning and growing towards a more useful app. The goal is to go through one full circle of coding, integration and deployment and prepare for the next iteration that could still go in any direction.

This exercise aims to deploy a small bug free Textual TUI app nonetheles.  Subsequently adding a small new feature, so it makes sense to test, integrate and deploy without breaking things.
