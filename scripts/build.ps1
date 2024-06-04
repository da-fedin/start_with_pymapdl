# scripts/build_project.ps1

param (
    [string]$requirementsFile = "requirements.txt",
    [string]$venvDir = ".venv",
    [string]$tmpDir = "tmp"
)

Write-Output "Build started..."

# Debug message for checking if the virtual environment exists
Write-Output "Checking if the virtual environment exists..."
Write-Output "venvDir: $venvDir"  # Print venvDir variable

# Activate virtual environment if it exists
if (Test-Path $venvDir) {
    Write-Output "Virtual environment found. Activating..."
    Write-Output "Activating script path: $venvDir/Scripts/activate.ps1"  # Print activate script path
    & $venvDir/Scripts/activate.ps1
} else {
    Write-Output "Virtual environment not found."
}

# Debug message for specifying the full path to the local pip executable
Write-Output "Specifying the full path to the local pip executable..."
Write-Output "pipExecutable: $pipExecutable"  # Print pipExecutable variable

# Specify the full path to the local pip executable
$pipExecutable = Join-Path $venvDir "Scripts\pip.exe"

# Debug message for installing requirements using the local pip executable
Write-Output "Installing requirements using the local pip executable..."
Write-Output "requirementsFile: $requirementsFile"  # Print requirementsFile variable

# Install requirements using the local pip executable
try {
    & $pipExecutable install -r $requirementsFile
    Write-Output "Requirements installed successfully!"

    # Install Jupyter using pip
    Write-Output "Installing Jupyter using pip..."
    & $pipExecutable install jupyter
    Write-Output "Jupyter installed successfully!"
}
catch {
    Write-Output "Failed to install requirements. Please check if pip is installed correctly."
}

Write-Output " --------------------------------------------- "

# Remove temporary files
Write-Output "Start to remove files from $tmpDir dir ..."

try {
    Remove-Item "$tmpDir/*.*"
}
catch {
    Write-Output "Failed to remove files from $tmpDir dir."
}

Write-Output " Files from $tmpDir dir removed"

Write-Output " --------------------------------------------- "

Write-Output "Build done."