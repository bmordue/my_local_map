{
  description = "Lumsden Tourist Map Generator - A Python-based map generator using OpenStreetMap data";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
      in
      {
        devShells.default = pkgs.mkShell {
          buildInputs = with pkgs; [
            # Minimal mapping dependencies (no PostgreSQL!)
            python312
            python312Packages.requests
            python312Packages.python-mapnik
            python312Packages.pytest
            python312Packages.pytest-mock
            python312Packages.pytest-cov
            python312Packages.cairosvg
            python312Packages.pillow
            
            # Code formatting and linting
            python312Packages.black
            python312Packages.isort
            python312Packages.flake8

            # GDAL for OSM conversion
            gdal
            
            # Basic tools
            curl
            unzip
          ];

          shellHook = ''
            echo "🗺️  Lumsden Tourist Map Generator - Nix Development Environment"
            echo "=============================================================="
            echo "Made available:"
            echo "  🐍 Python 3.12 + core packages (requests, Pillow)"
            echo "  🗺️  GDAL/OGR (for data conversion)"
            echo "  🎨 Mapnik (for map rendering)"
            echo "  🧪 pytest + pytest-mock + pytest-cov (for testing)"
            echo "  ✨ Code formatting: black, isort, flake8"
            echo ""
            echo "Ready to run:"
            echo "  python map_generator.py    # Generate maps"
            echo "  pytest tests/             # Run tests"
            echo "  black .                   # Format code"
            echo "  flake8 .                  # Lint code"
            echo ""
            echo "🚀 Happy mapping! 🗺️"
          '';
        };
      });
}