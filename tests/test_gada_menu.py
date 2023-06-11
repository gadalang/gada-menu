from typing import TYPE_CHECKING
import sys
from unittest.mock import patch

from gada_menu import main
from context_menu.pytest_plugin import MockedWinReg


def test_main(mocked_winreg: MockedWinReg) -> None:
    """Test the entrypoint."""
    # Install the menu
    with patch("sys.argv", ["", "install"]):
        main()
    mocked_winreg.assert_context_menu("Software\\Classes\\*\\shell", "Gada")
    mocked_winreg.assert_context_command(
        "Software\\Classes\\*\\shell\\Gada\\shell",
        "Rebuild",
        '"{}" -m gada run rebuild "%1"'.format(sys.executable),
    )

    # Remove the menu
    with patch("sys.argv", ["", "uninstall"]):
        main()
    assert mocked_winreg.get_key_value("Software\\Classes\\*\\shell\\Gada", "") == None
