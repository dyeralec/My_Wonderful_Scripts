from osgeo import ogr

inGDB = r'R:\GEO Workspace\D_Users\81_Dyer\Environmental Sensitivity Index\ChesapeakeBay\biofile_ExtraFeatures.gdb'

# open input layer with driver
inDriver = ogr.GetDriverByName('FileGDB')
inDataSource = inDriver.Open(inGDB ,1)
inLayer = inDataSource.GetLayer('BENTHIC_dissolved')
# fids are unique, fids may be sorted or unsorted, fids may be consecutive or have gaps
# don't care about semantics, don't touch fids and their order, reuse fids
fids = []
vals = []
inLayer.ResetReading()
for f in inLayer:
	fid = f.GetFID()
	fids.append(fid)
	vals.append((f.GetField('RARNUM'), fid))
vals.sort()
# index as dict: {newfid: oldfid, ...}
ix = {fids[i]: vals[i][1] for i in xrange(len(fids))}

# swap features around in groups/rings
for fidstart in ix.keys():
	if fidstart not in ix: continue
	ftmp = inLayer.GetFeature(fidstart)
	fiddst = fidstart
	while True:
		fidsrc = ix.pop(fiddst)
		if fidsrc == fidstart: break
		f = inLayer.GetFeature(fidsrc)
		f.SetFID(fiddst)
		inLayer.SetFeature(f)
		fiddst = fidsrc
	ftmp.SetFID(fiddst)
	inLayer.SetFeature(ftmp)

inLayer.ResetReading()

# Save and close DataSources
inDriver = None
inDataSource = None
inLayer = None