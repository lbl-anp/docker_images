FROM node:buster

RUN mkdir /work && mkdir /work/potree_demo && mkdir /data
WORKDIR /work
COPY . potree_demo

RUN apt-get update && \
    # apt-get install -yq software-properties-common && \
    # add-apt-repository ppa:ubuntu-toolchain-r/test && \
    apt-get update &&\
    apt-get install -yq \
        build-essential \
        cmake \
        gcc \
        g++ \
        # gcc-9 \
        # g++-9 \
        git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/m-schuetz/LAStools.git lastools && \
    cd lastools/LASzip && \
    git checkout master && \
    mkdir -p build && \
    cd build && \
    cmake -DCMAKE_BUILD_TYPE=Release .. && \
    make

RUN git clone https://github.com/potree/PotreeConverter.git potreeconverter && \
    cd potreeconverter && \
    git checkout 1.6_2018_07_29 && \
    mkdir -p build && \
    cd build && \
    cmake -DCMAKE_BUILD_TYPE=Release -DLASZIP_INCLUDE_DIRS=/work/lastools/LASzip/dll -DLASZIP_LIBRARY=/work/lastools/LASzip/build/src/liblaszip.so .. && \
    make && \
    # https://github.com/potree/PotreeConverter/issues/314
    cp -r ../PotreeConverter/resources ./PotreeConverter

RUN git clone https://github.com/potree/potree.git potree && \
    cd potree && \
    git checkout develop && \
    npm install --save && \
    npm install gulp rollup

CMD ["/work/potreeconverter/build/PotreeConverter/PotreeConverter"]
