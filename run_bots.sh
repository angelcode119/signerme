#!/bin/bash
# Multi-Bot Runner for Linux/Mac
# Run both bots simultaneously

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Print banner
echo -e "${BLUE}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                                                           ║${NC}"
echo -e "${BLUE}║  ${GREEN}🚀  Multi-Bot Runner - Professional Edition 🚀${BLUE}       ║${NC}"
echo -e "${BLUE}║                                                           ║${NC}"
echo -e "${BLUE}║  ${GREEN}✨ APK Generator Studio${BLUE}                              ║${NC}"
echo -e "${BLUE}║  ${CYAN}🔍 APK Analyzer Studio${BLUE}                               ║${NC}"
echo -e "${BLUE}║                                                           ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if files exist
if [ ! -f "m.py" ]; then
    echo -e "${RED}❌ Error: m.py not found!${NC}"
    exit 1
fi

if [ ! -f "bot2.py" ]; then
    echo -e "${RED}❌ Error: bot2.py not found!${NC}"
    exit 1
fi

echo -e "${GREEN}✅ All bot files found${NC}"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo -e "${YELLOW}🛑 Stopping all bots...${NC}"
    
    if [ ! -z "$BOT1_PID" ]; then
        kill $BOT1_PID 2>/dev/null
        echo -e "${CYAN}[Bot 1]${NC} Stopped"
    fi
    
    if [ ! -z "$BOT2_PID" ]; then
        kill $BOT2_PID 2>/dev/null
        echo -e "${CYAN}[Bot 2]${NC} Stopped"
    fi
    
    echo -e "${GREEN}✅ All bots stopped${NC}"
    exit 0
}

# Trap Ctrl+C
trap cleanup INT TERM

echo -e "${BLUE}Starting bots...${NC}"
echo ""

# Start Bot 1 in background
python3 m.py > bot1.log 2>&1 &
BOT1_PID=$!
echo -e "${GREEN}[Bot 1 - Generator]${NC} Started! PID: $BOT1_PID"

sleep 2

# Start Bot 2 in background
python3 bot2.py > bot2.log 2>&1 &
BOT2_PID=$!
echo -e "${CYAN}[Bot 2 - Analyzer]${NC} Started! PID: $BOT2_PID"

echo ""
echo -e "${GREEN}✅ All bots started successfully!${NC}"
echo -e "${YELLOW}Press Ctrl+C to stop all bots${NC}"
echo ""
echo -e "${BLUE}Logs:${NC}"
echo -e "  Bot 1: bot1.log"
echo -e "  Bot 2: bot2.log"
echo ""

# Wait for processes
while true; do
    # Check if Bot 1 is still running
    if ! kill -0 $BOT1_PID 2>/dev/null; then
        echo -e "${RED}[Bot 1]${NC} Stopped unexpectedly"
        cleanup
    fi
    
    # Check if Bot 2 is still running
    if ! kill -0 $BOT2_PID 2>/dev/null; then
        echo -e "${RED}[Bot 2]${NC} Stopped unexpectedly"
        cleanup
    fi
    
    sleep 1
done
