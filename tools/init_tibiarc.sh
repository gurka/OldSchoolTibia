#!/bin/bash
set -e

if [ -d tibiarc ]; then
    echo "tibiarc/ already exist, delete it first to re-init"
    exit 1
fi

mkdir -p tibiarc
pushd tibiarc

git clone https://github.com/tibiacast/tibiarc.git
pushd tibiarc
mkdir -p build
pushd build
cmake .. -DBUILD_SHARED_LIBS=ON
cmake --build . -t tibiarc
cp libtibiarc.so ../../
popd
popd

python3 -m venv venv
source venv/bin/activate
pip install ctypesgen
ctypesgen -llibtibiarc.so tibiarc/lib/*.h -o tibiarclib.py
touch __init__.py
mkdir clients

deactivate
rm -rf venv
rm -rf tibiarc

echo
echo
echo "Done!"
echo "Now, add directories and data files for all Tibia versions that you want to use"
echo "Example:"
echo "  tibiarc/clients/7.11/Tibia.dat"
echo "  tibiarc/clients/7.11/Tibia.spr"
echo "  tibiarc/clients/7.11/Tibia.pic"
echo "  tibiarc/clients/7.21/Tibia.dat"
echo "[...]"
echo
echo
