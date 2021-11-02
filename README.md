# docker_images

General use docker images containing commonly used OSS used within ANP.
Building, tagging and pushing are performed with the `maker.py` script which
requires `python>=3.6` (stdlib only) and `docker`. For example

```bash
./maker.py ros_base --rebuild --push
```

See `maker.py --help` for more details.
