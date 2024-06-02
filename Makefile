# Set variables
VENV_DIR := venv
SCRIPTS_DIR := scripts
PS_SCRIPT := $(SCRIPTS_DIR)/build_project.ps1
REQUIREMENTS_FILE := requirements.txt

.PHONY: build-project-win
# Build project
build-project-win:
	@powershell -ExecutionPolicy Bypass -File $(PS_SCRIPT)

.PHONY: build-project-linux
# Build project
build-project-linux:
	@echo '----- Build run -----'
	@chmod +x ./scripts/build.sh
	@./scripts/build.sh
	@echo '----- Build done -----'

# Install pre-commit hook
pre-commit-install:
	.venv\Scripts\pre-commit.exe install

# Run pre-commit hook
pre-commit-run:
	.venv\Scripts\pre-commit.exe run