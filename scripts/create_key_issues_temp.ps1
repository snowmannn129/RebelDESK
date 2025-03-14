# PowerShell script to create key GitHub issues for RebelDESK

# Check if GitHub CLI is installed
$gh = Get-Command gh -ErrorAction SilentlyContinue
if (!$gh) {
    Write-Error "GitHub CLI (gh) is not installed. Please install it first using the instructions in github_setup_guide.md"
    exit 1
}

# Check if authenticated with GitHub
$authStatus = gh auth status 2>&1
if ($authStatus -match "not logged") {
    Write-Error "You are not logged in to GitHub. Please run 'gh auth login' first."
    exit 1
}

# Define key issues to create
$keyIssues = @(
    # UI Issues
    @{
        title = "[UI] Implement dark/light themes"
        body = "Task from src/ui/progress_ui.md`nSection: Core UI Framework`nImplement a theme system that supports both dark and light modes with smooth transitions."
        labels = "ui,feature,normal-priority"
    },
    @{
        title = "[UI] Implement basic text editing"
        body = "Task from src/ui/progress_ui.md`nSection: Text Editor`nImplement basic text editing functionality including cursor movement, text insertion and deletion."
        labels = "ui,feature,high-priority"
    },
    @{
        title = "[UI] Add syntax highlighting"
        body = "Task from src/ui/progress_ui.md`nSection: Text Editor`nImplement syntax highlighting for multiple programming languages using a library like Pygments."
        labels = "ui,feature,normal-priority"
    },
    
    # Editor Issues
    @{
        title = "[EDITOR] Implement basic text editing capabilities"
        body = "Task from src/ui/editor/progress_editor.md`nSection: Core Editor Functionality`nImplement the core text editing capabilities including cursor movement, text insertion/deletion, and selection."
        labels = "editor,feature,high-priority"
    },
    @{
        title = "[EDITOR] Add undo/redo functionality"
        body = "Task from src/ui/editor/progress_editor.md`nSection: Core Editor Functionality`nImplement undo and redo functionality with proper command history tracking."
        labels = "editor,feature,normal-priority"
    },
    
    # Backend Issues
    @{
        title = "[BACKEND] Implement logging system"
        body = "Task from src/backend/progress_backend.md`nSection: Core Backend Framework`nImplement a comprehensive logging system with different log levels and output options."
        labels = "backend,feature,normal-priority"
    },
    @{
        title = "[BACKEND] Implement file opening/reading"
        body = "Task from src/backend/progress_backend.md`nSection: File Operations`nImplement functionality to open and read files of various formats and sizes."
        labels = "backend,feature,normal-priority"
    },
    
    # File Manager Issues
    @{
        title = "[FILE_MANAGER] Implement file opening"
        body = "Task from src/backend/file_manager/progress_file_manager.md`nSection: Core File Operations`nImplement functionality to open files with proper error handling and encoding detection."
        labels = "file_manager,feature,normal-priority"
    },
    @{
        title = "[FILE_MANAGER] Add file saving functionality"
        body = "Task from src/backend/file_manager/progress_file_manager.md`nSection: Core File Operations`nImplement functionality to save files with proper error handling and encoding preservation."
        labels = "file_manager,feature,normal-priority"
    },
    
    # AI Issues
    @{
        title = "[AI] Implement basic code completion"
        body = "Task from src/ai/progress_ai.md`nSection: Code Completion`nImplement basic code completion functionality that suggests completions based on context."
        labels = "ai,feature,high-priority"
    },
    @{
        title = "[AI] Add context-aware suggestions"
        body = "Task from src/ai/progress_ai.md`nSection: Code Completion`nEnhance code completion to provide context-aware suggestions based on the current code structure."
        labels = "ai,feature,normal-priority"
    },
    
    # Testing Issues
    @{
        title = "[TESTS] Implement UI component tests"
        body = "Task from src/tests/progress_tests.md`nSection: Unit Testing`nImplement tests for UI components to ensure they render and behave correctly."
        labels = "tests,feature,normal-priority"
    },
    @{
        title = "[TESTS] Add backend functionality tests"
        body = "Task from src/tests/progress_tests.md`nSection: Unit Testing`nImplement tests for backend functionality to ensure correct behavior."
        labels = "tests,feature,normal-priority"
    }
)

# Create the issues
Write-Output "Creating key GitHub issues for RebelDESK..."
$successCount = 0

foreach ($issue in $keyIssues) {
    Write-Output "Creating issue: $($issue.title)"
    
    try {
        # Removed the --project parameter
        gh issue create --title $issue.title --body $issue.body --label $issue.labels
        $successCount++
        Write-Output "Issue created successfully!"
    } catch {
        Write-Error "Failed to create issue: $_"
    }
    
    # Add a small delay to avoid rate limiting
    Start-Sleep -Seconds 1
}

Write-Output "Created $successCount out of $($keyIssues.Count) key issues."
Write-Output "You can now check your GitHub repository to see the issues."
