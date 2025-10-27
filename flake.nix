{
  description = "Lumsden Tourist Map Generator - A Python-based map generator using OpenStreetMap data";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.05";
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
            python311
            python311Packages.requests
            python311Packages.python-mapnik
            python311Packages.pytest
            python311Packages.pytest-mock
            python311Packages.pytest-cov
            python311Packages.cairosvg
            python311Packages.pillow
            
            # Code formatting and linting
            python311Packages.black
            python311Packages.isort
            python311Packages.flake8

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
            echo "  🐍 Python 3.11 + core packages (requests, Pillow)"
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