#!/usr/bin/python3

import os
import sys
import io
from hatchling.builders.hooks.plugin.interface import BuildHookInterface


class ManPageGenerator(BuildHookInterface):
    PLUGIN_NAME = "ManPageGenerator"

    def initialize(self, version, build_data):
        try:
            import pypandoc
        except ModuleNotFoundError:
            print(
                "*********************************************\n"
                "Module pypandoc not found, skipping man pages\n"
                "*********************************************\n",
                file=sys.stderr,
            )
            return

        # pypandoc spews install instructions to stderr when it can't find
        # pandoc. So we redirect stderr and restore it with a saner
        # message.
        old_stderr = sys.stderr
        pandoc_found = True
        try:
            with io.StringIO() as s:
                sys.stderr = s
                pypandoc.get_pandoc_version()
        except OSError:
            pandoc_found = False
        finally:
            sys.stderr = old_stderr

        if not pandoc_found:
            print(
                "*****************************************************\n"
                "Pandoc man page conversion failed, skipping man pages\n"
                "*****************************************************\n",
                file=sys.stderr,
            )
            return

        # now do the actual conversion
        here = "."
        mandir = os.path.join(here, "man")
        destdir = os.path.join(here, "dist", "man")
        os.makedirs(destdir, exist_ok=True)
        for f in os.listdir(mandir):
            if f.endswith(".md"):
                path = os.path.join(mandir, f)
                name = os.path.splitext(f)[0]
                outfile = os.path.join(destdir, f"{name}.1")
                pypandoc.convert_file(
                    path, "man", outputfile=outfile, extra_args=["-s"]
                )
