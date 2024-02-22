import sys

import pyodide
from js import Blob, Uint8Array, document, window
from pyodide.ffi.wrappers import add_event_listener

from main import convert_nifti_to_glb  # type: ignore[attr-defined]


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
    if not file_list:
        return
    data = Uint8Array.new(await file_list.item(0).arrayBuffer())
    try:
        output = convert_nifti_to_glb(
            data,
            "output.glb",
            laplacian_smoothing_iterations,
            marching_cubes_step_size,
        )
    except Exception:  # noqa: BLE001
        convert_button.disabled = False
        load_nifti_file_input_file.disabled = False
        marching_cubes_step_size_input_range.disabled = False
        laplacian_smoothing_iterations_input_range.disabled = False
        processing_div.textContent = (
            "Out of memory. Try reducing the iterations and/or increasing the step size"
        )
        sys.exit()
    content = pyodide.ffi.to_js(output)
    a = document.createElement("a")
    document.body.appendChild(a)
    a.style = "display: none"
    blob = Blob.new([content])
    url = window.URL.createObjectURL(blob)
    a.href = url
    file_name_without_extension = ".".join(file_list.item(0).name.split(".")[:-1])
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
