# RebelDESK GitHub Workflow Automation

This directory contains GitHub Actions workflows and configuration files for automating the RebelDESK development process.

## Workflows

### 1. Update Progress Checklist (`update_progress.yml`)

This workflow automatically updates the `progress.md` file when an issue is closed.

- **Trigger**: When an issue is closed
- **Action**: Updates the corresponding checklist item in `progress.md` from `[ ]` to `[x]`
- **Purpose**: Keeps the progress tracking files in sync with GitHub Issues

### 2. Run Automated Tests (`run_tests.yml`)

This workflow runs the project's test suite automatically when code is pushed or a pull request is created.

- **Trigger**: On push or pull request
- **Action**: Sets up Python, installs dependencies, and runs pytest
- **Purpose**: Ensures code quality and prevents regressions

### 3. Update Project Board (`update_project_board.yml`)

This workflow automatically moves issues and pull requests between columns on the project board based on their status.

- **Trigger**: When issues or PRs are opened, labeled, unlabeled, assigned, or unassigned
- **Actions**:
  - New issues go to "To-Do"
  - Issues labeled "in-progress" go to "In Progress"
  - Issues labeled "review" go to "In Review"
  - Issues labeled "testing" go to "Testing"
  - Closed issues go to "Completed"
- **Purpose**: Automates project management and provides visual workflow tracking

## Setup Scripts

The following scripts in the `scripts` directory help with GitHub setup:

### 1. Create GitHub Issues (`create_github_issues.ps1`)

- Converts checklist items from progress.md files into GitHub Issues
- Generates commands for creating issues with appropriate labels and descriptions

### 2. Setup GitHub Labels (`setup_github_labels.ps1`)

- Creates standardized labels for the repository
- Ensures consistent categorization of issues

## Usage

1. Ensure GitHub CLI (`gh`) is installed and authenticated
2. Run the setup scripts to initialize labels and create issues
3. The GitHub Actions workflows will automatically run based on their triggers

## Project Board Structure

The RebelDESK project uses a Kanban-style board with the following columns:

1. **To-Do**: Tasks that are planned but not yet started
2. **In Progress**: Tasks currently being worked on
3. **In Review**: Tasks that are complete and awaiting review
4. **Testing**: Tasks that have passed review and are being tested
5. **Completed**: Tasks that are fully complete and verified
