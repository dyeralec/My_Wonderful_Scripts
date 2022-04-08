from scipy.io import loadmat
import numpy as np
from osgeo import osr
import os

def _coordsToVerts(xVals,yVals,transform):


    ret = []
    ext=[np.inf,-np.inf,np.inf,-np.inf]
    for x,y in zip(xVals[0],yVals[0]) if len(xVals.shape)>1 else zip(xVals,yVals):
        x,y,_ = transform.TransformPoint(float(x),float(y))
        ret+=[x,y]
        ext[0] = min(ext[0], x)
        ext[1] = max(ext[1], x)
        ext[2] = min(ext[2], y)
        ext[3] = max(ext[3], y)

    # close loop
    ret+=ret[0:2]
    return ret,ext

def loadMatlabLayerData(path, xyLbls):

    # set up conversions
    with open(r"P:\03_DataFinal\GOM\!SpatialReference\GomAlbers84.prj", 'r') as inFile:
        content = inFile.read()
        worldSref = osr.SpatialReference()
        worldSref.ImportFromWkt(content)

    localSref = osr.SpatialReference()
    localSref.ImportFromEPSG(4326) # WGS 84

    if hasattr(worldSref, 'SetAxisMappingStrategy'):
        worldSref.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
        localSref.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)

    transform = osr.CoordinateTransformation(localSref,worldSref)
    # assume custom format used by wind/wave/event bounds
    raw = loadMatlabData(path)

    verts = []
    polys = []
    offset = 0
    ext = [np.inf, -np.inf, np.inf, -np.inf]
    for xLbl,yLbl in xyLbls:
        vs,subExt=_coordsToVerts(raw[xLbl],raw[yLbl],transform)
        ext[0]=min(ext[0],subExt[0])
        ext[1] = max(ext[1], subExt[1])
        ext[2] = min(ext[2], subExt[2])
        ext[3] = max(ext[3], subExt[3])

        count = len(vs) // 2
        verts += vs
        polys.append([(offset, count,)])
        offset += count

    return np.array(verts,dtype=np.float32), polys, ext

def _getRegionExtents(verts):

    ext = [np.inf,-np.inf,np.inf,-np.inf]

    for x,y in verts.reshape([len(verts)//2,2]):
        ext[0] = min(ext[0], x)
        ext[1] = max(ext[1], x)
        ext[2] = min(ext[2], y)
        ext[3] = max(ext[3], y)

    return ext

def loadMatlabLayerExtents(path,xyLbls):

    verts,groups,exts = loadMatlabLayerData(path, xyLbls)
    exts=[]
    for rng in groups:
        offs,cnt=rng[0]
        offs*=2
        cnt*=2
        exts.append(_getRegionExtents(verts[offs:offs+cnt]))
    return exts


def loadMatlabLayer(path,scene,xyLbls,**kwargs):

    verts,polys,exts = loadMatlabLayerData(path, xyLbls)
    return scene.AddPolyLayer(verts,polys,exts,**kwargs),len(polys)

def loadMatlabData(path):

    return loadmat(path) # ,simplify_cells=True

if __name__ == '__main__':

    file_path = r"C:\Users\dyera\Downloads\oga-tool-test-distrib-09_2021\OGA\SmartToolDataPackage\ciiam\climatological_strength_attraction_jan.mat"

    a, b, c = loadMatlabLayerData(file_path, [['lonx0', 'latx0']])
    # a = loadMatlabData(file_path)
    print('stop')