# RebelDESK GitHub Workflow Guide

This guide explains how to set up and use the GitHub workflow automation for the RebelDESK project.

## Prerequisites

1. **GitHub CLI**: Install the GitHub CLI from [https://cli.github.com/](https://cli.github.com/)
2. **GitHub Repository**: The RebelDESK repository is available at [https://github.com/snowmannn129/RebelDESK](https://github.com/snowmannn129/RebelDESK)
3. **GitHub Project Board**: The project board is available at [https://github.com/users/snowmannn129/projects/1](https://github.com/users/snowmannn129/projects/1)

## Setup Steps

### 1. Clone the Repository

If you haven't already, clone the repository to your local machine:

```powershell
git clone https://github.com/snowmannn129/RebelDESK.git
cd RebelDESK
```

### 2. Set Up GitHub Labels

Run the label setup script to create standardized labels for your repository:

```powershell
./scripts/setup_github_labels.ps1
```

This will create all the necessary labels for categorizing issues.

### 3. Generate GitHub Issues from Checklists

Run the issue creation script to convert checklist items to GitHub Issues:

```powershell
./scripts/create_github_issues.ps1
```

This will:
- Scan all progress.md files for pending checklist items
- Generate GitHub CLI commands for creating issues
- Save these commands to `reports/github_issues_YYYYMMDD.md`

### 4. Create the Issues

Open the generated file and run the commands to create the issues:

```powershell
# Open the file
code reports/github_issues_YYYYMMDD.md

# Run the commands from the file
# You can copy and paste them into your terminal
```

### 5. Push GitHub Actions Workflows

Ensure the GitHub Actions workflow files are pushed to your repository:

```powershell
git add .github/
git commit -m "Add GitHub Actions workflows"
git push
```

## Using the Workflow

Once set up, the GitHub workflow automation will:

1. **Track Progress Automatically**:
   - When you close an issue, the corresponding item in progress.md will be marked as complete
   - The GitHub Action will commit this change automatically

2. **Run Tests Automatically**:
   - Whenever code is pushed or a pull request is created, tests will run automatically
   - Check the Actions tab in your GitHub repository to see test results

3. **Update Project Board**:
   - New issues will be placed in the "To-Do" column
   - Add the "in-progress" label to move an issue to "In Progress"
   - Add the "review" label to move an issue to "In Review"
   - Add the "testing" label to move an issue to "Testing"
   - Closed issues will be moved to "Completed"

## Development Workflow

Follow this workflow for each feature or task:

1. **Select a Task**:
   - Choose an issue from the "To-Do" column
   - Assign it to yourself
   - Add the "in-progress" label

2. **Implement the Feature**:
   - Create a branch for the feature
   - Implement the feature with tests
   - Push your changes

3. **Review Process**:
   - Create a pull request
   - Add the "review" label
   - After review, add the "testing" label

4. **Testing and Completion**:
   - Verify the feature works as expected
   - Merge the pull request
   - Close the issue

## Troubleshooting

### GitHub Actions Not Running

If GitHub Actions workflows aren't running:

1. Check the `.github/workflows/` directory to ensure the workflow files are present
2. Verify that GitHub Actions is enabled in your repository settings
3. Check the Actions tab in your GitHub repository for any error messages

### Issues Not Moving on Project Board

If issues aren't moving between columns:

1. Verify that the project board is named exactly "RebelDESK Development"
2. Check that the column names match exactly: To-Do, In Progress, In Review, Testing, Completed
3. Ensure you're using the correct labels: "in-progress", "review", "testing"

### Progress.md Not Updating

If progress.md isn't updating when issues are closed:

1. Check that the issue title exactly matches the text in the progress.md checklist item
2. Verify that the GitHub Action has permission to commit changes to the repository
