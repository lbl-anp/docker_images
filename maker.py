#!/usr/bin/env python3
# Author: Joey Curtis @jccurtis
import argparse
import platform
import shutil
import logging
import json
from pathlib import Path
import docker

logging.basicConfig(
    level=logging.INFO, format="[%(asctime)s|%(levelname)-4s] %(message)s"
)
DOCKER_NAMESPACE = "lblanp"
DOCKER_CLIENT = docker.from_env()  # high level
DOCKER_API = docker.APIClient()  # low level
REPO_DIR = Path(__file__).parent
REPO_DOCKERIGNORE = REPO_DIR / ".dockerignore"
IMAGES_DIR = REPO_DIR / "images"


def do_build(
    dockerfile: Path, allow_cross_platform: bool = False, rebuild: bool = False
) -> str:
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
        if allow_cross_platform:
            logging.warning(
                "Attempting to build a cross platform image "
                f"(this={platform.machine()} vs requested={image_arch}): "
                f"{dockerfile}"
            )
        else:
            logging.warning(
                "Cannot build across platforms without `-x` option "
                f"(this={platform.machine()} vs requested={image_arch}): "
                f"Skipping: {dockerfile}"
            )
            return
    full_name = f"{DOCKER_NAMESPACE}/{dockerfile.parent.stem}"
    if len(extra_tags):
        full_name += "_" + "_".join(extra_tags)
    # Determine build context
    dockerignore_path = dockerfile.parent / ".dockerignore"
    if REPO_DOCKERIGNORE.is_file():
        REPO_DOCKERIGNORE.unlink()
    if dockerignore_path.is_file():
        logging.info(f"Found and copying docker ignore: {dockerignore_path}")
        shutil.copy(str(dockerignore_path), str(REPO_DOCKERIGNORE))
        build_path = REPO_DIR
    else:
        build_path = dockerfile.parent
    # Build the image
    options = {
        "path": str(build_path),
        "dockerfile": str(dockerfile).lstrip(str(build_path)),
        "tag": f"{full_name}:latest",
        "nocache": rebuild,
        "quiet": False,
    }
    logging.info(f"Building: {options}")
    for out in DOCKER_API.build(**options):
        logging.info("BUILD: {}".format(json.loads(out).get("stream", "").rstrip("\n")))
    if REPO_DOCKERIGNORE.is_file():
        REPO_DOCKERIGNORE.unlink()
    return full_name


def do_push(full_name: str, tags: list) -> None:
    for tag in tags:
        logging.info(f"Pushing: {full_name}:{tag}")
        DOCKER_CLIENT.images.push(full_name, tag=tag)


def main(
    name: str,
    allow_cross_platform: bool = False,
    push: bool = False,
    rebuild: bool = False,
) -> None:
    directory = Path(IMAGES_DIR / name)
    # Get dockerfiles
    dfiles = list(directory.glob("Dockerfile*"))
    if len(dfiles) == 0:
        logging.error(f"No `Dockerfile*`s found: {directory}")
        return
    # Build images
    for dfile in dfiles:
        full_name = do_build(
            dfile, allow_cross_platform=allow_cross_platform, rebuild=rebuild
        )
        if push:
            do_push(full_name, tags=["latest"])


def cli():
    # Get neighboring directories
    neighbors = list(p.name for p in IMAGES_DIR.iterdir() if p.is_dir())
    # Command line handling
    parser = argparse.ArgumentParser(
        description="Utility for building/tagging/pushing docker images."
    )
    parser.add_argument(
        "name",
        type=str,
        help="Docker image name (available options listed above).",
        choices=neighbors,
    )
    parser.add_argument(
        "-x",
        "--allow_cross_platform",
        action="store_true",
        help="Allow cross platform (x86 vs aarch64) building.",
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
