# Update GitHub Issue Status
# This script updates the status of GitHub issues based on the progress in the project

# Get the current directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$rootDir = Split-Path -Parent $scriptDir

# Function to get completed tasks from progress files
function Get-CompletedTasks {
    param (
        [string]$progressFile
    )
    
    $content = Get-Content -Path $progressFile -Raw
    $completedTasks = @()
    
    # Match lines with [x] which indicates completed tasks
    $matches = [regex]::Matches($content, '- \[x\] (.*?)(?=\r?\n)')
    foreach ($match in $matches) {
        $taskName = $match.Groups[1].Value.Trim()
        $completedTasks += $taskName
    }
    
    return $completedTasks
}

# Function to get in-progress tasks from progress files
function Get-InProgressTasks {
    param (
        [string]$progressFile
    )
    
    $content = Get-Content -Path $progressFile -Raw
    $inProgressTasks = @()
    
    # Match lines with [~] which indicates in-progress tasks
    $matches = [regex]::Matches($content, '- \[~\] (.*?)(?=\r?\n)')
    foreach ($match in $matches) {
        $taskName = $match.Groups[1].Value.Trim()
        $inProgressTasks += $taskName
    }
    
    return $inProgressTasks
}

# Get all progress files
$progressFiles = @(
    "$rootDir\progress.md",
    "$rootDir\src\ui\progress_ui.md",
    "$rootDir\src\ui\editor\progress_editor.md",
    "$rootDir\src\ui\settings\progress_settings.md",
    "$rootDir\src\backend\progress_backend.md",
    "$rootDir\src\backend\file_manager\progress_file_manager.md",
    "$rootDir\src\ai\progress_ai.md",
    "$rootDir\src\tests\progress_tests.md"
)

# Collect all completed and in-progress tasks
$allCompletedTasks = @()
$allInProgressTasks = @()

foreach ($file in $progressFiles) {
    if (Test-Path $file) {
        $allCompletedTasks += Get-CompletedTasks -progressFile $file
        $allInProgressTasks += Get-InProgressTasks -progressFile $file
    }
}

# Generate GitHub CLI commands to update issue status
$outputFile = "$rootDir\reports\github_issue_status_update_$(Get-Date -Format 'yyyyMMdd').md"

# Create the output directory if it doesn't exist
$outputDir = Split-Path -Parent $outputFile
if (-not (Test-Path $outputDir)) {
    New-Item -ItemType Directory -Path $outputDir | Out-Null
}

# Write header to the output file
@"
# GitHub Issue Status Update Commands
Generated on $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')

## Completed Tasks
The following commands will close issues for completed tasks:

```powershell
"@ | Out-File -FilePath $outputFile -Encoding utf8

# Generate commands for completed tasks
foreach ($task in $allCompletedTasks) {
    # Escape quotes in the task name
    $escapedTask = $task -replace '"', '\"'
    
    # Generate command to close the issue and add the 'completed' label
    "gh issue list --search `"$escapedTask in:title`" --json number --jq '.[].number' | ForEach-Object { gh issue close `$_ --comment `"Task completed`" }" | Out-File -FilePath $outputFile -Encoding utf8 -Append
}

# Write in-progress tasks section
@"
```

## In-Progress Tasks
The following commands will add the 'in-progress' label to in-progress tasks:

```powershell
"@ | Out-File -FilePath $outputFile -Encoding utf8 -Append

# Generate commands for in-progress tasks
foreach ($task in $allInProgressTasks) {
    # Escape quotes in the task name
    $escapedTask = $task -replace '"', '\"'
    
    # Generate command to add the 'in-progress' label
    "gh issue list --search `"$escapedTask in:title`" --json number --jq '.[].number' | ForEach-Object { gh issue edit `$_ --add-label `"in-progress`" }" | Out-File -FilePath $outputFile -Encoding utf8 -Append
}

# Close the code block
@"
```

## Instructions
1. Make sure you have the GitHub CLI installed and authenticated
2. Run these commands to update the status of your GitHub issues
3. The project board will be automatically updated based on the issue labels and status
"@ | Out-File -FilePath $outputFile -Encoding utf8 -Append

Write-Host "GitHub issue status update commands generated at: $outputFile"
