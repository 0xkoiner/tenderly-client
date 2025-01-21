import os
import sys
import asyncio
import platform
from pathlib import Path
from loguru import logger

from colorama import Fore, Style

if getattr(sys, 'frozen', False):
    ROOT_DIR = Path(sys.executable).parent.absolute()

else:
    ROOT_DIR = Path(__file__).parent.parent.absolute()

if platform.system() == 'Windows':
    GREEN = ''
    LIGHTGREEN_EX = ''
    RED = ''
    BLUE = ''
    RESET_ALL = ''
else:
    GREEN = Fore.GREEN
    LIGHTGREEN_EX = Fore.LIGHTGREEN_EX
    RED = Fore.RED
    BLUE = Fore.BLUE
    RESET_ALL = Style.RESET_ALL

FILES_DIR = os.path.join(ROOT_DIR, 'files')
ABIS_DIR = os.path.join(ROOT_DIR, 'data', 'abis')



logger.add(f'{FILES_DIR}/debug.log', format='{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}', level='DEBUG')
