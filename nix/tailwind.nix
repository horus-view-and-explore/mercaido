# SPDX-FileCopyrightText: 2023, 2024 Horus View and Explore B.V.
#
# SPDX-License-Identifier: MIT

{
  perSystem = { self', pkgs, system, ... }: {
    packages.tailwindcss =
      let
        version = "3.3.2";
        systemSuffix = {
          "x86_64-linux" = "linux-x64";
        };
      in
      pkgs.stdenv.mkDerivation {
        inherit version;
        pname = "tailwindcss";

        src = builtins.fetchurl {
          url = "https://github.com/tailwindlabs/tailwindcss/releases/download/v${version}/tailwindcss-${systemSuffix.${system}}";
          sha256 = "0r4zi1wj8lbgak3hxjlab0gvanb8lidxpwishjh3h3893q253ljv";
        };

        dontUnpack = true;
        dontPatch = true;
        dontConfigure = true;
        dontBuild = true;
        dontFixup = true;

        installPhase = ''
          install -Dm0755 $src $out/bin/tailwindcss
        '';
      };
  };
}
