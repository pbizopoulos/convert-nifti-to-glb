import sys
import unittest
from hashlib import sha256
from pathlib import Path
from urllib import request

import numpy as np
import trimesh
from nibabel import Nifti1Image
from skimage.measure import marching_cubes


def convert_nifti_to_glb(
    data: str,
    output_file_name: str,
    iterations: int,
    step_size: int,
) -> bytes:
    if isinstance(data, str):
        file_name = data.split("/")[-1]
        nifti_object = Nifti1Image.from_filename(data)
        ".".join(file_name.split(".")[:-1])
    else:
        nifti_object = Nifti1Image.from_bytes(bytearray(data))
    volume = nifti_object.get_fdata()
    volume = volume.astype("float32")
    if np.unique(volume).size == 2:  # noqa: PLR2004
        verts, faces, *_ = marching_cubes(
            volume,
            spacing=nifti_object.header.get_zooms(),
            step_size=step_size,
        )
        tm = trimesh.base.Trimesh(
            vertices=verts,
            faces=faces,
            visual=trimesh.visual.TextureVisuals(
                material=trimesh.visual.material.PBRMaterial(
                    alphaMode="BLEND",
                    baseColorFactor=[31, 119, 180, 127],
                ),
            ),
        )
        tm.apply_scale(10 ** (-3))
        trimesh.repair.fix_inversion(tm)
        trimesh.repair.fill_holes(tm)
        trimesh.smoothing.filter_laplacian(tm, iterations=iterations)
    elif np.unique(volume).size == 3:  # noqa: PLR2004
        volume[volume == 2] = 0  # noqa: PLR2004
        verts, faces, *_ = marching_cubes(
            volume,
            spacing=nifti_object.header.get_zooms(),
            step_size=step_size,
        )
        tm = trimesh.base.Trimesh(
            vertices=verts,
            faces=faces,
            visual=trimesh.visual.TextureVisuals(
                material=trimesh.visual.material.PBRMaterial(
                    alphaMode="BLEND",
                    baseColorFactor=[31, 119, 180, 127],
                ),
            ),
        )
        tm.apply_scale(10 ** (-3))
        trimesh.repair.fix_inversion(tm)
        trimesh.repair.fill_holes(tm)
        trimesh.smoothing.filter_laplacian(tm, iterations=iterations)
        volume = nifti_object.get_fdata()
        volume = volume.astype("float32")
        volume[volume == 1] = 0
        volume[volume == 2] = 1  # noqa: PLR2004
        verts2, faces2, *_ = marching_cubes(
            volume,
            spacing=nifti_object.header.get_zooms(),
            step_size=step_size,
        )
        tm2 = trimesh.base.Trimesh(
            vertices=verts2,
            faces=faces2,
            visual=trimesh.visual.TextureVisuals(
                material=trimesh.visual.material.PBRMaterial(
                    alphaMode="BLEND",
                    baseColorFactor=[255, 0, 0, 127],
                ),
            ),
        )
        tm2.apply_scale(10 ** (-3))
        trimesh.repair.fix_inversion(tm2)
        trimesh.repair.fill_holes(tm2)
        trimesh.smoothing.filter_laplacian(tm2, iterations=iterations)
        tm = trimesh.util.concatenate([tm, tm2])
        tm.visual.material.alphaMode = "BLEND"
    mesh: bytes = trimesh.exchange.export.export_mesh(tm, output_file_name)
    return mesh


class Tests(unittest.TestCase):
    def test_convert_nifti_to_glb(self: "Tests") -> None:
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
        assert (
            sha256(output_masks_multiclass).hexdigest()
            == "e32b75c132dba956d8c7bfff787d1b7014d203aeafa922c1c1ed558decd9e8ad"
        )


def main() -> None:
    num_arguments_allowed = 5
    if len(sys.argv) == num_arguments_allowed:
        masks = convert_nifti_to_glb(
            sys.argv[1],
            sys.argv[2],
            int(sys.argv[3]),
            int(sys.argv[4]),
        )
        with Path("output.glb").open("w") as file:
            file.write(masks)


if __name__ == "__main__":
    for mask_filename in ["masks-multiclass.nii", "masks.nii"]:
        if not Path(mask_filename).is_file():
            request.urlretrieve(  # noqa: S310
                f"https://github.com/pbizopoulos/semi-automatic-annotation-tool/releases/download/dist/{mask_filename}",
                f"tmp/{mask_filename}",
            )
    unittest.main()
