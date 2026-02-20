{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
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
    python311Packages.gdal  # GDAL Python bindings (osgeo module)
    python311Packages.numpy # For elevation processing

    # dev dependencies, linting etc
    python311Packages.flake8
    python311Packages.black
    python311Packages.isort

    # GDAL for OSM conversion
    gdal
    
    # Basic tools
    curl
    unzip
  ]
  ++ (if pkgs.config.allowUnfree or false then [
    pkgs.gemini-cli
    pkgs.claude-code
  ] else []);

  shellHook = ''
    echo "Made available:"
    echo "  Python 3.11 + requests + Pillow"
    echo "  GDAL/OGR (for data conversion)"
    echo "  GDAL Python bindings (osgeo module)"
    echo "  Mapnik (for rendering)"
    echo "  pytest + pytest-mock + pytest-cov (for testing)"
    echo "  NumPy (for elevation processing)"
    echo ""
    echo "Ready to run: python map_generator.py"
    echo "  or: pytest tests/"
    echo ""
    echo "Optional: npx @qwen-code/qwen-code"
  '';
}
