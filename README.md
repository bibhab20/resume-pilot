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
