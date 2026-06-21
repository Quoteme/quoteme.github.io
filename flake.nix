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
              quarto =
                (super.quarto.override {
                  extraPythonPackages = pythonPackages;
                }).overrideAttrs
                  (oldAttrs: {
                    postPatch = (oldAttrs.postPatch or "") + ''
                      substituteInPlace bin/quarto.js \
                        --replace-fail "syntax-highlighting" "highlight-style"
                    '';
                  });
            })
          ];
        };
        dependencies = with pkgs; [
          quarto
          git
          elan
          # lean4
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
              # if "lean4" is missing from the output of `jupyter kernelspec
              # list`, add it
              if [! jupyter kernelspec list | grep -q "lean4"]; then
                echo "Adding lean4 kernel to Jupyter"
                uv run python -m lean4_jupyter.install
              fi
              # check if `/.lean4_jupyter/repl` exists
              if [ ! -f "$HOME/.lean4_jupyter/repl" ]; then
                echo "Installing lean4 repl"
                mkdir -p .lean4_jupyter
                git clone https://github.com/leanprover-community/repl .lean4_jupyter/repl
                cd .lean4_jupyter/repl
                git checkout adbbfcb9d4e61c12db96c45d227de92f21cc17dd
                lake build
                cd ../..
              fi
              # add .lean4_jupyter/repl/.lake/build/bin/repl  to PATH (from cwdA)
              export PATH="$PATH:$(pwd)/.lean4_jupyter/repl/.lake/build/bin"
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
