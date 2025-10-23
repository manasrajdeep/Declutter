import logging
import shutil
from pathlib import Path
from typing import Union

from declutter.extensions import formats

# Logger setup (single-file handler)
log_file = Path.cwd() / "logs_declutter.log"
logger = logging.getLogger("declutter")
if not logger.handlers:
    handler = logging.FileHandler(log_file, encoding="utf-8")
    fmt = logging.Formatter("%(levelname)s: %(asctime)s - %(message)s")
    handler.setFormatter(fmt)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)


def create(dest: Union[str, Path] = ".") -> bool:
    """Create the Declutter root and subdirectories defined in `formats`.

    Accepts either a Path or str. Creates parent directories if needed.
    """
    dest = Path(dest)
    try:
        dest.mkdir(parents=True, exist_ok=True)
        for folder in formats.keys():
            (dest / folder).mkdir(exist_ok=True)
        logger.info("Created declutter structure at %s", dest)
        return True
    except Exception:
        logger.exception("Failed to create declutter directories")
        return False


def _unique_path(dest_dir: Path, name: str) -> Path:
    """Return a non-colliding Path in dest_dir by appending -1,-2,... if needed."""
    dest_dir = Path(dest_dir)
    stem = Path(name).stem
    suffix = Path(name).suffix
    candidate = dest_dir / f"{stem}{suffix}"
    i = 1
    while candidate.exists():
        candidate = dest_dir / f"{stem}-{i}{suffix}"
        i += 1
    return candidate


def rename(file: Union[str, Path], path: Union[str, Path] = ".") -> Path:
    """Rename `file` so its name does not collide in `path` and return new Path.

    Kept for backward compatibility with existing callers/tests.
    """
    file = Path(file)
    path = Path(path)
    new_path = _unique_path(path, file.name)
    new_path.parent.mkdir(parents=True, exist_ok=True)
    return file.rename(new_path)


def organize(src: Union[str, Path] = ".", dest: Union[str, Path] = ".") -> bool:
    """Move files from `src` into categorized subdirectories under `dest`.

    Skips directories and this module file. Uses `formats` mapping to decide
    destination folders. Returns True on success, False on any exception.
    """
    src = Path(src)
    dest = Path(dest)
    try:
        for item in src.iterdir():
            if not item.is_file():
                continue
            # skip this module file
            try:
                if item.resolve() == Path(__file__).resolve():
                    continue
            except Exception:
                pass

            ext = item.suffix.lower().lstrip(".")
            if not ext:
                # no extension: skip
                continue

            moved = False
            for folder, exts in formats.items():
                if ext in exts:
                    target_dir = dest / folder
                    target_dir.mkdir(parents=True, exist_ok=True)
                    target = target_dir / item.name
                    if target.exists():
                        target = _unique_path(target_dir, item.name)
                        logger.warning("File exists, renaming to %s", target.name)
                    shutil.move(str(item), str(target))
                    logger.info("Moved %s -> %s", item.name, target)
                    moved = True
                    break
            if not moved:
                logger.debug("No matching category for %s (.%s)", item.name, ext)
        return True
    except Exception:
        logger.exception("Failed to organize files")
        return False


def remove(src: Union[str, Path] = ".", dest: Union[str, Path] = ".") -> bool:
    """Move all files from Declutter subfolders back to `src` and remove the folders.

    If a file with the same name exists in `src`, a unique name is chosen.
    """
    src = Path(src)
    dest = Path(dest)
    try:
        # iterate only directories in dest
        for sub in [p for p in dest.iterdir() if p.is_dir()]:
            for f in sub.iterdir():
                target = src / f.name
                if target.exists():
                    target = _unique_path(src, f.name)
                shutil.move(str(f), str(target))
                logger.info("Moved back %s -> %s", f.name, target)
            # remove empty subfolder
            sub.rmdir()
        # remove dest folder if empty
        dest.rmdir()
        logger.info("Removed declutter folder %s", dest)
        return True
    except Exception:
        logger.exception("Failed to remove declutter folders/files")
        return False
