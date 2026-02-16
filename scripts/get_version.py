import argparse
import json
import os
import sys

# --- Configuration ---
CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'config.json')

def load_config():
    if not os.path.exists(CONFIG_FILE):
        print(f"❌ Error: Configuration file not found at {CONFIG_FILE}")
        sys.exit(1)
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)

def get_pdf_version(file_path):
    try:
        from pypdf import PdfReader
        
        if not os.path.exists(file_path):
            print(f"❌ Error: File not found at {file_path}")
            sys.exit(1)
            
        reader = PdfReader(file_path)
        metadata = reader.metadata
        
        if metadata:
            # Try custom /Version field first
            if '/Version' in metadata:
                return metadata['/Version']
            # Fallback to Subject if formatted as "Version: ..."
            elif '/Subject' in metadata:
                subject = metadata['/Subject']
                if subject.startswith("Version: "):
                    return subject.replace("Version: ", "")
                return subject
            elif '/Title' in metadata:
                return metadata['/Title']
        
        return None
        
    except ImportError:
        print("❌ Error: 'pypdf' not installed. Please run 'pip install pypdf'")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error reading PDF: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Get version name from Resume/Cover Letter PDF.")
    parser.add_argument('--type', choices=['resume', 'cover_letter'], required=True, help="Type of document")
    
    args = parser.parse_args()
    config = load_config()
    
    output_dir = config.get('output_path')
    output_name_base = config.get(f'{args.type}_output_name')
    
    if not output_dir or not output_name_base:
        print("❌ Error: Output path or name not configured in config.json")
        sys.exit(1)
        
    file_path = os.path.join(output_dir, f"{output_name_base}.pdf")
    
    version = get_pdf_version(file_path)
    
    if version:
        print(version)
    else:
        print("⚠️  No version metadata found.")

if __name__ == "__main__":
    main()
