from js import Blob, document, Uint8Array, window
from python.main import generate_mesh
import pyodide
import time


async def process_file(event):
    start_time = time.time()
    loadNiftiFileInputFile = document.getElementById('loadNiftiFileInputFile')
    loadNiftiFileInputFile.disabled = True
    processing_div = document.getElementById('processingDiv')
    processing_div.textContent = 'Converting NifTi to GLB. It might take a few minutes...'
    fileList = event.target.files.to_py()
    for f in fileList:
        data = Uint8Array.new(await f.arrayBuffer())
        output = generate_mesh(data)
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
        loadNiftiFileInputFile.disabled = False
        processing_div.textContent = f'Convertion done in {(time.time() - start_time):.1f} seconds.'


loadNiftiFileInputFile = document.getElementById('loadNiftiFileInputFile')
loadNiftiFileInputFile.addEventListener('change', pyodide.ffi.create_proxy(process_file), False)
