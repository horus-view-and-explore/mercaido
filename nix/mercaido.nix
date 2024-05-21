# SPDX-FileCopyrightText: 2023, 2024 Horus View and Explore B.V.
#
# SPDX-License-Identifier: MIT

{ inputs, ... }:
{
  perSystem =
    { self', pkgs, ... }:
    let
      poetry2nix = inputs.poetry2nix.lib.mkPoetry2Nix { inherit pkgs; };
      python-overrides = [
        poetry2nix.defaultPoetryOverrides
        (
          final: prev:
          let
            addNativeBuildInputs =
              name: nativeBuildInputs:
              prev.${name}.overridePythonAttrs (
                old: {
                  nativeBuildInputs =
                    (builtins.map (x: prev.${x}) nativeBuildInputs) ++ (old.nativeBuildInputs or [ ]);
                }
              );
            mkOverrides = pkgs.lib.attrsets.mapAttrs (name: value: addNativeBuildInputs name value);
          in
          mkOverrides {
            beautifulsoup4 = [ "hatchling" ];
            protobuf-init = [ "poetry" ];
            pymap3d = [ "setuptools" ];
            types-pika = [ "setuptools" ];
            horus-media-client = [ "setuptools" ];
            proquint = [ "setuptools" ];
          }
          // {
            ruff = null;
          }
        )
      ];
    in
    {
      packages = {
        mercaido-server = poetry2nix.mkPoetryApplication {
          projectDir = ./../mercaido_server;
          python = pkgs.python3;
          overrides = python-overrides;
        };
        mercaido-client = poetry2nix.mkPoetryApplication {
          projectDir = ./../mercaido_client;
          python = pkgs.python3;
          overrides = python-overrides;
        };
      };

      devShells.mercaido =
        with pkgs;
        let
          mercaido-server-env = poetry2nix.mkPoetryEnv {
            projectDir = ./../mercaido_server;
            python = python3;
            overrides = python-overrides;
          };
          mercaido-client-env = poetry2nix.mkPoetryEnv {
            projectDir = ./../mercaido_client;
            python = python3;
            overrides = python-overrides;
          };
          mercaido-dummy-service-env = poetry2nix.mkPoetryEnv {
            projectDir = ./../examples/mercaido_dummy_service;
            python = python3;
            overrides = python-overrides;
          };

          d2LibPath = lib.makeLibraryPath (with pkgs; [ expat ]);

          d2-wrapper = pkgs.writeShellScriptBin "d2" ''
            export LD_LIBRARY_PATH=${d2LibPath}:''${LD_LIBRARY_PATH}

            ${pkgs.d2}/bin/d2 $@
          '';
        in
        mkShell {
          name = "mercaido";
          packages = [
            mercaido-server-env
            mercaido-client-env
            mercaido-dummy-service-env

            buf
            cookiecutter
            d2-wrapper
            just
            nodejs
            nodePackages.prettier
            nodePackages.typescript-language-server
            nodePackages.vscode-html-languageserver-bin
            nodePackages.vscode-css-languageserver-bin
            nodePackages.yaml-language-server
            mypy
            poetry
            postgresql
            protobuf
            python3Packages.python-lsp-server
            python3Packages.python-lsp-ruff
            python3Packages.python-lsp-black
            ruff
            sqlite-interactive
            taplo
          ];
        };
    };
}
