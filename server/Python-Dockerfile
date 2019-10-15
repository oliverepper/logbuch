# build
FROM buildpack-deps:bionic as build-python
LABEL maintainer="Oliver Epper <oliver.epper@gmail.com>"

ENV LANG C.UTF-8

RUN apt-get update && apt-get -y upgrade

ENV GPG_KEY E3FF2839C048B25C084DEBE9B26995E310250568
ENV PYTHON_VERSION 3.8.0
ENV PREFIX /opt/python

RUN set -ex \
    \
    && wget -O python.tar.xz https://www.python.org/ftp/python/${PYTHON_VERSION%%[a-z]*}/Python-$PYTHON_VERSION.tar.xz \
    && wget -O python.tar.xz.asc https://www.python.org/ftp/python/${PYTHON_VERSION%%[a-z]*}/Python-$PYTHON_VERSION.tar.xz.asc \
    && export GNUPGHOME="$(mktemp -d)" \
    # && gpg --batch --keyserver ha.pool.sks-keyservers.net --recv-keys "$GPG_KEY" \
    && gpg --batch --keyserver keyserver.ubuntu.com --recv-keys "$GPG_KEY" \
    && gpg --batch --verify python.tar.xz.asc python.tar.xz \
    && { command -v gpgconf > /dev/null && gpgconf --kill all || :; } \
    && rm -rf $"GNUPGHOME" python.tar.xz.asc \
    && mkdir -p /usr/src/python \
    && tar -xJC /usr/src/python --strip-components=1 -f python.tar.xz \
    && rm python.tar.xz \
    \
    && cd /usr/src/python \
    && gnuArch="$(dpkg-architecture --query DEB_BUILD_GNU_TYPE)" \
    && ./configure \
        --prefix=${PREFIX} \
        --build="$gnuArch" \
        --enable-loadable-sqlite-extensions \
        --enable-optimizations \
        --enable-shared \
        --with-system-expat \
        --with-system-ffi \
        --without-ensurepip \
    && make -j "$(nproc)" \
    && make install

ENV PATH ${PREFIX}/bin:$PATH

RUN set -ex \
    \
    && echo "${PREFIX}/lib" > /etc/ld.so.conf.d/python.conf \
    && ldconfig \
    && find ${PREFIX} -depth \
		\( \
			\( -type d -a \( -name test -o -name tests \) \) \
			-o \
			\( -type f -a \( -name '*.pyc' -o -name '*.pyo' \) \) \
		\) -exec rm -rf '{}' + \
	&& rm -rf /usr/src/python \
	\
	&& python3 --version

RUN cd ${PREFIX}/bin \
	&& ln -s idle3 idle \
	&& ln -s pydoc3 pydoc \
	&& ln -s python3 python \
	&& ln -s python3-config python-config


# production
FROM ubuntu:18.04 as python
LABEL maintainer="Oliver Epper <oliver.epper@gmail.com>"

ENV PYTHON_HOME /opt/python
ENV PATH ${PYTHON_HOME}/bin:$PATH
RUN apt-get update && apt-get -y upgrade \
    && apt-get -y install libexpat1 libssl1.1 libsqlite3-0

COPY --from=build-python ${PYTHON_HOME} ${PYTHON_HOME}

RUN set -ex \
    \
    && echo "${PYTHON_HOME}/lib" > /etc/ld.so.conf.d/python.conf \
    && ldconfig
