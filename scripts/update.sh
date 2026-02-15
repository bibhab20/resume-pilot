#!/bin/bash

# ResumePilot Update Script
# Usage: ./scripts/update.sh [resume|cover_letter]

TYPE=${1:-resume}

if [ "$TYPE" == "resume" ]; then
    echo "Updating Resume..."
    cd resume
    pdflatex -interaction=nonstopmode -jobname="Resume_Bibhab_Pattnayak" main.tex
    cd ..
elif [ "$TYPE" == "cover_letter" ]; then
    echo "Updating Cover Letter..."
    cd cover_letter
    pdflatex -interaction=nonstopmode -jobname="Cover_Letter_Bibhab_Pattnayak" main.tex
    cd ..
else
    echo "Usage: $0 [resume|cover_letter]"
    exit 1
fi

echo "Done."
