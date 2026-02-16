import argparse
import json
import os
import shutil
import subprocess
import sys
import time
import ssl
import urllib.request
import urllib.error
from datetime import datetime

# --- Configuration ---
CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'config.json')

def get_ssl_context():
    """
    Creates an SSL context that tries to use certifi certificates if available,
    or falls back to unverified context on macOS if certs are missing.
    """
    try:
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        pass
    
    context = ssl.create_default_context()
    try:
        context.load_default_certs()
    except Exception:
        pass
    return context

def load_config():
    if not os.path.exists(CONFIG_FILE):
        print(f"Error: Configuration file not found at {CONFIG_FILE}")
        print("Please copy config.example.json to config.json and fill in your details.")
        sys.exit(1)
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)

# --- Git Operations ---
def get_git_info(directory):
    """Returns the current branch and commit hash."""
    try:
        branch = subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], cwd=os.getcwd()).decode('utf-8').strip()
        commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=os.getcwd()).decode('utf-8').strip()
        return branch, commit
    except subprocess.CalledProcessError:
        return "unknown", "unknown"

def sanitize_message(message):
    """Replaces whitespace with underscores and removes special characters."""
    if not message:
        return ""
    # Replace spaces with underscores
    sanitized = message.replace(" ", "_")
    # Keep only alphanumeric and underscores
    sanitized = "".join(c for c in sanitized if c.isalnum() or c == "_")
    return sanitized

def git_status_clean(directory):
    """Checks if the directory is clean (no modified or untracked files)."""
    # We need to check relative path from repo root or run inside the directory
    # 'git status --porcelain' is good for scripting
    try:
        # Check for modifications associated with the specific directory
        # This assumes the script is run from project root or handles paths correctly
        # We will run git commands from the project root.
        result = subprocess.run(
            ['git', 'status', '--porcelain', directory],
            capture_output=True, text=True, check=True
        )
        return len(result.stdout.strip()) == 0
    except subprocess.CalledProcessError as e:
        print(f"Error checking git status: {e}")
        sys.exit(1)

def git_commit(directory, message):
    """Commits changes in the specified directory."""
    try:
        subprocess.run(['git', 'add', directory], check=True)
        subprocess.run(['git', 'commit', '-m', message], check=True)
        print(f"Committed changes in {directory} with message: {message}")
    except subprocess.CalledProcessError as e:
        print(f"Error committing changes: {e}")
        sys.exit(1)

# --- Build operations ---
def build_pdf(doc_type):
    """Runs the update.sh script to build the PDF."""
    script_path = os.path.join(os.path.dirname(__file__), 'update.sh')
    try:
        subprocess.run([script_path, doc_type], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error building PDF: {e}")
        sys.exit(1)

# --- PDF Metadata Operations ---
def update_pdf_metadata(file_path, version_name):
    """Updates the PDF metadata with the version name."""
    try:
        from pypdf import PdfReader, PdfWriter
        
        reader = PdfReader(file_path)
        writer = PdfWriter()
        
        writer.append_pages_from_reader(reader)
        metadata = reader.metadata
        writer.add_metadata(metadata)
        
        # Add version info
        # We can add a custom 'Version' field or just overwrite 'Title' or 'Subject'
        # Standard fields are Title, Author, Subject, Keywords, Creator, Producer, CreationDate, ModDate
        writer.add_metadata({
            "/Version": version_name,
            "/Subject": f"Version: {version_name}",
            # Also updating 'Title' is common practice if the filename changes
             # "/Title": version_name 
        })
        
        with open(file_path, "wb") as f:
            writer.write(f)
            
        print(f"Updated metadata for {file_path}")
        
    except ImportError:
        print("⚠️  'pypdf' not installed. Skipping metadata update.")
        print("   pip install pypdf")
    except Exception as e:
        print(f"❌ Error updating PDF metadata: {e}")

# --- Notion Integration ---
def delete_notion_page(config, page_id):
    """Archives (deletes) a Notion page."""
    token = config.get('notion_token')
    url = f"https://api.notion.com/v1/pages/{page_id}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
    data = {"archived": True}
    req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers, method='PATCH')
    
    context = get_ssl_context()
    try:
        with urllib.request.urlopen(req, context=context) as response:
            print(f"Rolled back Notion entry {page_id}")
    except Exception as e:
        print(f"Failed to rollback Notion entry {page_id}: {e}")

def create_notion_entry(config, doc_type, version_name, commit_message, branch, commit_id):
    token = config.get('notion_token')
    database_id = config.get(f'{doc_type}_database_id')
    
    if not token or not database_id:
        print("Notion configuration missing. Skipping Notion entry.")
        return None

    url = "https://api.notion.com/v1/pages"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
    data = {
        "parent": {"database_id": database_id},
        "properties": {
            "Name": {
                "title": [
                    {
                        "text": {
                            "content": version_name
                        }
                    }
                ]
            },
            "Created Time": {
                "date": {
                    "start": datetime.now().isoformat()
                }
            },
            "Device": {
                "select": {
                    "name": config.get('device_name', 'Unknown Device')
                }
            },
            "Commit message": {
                "rich_text": [
                    {
                        "text": {
                            "content": commit_message
                        }
                    }
                ]
            },
            "Git Branch": { # Ensure this property exists in Notion
                "rich_text": [
                    {
                        "text": {
                            "content": branch
                        }
                    }
                ]
            },
            "Commit ID": { # Ensure this property exists in Notion
                "rich_text": [
                    {
                        "text": {
                            "content": commit_id
                        }
                    }
                ]
            }
        }
    }

    req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers)
    
    context = get_ssl_context()
    
    try:
        with urllib.request.urlopen(req, context=context) as response:
            print(f"Successfully created Notion entry for {version_name}")
            response_data = json.load(response)
            return response_data.get('id')
    except urllib.error.URLError as e:
        if "CERTIFICATE_VERIFY_FAILED" in str(e):
             print(f"SSL Error creating Notion entry: {e}")
             print("Trying fallback to unverified context...")
             try:
                 unverified_context = ssl._create_unverified_context()
                 with urllib.request.urlopen(req, context=unverified_context) as response:
                    print(f"Successfully created Notion entry (Fallback: Unverified Context)")
                    response_data = json.load(response)
                    return response_data.get('id')
             except Exception as e2:
                 raise Exception(f"Fallback Notion entry creation failed: {e2}")
        else:
             raise Exception(f"Error creating Notion entry: {e}")
    except urllib.error.HTTPError as e:
        error_content = e.read().decode('utf-8')
        raise Exception(f"Error creating Notion entry: {e.code} {e.reason} - {error_content}")

# --- Main Logic ---
def main():
    parser = argparse.ArgumentParser(description="Release resume/cover letter versions.")
    parser.add_argument('--type', choices=['resume', 'cover_letter'], required=True, help="Type of document to track")
    parser.add_argument('--message', required=False, help="Commit message (optional, inferred if not provided)")
    parser.add_argument('--force', action='store_true', help="Force version creation even if no changes detected")

    args = parser.parse_args()
    config = load_config()
    
    doc_type = args.type
    directory = doc_type # 'resume' or 'cover_letter' folder
    
    # Check for changes - Early exit
    if git_status_clean(directory) and not args.force:
        print(f"No changes detected in {directory}. Use --force to create a version anyway.")
        sys.exit(0)
    
    # Determine commit message
    message = args.message
    if not message:
        message = f"Update {doc_type} - {datetime.now().strftime('%Y-%m-%d %H:%M')}"

    print(f"Processing {doc_type}...")

    # 1. Build PDF (Non-atomic, if this fails we just stop)
    build_pdf(doc_type)

    # Prepare for Atomic Operations
    generated_pdf_name = ""
    prefix_name = config.get(f'{doc_type}_output_name', doc_type) # Get prefix from config
    
    if doc_type == 'resume':
        generated_pdf_name = "Resume_Bibhab_Pattnayak.pdf"
    else:
        generated_pdf_name = "Cover_Letter_Bibhab_Pattnayak.pdf"
        
    source_pdf_path = os.path.join(directory, generated_pdf_name)
    
    if not os.path.exists(source_pdf_path):
        print(f"Error: Generated PDF not found at {source_pdf_path}")
        sys.exit(1)

    archive_path = None
    output_path = None
    backup_output_path = None
    notion_page_id = None
    
    print("Starting atomic updates...")
    try:
        # 2a. Archive
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        sanitized_msg = sanitize_message(message)
        
        # Name format: Prefix + Sanitized Commit Msg (optional) + Date Time
        if sanitized_msg and sanitized_msg != f"Update_{doc_type}": # Avoid redundant "Update_resume" in filename if default
             # Check if message was the default one with timestamp, if so, we might want to skip or just use it.
             # Actually user said: "sanitized commit message(optional)"
             # If user provided a custom message, use it.
             if args.message:
                 version_name = f"{prefix_name}_{sanitized_msg}_{timestamp}.pdf"
             else:
                 version_name = f"{prefix_name}_{timestamp}.pdf"
        else:
             version_name = f"{prefix_name}_{timestamp}.pdf"

        archive_dir = config.get(f'{doc_type}_archive_path')
        if archive_dir:
            os.makedirs(archive_dir, exist_ok=True)
            archive_path = os.path.join(archive_dir, version_name)
            shutil.copy2(source_pdf_path, archive_path)
            print(f"Archived to {archive_path}")
        else:
            print("Archive path not configured. Skipping archive.")
            
        # 2b. Output
        output_dir = config.get('output_path')
        output_name_base = config.get(f'{doc_type}_output_name')
        
        if output_dir and output_name_base:
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, f"{output_name_base}.pdf")
            
            # Backup existing output
            if os.path.exists(output_path):
                backup_output_path = output_path + ".bak"
                shutil.copy2(output_path, backup_output_path)
            
            shutil.copy2(source_pdf_path, output_path)
            print(f"Copied to output {output_path}")
            
            # Update metadata
            update_pdf_metadata(output_path, version_name)
        else:
            print("Output path or name not configured. Skipping output copy.")
            
        # 2c. Notion
        branch, commit_id = get_git_info(directory)
        notion_page_id = create_notion_entry(config, doc_type, version_name, message, branch, commit_id)
        
    except Exception as e:
        print(f"\n❌ Error during atomic update: {e}")
        print("🔄 Rolling back changes...")
        
        # Rollback Notion
        if notion_page_id:
            delete_notion_page(config, notion_page_id)
            
        # Rollback Archive
        if archive_path and os.path.exists(archive_path):
            os.remove(archive_path)
            print(f"Deleted archive {archive_path}")
            
        # Rollback Output
        if output_path:
            if backup_output_path and os.path.exists(backup_output_path):
                shutil.move(backup_output_path, output_path)
                print(f"Restored output from backup")
            elif os.path.exists(output_path):
                # We created it new, so delete it
                os.remove(output_path)
                print(f"Deleted output {output_path}")
                
        sys.exit(1)
    finally:
        # Cleanup backup if it still exists (meaning we didn't use it for rollback)
        if backup_output_path and os.path.exists(backup_output_path):
            os.remove(backup_output_path)

    # 3. Commit (Only if changes detected)
    if not git_status_clean(directory):
        git_commit(directory, message)
    else:
        print("No changes detected in source files. Skipping git commit.")

if __name__ == "__main__":
    main()
