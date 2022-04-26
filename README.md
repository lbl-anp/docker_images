# docker_images

General use docker images containing commonly used OSS used within ANP.
Building, tagging and pushing are performed using the `parallel-docker-build`
package (`pip3 install parallel-docker-build`) which requires `python>=3.6` and
`docker-py`. The included workflow file first builds the `ros_base` images
before moving onto the others. These builds are run in parallel (see the workflow
file for the number of concurrent processes) and will attempt to build
cross-platform images (i.e. the ARM images on x86). In order to build run:

```bash
cd images
pip3 install parallel_docker_build
parallel-docker-build workflow workflow.yaml
```

See the command for more options: `parallel-docker-build -h`.
