{
  description = "My github pages blog";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixpkgs-unstable";
    flake-utils = {
      inputs.nixpkgs.follows = "nixpkgs";
      url = "github:numtide/flake-utils";
    };
  };

  outputs =
    {
      self,
      nixpkgs,
      flake-utils,
      ...
    }@inputs:
    flake-utils.lib.eachDefaultSystem (
      system:
      let
        pythonPackages =
          ps: with ps; [
            plotly
            numpy
            pandas
            matplotlib
            jupyter-cache
            gitpython
            ruff
            mypy
            ipython
            ipykernel
            pip
          ];
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
          # (python3.withPackages pythonPackages)
          uv
        ];
      in
      {
        # default shell
        devShells.default =
          with pkgs;
          mkShell {
            name = "blog-shell";
            QUARTO_PYTHON = "./.venv/bin/python";
            buildInputs = dependencies;
            shellHook = /* bash */ ''
              #!/usr/bin/env bash
              # check if this shell hook has been run before
              if [ -z "$RAN_SHELL_HOOK_BASIC" ]; then
                export RAN_SHELL_HOOK_BASIC=1
              else
                return
              fi
              ${pkgs.onefetch}/bin/onefetch
              uv sync
              source .venv/bin/activate
              trap deactivate EXIT
            '';
          };

        # build quarto blog
        # packages.default = pkgs.stdenv.mkDerivation {
        #   name = "build-blog";
        #   src = ./.;
        #   buildInputs = dependencies;
        #   QUARTO_PYTHON = "./.venv/bin/python";
        #   buildPhase = ''
        #     quarto render
        #   '';
        #   installPhase = ''
        #     mkdir -p $out
        #     cp -r _site/* $out/
        #   '';
        # };

      }
    );
}
