FROM alpine:3.9

COPY requirements_core.txt /requirements_core.txt

RUN apk add --no-cache python3 && \
    python3 -m ensurepip && \
    rm -r /usr/lib/python*/ensurepip && \
    pip3 install --upgrade pip setuptools && \
    if [ ! -e /usr/bin/pip ]; then ln -s pip3 /usr/bin/pip ; fi && \
    if [[ ! -e /usr/bin/python ]]; then ln -sf /usr/bin/python3 /usr/bin/python; fi && \
    rm -r /root/.cache

RUN apk add --no-cache \
        --virtual=.build-dependencies \
        g++ gfortran file binutils \
        musl-dev python3-dev openblas-dev && \
        apk add libstdc++ openblas && \
        ln -s locale.h /usr/include/xlocale.h && \
        pip install -r /requirements_core.txt && \
        rm -r /root/.cache && \
        find /usr/lib/python3.*/ -name 'tests' -exec rm -r '{}' + && \
        find /usr/lib/python3.*/site-packages/ -name '*.so' -print -exec sh -c 'file "{}" | grep -q "not stripped" && strip -s "{}"' \; && \
        \
        rm /usr/include/xlocale.h && \
        \
        apk del .build-dependencies

RUN cd /tmp && \
    apk add --no-cache \
        --virtual=.build-dependencies \
        gcc make file binutils \
        musl-dev python3-dev gmp-dev suitesparse-dev openblas-dev && \
    apk add gmp suitesparse && \
    \
    pip install cython && \
    pip install pycddlib && \
    pip uninstall --yes cython && \
    \
    wget "ftp://ftp.gnu.org/gnu/glpk/glpk-4.65.tar.gz" && \
    tar xzf "glpk-4.65.tar.gz" && \
    cd "glpk-4.65" && \
    ./configure --disable-static && \
    make -j4 && \
    make install-strip && \
    CVXOPT_BLAS_LIB=openblas CVXOPT_LAPACK_LIB=openblas CVXOPT_BUILD_GLPK=1 pip install --global-option=build_ext --global-option="-I/usr/include/suitesparse" cvxopt && \
    \
    rm -r /root/.cache && \
    find /usr/lib/python3.*/site-packages/ -name '*.so' -print -exec sh -c 'file "{}" | grep -q "not stripped" && strip -s "{}"' \; && \
    \
    apk del .build-dependencies && \
    rm -rf /tmp/*

RUN pip -V
RUN python -V
COPY requirements_app.txt /requirements_app.txt
RUN pip install -r /requirements_app.txt
COPY app.py /app/app.py
WORKDIR /app
EXPOSE 5000
CMD ["flask", "run", "--host=0.0.0.0"]
