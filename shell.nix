{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
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
    echo "  Python 3.12 + requests + Pillow"
    echo "  GDAL/OGR (for data conversion)"
    echo "  Mapnik (for rendering)"
    echo "  pytest + pytest-mock + pytest-cov (for testing)"
    echo ""
    echo "Ready to run: python map_generator.py"
    echo "  or: pytest tests/"
    echo ""
    echo "Optional: npx @qwen-code/qwen-code"
  '';
}
