from __future__ import annotations

import unittest
from hashlib import sha256
from pathlib import Path
from urllib import request

import numpy as np
import trimesh
from nibabel import Nifti1Image  # type: ignore[attr-defined]
from skimage.measure import marching_cubes


def convert_nifti_to_glb(
    input_file_name: bytes | str,
    output_file_name: str = "output.glb",
    iterations: int = 1,
    step_size: int = 2,
) -> bytes:
    if isinstance(input_file_name, str):
        nifti_object = Nifti1Image.from_filename(input_file_name)
    else:
        nifti_object = Nifti1Image.from_bytes(bytearray(input_file_name))
    volume = nifti_object.get_fdata()
    volume = volume.astype("float32")
    if np.unique(volume).size == 2:  # noqa: PLR2004
        verts, faces, *_ = marching_cubes(  # type: ignore[no-untyped-call]
            volume,
            spacing=nifti_object.header.get_zooms(),  # type: ignore[no-untyped-call]
            step_size=step_size,
        )
        tm = trimesh.base.Trimesh(
            vertices=verts,
            faces=faces,
            visual=trimesh.visual.TextureVisuals(  # type: ignore[no-untyped-call]
                material=trimesh.visual.material.PBRMaterial(  # type: ignore[no-untyped-call]
                    alphaMode="BLEND",
                    baseColorFactor=[31, 119, 180, 127],
                ),
            ),
        )
        tm.apply_scale(10 ** (-3))  # type: ignore[no-untyped-call]
        trimesh.repair.fix_inversion(tm)  # type: ignore[no-untyped-call]
        trimesh.repair.fill_holes(tm)  # type: ignore[no-untyped-call]
        trimesh.smoothing.filter_laplacian(tm, iterations=iterations)  # type: ignore[no-untyped-call]
    elif np.unique(volume).size == 3:  # noqa: PLR2004
        volume[volume == 2] = 0  # noqa: PLR2004
        verts, faces, *_ = marching_cubes(  # type: ignore[no-untyped-call]
            volume,
            spacing=nifti_object.header.get_zooms(),  # type: ignore[no-untyped-call]
            step_size=step_size,
        )
        tm = trimesh.base.Trimesh(
            vertices=verts,
            faces=faces,
            visual=trimesh.visual.TextureVisuals(  # type: ignore[no-untyped-call]
                material=trimesh.visual.material.PBRMaterial(  # type: ignore[no-untyped-call]
                    alphaMode="BLEND",
                    baseColorFactor=[31, 119, 180, 127],
                ),
            ),
        )
        tm.apply_scale(10 ** (-3))  # type: ignore[no-untyped-call]
        trimesh.repair.fix_inversion(tm)  # type: ignore[no-untyped-call]
        trimesh.repair.fill_holes(tm)  # type: ignore[no-untyped-call]
        trimesh.smoothing.filter_laplacian(tm, iterations=iterations)  # type: ignore[no-untyped-call]
        volume = nifti_object.get_fdata()
        volume = volume.astype("float32")
        volume[volume == 1] = 0
        volume[volume == 2] = 1  # noqa: PLR2004
        verts2, faces2, *_ = marching_cubes(  # type: ignore[no-untyped-call]
            volume,
            spacing=nifti_object.header.get_zooms(),  # type: ignore[no-untyped-call]
            step_size=step_size,
        )
        tm2 = trimesh.base.Trimesh(
            vertices=verts2,
            faces=faces2,
            visual=trimesh.visual.TextureVisuals(  # type: ignore[no-untyped-call]
                material=trimesh.visual.material.PBRMaterial(  # type: ignore[no-untyped-call]
                    alphaMode="BLEND",
                    baseColorFactor=[255, 0, 0, 127],
                ),
            ),
        )
        tm2.apply_scale(10 ** (-3))  # type: ignore[no-untyped-call]
        trimesh.repair.fix_inversion(tm2)  # type: ignore[no-untyped-call]
        trimesh.repair.fill_holes(tm2)  # type: ignore[no-untyped-call]
        trimesh.smoothing.filter_laplacian(tm2, iterations=iterations)  # type: ignore[no-untyped-call]
        tm = trimesh.util.concatenate([tm, tm2])  # type: ignore[no-untyped-call]
        tm.visual.material.alphaMode = "BLEND"
    mesh: bytes = trimesh.exchange.export.export_mesh(tm, output_file_name)  # type: ignore[no-untyped-call]
    return mesh


class Tests(unittest.TestCase):
    def test_convert_nifti_to_glb_bytes_input(self: Tests) -> None:
        with Path("tmp/masks.nii").open("rb") as file:
            masks_bytes = file.read()
        output_masks = convert_nifti_to_glb(masks_bytes, "tmp/masks.glb", 1, 2)
        assert (
            sha256(output_masks).hexdigest()
            == "8eec1367dd602133cee555a504eb5e54e7b2f7c0e550110e3657fcc7a13d65cb"
        )
        with Path("tmp/masks-multiclass.nii").open("rb") as file:
            masks_multiclass_bytes = file.read()
        output_masks_multiclass = convert_nifti_to_glb(
            masks_multiclass_bytes,
            "tmp/masks-multiclass.glb",
            1,
            2,
        )
        assert sha256(output_masks_multiclass).hexdigest() in [
            "e32b75c132dba956d8c7bfff787d1b7014d203aeafa922c1c1ed558decd9e8ad",
            "5eb4b65bf995f07078a7452c6407ad1746cbe0c19306802fef5fdae2b7ef7580",
        ]

    def test_convert_nifti_to_glb_file_input(self: Tests) -> None:
        output_masks = convert_nifti_to_glb("tmp/masks.nii", "tmp/masks.glb", 1, 2)
        assert (
            sha256(output_masks).hexdigest()
            == "8eec1367dd602133cee555a504eb5e54e7b2f7c0e550110e3657fcc7a13d65cb"
        )
        output_masks_multiclass = convert_nifti_to_glb(
            "tmp/masks-multiclass.nii",
            "tmp/masks-multiclass.glb",
            1,
            2,
        )
        assert sha256(output_masks_multiclass).hexdigest() in [
            "e32b75c132dba956d8c7bfff787d1b7014d203aeafa922c1c1ed558decd9e8ad",
            "5eb4b65bf995f07078a7452c6407ad1746cbe0c19306802fef5fdae2b7ef7580",
        ]


def main_cli() -> None:
    import fire

    fire.Fire(convert_nifti_to_glb)


def main() -> None:
    for mask_filename in ["masks-multiclass.nii", "masks.nii"]:
        if not Path(mask_filename).is_file():
            request.urlretrieve(  # noqa: S310
                f"https://github.com/pbizopoulos/semi-automatic-annotation-tool/releases/download/dist/{mask_filename}",
                f"tmp/{mask_filename}",
            )
    unittest.main()


if __name__ == "__main__":
    main()
