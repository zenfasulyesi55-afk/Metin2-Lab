#!/usr/bin/env bash
set -euo pipefail

rm -rf client-src /tmp/m2dev-server-src /tmp/m2dev-server /tmp/m2dev-client \
       /tmp/m2stage /tmp/m2pylib /tmp/m2serverpack /tmp/m2bundle

       git clone --depth 1 https://github.com/cemreefe/metin2-android.git client-src
       git -C client-src submodule update --init --recursive || true

       git clone https://github.com/d1str4ught/m2dev-server-src.git /tmp/m2dev-server-src
       git -C /tmp/m2dev-server-src checkout 66068c1

       git clone https://github.com/d1str4ught/m2dev-server.git /tmp/m2dev-server
       git -C /tmp/m2dev-server checkout ad30738

       git clone https://github.com/d1str4ught/m2dev-client.git /tmp/m2dev-client
       git -C /tmp/m2dev-client checkout 98d2c1af

       curl -sL https://www.python.org/ftp/python/2.7.18/Python-2.7.18.tgz -o /tmp/py27.tgz
       mkdir -p /tmp/m2pylib
       tar xzf /tmp/py27.tgz -C /tmp
       cp -r /tmp/Python-2.7.18/Lib/. /tmp/m2pylib/
       rm -rf /tmp/m2pylib/test /tmp/m2pylib/lib-tk /tmp/m2pylib/idlelib \
              /tmp/m2pylib/lib2to3 /tmp/m2pylib/ensurepip /tmp/m2pylib/bsddb \
                     /tmp/m2pylib/msilib /tmp/m2pylib/distutils /tmp/m2pylib/curses \
                            /tmp/m2pylib/pydoc_data /tmp/m2pylib/wsgiref.egg-info \
                                   /tmp/m2pylib/site-packages /tmp/m2pylib/unittest \
                                          /tmp/m2pylib/plat-* /tmp/Python-2.7.18 /tmp/py27.tgz

                                          chmod +x \
                                            "client-src/r10dev.net OPENGL-ITJA/server/tools/make-server-pack.sh" \
                                              "client-src/r10dev.net OPENGL-ITJA/android/tools/stage_client_data.sh" \
                                                "client-src/r10dev.net OPENGL-ITJA/android/tools/make_bundle.sh" \
                                                  "client-src/r10dev.net OPENGL-ITJA/android/tools/make_icon.sh"

                                                  "client-src/r10dev.net OPENGL-ITJA/server/tools/make-server-pack.sh" \
                                                    /tmp/m2dev-server /tmp/m2dev-server-src /tmp/m2serverpack

                                                    "client-src/r10dev.net OPENGL-ITJA/android/tools/stage_client_data.sh" \
                                                      /tmp/m2dev-client /tmp/m2stage en

                                                      rm -rf /tmp/m2dev-client /tmp/m2dev-server
                                                      