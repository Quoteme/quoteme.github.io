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
        pythonPackages = ps: with ps; [ plotly numpy pandas matplotlib ];
        pkgs = import nixpkgs {
          inherit system;
          config.allowUnfree = true;
          overlays = [
            (self: super: {
              quarto = super.quarto.override {
                extraRPackages = [ ];
                extraPythonPackages = pythonPackages;
              };
            })
          ];
        };
        dependencies = with pkgs; [
          quarto
          git
          (python3.withPackages pythonPackages)
        ];
      in {
        # default shell 
        devShells.default = with pkgs;
          mkShell {
            name = "blog-shell";
            buildInputs = dependencies;
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
