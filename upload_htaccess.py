#!/usr/bin/env python3
"""Upload .htaccess file to SiteGround to fix tile Content-Encoding headers."""

import ftplib
import os
from pathlib import Path

def main():
    """Upload .htaccess file to fix Content-Encoding headers."""
    
    # Try to load environment variables
    try:
        from dotenv import load_dotenv
        env_file = Path(__file__).parent / '.env'
        if env_file.exists():
            load_dotenv(env_file)
            print(f"✅ Loaded .env file from {env_file}")
        else:
            print(f"⚠️  No .env file found at {env_file}")
            print("Please ensure SiteGround credentials are set as environment variables:")
            print("SITEGROUND_HOST, SITEGROUND_USERNAME, SITEGROUND_PASSWORD")
    except ImportError:
        print("⚠️  python-dotenv not installed, using system environment only")
    
    host = os.environ.get('SITEGROUND_HOST', '')
    username = os.environ.get('SITEGROUND_USERNAME', '')
    password = os.environ.get('SITEGROUND_PASSWORD', '')
    
    if not all([host, username, password]):
        print("❌ SiteGround credentials not configured")
        print("Please set the following environment variables:")
        print("- SITEGROUND_HOST")
        print("- SITEGROUND_USERNAME") 
        print("- SITEGROUND_PASSWORD")
        print("Or create a .env file in the tile-server directory")
        return
    
    htaccess_file = Path('.htaccess-tiles')
    if not htaccess_file.exists():
        print("❌ .htaccess-tiles file not found")
        return
        
    try:
        with ftplib.FTP(host) as ftp:
            print(f"🔗 Connecting to {host}...")
            ftp.login(username, password)
            print("✅ Connected successfully")
            
            # Upload .htaccess to tiles directory
            remote_path = "bobd77.sg-host.com/public_html/tiles/.htaccess"
            
            print(f"📄 Uploading .htaccess-tiles to {remote_path}...")
            with open(htaccess_file, 'rb') as f:
                ftp.storbinary(f'STOR {remote_path}', f)
            
            print("✅ .htaccess uploaded successfully")
            print("🔧 This should fix the Content-Encoding headers for gzipped SVG tiles")
            print("🌐 Test URL: https://bobd77.sg-host.com/tiles/43.630_-79.360.svg.gz")
            print("📱 The map should now load tiles properly")
            
    except Exception as e:
        print(f"❌ Upload failed: {e}")

if __name__ == "__main__":
    main()