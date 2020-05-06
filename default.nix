let pkgs = (import <nixpkgs> {}); in
let stdenv = pkgs.stdenv; in
pkgs.mkShell rec {
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
