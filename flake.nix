{
  description = "my project description";

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
          ];
        };
        env = (pkgs.bundlerEnv
          {
            name = "your-package";
            rupy = pkgs.ruby;
            gemfile = ./Gemfile;
            lockfile = ./Gemfile.lock;
            gemset = ./gemset.nix;
          });
        jekylldeps = with pkgs; [
          env
          bundler
          bundix
          pkgs.ruby
        ];
        jekyllextensions = with pkgs; [
          # jekyll extensions
          rubyPackages.webrick
          rubyPackages.jekyll
          rubyPackages.jekyll-watch
          rubyPackages.jekyll-spaceship
        ];
        # ====
        editor = with pkgs; [
          (vscode-with-extensions.override {
            vscode = vscodium;
            vscodeExtensions = with pkgs.vscode-marketplace; [
              # Language packs
              ms-ceintl.vscode-language-pack-de
              vscodevim.vim
              christian-kohler.path-intellisense
              streetsidesoftware.code-spell-checker
              streetsidesoftware.code-spell-checker-german
              adamvoss.vscode-languagetool
              adamvoss.vscode-languagetool-de
              adamvoss.vscode-languagetool-en
              valentjn.vscode-ltex
              # markdown
              # yzhang.markdown-all-in-one
              # R
              tianyishi.rmarkdown
              reditorsupport.r
              rdebugger.r-debugger
              # mikhail-arkhipov.r
              # Copilot
              github.copilot-labs
              github.copilot
              github.remotehub
              github.copilot-chat
              # VIM
              vscodevim.vim
              # NIX
              bbenoist.nix
              jnoortheen.nix-ide
              # Python
              vscode-extensions.ms-python.python
              vscode-extensions.ms-python.vscode-pylance
              ms-python.flake8
              vscode-extensions.matangover.mypy
              charliermarsh.ruff
              ## Quarto
              quarto.quarto
              # latex
              mathematic.vscode-latex
              james-yu.latex-workshop
              # html
              dbaeumer.vscode-eslint
              dbaeumer.jshint
              ecmel.vscode-html-css
              formulahendry.auto-rename-tag
              mgmcdermott.vscode-language-babel
              ms-vscode.vscode-typescript-next
              # R
              reditorsupport.r
              rdebugger.r-debugger
              mikhail-arkhipov.r
              # bash
              rogalmic.bash-debug
              mads-hartmann.bash-ide-vscode
              # other
              donjayamanne.githistory
              usernamehw.errorlens
              jgclark.vscode-todo-highlight
              pkief.material-icon-theme
              eamodio.gitlens
            ];
          })
          R
          rPackages.languageserver
          rPackages.readr
          rPackages.kableExtra
          rPackages.dplyr
          rPackages.ggplot2
          rPackages.magrittr
          rPackages.car
          rPackages.statsr
          rPackages.broom
          rPackages.stargazer
          rPackages.tidyr
          rPackages.gridExtra
          rPackages.ggpubr
          rPackages.cowplot
          rPackages.knitr
          rPackages.ellipse
          texlive.combined.scheme-full
        ];
        shellHook = ''
          #!/usr/bin/env bash

          export AUTHOR="Luca Leon Happel"
          # print the following text in yellow
          echo -e "\033[33mWelcome $AUTHOR\033[0m"
          echo -e 'Run debug-server with "\033[33mblogServe\033[0m", or update using "\033[33mblogUpdate\033[0m"'
          alias blogServe="jekyll serve --watch --livereload --host"
          alias blogUpdate="nix-shell -p bundler -p bundix --run 'bundler update; bundler lock; bundler package --no-install --path vendor; bundix; rm -rf vendor' && exit"


          alias blogNewPost="./bin/newPost.sh"
        '';
      in
      {
        devShells.default = pkgs.mkShell {
          buildInputs = jekylldeps ++ jekyllextensions;
          shellHook = shellHook;
        };

        devShells.editor = pkgs.mkShell {
          buildInputs = editor ++ jekylldeps ++ jekyllextensions;
          shellHook = shellHook;
        };
      }
    );
}
