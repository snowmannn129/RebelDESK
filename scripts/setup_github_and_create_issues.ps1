# PowerShell script to install GitHub CLI and create issues

function Install-GitHubCLI {
    Write-Output "Installing GitHub CLI..."
    
    # Check if winget is available
    $winget = Get-Command winget -ErrorAction SilentlyContinue
    if ($winget) {
        Write-Output "Installing GitHub CLI using winget..."
        winget install GitHub.cli
        return $true
    }
    
    # Check if Chocolatey is available
    $choco = Get-Command choco -ErrorAction SilentlyContinue
    if ($choco) {
        Write-Output "Installing GitHub CLI using Chocolatey..."
        choco install gh
        return $true
    }
    
    # Check if Scoop is available
    $scoop = Get-Command scoop -ErrorAction SilentlyContinue
    if ($scoop) {
        Write-Output "Installing GitHub CLI using Scoop..."
        scoop install gh
        return $true
    }
    
    # If no package manager is available, download the installer
    Write-Output "No package manager found. Please install GitHub CLI manually from https://cli.github.com/"
    Start-Process "https://cli.github.com/"
    return $false
}

function Authenticate-GitHubCLI {
    Write-Output "Authenticating with GitHub..."
    Write-Output "Please follow the prompts to log in to your GitHub account."
    
    gh auth login
    
    # Check if authentication was successful
    $authStatus = gh auth status 2>&1
    if ($authStatus -match "Logged in") {
        Write-Output "Successfully authenticated with GitHub!"
        return $true
    } else {
        Write-Output "Failed to authenticate with GitHub. Please try again."
        return $false
    }
}

function Create-GitHubIssues {
    param (
        [string]$issuesFile
    )
    
    Write-Output "Creating GitHub issues from $issuesFile..."
    
    # Check if the file exists
    if (!(Test-Path $issuesFile)) {
        Write-Error "Issues file not found: $issuesFile"
        return
    }
    
    # Read the file content
    $content = Get-Content $issuesFile -Raw
    
    # Extract the commands section
    if ($content -match '```powershell([\s\S]*?)```') {
        $commands = $matches[1].Trim()
        
        # Split commands into an array
        $commandArray = $commands -split "`n"
        
        # Execute each command
        $totalCommands = $commandArray.Count
        $successCount = 0
        
        for ($i = 0; $i -lt $totalCommands; $i++) {
            $command = $commandArray[$i].Trim()
            if ($command) {
                Write-Output "Creating issue $($i+1) of $totalCommands..."
                try {
                    Invoke-Expression $command
                    $successCount++
                    Write-Output "Issue created successfully!"
                } catch {
                    Write-Error "Failed to create issue: $_"
                }
                
                # Add a small delay to avoid rate limiting
                Start-Sleep -Seconds 1
            }
        }
        
        Write-Output "Created $successCount out of $totalCommands issues."
    } else {
        Write-Error "Could not find commands section in the issues file."
    }
}

# Main script
Write-Output "GitHub CLI Setup and Issue Creation Script"
Write-Output "=========================================="

# Check if GitHub CLI is installed
$gh = Get-Command gh -ErrorAction SilentlyContinue
if (!$gh) {
    $installed = Install-GitHubCLI
    if (!$installed) {
        Write-Output "Please install GitHub CLI manually and run this script again."
        exit
    }
    
    # Refresh PATH
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")
}

# Check if GitHub CLI is authenticated
$authStatus = gh auth status 2>&1
if ($authStatus -match "not logged") {
    $authenticated = Authenticate-GitHubCLI
    if (!$authenticated) {
        Write-Output "Please authenticate with GitHub and run this script again."
        exit
    }
}

# Find the latest issues file
$issuesFiles = Get-ChildItem -Path "reports" -Filter "github_issues_*.md" | Sort-Object LastWriteTime -Descending
if ($issuesFiles.Count -eq 0) {
    Write-Output "No issues files found. Please run scripts/create_github_issues.ps1 first."
    exit
}

$latestIssuesFile = $issuesFiles[0].FullName
Write-Output "Found issues file: $latestIssuesFile"

# Ask for confirmation
Write-Output "This script will create GitHub issues based on the commands in $latestIssuesFile."
$confirmation = Read-Host "Do you want to continue? (Y/N)"
if ($confirmation -ne "Y" -and $confirmation -ne "y") {
    Write-Output "Operation cancelled."
    exit
}

# Create the issues
Create-GitHubIssues -issuesFile $latestIssuesFile

Write-Output "Script completed!"
