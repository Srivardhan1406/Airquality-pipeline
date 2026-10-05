#!/usr/bin/env bash
# Demonstrates Git branching + merge flow. Run from project root.
set -e
if [ ! -d .git ]; then
  git init -b main
  git add .
  git commit -m "chore: initial project structure"
fi
git checkout -b feature/data-collection main
git commit --allow-empty -m "feat: add REST API collector for Open-Meteo"
git checkout -b feature/log-analysis main
git commit --allow-empty -m "feat: add Linux log analysis script"
git checkout -b feature/docker-support main
git commit --allow-empty -m "feat: add Dockerfile and docker-compose"
git checkout main
git merge --no-ff feature/data-collection -m "Merge feature/data-collection"
git merge --no-ff feature/log-analysis -m "Merge feature/log-analysis"
git merge --no-ff feature/docker-support -m "Merge feature/docker-support"
git log --oneline --graph --all
echo
echo "To raise a Pull Request on GitHub (do this BEFORE merging if you want a real PR):"
echo "  git remote add origin https://github.com/<your-username>/airquality-pipeline.git"
echo "  git push -u origin main feature/data-collection feature/log-analysis feature/docker-support"
echo "  GitHub > Compare & pull request > base: main  <-  compare: feature/..."
