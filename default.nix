let
    pkgs = (import (builtins.fetchGit {
        url = "git@github.com:NixOS/nixpkgs.git";
        ref = "nixos-21.11";
        rev = "a7ecde854aee5c4c7cd6177f54a99d2c1ff28a31";
    }) { });
    stdenv = pkgs.stdenv;
in pkgs.mkShell rec {
    name = "interview";
    shellHook = ''
        source .bashrc
    '';
    buildInputs = (with pkgs; [
        bashInteractive
        (pkgs.python3.buildEnv.override {
            ignoreCollisions = true;
            extraLibs = with pkgs.python3.pkgs; [
                ipython
                nose
            ];
        })
    ]);
}
