# AI Instructions for RebelDESK Development

## Core Development Instructions

Please continue development on RebelDESK. Follow all rules and checklists at all times. See the following files for more information:
- scripts\README.md
- src\tests\progress_tests.md
- progress.md
- README.md
- C:\Users\snowm\Desktop\VSCode\RebelDESK\.github\README.md

## Progress Tracking and GitHub Integration

After completing any task or feature:

1. **Update Progress Files**:
   - Update the main progress.md file
   - Update the relevant module-specific progress file (e.g., src\ui\progress_ui.md)
   - Run `powershell -File scripts/get_progress.ps1` to generate an updated progress report

2. **Update GitHub Issues and Project Board**:
   - Run `powershell -File scripts/update_github_issue_status.ps1` to generate GitHub issue update commands
   - Execute the generated commands to update GitHub issues status
   - Ensure completed tasks are closed and in-progress tasks are properly labeled
   - The project board will automatically update based on issue status and labels

3. **Create New GitHub Issues for Pending Tasks**:
   - Run `powershell -File scripts/create_github_issues.ps1` to generate GitHub issue creation commands for new tasks
   - Execute the generated commands to create new GitHub issues

## Development Guidelines

- Follow all core instructions and development guidelines in the project documentation
- Ensure all code follows the established coding standards and best practices
- Write comprehensive tests for all new features and modifications
- Maintain the modular architecture of the project
- Document all changes and new features appropriately
- Verify that all UI components are properly connected to backend functions
- Run tests to ensure no regressions are introduced

Remember to always follow the established workflow:
1. Implement the feature with proper tests
2. Update progress tracking files
3. Update GitHub issues and project board
4. Document the changes
5. Verify everything works as expected
