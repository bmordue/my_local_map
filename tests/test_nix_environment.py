"""
Test Nix environment configuration and Cachix setup.
This test validates that the development environment works correctly.
"""

import pytest
import subprocess
import os
import json
from pathlib import Path


class TestNixEnvironment:
    """Test Nix development environment configuration"""

    @pytest.mark.unit
    def test_flake_nix_exists_and_valid(self):
        """Test that flake.nix exists and is valid JSON-like structure"""
        flake_path = Path("flake.nix")
        assert flake_path.exists(), "flake.nix should exist in project root"
        
        # Read flake content
        content = flake_path.read_text()
        
        # Basic validation - should contain expected sections
        assert "description" in content
        assert "nixpkgs" in content
        assert "flake-utils" in content
        assert "python312" in content
        assert "pytest" in content
        assert "gdal" in content

    @pytest.mark.unit  
    def test_shell_nix_exists_and_valid(self):
        """Test that shell.nix exists with required dependencies"""
        shell_path = Path("shell.nix")
        assert shell_path.exists(), "shell.nix should exist in project root"
        
        # Read shell.nix content
        content = shell_path.read_text()
        
        # Validate it contains our required dependencies
        required_deps = [
            "python312",
            "python312Packages.requests", 
            "python312Packages.pytest",
            "python312Packages.pytest-mock",
            "python312Packages.pytest-cov",
            "python312Packages.pillow",
            "gdal"
        ]
        
        for dep in required_deps:
            assert dep in content, f"Required dependency {dep} not found in shell.nix"

    @pytest.mark.unit
    def test_envrc_direnv_config(self):
        """Test that .envrc is configured for direnv support"""
        envrc_path = Path(".envrc")
        if envrc_path.exists():
            content = envrc_path.read_text().strip()
            assert content == "use flake", ".envrc should contain 'use flake'"

    @pytest.mark.unit
    def test_cachix_documentation_exists(self):
        """Test that Cachix documentation is present"""
        cachix_path = Path("CACHIX.md")
        assert cachix_path.exists(), "CACHIX.md should exist for documentation"
        
        content = cachix_path.read_text()
        
        # Should document key aspects
        assert "devenv" in content, "Should mention devenv cache"
        assert "Cache Configuration" in content, "Should have configuration section"
        assert "Performance Benefits" in content, "Should document benefits"

    @pytest.mark.unit
    def test_gitignore_nix_entries(self):
        """Test that .gitignore includes Nix-specific entries"""
        gitignore_path = Path(".gitignore")
        assert gitignore_path.exists(), ".gitignore should exist"
        
        content = gitignore_path.read_text()
        
        # Should ignore Nix artifacts
        nix_ignores = [".direnv/", "result", "flake.lock"]
        for ignore in nix_ignores:
            assert ignore in content, f"Should ignore {ignore} in .gitignore"

    @pytest.mark.integration
    def test_nix_command_availability(self):
        """Test if nix command is available (when running in Nix env)"""
        # This test only runs if we're in a Nix environment
        try:
            result = subprocess.run(
                ["which", "nix"], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            if result.returncode == 0:
                # We're in an environment with Nix, test it
                nix_result = subprocess.run(
                    ["nix", "--version"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                assert nix_result.returncode == 0, "nix --version should work"
                assert "nix" in nix_result.stdout.lower(), "Should output nix version"
            else:
                # Nix not available, skip this test
                pytest.skip("Nix not available in current environment")
                
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pytest.skip("Nix not available or timeout occurred")

    @pytest.mark.unit
    def test_github_workflows_use_cachix(self):
        """Test that GitHub workflows are configured for Cachix"""
        # Test test.yml workflow
        test_workflow = Path(".github/workflows/test.yml")
        assert test_workflow.exists(), "test.yml workflow should exist"
        
        content = test_workflow.read_text()
        
        # Should use Cachix action
        assert "cachix/install-nix-action" in content, "Should use install-nix-action"
        assert "cachix/cachix-action" in content, "Should use cachix-action"
        assert "devenv" in content, "Should use devenv cache"
        assert "nix develop" in content, "Should use modern nix develop commands"
        
        # Test generate-map-on-pr.yml workflow
        map_workflow = Path(".github/workflows/generate-map-on-pr.yml")
        assert map_workflow.exists(), "generate-map-on-pr.yml workflow should exist"
        
        map_content = map_workflow.read_text()
        
        # Should also use Cachix
        assert "cachix/install-nix-action" in map_content, "Map workflow should use install-nix-action"
        assert "cachix/cachix-action" in map_content, "Map workflow should use cachix-action"
        assert "devenv" in map_content, "Map workflow should use devenv cache"
        assert "nix develop" in map_content, "Map workflow should use modern nix develop commands"


class TestDependencyConsistency:
    """Test that dependencies are consistent across different configuration files"""

    @pytest.mark.unit
    def test_python_version_consistency(self):
        """Test that Python version is consistent across configs"""
        # Check flake.nix
        flake_content = Path("flake.nix").read_text()
        
        # Check shell.nix
        shell_content = Path("shell.nix").read_text()
        
        # Both should specify python312
        assert "python312" in flake_content, "flake.nix should specify python312"
        assert "python312" in shell_content, "shell.nix should specify python312"

    @pytest.mark.unit
    def test_test_dependencies_included(self):
        """Test that test dependencies are included in Nix configs"""
        flake_content = Path("flake.nix").read_text()
        shell_content = Path("shell.nix").read_text()
        
        test_deps = ["pytest", "pytest-mock", "pytest-cov"]
        
        for dep in test_deps:
            assert dep in flake_content, f"flake.nix should include {dep}"
            assert dep in shell_content, f"shell.nix should include {dep}"

    @pytest.mark.unit 
    def test_core_application_dependencies(self):
        """Test that core application dependencies are present"""
        flake_content = Path("flake.nix").read_text()
        shell_content = Path("shell.nix").read_text()
        
        core_deps = ["requests", "pillow", "gdal"]
        
        for dep in core_deps:
            # gdal is just gdal, others are python packages
            if dep == "gdal":
                assert dep in flake_content, f"flake.nix should include {dep}"
                assert dep in shell_content, f"shell.nix should include {dep}"
            else:
                package_name = f"python312Packages.{dep}"
                assert package_name in flake_content, f"flake.nix should include {package_name}"
                assert package_name in shell_content, f"shell.nix should include {package_name}"