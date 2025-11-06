#!/usr/bin/env python3
"""
Multi-Bot Runner
Run both bots simultaneously
"""

import subprocess
import sys
import time
import signal
import os

# ANSI colors for pretty output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_banner():
    """Print startup banner"""
    banner = f"""
{Colors.OKBLUE}╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║  {Colors.BOLD}🚀  Multi-Bot Runner - Professional Edition 🚀{Colors.ENDC}{Colors.OKBLUE}       ║
║                                                           ║
║  {Colors.OKGREEN}✨ APK Generator Studio{Colors.OKBLUE}                              ║
║  {Colors.OKCYAN}🔍 APK Analyzer Studio{Colors.OKBLUE}                               ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝{Colors.ENDC}
"""
    print(banner)


def run_bot(bot_file, bot_name, color):
    """Run a single bot"""
    print(f"{color}[{bot_name}]{Colors.ENDC} Starting...")
    
    try:
        process = subprocess.Popen(
            [sys.executable, bot_file],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            bufsize=1,
            universal_newlines=True
        )
        
        print(f"{color}[{bot_name}]{Colors.ENDC} {Colors.OKGREEN}Started!{Colors.ENDC} PID: {process.pid}")
        return process
        
    except Exception as e:
        print(f"{color}[{bot_name}]{Colors.ENDC} {Colors.FAIL}Failed to start: {str(e)}{Colors.ENDC}")
        return None


def main():
    """Main runner function"""
    print_banner()
    
    # Check if bot files exist
    if not os.path.exists('m.py'):
        print(f"{Colors.FAIL}❌ Error: m.py not found!{Colors.ENDC}")
        sys.exit(1)
    
    if not os.path.exists('bot2.py'):
        print(f"{Colors.FAIL}❌ Error: bot2.py not found!{Colors.ENDC}")
        sys.exit(1)
    
    print(f"{Colors.OKGREEN}✅ All bot files found{Colors.ENDC}\n")
    
    processes = []
    
    # Start Bot 1 (APK Generator)
    print(f"{Colors.HEADER}Starting bots...{Colors.ENDC}\n")
    bot1 = run_bot('m.py', 'Bot 1 - Generator', Colors.OKGREEN)
    if bot1:
        processes.append(('Bot 1', bot1))
    
    time.sleep(2)  # Wait between starts
    
    # Start Bot 2 (APK Analyzer)
    bot2 = run_bot('bot2.py', 'Bot 2 - Analyzer', Colors.OKCYAN)
    if bot2:
        processes.append(('Bot 2', bot2))
    
    if not processes:
        print(f"\n{Colors.FAIL}❌ No bots started successfully!{Colors.ENDC}")
        sys.exit(1)
    
    print(f"\n{Colors.OKGREEN}✅ All bots started successfully!{Colors.ENDC}")
    print(f"{Colors.WARNING}Press Ctrl+C to stop all bots{Colors.ENDC}\n")
    
    # Handle Ctrl+C
    def signal_handler(sig, frame):
        print(f"\n\n{Colors.WARNING}🛑 Stopping all bots...{Colors.ENDC}")
        
        for name, process in processes:
            try:
                process.terminate()
                print(f"{Colors.OKCYAN}[{name}]{Colors.ENDC} Terminated")
            except:
                pass
        
        print(f"{Colors.OKGREEN}✅ All bots stopped{Colors.ENDC}")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    # Monitor processes
    try:
        while True:
            time.sleep(1)
            
            # Check if any process died
            for name, process in processes:
                if process.poll() is not None:
                    print(f"{Colors.FAIL}[{name}]{Colors.ENDC} Stopped unexpectedly (exit code: {process.returncode})")
                    
                    # Print last output
                    try:
                        output = process.stdout.read()
                        if output:
                            print(f"{Colors.WARNING}Last output:{Colors.ENDC}")
                            print(output)
                    except:
                        pass
    
    except KeyboardInterrupt:
        signal_handler(None, None)


if __name__ == '__main__':
    main()
