#!/usr/bin/env zsh

export VICE_SRC_SVN="$HOME/src/other/vice-emu-sourceforge-svn/vice-emu-code/vice"
export VICE_SRC_GH="$HOME/src/other/github.com/drfiemost/vice-emu/"

pushd "$VICE_SRC_SVN" || exit
mkdir -p install

# gtk ui
./autogen.sh && ./configure --enable-debug --prefix=$(pwd)/install && make && make install

# sdl2 ui
# ./autogen.sh && ./configure --enable-sdl2ui --enable-debug --prefix="$(pwd)/install" && make -j 8 && make install



popd