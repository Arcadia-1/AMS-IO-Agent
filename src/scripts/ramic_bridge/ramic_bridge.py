"""
RAMIC Bridge Python Client Library

This module provides a Python interface to execute Skill commands in Virtuoso
through the RAMIC Bridge daemon, allowing Python applications to communicate
with Virtuoso's Skill interpreter via TCP socket connection.

Usage:
    from ramic_bridge import RBExc
    
    # Execute a simple Skill command (uses .env settings automatically)
    result = RBExc('1+2', timeout=10)
    print(result)
    
    # Execute more complex Skill code
    result = RBExc('''
        let((x y)
            x = 10
            y = 20
            x + y
        )
    ''', timeout=30)
    print(result)
    
    # Override host/port if needed
    result = RBExc('1+2', host='101.6.68.224', port=65432)

Dependencies:
    - socket: For TCP communication
    - json: For request serialization
    - os: For environment variables
    - dotenv: For .env file loading
"""

import socket
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def RBExc(skill: str, host: str = None, port: int = None, timeout: int = 30) -> str:
    """
    Executes Skill code in Virtuoso through the RAMIC Bridge.
    
    Args:
        skill (str): The Skill code to execute in Virtuoso.
        host (str, optional): The host address of the RAMIC Bridge daemon. 
                             If None, reads from RB_HOST environment variable (default: "127.0.0.1").
        port (int, optional): The port number of the RAMIC Bridge daemon.
                             If None, reads from RB_PORT environment variable (default: 65432).
        timeout (int): The timeout in seconds for the operation (default: 30).
    
    Returns:
        str: The result returned from Virtuoso's Skill interpreter.
        
    Example:
        result = RBExc('1+2', timeout=10)  # Uses .env settings automatically
        result = RBExc('1+2', host='101.6.68.224', port=65432)  # Override settings
    """
    # Get host and port from environment variables if not provided
    if host is None:
        host = os.getenv("RB_HOST", "127.0.0.1")
    
    if port is None:
        try:
            port = int(os.getenv("RB_PORT", "65432"))
        except (ValueError, TypeError):
            port = 65432
    
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
            # Package timeout parameter and skill script as JSON and send
            request_data = {
                "skill": skill,
                "timeout": timeout
            }
            s.sendall(json.dumps(request_data).encode('utf-8'))
            ret = s.recv(1024*1024).decode('utf-8', errors='ignore')
            s.shutdown(socket.SHUT_RDWR)
            s.close()
            return ret
    except Exception as e:
        print(f"RBExc ERROR: {e}\n",e)
        return ""
        



if __name__ == "__main__":
    print("Testing RAMIC Bridge with automatic .env configuration...")
    print(f"Using host: {os.getenv('RB_HOST', '127.0.0.1')}")
    print(f"Using port: {os.getenv('RB_PORT', '65432')}")
    print("-" * 50)
    # Example usage when run as a script

    # results = RBExc('1+2', timeout=10, host='101.6.68.224', port=65432)	# connect to thu-tang (101.6.68.224)
    # print(f"[1+2] results: {results}\n")

    
    results = RBExc("printf(\"\\n\\n\\n\")", timeout=10)
    print(f"[printf empty line] results: {results}\n")
    
    
    results = RBExc('list(1 2 3 4 5)', timeout=10)
    print(f"[list(1 2 3 4 5)] results: {results}\n")

    results = RBExc('1+2+3+4+5', timeout=10)
    print(f"[calculation] results: {results}\n")

    # with open('test_skill_code_to_execute.txt', 'r') as file:
    #     skill_code = file.read()
    # print(skill_code)
    # results = RBExc(skill_code, timeout=10, host='101.6.68.224', port=65432)	# connect to thu-tang (101.6.68.224)
    # print(f"[test_skill_code_to_execute] results: {results}\n")

    # results2 = RBExc('''
    #     let((x y)
    #         x = 1000
    #         y = 200
    #         x + y
    #     )
    # ''', timeout=30, host='101.6.68.224', port=65432)	# connect to thu-tang (101.6.68.224)
    # print(f"[multiple lines] results: {results2}\n")

    # try:
    #     result = RBExc(
    #         'csh("/home/lixintian/RAMIC_LXT/AMS-IO-Agent/scripts/run_pex.csh test_PEX LLM_Layout_Design")',
    #     )
    #     print(f"Command execution result: {result}")
    # except Exception as e:
    #     print(f"Command execution failed: {str(e)}")
