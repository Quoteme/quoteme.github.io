{
  description = "My github pages blog";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixpkgs-unstable";
    flake-utils = {
      inputs.nixpkgs.follows = "nixpkgs";
      url = "github:numtide/flake-utils";
    };
    nix-vscode-extensions.url = "github:nix-community/nix-vscode-extensions";
  };

  outputs = { self, nixpkgs, flake-utils, ... }@inputs:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs {
          inherit system;
          config.allowUnfree = true;
          overlays = [
            inputs.nix-vscode-extensions.overlays.default
            (self: super: {
              quarto = super.quarto.override {
                extraRPackages = [ ];
                extraPythonPackages = ps: with ps; [
                  plotly
                  numpy
                  pandas
                  matplotlib
                ];
              };
            })
          ];
        };
        dependencies = with pkgs; [
          quarto
        ];
      in
      {
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

      }
    );
}
