{ pkgs ? import <nixpkgs> { } }: with pkgs;
# Based on ideas from Matthew Rhone
# https://matthewrhone.dev/jekyll-in-nixos
let env = bundlerEnv {
  name = "your-package";
  inherit ruby;
  gemfile = ./Gemfile;
  lockfile = ./Gemfile.lock;
  gemset = ./gemset.nix;
};
in
stdenv.mkDerivation rec {
  version = "0.1";
  pname = "quoteme.github.io";
  src = ./.;
  buildInputs = with pkgs; [
    env
    bundler
    ruby
    (writeShellScriptBin
      "gojekyll"
      ''
        exec ${env}/bin/jekyll serve --watch --livereload
      '')
  ];
  # buildPhase = "ghc --make xmonadctl.hs";
  # installPhase = ''
  #   mkdir -p $out/bin
  #   cp xmonadctl $out/bin/
  #   chmod +x $out/bin/xmonadctl
  # '';
  shellHook = ''
    echo "Run debug-server with \"gojekyll\""
  '';
  meta = with lib; {
    author = "Luca Leon Happel";
    description = "My github pages website";
    homepage = "https://github.com/Quoteme/quoteme.github.io";
    platforms = platforms.all;
    mainProgram = "quoteme.github.io";
  };
}
