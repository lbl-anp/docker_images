# potree_converter

[`PotreeConverter`](https://github.com/potree/PotreeConverter) provides a utility to convert point cloud files (like `ply`) into a static/portable webpage with all assets alongside. On [docker hub](https://hub.docker.com/repository/docker/lblanp/potree_converter).

```bash
docker pull lblanp/potree_converter
```

## Run it

For a point cloud file with path: `/data/dir/cloud.ply`:

```bash
docker run -v "/data/dir":/data:rw -it --rm lblanp/potree_converter:latest \
    /work/potreeconverter/build/PotreeConverter/PotreeConverter \
        /data/"cloud.ply" \
        -o /data/"cloud" \
        -p potree_viz \
        --edl-enabled \
        --overwrite
```

A convenience script (requires `zshell`) is included here (not in the image) which takes an `INPUT` point cloud filename and then completes all the paths in the above command:

```bash
INPUT="path/to/point/cloud.ply" ./run_it.zsh
```

## CORS

Turn off cross origin restrictions so local files can be loaded in the web browser in [firefox and chrome](http://testingfreak.com/how-to-fix-cross-origin-request-security-cors-error-in-firefox-chrome-and-ie/).
