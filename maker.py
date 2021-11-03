#!/usr/bin/env python3
# Author: Joey Curtis @jccurtis
import argparse
import platform
import json
import multiprocessing
from pathlib import Path
import docker

DOCKER_NAMESPACE = "lblanp"
DOCKER_CLIENT = docker.from_env()  # high level
DOCKER_API = docker.APIClient()  # low level
REPO_DIR = Path(__file__).parent
REPO_DOCKERIGNORE = REPO_DIR / ".dockerignore"
IMAGES_DIR = REPO_DIR / "images"
MAX_JOBS = int(multiprocessing.cpu_count() // 2)


def parse_stream(out):
    data = json.loads(out)
    if "stream" in data:
        return data["stream"]
    elif "error" in data:
        return data["error"]
    else:
        return str(data)


def do_print(*args, name: str = None, quiet: bool = False) -> None:
    if not quiet:
        print(f"[maker.py{'' if name is None else f'|{name}'}]", *args)


def do_build(
    dockerfile: Path,
    full_name: str,
    rebuild: bool = False,
    quiet: bool = False,
) -> None:
    options = {
        "path": str(REPO_DIR),
        "dockerfile": str(dockerfile).lstrip(str(REPO_DIR)),
        "tag": f"{full_name}:latest",
        "nocache": rebuild,
        "quiet": False,
    }
    do_print(f"Building: {options}", name=full_name, quiet=quiet)
    for out in DOCKER_API.build(**options):
        do_print(parse_stream(out).rstrip("\n"), name=full_name, quiet=quiet)
    if REPO_DOCKERIGNORE.is_file():
        REPO_DOCKERIGNORE.unlink()


def do_push(full_name: str, tags: list, quiet: bool = False) -> None:
    for tag in tags:
        do_print(f"Pushing: {full_name}:{tag}", name=full_name, quiet=quiet)
        DOCKER_CLIENT.images.push(full_name, tag=tag)


def do_image_workflow(
    dockerfile: Path,
    allow_cross_platform: bool = False,
    push: bool = False,
    rebuild: bool = False,
    quiet: bool = False,
) -> None:
    # Short name for initial logging
    name = dockerfile.parent.stem
    # Parser full name and check platform
    extra_tags = [s.lstrip(".") for s in dockerfile.suffixes]
    for t in extra_tags:
        if t != t.lower():
            raise ValueError(
                f"Dockerfile suffix tags must all be lowercase: {dockerfile}"
            )
    image_arch = "x86_64"
    if "l4t" in extra_tags:
        do_print(f"Found Linux 4 Tegra tag in {dockerfile}", name=name)
        image_arch = "aarch64"
    if "arm64v8" in extra_tags:
        do_print(f"Found ARM64v8 tag in {dockerfile}", name=name)
        image_arch = "aarch64"
    if image_arch != platform.machine():
        if allow_cross_platform:
            do_print(
                "Attempting to build a cross platform image",
                f"(this={platform.machine()} vs requested={image_arch}):",
                f"{dockerfile}",
                name=name,
            )
        else:
            do_print(
                "Cannot build across platforms without `-x` option",
                f"(this={platform.machine()} vs requested={image_arch}):",
                f"Skipping: {dockerfile}",
                name=name,
            )
            return
    full_name = f"{DOCKER_NAMESPACE}/{dockerfile.parent.stem}"
    if len(extra_tags):
        full_name += "_" + "_".join(extra_tags)
    # Build it
    do_build(
        dockerfile,
        full_name,
        rebuild=rebuild,
        quiet=quiet,
    )
    # Push it
    if push:
        do_push(full_name, tags=["latest"], quiet=quiet)


def get_dockerfiles(names: list) -> list:
    all_files = []
    for name in names:
        directory = Path(IMAGES_DIR / name)
        these_files = list(directory.glob("Dockerfile*"))
        if len(these_files) == 0:
            do_print(f"No `Dockerfile*`s found, skipping: {directory}")
            continue
        all_files.extend(these_files)
    do_print(f"Found {len(all_files)} Dockerfiles!")
    return all_files


def parse_cmd_line_args():
    # Get neighboring directories
    neighbors = list(p.name for p in IMAGES_DIR.iterdir() if p.is_dir())
    # Command line handling
    parser = argparse.ArgumentParser(
        description="Utility for building/tagging/pushing docker images."
    )
    parser.add_argument(
        "names",
        type=str,
        nargs="+",
        help="Docker image name(s). The available options are listed above.",
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
    parser.add_argument(
        "-m",
        "--multiprocess",
        action="store_true",
        help="Run each image workflow in a separate process (output silenced).",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_cmd_line_args()
    dockerfiles = get_dockerfiles(args.names)
    if len(dockerfiles) == 1 or not args.multiprocess:
        for dockerfile in dockerfiles:
            do_image_workflow(
                dockerfile,
                allow_cross_platform=args.allow_cross_platform,
                rebuild=args.rebuild,
                push=args.push,
                quiet=False,
            )
    else:
        results = []
        with multiprocessing.Pool(min(MAX_JOBS, len(args.names))) as pool:
            for dockerfile in dockerfiles:
                print(f"Adding build job: {dockerfile}")
                results.append(
                    pool.apply_async(
                        do_image_workflow,
                        args=(dockerfile,),
                        kwds=dict(
                            allow_cross_platform=args.allow_cross_platform,
                            rebuild=args.rebuild,
                            push=args.push,
                            quiet=False,
                        ),
                    )
                )
            [r.wait() for r in results]
    print("Done!")
