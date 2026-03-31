#!/bin/bash

# Script to run git pull on challenges 02 through 16

echo "Starting git pull for challenges 02-16..."
echo "=========================================="

for i in $(seq -f "%02g" 2 16); do
    challenge_dir="challenge_${i}_"*
    
    # Find the matching directory
    for dir in $challenge_dir; do
        if [ -d "$dir" ]; then
            echo ""
            echo "Processing: $dir"
            echo "---"
            cd "$dir" || continue
            
            # Check if it's a git repository
            if [ -d ".git" ]; then
                git pull
            else
                echo "  Warning: Not a git repository, skipping..."
            fi
            
            cd ..
        fi
    done
done

echo ""
echo "=========================================="
echo "Completed git pull for all challenges!"
