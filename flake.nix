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
        quarto1_4overlay = final: prev: {
          # change the version and source of the quarto package
          quarto =
            let
              ver = "1.4.550";
            in
            prev.quarto.overrideAttrs (old: {
              version = ver;
              src = (builtins.fetchurl {
                url = "https://github.com/quarto-dev/quarto-cli/releases/download/v${ver}/quarto-${ver}-linux-amd64.tar.gz";
                sha256 = "sha256:1y2n79l4n4b173d9c9wz0zkc0c5r1fpmbn11d59x81c6jpnxsqbi";
              });
              patches = [ ];
              nativeBuildInputs = prev.quarto.nativeBuildInputs ++ [ pkgs.deno ];
              installPhase = ''
                runHook preInstall
                mkdir -p $out/bin $out/share
                # rm -r bin/tools
                mv bin/* $out/bin
                mv share/* $out/share

                # instead of deleting the shipped deno binary,
                # we replace it by nix's deno
                rm $out/bin/tools/x86_64/deno
                ln -s ${pkgs.deno}/bin/deno $out/bin/tools/x86_64/deno
                runHook postInstall
              '';
            });
        };
        pygments2_18overlay = final: prev: {
          # change the version and source of the pygments package
          python312Packages.pygments = prev.python312Packages.pygments.overridePythonAttrs (old: {
            src = (pkgs.fetchFromGitHub {
              owner = "pygments";
              repo = "pygments";
              rev = "26ffe8f472d18ed190a5ced00335682c618037d4";
              sha256 = "sha256-dbV7qLsSh88RKBbg1CI8OooSfsWZF7HVjAiIEj9pTMo="; # TODO
            });
            # propagatedBuildInputs = prev.python312Packages.pygments.propagatedBuildInputs ++ [ prev.python312Packages.pandocfilters ];
            # buildInputs = prev.python312Packages.pygments.buildInputs ++ [ prev.python312Packages.pandocfilters ];
            # nativeBuildInputs = prev.python312Packages.pygments.nativeBuildInputs ++ [ prev.python312Packages.pandocfilters ];
          });
        };
        pkgs = import nixpkgs {
          inherit system;
          config.allowUnfree = true;
          overlays = [
            inputs.nix-vscode-extensions.overlays.default
            quarto1_4overlay
            pygments2_18overlay
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
        # default shell 
        devShells.default = pkgs.mkShell {
          name = "blog-shell";
          buildInputs = dependencies;
          shellHook = ''
            export PYGMENTIZE=${pkgs.python312Packages.pygments}/bin/pygmentize
            export PATH=${pkgs.quarto}/bin:${pkgs.python312Packages.pygments}/bin:${pkgs.python312}/bin:$PATH
            export PYTHONPATH=${pkgs.python312Packages.pygments}/lib/python3.12/site-packages:${pkgs.python311Packages.pandocfilters}/lib/python3.11/site-packages
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

      }
    );
}
