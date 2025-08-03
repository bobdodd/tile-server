#!/usr/bin/env python3
"""Debug script to explore FTP directory structure."""

import ftplib
import os
from pathlib import Path

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    env_file = Path(__file__).parent / '.env'
    if env_file.exists():
        load_dotenv(env_file)
        print(f"✅ Loaded .env file from {env_file}")
    else:
        print(f"⚠️  No .env file found at {env_file}")
except ImportError:
    print("⚠️  python-dotenv not installed, using system environment only")

def explore_ftp_directory(ftp, path="/", max_depth=3, current_depth=0):
    """Recursively explore FTP directory structure."""
    if current_depth > max_depth:
        return
    
    try:
        # Change to directory
        ftp.cwd(path)
        print(f"{'  ' * current_depth}📁 {path}/")
        
        # List contents
        items = []
        ftp.retrlines('NLST', items.append)
        
        # Sort items
        items.sort()
        
        for item in items:
            if item in ['.', '..']:
                continue
                
            item_path = f"{path.rstrip('/')}/{item}" if path != "/" else f"/{item}"
            
            try:
                # Try to change to item to see if it's a directory
                original_dir = ftp.pwd()
                ftp.cwd(item_path)
                # If successful, it's a directory - explore it
                explore_ftp_directory(ftp, item_path, max_depth, current_depth + 1)
                ftp.cwd(original_dir)
                
            except ftplib.error_perm:
                # Not a directory, it's a file
                print(f"{'  ' * (current_depth + 1)}📄 {item}")
                
    except ftplib.error_perm as e:
        print(f"{'  ' * current_depth}❌ Cannot access {path}: {e}")

def main():
    """Explore SiteGround FTP structure."""
    host = os.environ.get('SITEGROUND_HOST', '')
    username = os.environ.get('SITEGROUND_USERNAME', '')
    password = os.environ.get('SITEGROUND_PASSWORD', '')
    
    if not all([host, username, password]):
        print("❌ SiteGround credentials not configured")
        print("Set SITEGROUND_HOST, SITEGROUND_USERNAME, SITEGROUND_PASSWORD")
        return
    
    try:
        print(f"🔗 Connecting to {host}...")
        with ftplib.FTP(host) as ftp:
            ftp.login(username, password)
            print(f"✅ Connected successfully")
            print(f"📍 Starting directory: {ftp.pwd()}")
            print("\n" + "="*50)
            print("FTP DIRECTORY STRUCTURE")
            print("="*50)
            
            explore_ftp_directory(ftp, "/", max_depth=4)
            
    except Exception as e:
        print(f"❌ FTP Error: {e}")

if __name__ == '__main__':
    main()