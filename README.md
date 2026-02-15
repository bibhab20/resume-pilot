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

## Setup
1.  Ensure you have a LaTeX distribution installed (e.g., TeX Live, MiKTeX).
2.  Install the "LaTeX Workshop" extension for VS Code.
3.  Configure `scripts/env.sh` with your local paths.
4.  Make scripts executable: `chmod +x scripts/*.sh`

## Usage
### Building the Resume
Open `resume/main.tex` in VS Code and use the LaTeX Workshop build command.

### Building the Cover Letter
Open `cover_letter/main.tex` in VS Code and use the LaTeX Workshop build command.

### Updating and Archiving
Use `scripts/update.sh` to commit changes and archive the generated PDF.
```bash
./scripts/update.sh "Your commit message"
```
