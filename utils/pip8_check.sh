#!/bin/bash
# Pre-commit hook for Python PEP 8 enforcement
# Place this file at .git/hooks/pre-commit and make it executable

set -e  # Exit on any error

# Configuration
MAX_LINE_LENGTH=88  # Black's default, change to 79 for strict PEP 8
IGNORE_ERRORS="E203,W503"  # Errors to ignore (Black compatibility)
AUTOFIX=${AUTOFIX:-false}  # Set to true to auto-fix issues

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_color() {
    printf "${1}%s${NC}\n" "$2"
}

print_header() {
    print_color $BLUE "🐍 Python PEP 8 Pre-commit Hook"
    echo "=================================="
}

# Check if required tools are installed
check_dependencies() {
    local missing_tools=()
    
    command -v flake8 >/dev/null 2>&1 || missing_tools+=("flake8")
    command -v black >/dev/null 2>&1 || missing_tools+=("black")
    command -v isort >/dev/null 2>&1 || missing_tools+=("isort")
    
    if [ ${#missing_tools[@]} -ne 0 ]; then
        print_color $RED "❌ Missing required tools: ${missing_tools[*]}"
        print_color $YELLOW "Install with: pip install flake8 black isort"
        exit 1
    fi
}

# Get list of Python files being committed
get_python_files() {
    find . -type f -iname '*py'
#    git diff --cached --name-only --diff-filter=ACM | grep -E '\.py$' || true
}

# Run Black formatter check
check_black() {
    local files=("$@")
    if [ ${#files[@]} -eq 0 ]; then
        return 0
    fi
    
    print_color $BLUE "🔍 Checking Black formatting..."
    
    if [ "$AUTOFIX" = true ]; then
        black --line-length $MAX_LINE_LENGTH "${files[@]}"
        # Re-add files if they were modified
        for file in "${files[@]}"; do
            if ! git diff --quiet "$file"; then
                git add "$file"
                print_color $GREEN "✅ Auto-formatted: $file"
            fi
        done
    else
        if ! black --check --line-length $MAX_LINE_LENGTH "${files[@]}"; then
            print_color $RED "❌ Black formatting issues found!"
            print_color $YELLOW "💡 Run 'black --line-length $MAX_LINE_LENGTH .' to fix formatting"
            print_color $YELLOW "💡 Or set AUTOFIX=true to auto-format during commits"
            return 1
        fi
    fi
    
    print_color $GREEN "✅ Black formatting passed"
    return 0
}

# Run isort import sorting check
check_isort() {
    local files=("$@")
    if [ ${#files[@]} -eq 0 ]; then
        return 0
    fi
    
    print_color $BLUE "🔍 Checking import sorting..."
    
    if [ "$AUTOFIX" = true ]; then
        isort --profile black "${files[@]}"
        # Re-add files if they were modified
        for file in "${files[@]}"; do
            if ! git diff --quiet "$file"; then
                git add "$file"
                print_color $GREEN "✅ Auto-sorted imports: $file"
            fi
        done
    else
        if ! isort --profile black --check-only "${files[@]}"; then
            print_color $RED "❌ Import sorting issues found!"
            print_color $YELLOW "💡 Run 'isort --profile black .' to fix import order"
            print_color $YELLOW "💡 Or set AUTOFIX=true to auto-sort during commits"
            return 1
        fi
    fi
    
    print_color $GREEN "✅ Import sorting passed"
    return 0
}

# Run flake8 linting
check_flake8() {
    local files=("$@")
    if [ ${#files[@]} -eq 0 ]; then
        return 0
    fi
    
    print_color $BLUE "🔍 Running flake8 linting..."
    
    local flake8_config=""
    if [ -f "setup.cfg" ] && grep -q "\[flake8\]" setup.cfg; then
        flake8_config="--config=setup.cfg"
    elif [ -f ".flake8" ]; then
        flake8_config="--config=.flake8"
    elif [ -f "tox.ini" ] && grep -q "\[flake8\]" tox.ini; then
        flake8_config="--config=tox.ini"
    fi
    
    if ! flake8 $flake8_config \
        --max-line-length=$MAX_LINE_LENGTH \
        --ignore=$IGNORE_ERRORS \
        --statistics \
        --count \
        "${files[@]}"; then
        print_color $RED "❌ Flake8 found PEP 8 violations!"
        print_color $YELLOW "💡 Fix the issues above before committing"
        return 1
    fi
    
    print_color $GREEN "✅ Flake8 linting passed"
    return 0
}

# Check for common Python issues
check_python_issues() {
    local files=("$@")
    if [ ${#files[@]} -eq 0 ]; then
        return 0
    fi
    
    print_color $BLUE "🔍 Checking for common Python issues..."
    
    local issues_found=false
    
    for file in "${files[@]}"; do
        # Check for print statements (might want to use logging)
        if grep -n "print(" "$file" >/dev/null 2>&1; then
            print_color $YELLOW "⚠️  Print statements found in $file (consider using logging)"
            grep -n "print(" "$file"
        fi
        
        # Check for TODO/FIXME comments
        if grep -n -i "TODO\|FIXME" "$file" >/dev/null 2>&1; then
            print_color $YELLOW "⚠️  TODO/FIXME found in $file"
            grep -n -i "TODO\|FIXME" "$file"
        fi
        
        # Check for debugging statements
        if grep -n -E "pdb\.set_trace\(\)|breakpoint\(\)|ipdb\.set_trace\(\)" "$file" >/dev/null 2>&1; then
            print_color $RED "❌ Debugging statements found in $file"
            grep -n -E "pdb\.set_trace\(\)|breakpoint\(\)|ipdb\.set_trace\(\)" "$file"
            issues_found=true
        fi
        
        # Check for bare except clauses
        if grep -n "except:" "$file" >/dev/null 2>&1; then
            print_color $RED "❌ Bare except clauses found in $file (use specific exceptions)"
            grep -n "except:" "$file"
            issues_found=true
        fi
    done
    
    if [ "$issues_found" = true ]; then
        return 1
    fi
    
    print_color $GREEN "✅ Python issue check passed"
    return 0
}

# Main execution
main() {
    print_header
    
    # Check if we're in a git repository
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        print_color $RED "❌ Not in a git repository"
        exit 1
    fi
    
    # Check dependencies
    check_dependencies
    
    # Get Python files to check
    mapfile -t python_files < <(get_python_files)
    
    if [ ${#python_files[@]} -eq 0 ]; then
        print_color $GREEN "✅ No Python files to check"
        exit 0
    fi
    
    print_color $BLUE "📝 Checking ${#python_files[@]} Python file(s):"
    printf '  - %s\n' "${python_files[@]}"
    echo
    
    # Run all checks
    local exit_code=0
    
    check_black "${python_files[@]}" || exit_code=1
    echo
    
    check_isort "${python_files[@]}" || exit_code=1
    echo
    
    check_flake8 "${python_files[@]}" || exit_code=1
    echo
    
    check_python_issues "${python_files[@]}" || exit_code=1
    echo
    
    if [ $exit_code -eq 0 ]; then
        print_color $GREEN "🎉 All PEP 8 checks passed! Commit proceeding..."
    else
        print_color $RED "💥 Pre-commit checks failed. Commit aborted."
        echo
        print_color $YELLOW "💡 Tips:"
        print_color $YELLOW "   - Run checks manually: ./scripts/check-python.sh"
        print_color $YELLOW "   - Auto-fix formatting: AUTOFIX=true git commit"
        print_color $YELLOW "   - Skip hook (not recommended): git commit --no-verify"
    fi
    
    exit $exit_code
}

# Run main function
main "$@"
