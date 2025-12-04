#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ANSI color codes
ORANGE = '\033[33m'
GREEN = '\033[32m'
CYAN = '\033[36m'
PURPLE = '\033[35m'
RED = '\033[31m'
BLUE = '\033[34m'
YELLOW = '\033[93m'  # Bright yellow
RESET = '\033[0m'

def test_color_codes():
    """Test ANSI color codes output"""
    print(f"{ORANGE}This is ORANGE (\\033[33m){RESET}")
    print(f"{GREEN}This is GREEN (\\033[32m){RESET}")
    print(f"{CYAN}This is CYAN (\\033[36m){RESET}")
    print(f"{PURPLE}This is PURPLE (\\033[35m){RESET}")
    print(f"{RED}This is RED (\\033[31m){RESET}")
    print(f"{BLUE}This is BLUE (\\033[34m){RESET}")
    print(f"{YELLOW}This is BRIGHT YELLOW (\\033[93m){RESET}")
    
    # Verify color codes are defined
    assert ORANGE == '\033[33m'
    assert GREEN == '\033[32m'
    assert CYAN == '\033[36m'
    assert RESET == '\033[0m'

def test_logger_style_output():
    """Test logger-style color output"""
    print("\n")
    print(f"{ORANGE}Thought: The user is testing colors...{RESET}")
    print(f"{GREEN}Final answer: Colors are working correctly!{RESET}")
    print(f"{CYAN}[Step 1: Duration 1.23 seconds | Tokens: 100]{RESET}")
    assert True

if __name__ == "__main__":
    test_color_codes()
    test_logger_style_output()


