"""
Arrange some ML data to ImageNet Style.


Given class paths with a format like:

classA/
    img1.jpg
    img2.png
    ...
classB/
    img1.jpg
    img2.png
    ...
...


generates the following at output path:

train/
    classA/
        ...
    classB/
        ...
    ...
valid/
    classA/
    classB/
test/
    classA/
    classB/
"""
import logging
import math
import pathlib
import random
import shutil
import typing

LOGGER = logging.getLogger(__name__)

# 80% train / 10% test / 10% valid
DEFAULT_SPLITS = {
    "train": 0.8, 
    "test": 0.1,
    "valid": 0.1
}

def _validate_splits(splits):
    if not math.isclose(sum(splits.values()), 1):
        raise ValueError("splits did not sum up to 100")


def _validate_path_exists(path: pathlib.Path):
    if not path.exists():
        raise FileNotFoundError(f"{path} does not exist.")


def partition_files(files: typing.Sequence[pathlib.Path], split_weights: typing.Mapping):
    total_num_files = len(files)

    # shuffle the list
    shuffled_files = random.sample(files, k=total_num_files)

    # pick number of items and leave the rest for the later
    partitioned_files = {}
    for split, weight in split_weights.items():
        number_of_items_to_take = math.floor(weight * total_num_files) # better safe than IndexError?
        partitioned_files[split] = shuffled_files[:number_of_items_to_take]
    
    return partitioned_files


def move_files_to_directory(files, dest_dir, dry_run=True, copy=True):
    move = shutil.move if not copy else shutil.copy
    
    for f in files:
        print(f"moving: {f} -> {dest_dir}")
        
        if dry_run:
            continue

        move(f, dest_dir)

def get_or_create_output_dir(out_path: pathlib.Path, split : str, class_name : str):
    output = out_path / split / class_name
    output.mkdir(parents=True, exist_ok=True) # create if it doesn't exist
    return output


def main(class_paths : typing.Sequence[pathlib.Path], out_path: pathlib.Path, splits=DEFAULT_SPLITS, dry_run=True):
    [_validate_path_exists(p) for p in class_paths]
    _validate_splits(splits)

    for class_path in class_paths:
        if not class_path.exists() or not class_path.is_dir():
            LOGGER.warning("Skipping %s: was not an existing directory", class_path)
            continue

        files = [f for f in class_path.iterdir()]
        files_for_splits = partition_files(files, splits)

        for split, files_for_split in files_for_splits.items():
            output_path = get_or_create_output_dir(out_path, split, class_path.name)
            move_files_to_directory(files_for_split, output_path, dry_run=dry_run)


def parse_cli_args():
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('class_paths', metavar='class_path', type=str, nargs='+', help='classes to generate splits for')
    parser.add_argument('-o','--output', dest='output_path', help='output')
    parser.add_argument('-v', '--verbosity', action='count', default=0)
    

    args = parser.parse_args()
    class_paths = set(pathlib.Path(p) for p in args.class_paths)
    output_path = pathlib.Path(args.output_path)
    verbosity = args.verbosity * -10

    return class_paths, output_path, verbosity
    

if __name__ == "__main__":
    class_paths, output_path, verbosity = parse_cli_args()
    main(class_paths, output_path, dry_run=False)
