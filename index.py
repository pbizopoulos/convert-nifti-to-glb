from js import Blob, document, Uint8Array, window
from pyodide import create_proxy, to_js
from skimage.measure import marching_cubes
import asyncio
import nibabel as nib
import pyodide
import trimesh


async def process_file(event):
    fileList = event.target.files.to_py()
    for f in fileList:
        data = Uint8Array.new(await f.arrayBuffer())
        nifti_object = nib.Nifti1Image.from_bytes(bytearray(data))
        (verts, faces, *_) = marching_cubes(nifti_object.get_fdata(), 0.5, spacing=(1.0, 1.0, 10.0), step_size=1)
        tm = trimesh.Trimesh(vertices=verts, faces=faces)
        tm.apply_translation(-tm.center_mass)
        trimesh.repair.fix_inversion(tm)
        trimesh.repair.fill_holes(tm)
        trimesh.smoothing.filter_laplacian(tm, iterations=1)
        tm.visual.face_colors = [31,119,180,127]
        output = trimesh.exchange.export.export_mesh(tm, 'output.glb')
        content = to_js(output)
        a = document.createElement('a')
        document.body.appendChild(a)
        a.style = 'display: none'
        blob = Blob.new([content])
        url = window.URL.createObjectURL(blob)
        a.href = url
        a.download = 'output.glb'
        a.click()
        window.URL.revokeObjectURL(url)


loadNiftiFileInputFile = document.getElementById('loadNiftiFileInputFile')
loadNiftiFileInputFile.addEventListener('change', create_proxy(process_file), False)
