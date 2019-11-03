#!/usr/bin/env python3

import os
import argparse
import zipfile

def get_source_items(source_folder):
    names = [name for name in os.listdir(source_folder)]
    paths = [os.path.join(source_folder, name) for name in names]
    return list(sorted([p for p in paths if p.endswith('.zip')]))

def get_target_items(target_folder):
    names = [name for name in os.listdir(target_folder)]
    paths = [os.path.join(target_folder, name) for name in names]
    return list(sorted([p for p in paths if os.path.isdir(p)]))

def get_initial_mapping(source_items):
    return {k:'' for k in source_items}

def get_source_id(index):
    return str(chr(index + 97))

def get_target_id(index):
    return str(chr(index + 49))

def get_source_index(id):
    assert len(id)==1 and 'a' <= id[0] <= 'z'
    return ord(id[0])-97

def get_target_index(id):
    assert len(id)==1 and '0' <= id[0] <= '9'
    return ord(id[0])-49

def display_info(source_items, target_items, mapping):
    print("Source items")
    for i in range(len(source_items)):
        print(get_source_id(i), source_items[i])
    print("")

    print("Target items")
    for i in range(len(target_items)):
        print(get_target_id(i), target_items[i])
    print("")

    print("Mapping")
    for i in range(len(source_items)):
        print(get_source_id(i), source_items[i], "->", mapping[source_items[i]] or "(none)")
    print("")

def extract(zip_file, folder):
    with zipfile.ZipFile(zip_file, 'r') as zip_obj:
        zip_obj.extractall(folder)

def execute(mapping):
    for k in mapping:
        v = mapping[k]
        if v != '':
            extract(k, v)

def get_recursive_path_list(folder):
    paths = []
    # r=root, d=directories, f = files
    for r, d, f in os.walk(folder):
        for name in d + f:
            paths.append(os.path.join(r, name))
    return paths

def get_relative_paths(paths, root):
    return [os.path.relpath(p, root) for p in paths]

def get_zip_name_list(file):
    with zipfile.ZipFile(file, 'r') as zip_obj:
        return zip_obj.namelist()

def score(source_item, target_item):
    source_paths = get_zip_name_list(source_item)
    target_paths = get_relative_paths(get_recursive_path_list(target_item), target_item)
    good_paths = [s for s in source_paths if s in target_paths]
    return len(good_paths)

def get_auto_mapping(source_items, target_items):
    mapping = get_initial_mapping(source_items)
    for s in source_items:
        potentials = [t for t in target_items if score(s, t) > 0]
        if len(potentials) == 1:
            mapping[s] = potentials[0]
    return mapping

def get_auto_mapping_choose_max(source_items, target_items):
    mapping = get_initial_mapping(source_items)
    for s in source_items:
        best_score = max(score(s, t) for t in target_items)
        potentials = [t for t in target_items if score(s, t) == best_score]
        if len(potentials) == 1 and best_score > 0:
            mapping[s] = potentials[0]
    return mapping

def delete_mapped_source_items(mapping):
    for k in mapping:
        if mapping[k]:
            os.remove(k)

HELP_MESSAGE = """
XY: Map X to Y, X='a'..'z', Y=1..n. For example, 'a1' maps item a with item 1.
q: Quit
x: Execute, i.e. unzip ZIP files to the mapped target folders
X: Execute, then delete mapped source files
c: Clear mapping
a: Auto mapping
A: Auto mapping, choose the best match if there are multiple matches
d: Delete mapped source files, then reload
r: Reload
h: Show this help
"""

def interact(args):
    source_folder = args.source_folder or input("Source folder: ")
    target_folder = args.target_folder or input("Target folder: ")

    source_items = get_source_items(source_folder)
    target_items = get_target_items(target_folder)

    # mapping = get_initial_mapping(source_items)
    mapping = get_auto_mapping(source_items, target_items)

    while True:
        display_info(source_items, target_items, mapping)

        command = input('Enter command: ')
        if command == '':
            pass
        elif len(command) == 2:
            x, y = command
            source_index = get_source_index(str(x))
            target_index = -1 if y=='0' else get_target_index(str(y))
            ss = source_items[source_index]
            tt = '' if target_index == -1 else target_items[target_index]
            mapping[ss] = tt
        elif len(command) == 1:
            if command == 'q':
                return
            elif command == 'x':
                execute(mapping)
                return
            elif command == 'X':
                execute(mapping)
                delete_mapped_source_items(mapping)
                return
            elif command == 'c':
                mapping = get_initial_mapping(source_items)
            elif command == 'a':
                mapping = get_auto_mapping(source_items, target_items)
            elif command == 'A':
                mapping = get_auto_mapping_choose_max(source_items, target_items)
            elif command == 'd':
                delete_mapped_source_items(mapping)
                interact(args) # Reload
                return
            elif command == 'r':
                interact(args) # Reload
                return
            elif command == 'h':
                print(HELP_MESSAGE)

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Extract ZIP files downloaded from Luminus to the correct folders')
    parser.add_argument('-s', '--source-folder', type=str)
    parser.add_argument('-t', '--target-folder', type=str)

    args = parser.parse_args()
    interact(args)
