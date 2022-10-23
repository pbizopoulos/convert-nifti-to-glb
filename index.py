from js import Blob, document, Uint8Array, window
from main import generate_mesh
import pyodide
import time


async def process_file(event):
    start_time = time.time()
    convertButton = document.getElementById('convertButton')
    convertButton.disabled = True
    iterationsInputRange = document.getElementById('iterationsInputRange')
    iterationsInputRange.disabled = True
    loadNiftiFileInputFile = document.getElementById('loadNiftiFileInputFile')
    loadNiftiFileInputFile.disabled = True
    stepSizeInputRange = document.getElementById('stepSizeInputRange')
    stepSizeInputRange.disabled = True
    processing_div = document.getElementById('processingDiv')
    processing_div.textContent = 'Converting NifTi to GLB. It might take a few minutes...'
    step_size = int(stepSizeInputRange.value)
    iterations = int(iterationsInputRange.value)
    fileList = loadNiftiFileInputFile.files.to_py()
    for f in fileList:
        data = Uint8Array.new(await f.arrayBuffer())
        output = generate_mesh(data, step_size, iterations)
        content = pyodide.ffi.to_js(output)
        a = document.createElement('a')
        document.body.appendChild(a)
        a.style = 'display: none'
        blob = Blob.new([content])
        url = window.URL.createObjectURL(blob)
        a.href = url
        a.download = 'output.glb'
        a.click()
        window.URL.revokeObjectURL(url)
        convertButton.disabled = False
        loadNiftiFileInputFile.disabled = False
        stepSizeInputRange.disabled = False
        iterationsInputRange.disabled = False
        processing_div.textContent = f'Conversion done in {(time.time() - start_time):.1f} seconds.'

convertButton = document.getElementById('convertButton')
convertButton.addEventListener('click', pyodide.ffi.create_proxy(process_file), False)
