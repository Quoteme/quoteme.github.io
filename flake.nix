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
        # scaffold a new blog post under posts/<slug>/index.qmd, prefilled
        # with today's date (quarto itself has no "new post" prompt, only
        # `quarto create` for whole projects/extensions)
        newPost = pkgs.writeShellApplication {
          name = "new-post";
          runtimeInputs = with pkgs; [
            coreutils
            gnused
          ];
          text = /* bash */ ''
            title="''${*:-}"
            if [ -z "$title" ]; then
              read -rp "Post title: " title
            fi
            if [ -z "$title" ]; then
              echo "Aborting: no title given." >&2
              exit 1
            fi

            slug=$(echo "$title" \
              | tr '[:upper:]' '[:lower:]' \
              | sed -E 's/[^a-z0-9]+/-/g; s/^-+|-+$//g')
            if [ -z "$slug" ]; then
              echo "Aborting: title produced an empty slug." >&2
              exit 1
            fi

            post_dir="posts/$slug"
            if [ -e "$post_dir" ]; then
              echo "Aborting: $post_dir already exists." >&2
              exit 1
            fi

            date=$(date +%Y-%m-%d)
            mkdir -p "$post_dir"
            cat > "$post_dir/index.qmd" <<EOF
---
title: "$title"
author: "Luca Leon Happel"
date: "$date"
categories: []
draft: true
---

EOF

            echo "Created $post_dir/index.qmd"
          '';
        };
        dependencies = with pkgs; [
          quarto
          git
          elan
          newPost
          # lean4
          # (python3.withPackages pythonPackages)
          uv
          (haskellPackages.ghcWithPackages (
            p: with p; [
              ihaskell
              ihaskell-magic
              ihaskell-basic
              ihaskell-hatex
              # no external packages so far...
            ]
          ))
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
              # if "lean4" is missing from the output of `jupyter kernelspec
              # list`, add it
              jupyter kernelspec list | grep -q "lean4" \
                || {
                  echo "installing Lean4 kernel" ;
                  uv run python -m lean4_jupyter.install --sys-prefix
                }
              jupyter kernelspec list | grep -q "ihaskell" \
                || { 
                  echo "installing Haskell kernel" ;
                  ihaskell install --ghclib="$(ghc --print-libdir)" --prefix=".venv/";
                }
              [ -d ".lean4_jupyter/repl" ] || {
                echo "Installing lean4 repl";
                mkdir -p .lean4_jupyter;
                git clone https://github.com/leanprover-community/repl .lean4_jupyter/repl;
                (cd .lean4_jupyter/repl && git checkout adbbfcb9d4e61c12db96c45d227de92f21cc17dd && lake build);
              }
              # add .lean4_jupyter/repl/.lake/build/bin/repl  to PATH (from cwdA)
              export PATH="$PATH:$(pwd)/.lean4_jupyter/repl/.lake/build/bin"
              # trap deactivate EXIT
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
