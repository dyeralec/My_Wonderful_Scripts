import xml.etree.ElementTree as ET
import os
import json
import csv

def opencsv(filename):
    with open(filename, 'rb') as f:
        dreader = csv.DictReader(f)
        csvdata = list(dreader)
        return csvdata, dreader

def openxml(xmlfilename):
    xmlelement = ET.parse(xmlfilename)
    root = xmlelement.getroot()
    return root

def listfiles(directory):
    xmlfiles = []
    for path, dirs, files in os.walk(directory):
        for f in files:
            if f.endswith(".xml"):
                xmlfiles.append(f)
    return xmlfiles

if __name__=="__main__":
    
    main_dir = r'R:\GEOWorkspace\C_Projects\BOEM IAA\BOEM_IAA_Database'
    
    for filename in os.listdir(main_dir):
        
        if filename == "1. Database Notes.txt":
            continue
        
        if filename.endswith('.txt'):
            
            name = filename
            
            dataoutput = {}
            metadata = {}
            
            print("converting data from csv to json...")
            with open(os.path.join(main_dir,filename), 'r') as f:
                lines = f.readlines()
                for l in lines:
                    
                    if 'Data Name' in l:
                        dataoutput['LayerName'] = l.split(': ')[1].replace('\n','')
                        layer_name = l.split(': ')[1].replace('\n','')
                    if 'Data Format' in l:
                        metadata['SpatialType'] = l.split(': ')[1].replace('\n','')
                    if 'Brief Description' in l:
                        metadata['LayerDescription'] = l.split(': ')[1].replace('\n','')
                    if 'Data Source Information' in l:
                        metadata['Source'] = l.split(': ')[1].replace('\n','')
                    if 'Weblink' in l:
                        metadata['SourceWebsite'] = l.split(': ')[1].replace('\n', '')
                    if 'Acquisition date' in l:
                        metadata['LastUpdate'] = l.split(': ')[1].replace('\n', '')
        
                    metadata['LayerFileName'] = name.replace('.txt','.shp')
                    
                sendtojson = {}
                sendtojson['Data'] = []
                dataoutput['Metadata'] = metadata
                sendtojson['Data'].append(dataoutput)
                #print sendtojson
                print("saving {} to json file...".format(layer_name))
                with open('{}_metadata'.format(os.path.join(main_dir,layer_name)), 'w') as outfile:
                    json.dump(sendtojson, outfile, indent=4)
    print("-- complete --")
