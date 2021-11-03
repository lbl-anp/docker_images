# docker_images

General use docker images containing commonly used OSS used within ANP.
Building, tagging and pushing are performed with the `maker.py` script which
requires `python>=3.6` and `docker-py` (`pip3 install docker`).

```bash
./maker.py ros_base --rebuild --push --allow_cross_platform --multiprocess
```

Or build multiple images in parallel:

```bash
./maker.py -xpm ros_board ros_viz cv_camera potree_converter
```

See `maker.py --help` for more details:

```txt
usage: maker.py [-h] [-x] [-r] [-p] [-m]
                {ros_viz,cartographer,ros_board,potree_converter,ros_base,cv_camera} [{ros_viz,cartographer,ros_board,potree_converter,ros_base,cv_camera} ...]

Utility for building/tagging/pushing docker images.

positional arguments:
  {ros_viz,cartographer,ros_board,potree_converter,ros_base,cv_camera}
                        Docker image name(s). The available options are listed above.

optional arguments:
  -h, --help            show this help message and exit
  -x, --allow_cross_platform
                        Allow cross platform (x86 vs aarch64) building.
  -r, --rebuild         Rebuild with --no-cache option
  -p, --push            Run docker push on the latest tag
  -m, --multiprocess    Run each image workflow in a separate process.
```
