from js import Blob, document, Uint8Array, window
from nibabel import Nifti1Image
from skimage.measure import marching_cubes
import asyncio
import numpy as np
import pyodide
import time
import trimesh


async def process_file(event):
    start_time = time.time()
    loadNiftiFileInputFile = document.getElementById('loadNiftiFileInputFile')
    loadNiftiFileInputFile.disabled = True
    processing_div = document.getElementById('processingDiv')
    processing_div.textContent = 'Converting NifTi to GLB. It might take a few minutes...'
    fileList = event.target.files.to_py()
    for f in fileList:
        data = Uint8Array.new(await f.arrayBuffer())
        nifti_object = Nifti1Image.from_bytes(bytearray(data))
        volume = nifti_object.get_fdata()
        volume = volume.astype('float32')
        if np.unique(volume).size == 2:
            (verts, faces, *_) = marching_cubes(volume, 0.5, spacing=nifti_object.header.get_zooms(), step_size=1)
            tm = trimesh.Trimesh(vertices=verts, faces=faces)
            tm.apply_scale(10**(-3))
            trimesh.repair.fix_inversion(tm)
            trimesh.repair.fill_holes(tm)
            trimesh.smoothing.filter_laplacian(tm, iterations=10)
            tm.visual = trimesh.visual.TextureVisuals(material=trimesh.visual.material.PBRMaterial())
            tm.visual.material.alphaMode = 'BLEND'
            tm.visual.material.baseColorFactor = [31, 119, 180, 127]
        elif np.unique(volume).size == 3:
            volume[volume == 2] = 0
            (verts, faces, *_) = marching_cubes(volume, spacing=nifti_object.header.get_zooms(), step_size=1)
            tm = trimesh.Trimesh(vertices=verts, faces=faces)
            tm.apply_scale(10**(-3))
            trimesh.repair.fix_inversion(tm)
            trimesh.repair.fill_holes(tm)
            # trimesh.smoothing.filter_laplacian(tm, iterations=10)
            tm.visual = trimesh.visual.TextureVisuals(material=trimesh.visual.material.PBRMaterial())
            tm.visual.material.alphaMode = 'BLEND'
            tm.visual.material.baseColorFactor = [31, 119, 180, 127]
            volume = nifti_object.get_fdata()
            volume = volume.astype('float32')
            volume[volume == 1] = 0
            volume[volume == 2] = 1
            (verts2, faces2, *_) = marching_cubes(volume, spacing=nifti_object.header.get_zooms(), step_size=1)
            tm2 = trimesh.Trimesh(vertices=verts2, faces=faces2)
            tm2.apply_scale(10**(-3))
            trimesh.repair.fix_inversion(tm2)
            trimesh.repair.fill_holes(tm2)
            # trimesh.smoothing.filter_laplacian(tm2, iterations=10)
            tm2.visual = trimesh.visual.TextureVisuals(material=trimesh.visual.material.PBRMaterial())
            tm2.visual.material.alphaMode = 'BLEND'
            tm2.visual.material.baseColorFactor = [255, 0, 0, 127]
            tm = trimesh.util.concatenate([tm, tm2])
        output = trimesh.exchange.export.export_mesh(tm, 'glb')
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
