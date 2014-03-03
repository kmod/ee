# Taken from http://clalance.blogspot.com/2014/01/developing-stm32-microcontroller-code.html

set -eu
set -x

sudo apt-get install texinfo libusb-dev libusb-1.0-0-dev

export TOPDIR=~/cross-src
export TARGET=arm-none-eabi
export PREFIX=~/arm-cross
export BUILDPROCS=$( getconf _NPROCESSORS_ONLN )
# export BUILDPROCS=2
export PATH=$PREFIX/bin:$PATH

mkdir -p $TOPDIR
cd $TOPDIR
wget --continue ftp://ftp.gnu.org/gnu/binutils/binutils-2.24.tar.gz &
wget --continue ftp://ftp.gnu.org/gnu/gcc/gcc-4.8.2/gcc-4.8.2.tar.bz2 &
wget --continue ftp://sources.redhat.com/pub/newlib/newlib-2.0.0.tar.gz &
wget --continue ftp://ftp.gnu.org/gnu/gdb/gdb-7.6.tar.gz &
wget --continue http://downloads.sourceforge.net/project/openocd/openocd/0.7.0/openocd-0.7.0.tar.gz &
wait
git clone git://github.com/libopencm3/libopencm3.git

cd $TOPDIR
tar -xvf binutils-2.24.tar.gz
mkdir build-binutils
cd build-binutils
../binutils-2.24/configure --target=$TARGET --prefix=$PREFIX --enable-interwork --disable-nls
make -j$BUILDPROCS
make install

cd $TOPDIR
tar -xvf newlib-2.0.0.tar.gz
tar -xvf gcc-4.8.2.tar.bz2
mkdir build-gcc
cd build-gcc
../gcc-4.8.2/configure --target=$TARGET --prefix=$PREFIX --enable-interwork --disable-nls --enable-languages="c,c++" --without-headers --with-newlib --with-headers=$TOPDIR/newlib-2.0.0/newlib/libc/include
make -j$BUILDPROCS all-gcc
make install-gcc

cd $TOPDIR
mkdir -p build-newlib
cd build-newlib
../newlib-2.0.0/configure --target=$TARGET --prefix=$PREFIX --enable-interwork
make -j$BUILDPROCS
make install

cd $TOPDIR/build-gcc
make -j$BUILDPROCS
make install

cd $TOPDIR
tar -xvf gdb-7.6.tar.gz
mkdir build-gdb
cd build-gdb
../gdb-7.6/configure --target=$TARGET --prefix=$PREFIX --enable-interwork
make -j$BUILDPROCS
make install

cd $TOPDIR
tar -xvf openocd-0.7.0.tar.gz
cd openocd-0.7.0
./configure --enable-stlink --prefix=$PREFIX
make
make install

cd $TOPDIR
cd libopencm3
git checkout -b clalancette-tutorial a909b5ca9e18f802e3caef19e63d38861662c128
unset PREFIX
make DETECT_TOOLCHAIN=1
make DETECT_TOOLCHAIN=1 install
export PREFIX=~/arm-cross
