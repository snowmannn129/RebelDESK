# PowerShell script to set up GitHub labels for RebelDESK repository

# Define the labels to create
$labels = @(
    @{
        name = "ui"
        color = "0366d6"
        description = "UI-related tasks and issues"
    },
    @{
        name = "backend"
        color = "d73a4a"
        description = "Backend-related tasks and issues"
    },
    @{
        name = "ai"
        color = "6f42c1"
        description = "AI-related tasks and issues"
    },
    @{
        name = "tests"
        color = "0e8a16"
        description = "Testing-related tasks and issues"
    },
    @{
        name = "editor"
        color = "1d76db"
        description = "Editor component tasks and issues"
    },
    @{
        name = "settings"
        color = "5319e7"
        description = "Settings component tasks and issues"
    },
    @{
        name = "file_manager"
        color = "fbca04"
        description = "File manager tasks and issues"
    },
    @{
        name = "high-priority"
        color = "b60205"
        description = "High priority tasks that need immediate attention"
    },
    @{
        name = "normal-priority"
        color = "0e8a16"
        description = "Normal priority tasks"
    },
    @{
        name = "feature"
        color = "c2e0c6"
        description = "New feature implementation"
    },
    @{
        name = "enhancement"
        color = "a2eeef"
        description = "Enhancement to existing functionality"
    },
    @{
        name = "bug"
        color = "d73a4a"
        description = "Something isn't working"
    },
    @{
        name = "documentation"
        color = "0075ca"
        description = "Documentation improvements"
    },
    @{
        name = "in-progress"
        color = "ffccd7"
        description = "Work in progress"
    },
    @{
        name = "review"
        color = "f9d0c4"
        description = "Ready for review"
    },
    @{
        name = "testing"
        color = "c5def5"
        description = "Ready for testing"
    },
    @{
        name = "task"
        color = "d4c5f9"
        description = "Task from progress checklist"
    }
)

# Function to create GitHub labels using gh CLI
function Create-GitHubLabels {
    foreach ($label in $labels) {
        Write-Output "Creating label: $($label.name)"
        
        # Check if label exists
        $labelExists = gh label list | Select-String -Pattern "^$($label.name)\s"
        
        if ($labelExists) {
            # Update existing label
            gh label edit $label.name --color $label.color --description "$($label.description)"
        } else {
            # Create new label
            gh label create $label.name --color $label.color --description "$($label.description)"
        }
    }
}

# Check if gh CLI is installed
try {
    $ghVersion = gh --version
    Write-Output "GitHub CLI detected: $ghVersion"
} catch {
    Write-Error "GitHub CLI (gh) is not installed or not in PATH. Please install it from https://cli.github.com/"
    exit 1
}

# Check if logged in to GitHub
$loggedIn = gh auth status 2>&1
if ($loggedIn -match "not logged") {
    Write-Output "You need to log in to GitHub CLI first. Run 'gh auth login' and follow the prompts."
    exit 1
}

# Create the labels
Write-Output "Setting up GitHub labels for RebelDESK repository..."
Create-GitHubLabels

Write-Output "GitHub labels setup complete!"
