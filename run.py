
import subprocess
import sys
import time
import signal
import os

class Colors:
    OKGREEN = '\033[92m'
    OKCYAN = '\033[96m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_banner():
    banner = f"""
{Colors.OKGREEN}╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║  {Colors.BOLD}🚀  APK Studio - Multi-Bot Runner  🚀{Colors.ENDC}{Colors.OKGREEN}              ║
║                                                           ║
║  ✨ Bot 1: APK Generator                                 ║
║  🎯 Bot 2: Payload Injector                              ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝{Colors.ENDC}