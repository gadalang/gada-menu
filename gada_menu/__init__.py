from __future__ import annotations
from typing import TYPE_CHECKING
import sys
import argparse
from context_menu import menus

from . import __version__ as version_info
from .__version__ import __version_major__, __version_long__, __version__, __status__

from gada import nodeutil

if TYPE_CHECKING:
    from typing import Any

__all__ = ["install", "uninstall", "main", "__version__", "version_info"]


def install() -> None:
    """Install the gada menu."""
    uninstall()

    nodes = list(nodeutil.iter_nodes())

    for k, v in (
        ("FILES", "files"),
        ("DIRECTORY", "directory"),
        ("DIRECTORY_BACKGROUND", "background"),
    ):
        cm = menus.ContextMenu("Gada", type=k)
        tree: dict[str, Any] = {"children": {}, "menu": cm}
        for node in nodes:
            menu_config = node.config.get("menu", None)
            if not menu_config:
                continue

            if v not in menu_config["type"] and "all" not in menu_config["type"]:
                continue

            path = list(menu_config["path"])
            parent_dict = tree
            for i in range(len(path) - 1):
                child_name = path[i]
                child_dict = parent_dict["children"].get(child_name, None)
                if child_dict is None:
                    child = menus.ContextMenu(child_name)
                    child_dict = {
                        "children": {},
                        "menu": child,
                    }
                    parent_dict["menu"].add_items([child])
                    parent_dict["children"][child_name] = child_dict

                parent_dict = child_dict

            entry = menus.ContextCommand(
                path[-1],
                command='"{}" -m gada run {}{}'.format(
                    sys.executable,
                    node.config["name"],
                    ' "%1"' if k in ("FILES", "DIRECTORY") else "",
                ),
            )
            parent_dict["menu"].add_items([entry])

        cm.compile()


def uninstall() -> None:
    """Uninstall the gada menu."""
    for k in ("FILES", "DIRECTORY", "DIRECTORY_BACKGROUND"):
        try:
            menus.removeMenu("Gada", k)
        except:
            pass


def main(argv: list[str] | None = None) -> None:
    """Main entrypoint."""
    parser = argparse.ArgumentParser(prog="gada-menu", description="Help")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbosity level")
    subparsers = parser.add_subparsers(help="sub-command help", required=True)

    def parse_install(args: Any) -> None:
        install()

    def parse_uninstall(args: Any) -> None:
        uninstall()

    install_parser = subparsers.add_parser("install", help="setup the menu")
    install_parser.set_defaults(func=parse_install)

    uninstall_parser = subparsers.add_parser("uninstall", help="remove the menu")
    uninstall_parser.set_defaults(func=parse_uninstall)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
