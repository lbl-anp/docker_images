#!/bin/zsh

docker run -v ${INPUT:h}:/data -it --rm lblanp/$(basename $(dirname ${0:A})):latest \
    /work/potreeconverter/build/PotreeConverter/PotreeConverter \
        /data/${INPUT:t} \
        -o /data/${INPUT:t:r} \
        -p potree_viz \
        --edl-enabled \
        --overwrite
