"""
Contains colors to be used in tests console ouptut.
"""

from colorama import Fore, Back, Style

# color of pass messages
PASS = Fore.LIGHTGREEN_EX
# color of fail messages
FAIL = Fore.LIGHTRED_EX
# color of console output of tested script
CONSOLE = Fore.LIGHTYELLOW_EX
# color of delete messages
DELETE = Fore.LIGHTRED_EX
# default color
DEFAULT = Style.RESET_ALL