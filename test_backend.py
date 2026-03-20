"""
Backend Connection Test Script
Tests the API server and WebSocket connectivity
"""

import asyncio
import requests
import websockets
import json
import sys
from typing import Dict, Any

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text: str):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(60)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}\n")

def print_test(test_name: str):
    print(f"{Colors.BOLD}Testing: {test_name}{Colors.END}")

def print_success(message: str):
    print(f"  {Colors.GREEN}✓{Colors.END} {message}")

def print_error(message: str):
    print(f"  {Colors.RED}✗{Colors.END} {message}")

def print_warning(message: str):
    print(f"  {Colors.YELLOW}⚠{Colors.END} {message}")

def print_info(message: str):
    print(f"  {Colors.BLUE}ℹ{Colors.END} {message}")

# Test configuration
BACKEND_URL = "https://apiforpvlaagent.onrender.com"  #"http://localhost:8000"
WS_URL = "wss://apiforpvlaagent.onrender.com" #"ws://localhost:8000"
SESSION_ID = "test_session_123"

def test_health_check() -> bool:
    """Test backend health endpoint"""
    print_test("Health Check")
    
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Backend is {data.get('status', 'unknown')}")
            
            if data.get('assistant_initialized'):
                print_success("Assistant initialized successfully")
            else:
                print_error("Assistant not initialized")
                return False
            
            return True
        else:
            print_error(f"Health check failed with status {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print_error("Cannot connect to backend")
        print_info("Make sure backend is running: python api_server.py")
        return False
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        return False

def test_chat_endpoint() -> bool:
    """Test REST chat endpoint"""
    print_test("REST Chat Endpoint")
    
    try:
        payload = {
            "message": "Hello, this is a test message",
            "session_id": SESSION_ID
        }
        
        response = requests.post(
            f"{BACKEND_URL}/chat",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success("Chat endpoint responding")
            print_info(f"Response: {data.get('response', 'No response')[:100]}...")
            return True
        else:
            print_error(f"Chat failed with status {response.status_code}")
            return False
            
    except requests.exceptions.Timeout:
        print_error("Request timed out (> 30s)")
        print_warning("This might indicate backend processing issues")
        return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False

async def test_websocket() -> bool:
    """Test WebSocket connection"""
    print_test("WebSocket Connection")
    
    try:
        uri = f"{WS_URL}/ws/{SESSION_ID}"
        print_info(f"Connecting to {uri}")
        
        async with websockets.connect(uri, ping_timeout=10) as websocket:
            print_success("WebSocket connected")
            
            # Send a test message
            test_message = {
                "type": "chat",
                "message": "Hello via WebSocket",
                "timestamp": 1234567890
            }
            
            await websocket.send(json.dumps(test_message))
            print_success("Test message sent")
            
            # Wait for responses (with timeout)
            try:
                messages_received = 0
                async for message in websocket:
                    data = json.loads(message)
                    messages_received += 1
                    
                    msg_type = data.get('type')
                    print_info(f"Received {msg_type} message")
                    
                    if msg_type == 'response':
                        print_success(f"Got response: {data.get('message', '')[:100]}")
                        break
                    
                    if messages_received > 10:
                        print_warning("Received many messages, stopping test")
                        break
                        
            except asyncio.TimeoutError:
                print_warning("Response timeout")
                return False
            
            print_success("WebSocket communication successful")
            return True
            
    except websockets.exceptions.InvalidStatusCode as e:
        print_error(f"WebSocket connection failed: {e}")
        print_info("Check if backend WebSocket endpoint is working")
        return False
    except OSError as e:
        print_error(f"Connection error: {e}")
        print_info("Make sure backend is running on port 8000")
        return False
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        return False

def test_cors_headers() -> bool:
    """Test CORS configuration"""
    print_test("CORS Configuration")
    
    try:
        response = requests.options(
            f"{BACKEND_URL}/chat",
            headers={
                'Origin': 'http://localhost:5173',
                'Access-Control-Request-Method': 'POST'
            },
            timeout=5
        )
        
        cors_origin = response.headers.get('Access-Control-Allow-Origin')
        
        if cors_origin:
            print_success(f"CORS enabled for: {cors_origin}")
            
            if cors_origin == '*' or 'localhost:5173' in cors_origin:
                print_success("Frontend origin allowed")
                return True
            else:
                print_warning(f"Frontend origin may not be allowed")
                return False
        else:
            print_warning("CORS headers not found")
            print_info("Frontend might have issues connecting")
            return False
            
    except Exception as e:
        print_error(f"Error checking CORS: {e}")
        return False

def main():
    """Run all tests"""
    print_header("Backend Connection Test Suite")
    
    print_info(f"Backend URL: {BACKEND_URL}")
    print_info(f"WebSocket URL: {WS_URL}")
    print("")
    
    results = {}
    
    # Run tests
    results['health'] = test_health_check()
    print("")
    
    if not results['health']:
        print_error("Health check failed - stopping tests")
        print_info("Start backend with: python api_server.py")
        sys.exit(1)
    
    results['cors'] = test_cors_headers()
    print("")
    
    results['chat'] = test_chat_endpoint()
    print("")
    
    # WebSocket test (async)
    results['websocket'] = asyncio.run(test_websocket())
    print("")
    
    # Summary
    print_header("Test Summary")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    for test_name, passed_test in results.items():
        status = f"{Colors.GREEN}✓ PASS{Colors.END}" if passed_test else f"{Colors.RED}✗ FAIL{Colors.END}"
        print(f"  {test_name.ljust(15)} {status}")
    
    print("")
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print_success("All tests passed! Backend is ready.")
        print_info("You can now start the frontend: cd ui && npm run dev")
        sys.exit(0)
    else:
        print_error("Some tests failed. Please fix issues before starting frontend.")
        print_info("Check WEBSOCKET_TROUBLESHOOTING.md for help")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
