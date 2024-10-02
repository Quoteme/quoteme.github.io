{
  description = "My github pages blog";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixpkgs-unstable";
    flake-utils = {
      inputs.nixpkgs.follows = "nixpkgs";
      url = "github:numtide/flake-utils";
    };
  };

  outputs = { self, nixpkgs, flake-utils, ... }@inputs:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs {
          inherit system;
          config.allowUnfree = true;
          overlays = [
            (self: super: {
              quarto = super.quarto.override {
                extraRPackages = [ ];
                extraPythonPackages = ps:
                  with ps; [
                    plotly
                    numpy
                    pandas
                    matplotlib
                  ];
              };
            })
          ];
        };
        dependencies = with pkgs; [ quarto ];
      in {
        # default shell 
        devShells.default = with pkgs;
          mkShell {
            name = "blog-shell";
            buildInputs = dependencies;
            shellHook = ''
              export PYGMENTIZE=${python313Packages.pygments}/bin/pygmentize
              export PATH=${quarto}/bin:${python313Packages.pygments}/bin:${python313}/bin:$PATH
              export PYTHONPATH=${python313Packages.pygments}/lib/python3.13/site-packages:${python311Packages.pandocfilters}/lib/python3.11/site-packages
            '';
          };

        # build quarto blog
        packages.default = pkgs.stdenv.mkDerivation {
          name = "build-blog";
          src = ./.;
          buildInputs = dependencies;
          buildPhase = ''
            quarto render
          '';
          installPhase = ''
            mkdir -p $out
            cp -r _site/* $out/
          '';
        };

      });
}
