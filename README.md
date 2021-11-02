# docker_images

General use docker images containing commonly used OSS used within ANP.
Building, tagging and pushing are performed with the `maker.py` script which
requires `python>=3.6` and `docker-py` (`pip3 install docker`).

```bash
./maker.py ros_base --rebuild --push --allow_cross_platform
```

See `maker.py --help` for more details.
