FROM node:bullseye

RUN mkdir /work && mkdir /work/potree_demo && mkdir /data
WORKDIR /work
COPY . potree_demo

RUN apt-get update && \
    apt-get update &&\
    apt-get install -yq \
        build-essential \
        cmake \
        gcc \
        g++ \
        libtbb-dev \
        git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/potree/PotreeConverter.git potreeconverter && \
    cd potreeconverter && \
    git checkout 2.1 && \
    mkdir -p build && \
    cd build && \
    cmake -DTBB_DIR=/usr/include/tbb/ -DCMAKE_PREFIX_PATH=/usr/share/cmake/Modules/FindTBB.cmake .. && \
    make

RUN git clone https://github.com/potree/potree.git potree && \
    cd potree && \
    git checkout 1.8 && \
    npm install --save && \
    npm install gulp rollup

CMD ["/work/potreeconverter/build/PotreeConverter/PotreeConverter"]
