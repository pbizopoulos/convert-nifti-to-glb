from js import Blob, document, Uint8Array, window
from main import generate_mesh
from pyodide.ffi.wrappers import add_event_listener
import pyodide
import sys
import time


async def process_file(event):
    start_time = time.time()
    convertButton = document.getElementById('convert-button')
    convertButton.disabled = True
    laplacianSmoothingIterationsInputRange = document.getElementById('laplacian-smoothing-iterations-input-range')
    laplacianSmoothingIterationsInputRange.disabled = True
    loadNiftiFileInputFile = document.getElementById('load-nifti-file-input-file')
    loadNiftiFileInputFile.disabled = True
    marchingCubesStepSizeInputRange = document.getElementById('marching-cubes-step-size-input-range')
    marchingCubesStepSizeInputRange.disabled = True
    processing_div = document.getElementById('processing-div')
    processing_div.textContent = 'Converting NifTi to GLB. It might take a few minutes...'
    marching_cubes_step_size = int(marchingCubesStepSizeInputRange.value)
    laplacian_smoothing_iterations = int(laplacianSmoothingIterationsInputRange.value)
    fileList = loadNiftiFileInputFile.files.to_py()
    for file in fileList:
        data = Uint8Array.new(await file.arrayBuffer())
        try:
            output = generate_mesh(data, laplacian_smoothing_iterations, marching_cubes_step_size)
        except Exception as exception:
            convertButton.disabled = False
            loadNiftiFileInputFile.disabled = False
            marchingCubesStepSizeInputRange.disabled = False
            laplacianSmoothingIterationsInputRange.disabled = False
            processing_div.textContent = 'Out of memory. Try reducing the iterations and/or increasing the step size'
            sys.exit()
        content = pyodide.ffi.to_js(output)
        a = document.createElement('a')
        document.body.appendChild(a)
        a.style = 'display: none'
        blob = Blob.new([content])
        url = window.URL.createObjectURL(blob)
        a.href = url
        file_name_without_extension = '.'.join(file.name.split('.')[:-1])
        a.download = f'{file_name_without_extension}-step-size-{marching_cubes_step_size}-iterations-{laplacian_smoothing_iterations}.glb'
        a.click()
        window.URL.revokeObjectURL(url)
        convertButton.disabled = False
        loadNiftiFileInputFile.disabled = False
        marchingCubesStepSizeInputRange.disabled = False
        laplacianSmoothingIterationsInputRange.disabled = False
        processing_div.textContent = f'Conversion done in {(time.time() - start_time):.1f} seconds.'

def main():
    add_event_listener(document.getElementById('convert-button'), 'click', process_file)


if __name__ == '__main__':
    main()
