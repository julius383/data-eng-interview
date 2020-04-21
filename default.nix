let pkgs = (import <nixpkgs> {}); in
let stdenv = pkgs.stdenv; in
pkgs.mkShell rec {
    name = "interview";
    shellHook = ''
        source .bashrc
    '';
    buildInputs = (with pkgs; [
        bashInteractive
        (pkgs.python38.buildEnv.override {
            ignoreCollisions = true;
            extraLibs = with pkgs.python38.pkgs; [
                ipython
                nose
            ];
        })
    ]);
}
