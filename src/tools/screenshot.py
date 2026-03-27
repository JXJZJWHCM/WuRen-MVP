import argparse
import subprocess
import shutil
import sys
import os
import time

def find_browser():
    """Find available browser executable."""
    browsers = [
        "chromium", 
        "chromium-browser", 
        "google-chrome", 
        "google-chrome-stable", 
        "firefox", 
        "firefox-esr"
    ]
    
    # Check PATH first
    for browser in browsers:
        if shutil.which(browser):
            return browser
            
    return None

def take_screenshot(url, output_path, browser=None):
    """Take screenshot using CLI tools."""
    if not browser:
        browser = find_browser()
    
    if not browser:
        print("[Error] No supported browser found (chromium, chrome, firefox).")
        sys.exit(1)
        
    print(f"[Info] Using browser: {browser}")
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    
    cmd = []
    if "firefox" in browser:
        # Firefox headless
        # firefox --headless --screenshot output.png http://example.com
        # Note: Firefox usually dumps to PWD if path isn't absolute or handled well, 
        # but --screenshot <path> usually works in recent versions.
        cmd = [
            browser,
            "--headless",
            "--screenshot",
            os.path.abspath(output_path),
            "--window-size=1280,1024",
            url
        ]
    else:
        # Chromium/Chrome headless
        # chromium --headless --disable-gpu --screenshot=output.png http://example.com
        cmd = [
            browser,
            "--headless",
            "--disable-gpu",
            "--no-sandbox",
            "--ignore-certificate-errors",
            f"--screenshot={os.path.abspath(output_path)}",
            "--window-size=1280,1024",
            "--timeout=30000",
            url
        ]
        
    print(f"[Exec] {' '.join(cmd)}")
    
    try:
        # Run with timeout
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0 and os.path.exists(output_path):
            print(f"[Success] Screenshot saved to {output_path}")
            return True
        else:
            print(f"[Error] Command failed with code {result.returncode}")
            print(f"Stdout: {result.stdout}")
            print(f"Stderr: {result.stderr}")
            
            # Fallback check for Firefox: sometimes it saves to 'screenshot.png' in CWD
            if "firefox" in browser and os.path.exists("screenshot.png"):
                os.rename("screenshot.png", output_path)
                print(f"[Success] Recovered screenshot from default location to {output_path}")
                return True
                
            return False
            
    except subprocess.TimeoutExpired:
        print("[Error] Timeout while taking screenshot")
        return False
    except Exception as e:
        print(f"[Error] Exception: {e}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Take a website screenshot via headless browser.")
    parser.add_argument("url", help="Target URL")
    parser.add_argument("output", help="Output file path (e.g. data/reports/images/evidence.png)")
    
    args = parser.parse_args()
    
    if not args.url.startswith("http"):
        args.url = "http://" + args.url
        
    success = take_screenshot(args.url, args.output)
    if not success:
        sys.exit(1)
