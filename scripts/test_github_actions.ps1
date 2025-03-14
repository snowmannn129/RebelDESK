# PowerShell script to test GitHub Actions workflows locally using act
# https://github.com/nektos/act

function Test-GithubActionsWorkflow {
    param (
        [string]$workflow,
        [string]$event = "push"
    )
    
    # Check if act is installed
    try {
        $actVersion = act --version
        Write-Output "Act detected: $actVersion"
    } catch {
        Write-Error "Act is not installed. Please install it from https://github.com/nektos/act"
        Write-Output "You can install it with:"
        Write-Output "  - Windows (with Chocolatey): choco install act-cli"
        Write-Output "  - Windows (with Scoop): scoop install act"
        exit 1
    }
    
    # Run the workflow
    Write-Output "Testing workflow: $workflow with event: $event"
    act -W .github/workflows/$workflow -e .github/test_events/$event.json
}

# Create test events directory if it doesn't exist
if (!(Test-Path -Path ".github/test_events")) {
    New-Item -ItemType Directory -Path ".github/test_events" | Out-Null
}

# Create sample test events if they don't exist
$pushEvent = @"
{
  "ref": "refs/heads/main",
  "before": "0000000000000000000000000000000000000000",
  "after": "1111111111111111111111111111111111111111",
  "repository": {
    "name": "RebelDESK",
    "full_name": "yourusername/RebelDESK",
    "private": false,
    "owner": {
      "name": "yourusername",
      "email": "your.email@example.com"
    }
  },
  "pusher": {
    "name": "yourusername",
    "email": "your.email@example.com"
  },
  "commits": [
    {
      "id": "1111111111111111111111111111111111111111",
      "message": "Test commit",
      "timestamp": "2025-03-14T10:00:00Z",
      "author": {
        "name": "Your Name",
        "email": "your.email@example.com"
      },
      "committer": {
        "name": "Your Name",
        "email": "your.email@example.com"
      }
    }
  ]
}
"@

$issueClosedEvent = @"
{
  "action": "closed",
  "issue": {
    "number": 1,
    "title": "Implement dark/light themes",
    "body": "Task from src/ui/progress_ui.md\nSection: Core UI Framework",
    "labels": [
      {
        "name": "ui"
      },
      {
        "name": "feature"
      }
    ]
  },
  "repository": {
    "name": "RebelDESK",
    "full_name": "yourusername/RebelDESK",
    "private": false,
    "owner": {
      "name": "yourusername",
      "email": "your.email@example.com"
    }
  }
}
"@

$issueOpenedEvent = @"
{
  "action": "opened",
  "issue": {
    "number": 2,
    "title": "Add syntax highlighting",
    "body": "Task from src/ui/editor/progress_editor.md\nSection: Code Editing Features",
    "labels": [
      {
        "name": "editor"
      },
      {
        "name": "feature"
      }
    ]
  },
  "repository": {
    "name": "RebelDESK",
    "full_name": "yourusername/RebelDESK",
    "private": false,
    "owner": {
      "name": "yourusername",
      "email": "your.email@example.com"
    }
  }
}
"@

$issueLabeledEvent = @"
{
  "action": "labeled",
  "issue": {
    "number": 3,
    "title": "Implement file opening/reading",
    "body": "Task from src/backend/progress_backend.md\nSection: File Operations",
    "labels": [
      {
        "name": "backend"
      },
      {
        "name": "feature"
      },
      {
        "name": "in-progress"
      }
    ]
  },
  "label": {
    "name": "in-progress"
  },
  "repository": {
    "name": "RebelDESK",
    "full_name": "yourusername/RebelDESK",
    "private": false,
    "owner": {
      "name": "yourusername",
      "email": "your.email@example.com"
    }
  }
}
"@

# Write test events to files
$pushEvent | Out-File -FilePath ".github/test_events/push.json" -Encoding utf8
$issueClosedEvent | Out-File -FilePath ".github/test_events/issue_closed.json" -Encoding utf8
$issueOpenedEvent | Out-File -FilePath ".github/test_events/issue_opened.json" -Encoding utf8
$issueLabeledEvent | Out-File -FilePath ".github/test_events/issue_labeled.json" -Encoding utf8

# Display menu
Write-Output "GitHub Actions Workflow Tester"
Write-Output "============================"
Write-Output ""
Write-Output "Available workflows:"
Write-Output "1. update_progress.yml (Updates progress.md when issues are closed)"
Write-Output "2. run_tests.yml (Runs tests on push or pull request)"
Write-Output "3. update_project_board.yml (Updates project board based on issue status)"
Write-Output ""
Write-Output "Available events:"
Write-Output "a. push.json (Simulates a push event)"
Write-Output "b. issue_closed.json (Simulates an issue being closed)"
Write-Output "c. issue_opened.json (Simulates an issue being opened)"
Write-Output "d. issue_labeled.json (Simulates an issue being labeled)"
Write-Output ""

# Get user input
$workflowChoice = Read-Host "Select a workflow to test (1-3)"
$eventChoice = Read-Host "Select an event to use (a-d)"

# Map choices to values
$workflowMap = @{
    "1" = "update_progress.yml"
    "2" = "run_tests.yml"
    "3" = "update_project_board.yml"
}

$eventMap = @{
    "a" = "push"
    "b" = "issue_closed"
    "c" = "issue_opened"
    "d" = "issue_labeled"
}

# Run the test
if ($workflowMap.ContainsKey($workflowChoice) -and $eventMap.ContainsKey($eventChoice)) {
    $workflow = $workflowMap[$workflowChoice]
    $event = $eventMap[$eventChoice]
    
    Test-GithubActionsWorkflow -workflow $workflow -event $event
} else {
    Write-Error "Invalid selection. Please run the script again with valid choices."
}
