# -*- coding: utf-8 -*-
"""
Created on Thu Mar  2 09:29:13 2023

@author: Marie
"""
'''
import tifffile
with tifffile.TiffFile('image.tif') as tif:
    sem = tif.fei_metadata['System']['SystemType'] #SEM
    detector = tif.fei_metadata['Detectors']['Name'] #Detector
    accvolt = tif.fei_metadata['EBeam']['HV'] #U_0
    current = tif.fei_metadata['EBeam']['BeamCurrent'] #I_0
    wd = tif.fei_metadata['EBeam']['WD'] #WD
    magnif = tif.fei_metadata['Image']['MagCanvasRealWidth'] #Magnif
    pxres_x = tif.fei_metadata['Image']['ResolutionX'] #Auflösung
    pxres_y = tif.fei_metadata['Image']['ResolutionY'] #Auflösung
    pxsize = tif.fei_metadata['Scan']['PixelWidth'] #phys pix size
    print(sem, detector, accvolt, current, wd, magnif, pxres_x, pxres_y, pxsize)
'''

import os
import tifffile
import csv

data_path = r"C:\Users\Marie\Documents\AI Promotion\3 AP1 - Datenakquise\HCCI"
input_path = os.path.join(data_path, 'Pranav')
output_file = os.path.join(data_path, 'HCCI_REM_Daten_Pranav.csv')
i=0

metadata = []

with open(output_file, 'w', newline='') as csvfile:

    writer=csv.writer(csvfile, delimiter=';')
    description=['Lfd. Nr.', 'Dateiname', 'REM', 'Detektor', 'Spannung /kV', 'Strahlstrom /nA', 'WD /mm', 'X /px', 'Y /px', 'Pixelweite /um']
    writer.writerow(description)
    
    for root, dirs, files in os.walk(input_path):
        for file_name in files:
            # Check if file is a TIFF file
            if file_name.endswith('.tif') or file_name.endswith('.tiff'):
                # Get the full path of the file
                file_path = os.path.join(root, file_name)
                
                # Apply your metadata extraction code
                try:
                    with tifffile.TiffFile(file_path) as tif:
                    # your code here
                        sem = tif.fei_metadata['System']['SystemType'] #SEM
                        detector = tif.fei_metadata['Detectors']['Name'] #Detector
                        accvolt = tif.fei_metadata['EBeam']['HV'] #U_0
                        accvolt = accvolt/1000
                        current = tif.fei_metadata['EBeam']['BeamCurrent'] #I_0
                        current = current * (10**9)
                        wd = float(tif.fei_metadata['EBeam']['WD']) #WD
                        wd = wd*1000
                        #magnif = tif.fei_metadata['Image']['MagCanvasRealWidth'] #Magnif
                        pxres_x = tif.fei_metadata['Image']['ResolutionX'] #Auflösung
                        pxres_y = tif.fei_metadata['Image']['ResolutionY'] #Auflösung
                        pxsize = tif.fei_metadata['Scan']['PixelWidth'] #phys pix size
                        pxsize = pxsize * (10**6)
                    
                        i = i+1
                        metadata = [i, file_name, sem, detector, accvolt, current, wd, pxres_x, pxres_y, pxsize]
                       # print(metadata)
                        #print (i)
                        #print(file_name)
                        #print(sem, detector, accvolt, current, wd, magnif, pxres_x, pxres_y, pxsize)
                except:
                    
                    continue
                
                writer.writerow(metadata)
              
csvfile.close()