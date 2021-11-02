#!/usr/bin/env python3
# Author: Joey Curtis @jccurtis
import argparse
import subprocess
import shlex
import platform
from pathlib import Path
import logging

logging.basicConfig(
    level=logging.INFO, format="[%(asctime)s|%(levelname)-4s] %(message)s"
)
DOCKER_NAMESPACE = "lblanp"
PARENT_DIR = Path(__file__).parent


def build(dockerfile: Path, rebuild: bool = False) -> str:
    # Handle tags / arch
    extra_tags = [s.lstrip(".") for s in dockerfile.suffixes]
    for t in extra_tags:
        if t != t.lower():
            raise ValueError(
                f"Dockerfile suffix tags must all be lowercase: {dockerfile}"
            )
    image_arch = "x86_64"
    if "l4t" in extra_tags:
        logging.info(f"Found Linux 4 Tegra tag in {dockerfile}")
        image_arch = "aarch64"
    if "arm64v8" in extra_tags:
        logging.info(f"Found ARM64v8 tag in {dockerfile}")
        image_arch = "aarch64"
    if image_arch != platform.machine():
        logging.warning(
            f"Cannot currently build across platforms (this={platform.machine()} "
            f"vs requested={image_arch}) Skipping: {dockerfile}"
        )
        return
    full_name = f"{DOCKER_NAMESPACE}/{dockerfile.parent.stem}"
    if len(extra_tags):
        full_name += "_" + "_".join(extra_tags)
    # Prepare cmd
    cmd = (
        f"cd {dockerfile.parent} && "
        f"docker build -t {full_name}:latest -f {dockerfile.name} "
        f"{'--no-cache ' if rebuild else ''}"
        "."
    )
    logging.info(f"Building: {cmd}")
    subprocess.Popen(shlex.split(cmd), shell=True).wait()
    return full_name


def push(full_name: str, tags: list) -> None:
    for tag in tags:
        cmd = f"docker push {full_name}:{tag}"
        logging.info(f"Pushing: {cmd}")
        subprocess.Popen(shlex.split(cmd), shell=True).wait()


def main(name: str, push: bool = False, rebuild: bool = False) -> None:
    directory = Path(PARENT_DIR / name)
    # Get dockerfiles
    dfiles = list(directory.glob("Dockerfile*"))
    if len(dfiles) == 0:
        logging.error(f"No `Dockerfile*`s found: {directory}")
        return
    # Build images
    for dfile in dfiles:
        full_name = build(dfile, rebuild=rebuild)
        if push:
            push(full_name, tags=["latest"])


def cli():
    # Get neighboring directories
    neighbors = list(p.name for p in PARENT_DIR.iterdir() if p.is_dir())
    # Command line handling
    parser = argparse.ArgumentParser(
        description="Utility for building/tagging/pushing docker images"
    )
    parser.add_argument(
        "name",
        type=str,
        help="Docker image name",
        choices=neighbors,
    )
    parser.add_argument(
        "-r",
        "--rebuild",
        action="store_true",
        help="Rebuild with --no-cache option",
    )
    parser.add_argument(
        "-p",
        "--push",
        action="store_true",
        help="Run docker push on the latest tag",
    )
    args = parser.parse_args()
    main(**vars(args))


if __name__ == "__main__":
    cli()
