{
  description = "my project description";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixpkgs-unstable";
    flake-utils = {
      inputs.nixpkgs.follows = "nixpkgs";
      url = "github:numtide/flake-utils";
    };
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs {
          inherit system;
          config.allowUnfree = true;
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
      in
      {
        devShells.default = pkgs.mkShell {
          buildInputs = jekylldeps ++ jekyllextensions;
          shellHook = builtins.readFile ./bin/shellHook.sh;
        };
      }
    );
}
