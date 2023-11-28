from __future__ import annotations

from os import getenv

import PyInstaller.__main__
from gooey import Gooey, GooeyParser

from python.main import convert_nifti_to_glb


@Gooey  # type: ignore[misc]
def main_gui() -> None:
    parser = GooeyParser(description="Convert NIfTI to GLB")
    parser.add_argument("--input_file_name", widget="FileChooser")
    parser.add_argument(
        "--output_file_name",
        widget="FileSaver",
        gooey_options={
            "wildcard": "GL Transmission Format Binary file (*.glb)|*.glb|All files (*.*)|*.*",  # noqa: E501
            "default_dir": ".",
            "default_file": "output.glb",
        },
    )
    parser.add_argument(
        "--iterations",
        widget="IntegerField",
        type=int,
        gooey_options={"initial_value": 1},
    )
    parser.add_argument(
        "--step_size",
        widget="IntegerField",
        type=int,
        gooey_options={
            "initial_value": 2,
        },
    )
    args = parser.parse_args()
    convert_nifti_to_glb(
        args.input_file_name,
        args.output_file_name,
        args.iterations,
        args.step_size,
    )


def main() -> None:
    if getenv("STAGING"):
        main_gui()
    else:
        PyInstaller.__main__.run(
            [
                "main.py",
                "--distpath",
                "tmp/dist",
                "--runtime-hook",
                "prm/runtime_hook.py",
                "--onefile",
                "--specpath",
                "tmp/spec",
                "--windowed",
                "--workpath",
                "tmp/build",
            ],
        )


if __name__ == "__main__":
    main()
