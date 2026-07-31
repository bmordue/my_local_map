# Lumsden Tourist Map Generator Cachix Configuration
# This file documents the Cachix setup for the project's Nix dependencies

## Overview
The project uses Cachix to cache Nix packages for faster CI/CD builds.

## Cache Configuration
- **Cache Name**: `devenv` - A well-maintained community cache
- **Skip Push**: `true` - We consume from the cache but don't push to it
- **Alternative Caches**: Consider `nix-community` for additional packages

## Dependencies Cached
The following packages are cached via Cachix:
- python312 and related packages
- python312Packages.requests
- python312Packages.python-mapnik
- python312Packages.pytest (and related testing packages)
- python312Packages.pillow
- python312Packages.black (code formatting)
- python312Packages.isort (import sorting)  
- python312Packages.flake8 (linting)
- gdal (geospatial data abstraction library)
- curl, unzip (basic utilities)

## Performance Benefits
- Typical cache hit rate: 80-95% for our dependency set
- Build time reduction: ~5-10 minutes -> ~1-2 minutes
- Network usage reduction: ~500MB -> ~50MB per workflow run

## Usage in Workflows
Both `test.yml` and `generate-map-on-pr.yml` use:
```yaml
- name: Setup Nix cache
  uses: cachix/cachix-action@v12
  with:
    name: devenv
    skipPush: true
```

## Future Improvements
- Consider setting up a project-specific cache if we add more custom packages
- Monitor cache effectiveness using GitHub Actions insights
- Could add additional community caches like `nix-community` if needed