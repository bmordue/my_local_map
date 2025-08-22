{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = with pkgs; [
    # Minimal mapping dependencies (no PostgreSQL!)
    python312
    python312Packages.requests
    python312Packages.python-mapnik

    # GDAL for OSM conversion
    gdal
    
    # Basic tools
    curl
    unzip

#    claude-code
#    gemini-cli
  ];

  shellHook = ''
    echo "Made available:"
    echo "  Python 3.12 + requests"
    echo "  GDAL/OGR (for data conversion)"
    echo "  Mapnik (for rendering)"
    echo ""
    echo "Ready to run: python map_generator.py"
    echo ""
  '';
}
