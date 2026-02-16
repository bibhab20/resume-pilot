# ResumePilot

ResumePilot is a career operations system for managing your resume, cover letters, and job applications. It leverages LaTeX for high-quality document generation and uses a structured approach to tailor your resume for specific job descriptions.

## Features
*   **Resume Management**: LaTeX-based resume project with modular sections.
*   **Cover Letter Management**: Dedicated LaTeX project for cover letters.
*   **Skill Selection**: Easily select relevant skills and experience for each application.
*   **AI Integration**: (Planned) Generate resume content based on Job Descriptions.
*   **Tracking**: Track resume versions and job applications (integrated with Notion).

## Directory Structure
*   `resume/`: Contains the main resume LaTeX project.
    *   `main.tex`: The entry point for the resume.
    *   `templates/`: Reusable sections for experience, skills, education, etc.
*   `cover_letter/`: Contains the main cover letter LaTeX project.
*   `scripts/`: Shell scripts for managing updates, archiving, and other utilities.

## Development Setup

### Prerequisites
1.  **VS Code**: Install [Visual Studio Code](https://code.visualstudio.com/).
2.  **LaTeX Distribution (MiKTeX)**:
    -   Download and install [MiKTeX](https://miktex.org/download) for macOS.
    -   During installation, ensure you select "Always install missing packages on-the-fly" to automatically handle dependencies.
    -   After installation, open the MiKTeX Console to check for updates.
3.  **VS Code Extension**:
    -   Install the **LaTeX Workshop** extension by James Yu in VS Code.

### Building with VS Code & LaTeX Workshop
1.  **Open the Project**: Open the root `resume-pilot` folder in VS Code.
2.  **Open a Main File**: Navigate to either `resume/main.tex` or `cover_letter/main.tex` and open the file.
3.  **Build**:
    -   Save the file (Cmd+S) - strictly configured to auto-build on save by default.
    -   Or open the LaTeX Workshop side panel (icon with `TEX`) and click "Build LaTeX project".
    -   Or use the shortcut `Cmd+Option+B`.
4.  **View PDF**:
    -   Click "View LaTeX PDF" in the side panel.
    -   Or use the shortcut `Cmd+Option+V`.

### Building with Shell Scripts
You can also use the included scripts for compiling:

-   **Resume**: `./scripts/update.sh resume`
-   **Cover Letter**: `./scripts/update.sh cover_letter`

### Version Tracking
You can automatically build, archive, and commit versions of your resume and cover letter using the `release.py` script.

#### Prerequisites
1.  **Notion Integration**:
    -   Create a Notion Integration and get the **Internal Integration Token**.
    -   Share your databases with this integration.
2.  **Notion Databases Setup**:
    You need to create two separate databases in Notion: one for **Resume Versions** and one for **Cover Letter Versions**.
    
    For **EACH** database, add the following properties with the exact names and types:
    
    | Property Name | Type | Description |
    | :--- | :--- | :--- |
    | `Name` | **Title** | The default title property. |
    | `Created Time` | **Date** | Date and time of the version. |
    | `Device` | **Select** | The device where the version was created. |
    | `Commit message` | **Text** | The git commit message or description (Select "Text" or "Rich Text"). |
    | `Git Branch` | **Text** | The git branch name (Select "Text" or "Rich Text"). |
    | `Commit ID` | **Text** | The git commit hash (Select "Text" or "Rich Text"). |

    **Naming Convention**:
    The generated PDF filename follows this pattern:
    `[Prefix]_[Sanitized_Commit_Message]_[Timestamp].pdf`
    
    -   **Prefix**: Configured in `config.json` (e.g., `Resume_Bibhab_Pattnayak`).
    -   **Sanitized Commit Message**: Spaces are replaced with underscores, special characters removed.
    -   **Timestamp**: `YYYYMMDD_HHMMSS`.

3.  **Python 3**: Ensure Python 3 is installed on your system.

4.  **Virtual Environment**:
    To avoid SSL errors and manage dependencies, set up a virtual environment:
    ```bash
    ./scripts/setup_env.sh
    source venv/bin/activate
    ```
    Always run `source venv/bin/activate` before running the tracking scripts.

#### Configuration
1.  **Setup**:

    -   Copy `scripts/config.example.json` to `scripts/config.json`.
    -   Fill in your paths, Notion token, and database IDs.

2.  **Validation**:
    Verify your setup by running:
    
    ```bash
    python3 scripts/validate_notion.py
    ```

3.  **Usage**:
    Run the script from the project root:

    ```bash
    # Track Resume changes
    ./scripts/release.sh --type resume

    # Track Cover Letter changes
    ./scripts/release.sh --type cover_letter

    # Force a version creation even without changes
    ./scripts/release.sh --type resume --force
    
    # Get the current version name from the output PDF
    python3 scripts/get_version.py --type resume
    ```

    ### Key Features
    -   **Atomic Updates**: The script ensures that updating the output file, archiving, and creating a Notion entry happen as a single transaction. If any step fails (e.g., Notion API error), changes are rolled back to prevent inconsistent states.
    -   **Smart Git Commits**: The script only creates a git commit if there are actual changes in the source files. If you run the script without changes, it will update the build artifacts but skip the commit (unless forced).
    -   **PDF Metadata**: The generated PDF will have its metadata (Subject/Version) updated with the version name, making it easier to track file versions externally.

    The script workflow:
    1.  Checks for git changes in the target directory (Exits if none, unless `--force`).
    2.  Builds the PDF.
    3.  **Atomic Transaction**:
        -   Archives the PDF with a timestamp (e.g., `Resume_YYYYMMDD_HHMMSS.pdf`).
        -   Updates the "latest" PDF in your output directory (with backup/restore on failure).
        -   Updates PDF metadata with version info.
        -   Creates a new entry in your Notion database.
    4.  Commits changes to Git with a message (default: timestamp).

