import sys

import pyodide
from js import Blob, Uint8Array, document, window
from main import generate_mesh
from pyodide.ffi.wrappers import add_event_listener


async def process_file(_: str) -> None:
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
    add_event_listener(document.getElementById("convert-button"), "click", process_file)


if __name__ == "__main__":
    main()
