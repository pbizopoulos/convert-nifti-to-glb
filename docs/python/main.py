from pathlib import Path
from urllib import request

import numpy as np
import trimesh
from nibabel import Nifti1Image  # type: ignore[attr-defined]
from skimage.measure import marching_cubes


def generate_mesh(
    data: str,
    laplacian_smoothing_iterations: int,
    marching_cubes_step_size: int,
) -> bytes:
    if isinstance(data, str):
        file_name = data.split("/")[-1]
        if not Path(data).is_file():
            request.urlretrieve(  # noqa: S310
                f"https://github.com/pbizopoulos/semi-automatic-annotation-tool/releases/download/dist/{file_name}",
                data,
            )
        nifti_object = Nifti1Image.from_filename(data)
        file_name_without_extension = ".".join(file_name.split(".")[:-1])
        output_file_name = f"bin/{file_name_without_extension}-step-size-{marching_cubes_step_size}-iterations-{laplacian_smoothing_iterations}.glb"  # noqa: E501
    else:
        nifti_object = Nifti1Image.from_bytes(bytearray(data))
        output_file_name = "output.glb"
    volume = nifti_object.get_fdata()
    volume = volume.astype("float32")
    if np.unique(volume).size == 2:  # noqa: PLR2004
        verts, faces, *_ = marching_cubes(
            volume,
            spacing=nifti_object.header.get_zooms(),  # type: ignore[no-untyped-call]
            step_size=marching_cubes_step_size,
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
        trimesh.smoothing.filter_laplacian(
            tm,
            iterations=laplacian_smoothing_iterations,
        )
    elif np.unique(volume).size == 3:  # noqa: PLR2004
        volume[volume == 2] = 0  # noqa: PLR2004
        verts, faces, *_ = marching_cubes(
            volume,
            spacing=nifti_object.header.get_zooms(),  # type: ignore[no-untyped-call]
            step_size=marching_cubes_step_size,
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
        trimesh.smoothing.filter_laplacian(
            tm,
            iterations=laplacian_smoothing_iterations,
        )
        volume = nifti_object.get_fdata()
        volume = volume.astype("float32")
        volume[volume == 1] = 0
        volume[volume == 2] = 1  # noqa: PLR2004
        verts2, faces2, *_ = marching_cubes(
            volume,
            spacing=nifti_object.header.get_zooms(),  # type: ignore[no-untyped-call]
            step_size=marching_cubes_step_size,
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
        trimesh.smoothing.filter_laplacian(
            tm2,
            iterations=laplacian_smoothing_iterations,
        )
        tm = trimesh.util.concatenate([tm, tm2])
        tm.visual.material = tm.visual.material.to_pbr()
        tm.visual.material.alphaMode = "BLEND"
        tm.visual.material.baseColorFactor[-1] = 127
    output: bytes = trimesh.exchange.export.export_mesh(tm, output_file_name)
    return output


def main() -> None:
    bin_file_path = Path("bin")
    if not bin_file_path.exists():
        bin_file_path.mkdir(parents=True)
    data_file_path = Path("data")
    if not data_file_path.exists():
        data_file_path.mkdir(parents=True)
    generate_mesh("data/masks.nii", 1, 2)
    generate_mesh("data/masks-multiclass.nii", 1, 2)


if __name__ == "__main__":
    main()
