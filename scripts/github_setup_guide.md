# GitHub Workflow Setup Guide for RebelDESK

## Step 1: Install GitHub CLI

You need to install the GitHub CLI (gh) to create issues and manage your GitHub repository from the command line.

### Windows Installation Options:

**Option 1: Using winget**
```powershell
winget install GitHub.cli
```

**Option 2: Using Chocolatey**
```powershell
choco install gh
```

**Option 3: Using Scoop**
```powershell
scoop install gh
```

**Option 4: Manual Installation**
Download and install from: https://cli.github.com/

## Step 2: Authenticate with GitHub

After installing GitHub CLI, you need to authenticate:

```powershell
gh auth login
```

Follow the prompts:
- Select "GitHub.com"
- Select "HTTPS" for preferred protocol
- Confirm whether to authenticate with your GitHub credentials
- Select "Login with a web browser"
- Copy the one-time code and press Enter
- A browser will open; paste the code and authorize GitHub CLI

## Step 3: Push GitHub Actions Workflows to Your Repository

First, make sure you have a GitHub repository for RebelDESK. If not, create one:

```powershell
gh repo create RebelDESK --public --source=. --push
```

Then push the GitHub Actions workflows:

```powershell
git add .github/
git commit -m "Add GitHub Actions workflows"
git push
```

## Step 4: Set Up GitHub Project Board

1. Go to your GitHub repository in a browser
2. Click on "Projects" tab
3. Click "Create project"
4. Select "Board" as the template
5. Name it "RebelDESK Development"
6. Make sure it has these columns: To-Do, In Progress, In Review, Testing, Completed

## Step 5: Create GitHub Labels

Run the label setup script:

```powershell
gh label create ui --color 0366d6 --description "UI-related tasks and issues"
gh label create backend --color d73a4a --description "Backend-related tasks and issues"
gh label create ai --color 6f42c1 --description "AI-related tasks and issues"
gh label create tests --color 0e8a16 --description "Testing-related tasks and issues"
gh label create editor --color 1d76db --description "Editor component tasks and issues"
gh label create settings --color 5319e7 --description "Settings component tasks and issues"
gh label create file_manager --color fbca04 --description "File manager tasks and issues"
gh label create high-priority --color b60205 --description "High priority tasks that need immediate attention"
gh label create normal-priority --color 0e8a16 --description "Normal priority tasks"
gh label create feature --color c2e0c6 --description "New feature implementation"
gh label create enhancement --color a2eeef --description "Enhancement to existing functionality"
gh label create task --color d4c5f9 --description "Task from progress checklist"
```

## Step 6: Create GitHub Issues

To create all 154 issues at once, you can run the commands in the generated file:

```powershell
# Open the file in a text editor
code reports/github_issues_20250314.md

# Copy the commands between the ```powershell and ``` markers
# Run them in PowerShell
```

Alternatively, you can create a few key issues manually:

```powershell
gh issue create --title "[UI] Implement dark/light themes" --body "Task from progress_ui.md" --label "ui,feature" --project "https://github.com/users/snowmannn129/projects/1"
gh issue create --title "[EDITOR] Implement basic text editing capabilities" --body "Task from progress_editor.md" --label "editor,high-priority,feature" --project "https://github.com/users/snowmannn129/projects/1"
gh issue create --title "[BACKEND] Implement file opening/reading" --body "Task from progress_backend.md" --label "backend,feature" --project "https://github.com/users/snowmannn129/projects/1"
```

## Step 7: Verify Setup

1. Check your GitHub repository to ensure:
   - GitHub Actions workflows are present in the Actions tab
   - Issues have been created and appear in your project board
   - Labels have been created and applied to issues

2. Test the workflow by:
   - Closing an issue and verifying progress.md is updated
   - Pushing code and verifying tests run automatically
