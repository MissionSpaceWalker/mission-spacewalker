#!/bin/bash

set -e  # exit on error

./format.sh
echo "committing changes..."

AMEND=false
COMMIT_MESSAGE=""

# parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --amend|-a)
            AMEND=true
            shift
            ;;
        *)
            if [[ -z "$COMMIT_MESSAGE" ]]; then
                COMMIT_MESSAGE="$1"
            else
                echo "error: multiple commit messages provided"
                echo "usage: ./commit.sh [--amend|-a] [\"commit message\"]"
                exit 1
            fi
            shift
            ;;
    esac
done

# stage all changes
git add -A

if $AMEND; then
    if [[ -n "$COMMIT_MESSAGE" ]]; then
        git commit --amend -m "$COMMIT_MESSAGE"
    else
        git commit --amend --no-edit
    fi
    git push --force-with-lease
else
    # if no commit message provided, prompt for one
    if [[ -z "$COMMIT_MESSAGE" ]]; then
        echo "enter commit message: "
        read -r COMMIT_MESSAGE
        while [[ -z "$COMMIT_MESSAGE" ]]; do
            echo "commit message cannot be empty. please enter a commit message: "
            read -r COMMIT_MESSAGE
        done
    fi
    git commit -m "$COMMIT_MESSAGE"
    git push
fi
