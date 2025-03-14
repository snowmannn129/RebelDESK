@echo off
echo ===================================================
echo RebelDESK GitHub Workflow Setup
echo ===================================================
echo.
echo This script will guide you through setting up the GitHub workflow for RebelDESK.
echo.
echo Steps:
echo 1. Install GitHub CLI
echo 2. Authenticate with GitHub
echo 3. Create GitHub repository (if needed)
echo 4. Push GitHub Actions workflows
echo 5. Create GitHub labels
echo 6. Create key GitHub issues
echo.
pause

cls
echo ===================================================
echo Step 1: Install GitHub CLI
echo ===================================================
echo.
echo You need to install the GitHub CLI (gh) to create issues and manage your GitHub repository.
echo.
echo Installation options:
echo 1. Using winget:    winget install GitHub.cli
echo 2. Using Chocolatey: choco install gh
echo 3. Using Scoop:      scoop install gh
echo 4. Manual download:  https://cli.github.com/
echo.
echo Please install GitHub CLI using one of these methods.
echo.
set /p choice=Have you installed GitHub CLI? (y/n): 
if /i "%choice%" neq "y" (
    echo Please install GitHub CLI and run this script again.
    pause
    exit
)

cls
echo ===================================================
echo Step 2: Authenticate with GitHub
echo ===================================================
echo.
echo You need to authenticate with GitHub using the GitHub CLI.
echo.
echo Run the following command in a new terminal:
echo    gh auth login
echo.
echo Follow the prompts:
echo - Select "GitHub.com"
echo - Select "HTTPS" for preferred protocol
echo - Confirm whether to authenticate with your GitHub credentials
echo - Select "Login with a web browser"
echo - Copy the one-time code and press Enter
echo - A browser will open; paste the code and authorize GitHub CLI
echo.
set /p choice=Have you authenticated with GitHub? (y/n): 
if /i "%choice%" neq "y" (
    echo Please authenticate with GitHub and run this script again.
    pause
    exit
)

cls
echo ===================================================
echo Step 3: Create GitHub Repository (if needed)
echo ===================================================
echo.
echo If you don't already have a GitHub repository for RebelDESK, you need to create one.
echo.
echo Run the following command in a new terminal:
echo    gh repo create RebelDESK --public --source=. --push
echo.
set /p choice=Do you already have a GitHub repository for RebelDESK or have you created one now? (y/n): 
if /i "%choice%" neq "y" (
    echo Please create a GitHub repository and run this script again.
    pause
    exit
)

cls
echo ===================================================
echo Step 4: Push GitHub Actions Workflows
echo ===================================================
echo.
echo Now you need to push the GitHub Actions workflows to your repository.
echo.
echo Run the following commands in a new terminal:
echo    git add .github/
echo    git commit -m "Add GitHub Actions workflows"
echo    git push
echo.
set /p choice=Have you pushed the GitHub Actions workflows? (y/n): 
if /i "%choice%" neq "y" (
    echo Please push the GitHub Actions workflows and run this script again.
    pause
    exit
)

cls
echo ===================================================
echo Step 5: Create GitHub Labels
echo ===================================================
echo.
echo Now you need to create the GitHub labels for your repository.
echo.
echo Run the following command in a new terminal:
echo    powershell -File scripts/setup_github_labels.ps1
echo.
echo If that doesn't work, you can create the labels manually using the commands in:
echo    scripts/github_setup_guide.md
echo.
set /p choice=Have you created the GitHub labels? (y/n): 
if /i "%choice%" neq "y" (
    echo Please create the GitHub labels and run this script again.
    pause
    exit
)

cls
echo ===================================================
echo Step 6: Create Key GitHub Issues
echo ===================================================
echo.
echo Finally, you need to create the key GitHub issues for your repository.
echo.
echo Run the following command in a new terminal:
echo    powershell -File scripts/create_key_issues.ps1
echo.
echo This will create 13 key issues across different modules.
echo.
echo If you want to create all 154 issues, you can use:
echo    powershell -File scripts/create_github_issues.ps1
echo    powershell -File scripts/setup_github_and_create_issues.ps1
echo.
set /p choice=Have you created the GitHub issues? (y/n): 
if /i "%choice%" neq "y" (
    echo Please create the GitHub issues and run this script again.
    pause
    exit
)

cls
echo ===================================================
echo GitHub Workflow Setup Complete!
echo ===================================================
echo.
echo Congratulations! You have successfully set up the GitHub workflow for RebelDESK.
echo.
echo Your GitHub repository now has:
echo - GitHub Actions workflows for automated testing and progress tracking
echo - GitHub labels for categorizing issues
echo - GitHub issues for tracking tasks
echo.
echo You can now use the GitHub workflow to manage your RebelDESK development.
echo.
echo When you close an issue, the corresponding item in progress.md will be automatically marked as complete.
echo When you push code, tests will run automatically.
echo.
pause
