#! /bin/bash

# Ugly script to vuild graphviz and some dependencies. Use this to get
# a custom-built set of graphviz binaries in ~/gvbuild/usr/bin. If you
# read this thing, be careful you don't go blind from how bad it is.



EXPAT=expat-2.1.0
EXPAT_URL=https://s3-us-west-1.amazonaws.com/cjeffers-graphviz/$EXPAT.tar.gz
EXPAT_CONF_OPTS='--prefix=/app/exbuild/usr'

cd
mkdir exbuild
cd exbuild
mkdir usr
curl -O $EXPAT_URL
tar xzf $EXPAT.tar.gz
cd $EXPAT
./configure $EXPAT_CONF_OPTS
make
make install
export PKG_CONFIG_PATH=$PKG_CONFIG_PATH:/app/exbuild/$EXPAT



FONTCONFIG=fontconfig-2.10.93
FONTCONFIG_URL=http://www.freedesktop.org/software/fontconfig/release/$FONTCONFIG.tar.bz2
FONTCONFIG_CONF_OPTS='--prefix=/app/fcbuild/usr --sysconfdir=/app/fcbuild/etc --localstatedir=/app/fcbuild/var --disable-docs'

cd
mkdir fcbuild
cd fcbuild
mkdir var
mkdir etc
mkdir -p usr/share
cp -r /usr/share/fonts usr/share
curl -O $FONTCONFIG_URL
tar xjf $FONTCONFIG.tar.bz2
cd $FONTCONFIG
./configure $FONTCONFIG_CONF_OPTS
make
make install
export PKG_CONFIG_PATH=$PKG_CONFIG_PATH:/app/fcbuild/$FONTCONFIG



GRAPHVIZ=graphviz-2.26.3
GRAPHVIZ_URL=http://www.graphviz.org/pub/graphviz/stable/SOURCES/$GRAPHVIZ.tar.gz
GRAPHVIZ_CONF_OPTS='--prefix=/app/gvbuild/usr --enable-static --enable-fontconfig'

cd
mkdir gvbuild
cd gvbuild
mkdir usr
curl -O $GRAPHVIZ_URL
tar xzf $GRAPHVIZ.tar.gz
cd $GRAPHVIZ
./configure $GRAPHVIZ_CONF_OPTS
make
make install
