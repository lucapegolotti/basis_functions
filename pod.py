import os
import vtk
import numpy as np
from vtk.util.numpy_support import vtk_to_numpy as v2n
from vtk.util.numpy_support import numpy_to_vtk as n2v

def read_geo(fname):
    _, ext = os.path.splitext(fname)
    if ext == ".vtp":
        reader = vtk.vtkXMLPolyDataReader()
    elif ext == ".vtu":
        reader = vtk.vtkXMLUnstructuredGridReader()
    else:
        raise ValueError("File extension " + ext + " unknown.")
    reader.SetFileName(fname)
    reader.Update()
    return reader.GetOutput()

def pod(mat):
    C = np.matmul(mat.transpose(), mat)
    linalg.eig(C)

def get_velocities(geo):
    narrs = geo.GetPointData().GetNumberOfArrays()
    velocities = []

    count = 0
    for ind in range(narrs):
        name = geo.GetPointData().GetArrayName(ind)
        if 'velocity_' in name and not 'average_' in name:
            if count % 10 == 0:
                print(name)
                cur_velocity = v2n(geo.GetPointData().GetArray(ind))
                velocities.append(np.reshape(cur_velocity, cur_velocity.size))
                print(count)
            count = count + 1

    velocities = np.array(velocities)
    return velocities

def clean_geo(geo):
    narrs = geo.GetPointData().GetNumberOfArrays()
    velocities = []

    count = 0
    for ind in range(narrs):
        name = geo.GetPointData().GetArrayName(ind)
        if 'velocity_' in name and not 'average_' in name:
            if count % 10 == 0:
                print(name)
                cur_velocity = v2n(geo.GetPointData().GetArray(ind))
                velocities.append(np.reshape(cur_velocity, cur_velocity.size))
                print(count)
            count = count + 1


def write_geo(fname, input):
    """
    Write geometry to file
    Args:
        fname: file name
    """
    _, ext = os.path.splitext(fname)
    if ext == '.vtp':
        writer = vtk.vtkXMLPolyDataWriter()
    elif ext == '.vtu':
        writer = vtk.vtkXMLUnstructuredGridWriter()
    else:
        raise ValueError('File extension ' + ext + ' unknown.')
    writer.SetFileName(fname)
    writer.SetInputData(input)
    writer.Update()
    writer.Write()

def add_array(geo, name, array):
    arr = n2v(array)
    arr.SetName(name)
    geo.GetPointData().AddArray(arr)

if __name__ == "__main__":
    geo = read_geo('0075_1001.vtu')

    velocities = get_velocities(geo)
    svd = np.linalg.svd(velocities.transpose(), full_matrices=False)

    node_all = geo.GetPointData()
    for i in range(node_all.GetNumberOfArrays() - 1):
        node_all.RemoveArray(1)

    ncomps = int(svd[0].shape[0]/3)

    add_array(geo, 'mode_1', np.reshape(svd[0][:,0],(ncomps,3)))
    add_array(geo, 'mode_2', np.reshape(svd[0][:,1],(ncomps,3)))
    add_array(geo, 'mode_3', np.reshape(svd[0][:,2],(ncomps,3)))

    write_geo('test.vtu', geo)
