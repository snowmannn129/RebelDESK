# RebelDESK Scripts

This directory contains various scripts for managing the RebelDESK project.

## GitHub Workflow Scripts

### `setup_github_workflow.bat`

**Purpose**: Interactive guide to set up the complete GitHub workflow.

**Usage**:
```
.\scripts\setup_github_workflow.bat
```

This batch file will guide you step-by-step through the entire GitHub workflow setup process, including:
- Installing GitHub CLI
- Authenticating with GitHub
- Creating a GitHub repository
- Pushing GitHub Actions workflows
- Creating GitHub labels
- Creating GitHub issues

### `github_setup_guide.md`

**Purpose**: Detailed documentation of the GitHub workflow setup process.

**Usage**: Open and follow the instructions in this markdown file.

This guide provides detailed instructions for setting up the GitHub workflow, including code snippets and explanations.

### `create_key_issues.ps1`

**Purpose**: Create a subset of key GitHub issues (13 issues) for the RebelDESK project.

**Usage**:
```powershell
powershell -File scripts/create_key_issues.ps1
```

This script creates 13 key issues across different modules, providing a good starting point without creating all 154 issues at once.

### `create_github_issues.ps1`

**Purpose**: Generate GitHub issue creation commands for all checklist items in progress.md files.

**Usage**:
```powershell
powershell -File scripts/create_github_issues.ps1
```

This script scans all progress.md files for checklist items and generates GitHub CLI commands to create issues for them. The commands are saved to `reports/github_issues_YYYYMMDD.md`.

### `setup_github_and_create_issues.ps1`

**Purpose**: Install GitHub CLI and create all GitHub issues.

**Usage**:
```powershell
powershell -File scripts/setup_github_and_create_issues.ps1
```

This script checks if GitHub CLI is installed, installs it if necessary, authenticates with GitHub, and creates all 154 GitHub issues.

### `setup_github_labels.ps1`

**Purpose**: Create standardized labels for the GitHub repository.

**Usage**:
```powershell
powershell -File scripts/setup_github_labels.ps1
```

This script creates all the necessary labels for categorizing issues in the GitHub repository.

### `test_github_actions.ps1`

**Purpose**: Test GitHub Actions workflows locally.

**Usage**:
```powershell
powershell -File scripts/test_github_actions.ps1
```

This script helps test GitHub Actions workflows locally using the `act` tool.

## Project Management Scripts

### `get_progress.ps1`

**Purpose**: Generate a progress report for the RebelDESK project.

**Usage**:
```powershell
powershell -File scripts/get_progress.ps1
```

This script scans all progress.md files and generates a summary report of the project's progress, including completion percentages for each module.

## Workflow

The recommended workflow for setting up GitHub integration is:

1. Run `setup_github_workflow.bat` and follow the interactive guide
2. Alternatively, follow the steps in `github_setup_guide.md`
3. For a quick start, create key issues with `create_key_issues.ps1`
4. For complete setup, create all issues using the commands in `reports/github_issues_YYYYMMDD.md`
5. Track progress using `get_progress.ps1`

## Notes

- All scripts are designed to be run from the root directory of the RebelDESK project
- PowerShell scripts require PowerShell to be installed
- GitHub CLI scripts require GitHub CLI to be installed and authenticated
