#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""brgp main file"""

import os
import sys
import codecs

CURDIR = os.path.abspath(os.curdir)
BRGP_NAME = os.path.basename(__file__)
BRGP_FILE = os.path.abspath(__file__)

HOOK_DIR = os.path.join(os.path.join(CURDIR, ".git"), "hooks")

HELP_TEXT = \
"""brgp

usage:
%s [help]
    print help infomation.
%s init [python exec]
    init brgp and write to git pre-commit.
%s clear [add|noadd]
    clear all boms and add (optionally) it in git.
    noadd is default.
""" % (BRGP_NAME, BRGP_NAME, BRGP_NAME)

PRECOMMIT = \
"""#!/bin/sh

cd $GIT_DIR
cd ..
%s "%s" clear add
"""

DEFAULT_PYTHON_EXEC = "python"

def process_single_file(file: str, noadd: bool) -> None:
    """remove bom for a single file"""

    cont_rb = None
    try:
        cont_rb = open(file, "rb")
    except PermissionError:
        print("rejected %s" % file)

    if cont_rb is None:
        return

    if cont_rb.read(3) == codecs.BOM_UTF8:
        cont_rb.close()

        cont_rt = open(file, 'r+', encoding='utf-8')
        cont = cont_rt.read()
        cont_rt.seek(0)
        cont_rt.truncate(0)
        cont_rt.write(cont[1:])
        cont_rt.flush()
        cont_rt.close()

        print("processed %s" % file)
        if not noadd:
            os.system("git add %s" % file)
            print("git add %s" % file)
    else:
        cont_rb.close()

        print("skip %s" % file)

def clear(argv: list) -> None:
    """clear bom of all files under current directory recursively"""
    noadd = (not argv) or argv[0].lower() == "noadd"
    gitdir = os.path.join(CURDIR, ".git")

    for path, _, files in os.walk(CURDIR):
        if os.path.relpath(path, gitdir)[:2] != '..':
            continue
        for file in files:
            # if f.split('.')[-1] in EXTS:
            process_single_file(os.path.join(path, file), noadd)

def get_precommit_file_content(python_exec: str) -> str:
    """get pre-commit file content"""
    return PRECOMMIT % (python_exec, BRGP_FILE)

def init(argv: list):
    """write pre-commit"""
    python_exec = DEFAULT_PYTHON_EXEC if not argv else argv[0]

    precommit = get_precommit_file_content(python_exec)

    precommit_file = open(os.path.join(HOOK_DIR, "pre-commit"), 'w', encoding="utf-8")
    precommit_file.write(precommit)
    precommit_file.flush()
    precommit_file.close()

def print_helpinfo():
    """print help infomation"""
    print(HELP_TEXT)

def main():
    """entry point"""

    argv = sys.argv[1:]

    if (not argv) or argv[0] == "help":
        print_helpinfo()
    elif argv[0] == "init":
        init(argv[1:])
    elif argv[0] == "clear":
        clear(argv[1:])

if __name__ == "__main__":
    main()
