# PowerShell script to convert progress.md checklist items to GitHub Issues

function Get-ChecklistItems {
    param (
        [string]$folder = "."
    )
    
    $progressFiles = Get-ChildItem -Path $folder -Recurse -Filter "*progress*.md"
    $issues = @()
    
    foreach ($file in $progressFiles) {
        $content = Get-Content $file.FullName
        $moduleName = $file.Directory.Name
        
        # Extract module name from file path
        if ($file.Name -eq "progress.md") {
            $moduleName = "Overall"
        } elseif ($file.Name -match "progress_(.+)\.md") {
            $moduleName = $matches[1].ToUpper()
        }
        
        $inChecklist = $false
        $currentSection = ""
        
        foreach ($line in $content) {
            # Detect section headers
            if ($line -match "^##?\s+\*\*(.+?)\*\*") {
                $currentSection = $matches[1]
                continue
            }
            
            # Detect checklist items
            if ($line -match "^\s*-\s+\[\s\]\s+(.+)$") {
                $taskName = $matches[1]
                
                # Remove any trailing comments or notes in parentheses
                $taskName = $taskName -replace "\s*\(.+?\)\s*$", ""
                $taskName = $taskName -replace "\s*\*.+?\*\s*$", ""
                
                $issue = @{
                    Title = "[$moduleName] $taskName"
                    Description = "Task from $($file.FullName)`nSection: $currentSection"
                    Labels = @($moduleName.ToLower(), "task")
                    File = $file.FullName
                }
                
                # Add priority label based on keywords
                if ($taskName -match "(core|basic|essential|critical|main|primary)") {
                    $issue.Labels += "high-priority"
                } else {
                    $issue.Labels += "normal-priority"
                }
                
                # Add feature or enhancement label
                if ($taskName -match "(implement|create|add|enable)") {
                    $issue.Labels += "feature"
                } else {
                    $issue.Labels += "enhancement"
                }
                
                $issues += $issue
            }
        }
    }
    
    return $issues
}

function Format-GithubIssueCommand {
    param (
        [hashtable]$issue
    )
    
    $title = $issue.Title -replace '"', '\"'
    $description = $issue.Description -replace '"', '\"'
    $labels = $issue.Labels -join ","
    
    return "gh issue create --title `"$title`" --body `"$description`" --label `"$labels`" --project `"https://github.com/users/snowmannn129/projects/1`""
}

# Get all checklist items
$issues = Get-ChecklistItems -folder "."

# Create output directory if it doesn't exist
if (!(Test-Path -Path "reports")) {
    New-Item -ItemType Directory -Path "reports" | Out-Null
}

# Generate GitHub issue creation commands
$outputFile = "reports/github_issues_$(Get-Date -Format 'yyyyMMdd').md"

"# GitHub Issue Creation Commands" | Out-File -FilePath $outputFile -Encoding utf8
"Generated on $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')`n" | Out-File -FilePath $outputFile -Encoding utf8 -Append
"## Issue Summary" | Out-File -FilePath $outputFile -Encoding utf8 -Append
"Total issues to create: $($issues.Count)`n" | Out-File -FilePath $outputFile -Encoding utf8 -Append

"## GitHub CLI Commands" | Out-File -FilePath $outputFile -Encoding utf8 -Append
"Run these commands to create the issues in your GitHub repository:`n" | Out-File -FilePath $outputFile -Encoding utf8 -Append
"```powershell" | Out-File -FilePath $outputFile -Encoding utf8 -Append

foreach ($issue in $issues) {
    $command = Format-GithubIssueCommand -issue $issue
    $command | Out-File -FilePath $outputFile -Encoding utf8 -Append
}

"```" | Out-File -FilePath $outputFile -Encoding utf8 -Append

"## Issue Details" | Out-File -FilePath $outputFile -Encoding utf8 -Append
foreach ($issue in $issues) {
    "### $($issue.Title)" | Out-File -FilePath $outputFile -Encoding utf8 -Append
    "- **Description**: $($issue.Description)" | Out-File -FilePath $outputFile -Encoding utf8 -Append
    "- **Labels**: $($issue.Labels -join ", ")" | Out-File -FilePath $outputFile -Encoding utf8 -Append
    "- **Source File**: $($issue.File)`n" | Out-File -FilePath $outputFile -Encoding utf8 -Append
}

Write-Output "GitHub issue creation commands generated at: $outputFile"

# Display summary
Write-Output "Found $($issues.Count) pending tasks to convert to GitHub issues"
Write-Output "Run the commands in $outputFile to create these issues in your GitHub repository"
