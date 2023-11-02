import sys
from pathlib import Path
from urllib import request

import numpy as np
import pyodide
import trimesh
from js import Blob, Uint8Array, document, window
from nibabel import Nifti1Image
from pyodide.ffi.wrappers import add_event_listener
from skimage.measure import marching_cubes


def generate_mesh(data: str, iterations: int, step_size: int) -> bytes:
    if isinstance(data, str):
        file_name = data.split("/")[-1]
        if not Path(data).is_file():
            request.urlretrieve(  # noqa: S310
                f"https://github.com/pbizopoulos/semi-automatic-annotation-tool/releases/download/dist/{file_name}",
                data,
            )
        nifti_object = Nifti1Image.from_filename(data)
        file_name_without_extension = ".".join(file_name.split(".")[:-1])
        output_file_name = f"tmp/{file_name_without_extension}-step-size-{step_size}-iterations-{iterations}.glb"  # noqa: E501
    else:
        nifti_object = Nifti1Image.from_bytes(bytearray(data))
        output_file_name = "output.glb"
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
    output: bytes = trimesh.exchange.export.export_mesh(tm, output_file_name)
    return output


async def on_click_convert_button(_: str) -> None:
    convert_button = document.getElementById("convert-button")
    convert_button.disabled = True
    laplacian_smoothing_iterations_input_range = document.getElementById(
        "laplacian-smoothing-iterations-input-range",
    )
    laplacian_smoothing_iterations_input_range.disabled = True
    load_nifti_file_input_file = document.getElementById("load-nifti-file-input-file")
    load_nifti_file_input_file.disabled = True
    marching_cubes_step_size_input_range = document.getElementById(
        "marching-cubes-step-size-input-range",
    )
    marching_cubes_step_size_input_range.disabled = True
    processing_div = document.getElementById("processing-div")
    processing_div.textContent = (
        "Converting NIfTI to GLB. It might take a few minutes..."
    )
    marching_cubes_step_size = int(marching_cubes_step_size_input_range.value)
    laplacian_smoothing_iterations = int(
        laplacian_smoothing_iterations_input_range.value,
    )
    file_list = load_nifti_file_input_file.files.to_py()
    for file in file_list:
        data = Uint8Array.new(await file.arrayBuffer())
        try:
            output = generate_mesh(
                data,
                laplacian_smoothing_iterations,
                marching_cubes_step_size,
            )
        except Exception:  # noqa: BLE001
            convert_button.disabled = False
            load_nifti_file_input_file.disabled = False
            marching_cubes_step_size_input_range.disabled = False
            laplacian_smoothing_iterations_input_range.disabled = False
            processing_div.textContent = "Out of memory. Try reducing the iterations and/or increasing the step size"  # noqa: E501
            sys.exit()
        content = pyodide.ffi.to_js(output)
        a = document.createElement("a")
        document.body.appendChild(a)
        a.style = "display: none"
        blob = Blob.new([content])
        url = window.URL.createObjectURL(blob)
        a.href = url
        file_name_without_extension = ".".join(file.name.split(".")[:-1])
        a.download = f"{file_name_without_extension}-step-size-{marching_cubes_step_size}-iterations-{laplacian_smoothing_iterations}.glb"  # noqa: E501
        a.click()
        window.URL.revokeObjectURL(url)
        convert_button.disabled = False
        load_nifti_file_input_file.disabled = False
        marching_cubes_step_size_input_range.disabled = False
        laplacian_smoothing_iterations_input_range.disabled = False
        processing_div.textContent = "Conversion done."


def main() -> None:
    add_event_listener(
        document.getElementById("convert-button"),
        "click",
        on_click_convert_button,
    )


if __name__ == "__main__":
    main()
