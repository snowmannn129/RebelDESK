# PowerShell script to summarize progress across all checklist files

function Get-Progress {
    param (
        [string]$folder = "."
    )
    
    Write-Output "# RebelDESK Development Progress Summary"
    Write-Output "## Generated on $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')`n"
    
    $progressFiles = Get-ChildItem -Path $folder -Recurse -Filter "*progress*.md"
    $totalCompleted = 0
    $totalTasks = 0
    
    foreach ($file in $progressFiles) {
        $content = Get-Content $file.FullName
        $completed = ($content | Select-String '\[x\]').Count
        $pending = ($content | Select-String '\[ \]').Count
        $proposed = ($content | Select-String '\[~\]').Count
        
        $total = $completed + $pending
        $percent = if ($total -eq 0) { 0 } else { [math]::Round(($completed / $total) * 100) }
        
        # Extract module name from file path
        $moduleName = $file.Directory.Name
        if ($file.Name -eq "progress.md") {
            $moduleName = "Overall"
        } elseif ($file.Name -match "progress_(.+)\.md") {
            $moduleName = $matches[1].ToUpper()
        }
        
        Write-Output "### $moduleName Module"
        Write-Output "- **Status**: $completed/$total tasks completed ($percent%)"
        Write-Output "- **Proposed Features**: $proposed items"
        Write-Output "- **File**: $($file.FullName)`n"
        
        $totalCompleted += $completed
        $totalTasks += $total
    }
    
    $overallPercent = if ($totalTasks -eq 0) { 0 } else { [math]::Round(($totalCompleted / $totalTasks) * 100) }
    Write-Output "## Summary"
    Write-Output "- **Overall Progress**: $totalCompleted/$totalTasks tasks completed ($overallPercent%)"
    Write-Output "- **Total Checklist Files**: $($progressFiles.Count)"
}

# Create directory if it doesn't exist
if (!(Test-Path -Path "reports")) {
    New-Item -ItemType Directory -Path "reports" | Out-Null
}

# Generate progress report
$reportPath = "reports/progress_report_$(Get-Date -Format 'yyyyMMdd').md"
Get-Progress | Out-File -FilePath $reportPath -Encoding utf8

Write-Output "Progress report generated at: $reportPath"

# Display progress in console
