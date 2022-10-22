from nibabel import Nifti1Image
from os.path import isfile, join
from skimage.measure import marching_cubes
from urllib import request
import numpy as np
import trimesh


def generate_mesh(data):
    if isinstance(data, str):
        if not isfile(data):
            request.urlretrieve(f'https://github.com/pbizopoulos/semi-automatic-annotation-tool/releases/download/dist/{data.split("/")[1]}', data)
        nifti_object = Nifti1Image.from_filename(data)
        output_file_name = join('bin', 'output.glb')
    else:
        nifti_object = Nifti1Image.from_bytes(bytearray(data))
        output_file_name = 'output.glb'
    volume = nifti_object.get_fdata()
    volume = volume.astype('float32')
    if np.unique(volume).size == 2:
        (verts, faces, *_) = marching_cubes(volume, spacing=nifti_object.header.get_zooms(), step_size=1)
        tm = trimesh.base.Trimesh(vertices=verts, faces=faces, visual=trimesh.visual.TextureVisuals(material=trimesh.visual.material.PBRMaterial(alphaMode='BLEND', baseColorFactor=[31, 119, 180, 127])))
        tm.apply_scale(10 ** (-3))
        trimesh.repair.fix_inversion(tm)
        trimesh.repair.fill_holes(tm)
        trimesh.smoothing.filter_laplacian(tm, iterations=10)
    elif np.unique(volume).size == 3:
        volume[volume == 2] = 0
        (verts, faces, *_) = marching_cubes(volume, spacing=nifti_object.header.get_zooms(), step_size=1)
        tm = trimesh.base.Trimesh(vertices=verts, faces=faces, visual=trimesh.visual.TextureVisuals(material=trimesh.visual.material.PBRMaterial(alphaMode='BLEND', baseColorFactor=[31, 119, 180, 127])))
        tm.apply_scale(10 ** (-3))
        trimesh.repair.fix_inversion(tm)
        trimesh.repair.fill_holes(tm)
        volume = nifti_object.get_fdata()
        volume = volume.astype('float32')
        volume[volume == 1] = 0
        volume[volume == 2] = 1
        (verts2, faces2, *_) = marching_cubes(volume, spacing=nifti_object.header.get_zooms(), step_size=1)
        tm2 = trimesh.base.Trimesh(vertices=verts2, faces=faces2, visual=trimesh.visual.TextureVisuals(material=trimesh.visual.material.PBRMaterial(alphaMode='BLEND', baseColorFactor=[255, 0, 0, 127])))
        tm2.apply_scale(10 ** (-3))
        trimesh.repair.fix_inversion(tm2)
        trimesh.repair.fill_holes(tm2)
        tm = trimesh.util.concatenate([tm, tm2])
        tm.visual.material = tm.visual.material.to_pbr()
        tm.visual.material.alphaMode = 'BLEND'
        tm.visual.material.baseColorFactor[-1] = 127
    return trimesh.exchange.export.export_mesh(tm, output_file_name)


def main():
    generate_mesh(join('bin', 'masks.nii'))
    generate_mesh(join('bin', 'masks-multiclass.nii'))


if __name__ == '__main__':
    main()
