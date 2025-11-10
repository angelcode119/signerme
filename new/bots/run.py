#!/usr/bin/env python3
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
    print(f"{Colors.OKGREEN}APK Studio - Multi-Bot Runner{Colors.ENDC}")
    print(f"{Colors.OKGREEN}Bot 1: APK Generator{Colors.ENDC}")
    print(f"{Colors.OKCYAN}Bot 2: Payload Injector{Colors.ENDC}")


def main():
    print_banner()
    bot1_path = os.path.join('bots', 'bot1_generator.py')
    bot2_path = os.path.join('bots', 'bot2_payload.py')
    if not os.path.exists(bot1_path):
        print(f"{Colors.FAIL}Bot 1 not found: {bot1_path}{Colors.ENDC}")
        sys.exit(1)
    if not os.path.exists(bot2_path):
        print(f"{Colors.FAIL}Bot 2 not found: {bot2_path}{Colors.ENDC}")
        sys.exit(1)
    processes = []
    print(f"{Colors.OKGREEN}[Bot 1]{Colors.ENDC} Starting...")
    try:
        bot1 = subprocess.Popen([sys.executable, bot1_path])
        processes.append(('Bot 1', bot1))
        print(f"{Colors.OKGREEN}[Bot 1]{Colors.ENDC} Started! PID: {bot1.pid}")
    except Exception as e:
        print(f"{Colors.FAIL}[Bot 1] Failed: {e}{Colors.ENDC}")
    time.sleep(2)
    print(f"{Colors.OKCYAN}[Bot 2]{Colors.ENDC} Starting...")
    try:
        bot2 = subprocess.Popen([sys.executable, bot2_path])
        processes.append(('Bot 2', bot2))
        print(f"{Colors.OKCYAN}[Bot 2]{Colors.ENDC} Started! PID: {bot2.pid}")
    except Exception as e:
        print(f"{Colors.FAIL}[Bot 2] Failed: {e}{Colors.ENDC}")
    if not processes:
        print(f"\n{Colors.FAIL}No bots started!{Colors.ENDC}")
        sys.exit(1)
    print(f"\n{Colors.OKGREEN}All bots started!{Colors.ENDC}")
    print(f"{Colors.WARNING}Press Ctrl+C to stop{Colors.ENDC}\n")
    def signal_handler(sig, frame):
        print(f"\n\n{Colors.WARNING}Stopping all bots...{Colors.ENDC}")
        for name, process in processes:
            try:
                process.terminate()
                print(f"[{name}] Stopped")
            except:
                pass
        print(f"{Colors.OKGREEN}Done{Colors.ENDC}")
        sys.exit(0)
    signal.signal(signal.SIGINT, signal_handler)
    try:
        while True:
            time.sleep(1)
            for name, process in processes:
                if process.poll() is not None:
                    print(f"{Colors.FAIL}[{name}] Stopped (exit code: {process.returncode}){Colors.ENDC}")
    except KeyboardInterrupt:
        signal_handler(None, None)


if __name__ == '__main__':
    main()
