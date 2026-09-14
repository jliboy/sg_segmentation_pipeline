#Code for segmeting cells and stress granules, and extracting properties of each.

#Reading images in the folder of interest. 
import os 
import glob
import tkinter as tk 
from tkinter import filedialog

root = tk.Tk()
root.withdraw()

directory_path = filedialog.askdirectory()
images_path = glob.glob(os.path.join(directory_path, "20x*"))

import sys
sys.path.append('src')

import numpy as np
import nd2reader as nd2
from bit_depth import convert
import pandas as pd
from regions_prop import object_count

from skimage.exposure import rescale_intensity
from skimage.color import label2rgb


nuclear_overlays = []
cell_overlays = []
sg_overlays = []
filename = [] #Saving the filename for each segmented image. 

cell_properties = [] #Save properties of cells
cell_count = [] #Saving count of cells per field of view
nuclear_properties = []
nuclear_count = []

SG_properties = [] #Save properties of cells
SG_count = [] #Saving count of cells per field of view

for img in images_path:
    data = nd2.ND2Reader(img)
    filename.append(os.path.basename(img))

    print(f"Processing the following file: {os.path.basename(img)}")
    for t in range(data.sizes['t']): #t corresponds to the time point.
        print(f"Time point: {t}/{data.sizes['t']-1}")

        for i in range(data.sizes['v']): #i corresponds to the field of view
            print(f"Field of view: {i}/{data.sizes['v']-1}")
            #Nuclear segmentation
            print("Segmenting nuclei...")
            from nuclear_segmentation import nuclear_segment
            nuclei = data.get_frame_2D(c=0, t=t, v=i) #Read the nuclear channel
            #c=0 correspond to the nuclear channel
            min_nuclear_size = 100
            min_distance = 15 #Minimum distance between nuclei
            gaussian_nuclei = 10 
            dilation_radius = 5 #Radius for dilation to connect fragmented nuclei
            label_nuclei = nuclear_segment(nuclei, min_nuclear_size, min_distance, gaussian_nuclei, dilation_radius)

            num_nuclei = label_nuclei.max()
            print("Number of segmented nuclei:", num_nuclei)
            
            #Cell segmentation
            from cell_segmentation import cyto_segment
            
            cytoplasm = data.get_frame_2D(c=1, t=t, v=i)
            #c=1 corresponds to the cytoplasmic channel
            gaussian_sigma = 5
            closing_radius = 10 #Radius for morphological closing to fill gaps in the cell segmentation
            
            #Cell segmentation using the segmented nuclei as seeds for watershed
            print("Segmenting cells...")
            segmented_cells = cyto_segment(cytoplasm, label_nuclei, gaussian_sigma, closing_radius)

            
            cell_overlay = label2rgb(segmented_cells, image=cytoplasm*50, bg_label=0)
            nuclear_overlay = label2rgb(label_nuclei, image=nuclei, bg_label=0)

            #Save images
            cell_overlays.append(cell_overlay)
            nuclear_overlays.append(nuclear_overlay)

            from cell_conditions import protein, treatment
            
            cyto_properties = object_count(segmented_cells, cytoplasm)
            cyto_properties[1]['field_view'] = i
            cyto_properties[1]['time'] = t
            
            #Matching filtered cells to original nuclei
            from matching_features import matching_parent
            cell_to_nucleus = matching_parent(segmented_cells, label_nuclei)
            cyto_properties[1]['label'] = cyto_properties[1]['label'].map(cell_to_nucleus)
            
            nuclei_properties = object_count(label_nuclei, nuclei)
            nuclei_properties[1]['field_view'] = i
            nuclei_properties[1]['time'] = t
            nuclei_properties[1]['protein'] = protein(i)
            nuclei_properties[1]['treatment'] = treatment(i)
            
            cell_count.append(cyto_properties[0])
            cell_properties.append(cyto_properties[1])
            nuclear_count.append(nuclei_properties[0])
            nuclear_properties.append(nuclei_properties[1])
            
            #Segmenting stress granules
            print("Segmenting stress granules...")
            from sg_segmentation import sg_segment
            
            blob_threshold = 0.075
            min_sigma = 1
            max_sigma = 10
            min_sg_size = 1
            max_sg_size = 100
            mask_sg = sg_segment(cytoplasm, blob_threshold, min_sigma, max_sigma, min_sg_size, max_sg_size)

            sg_overlay_mask = label2rgb(mask_sg, image=cytoplasm, bg_label=0)
            sg_overlays.append(sg_overlay_mask)

            sg_to_cell = matching_parent(mask_sg, segmented_cells)

            #Calculating properties
            granule_properties = object_count(mask_sg, cytoplasm)
            granule_properties[1]['label_cell'] = granule_properties[1]['label'].map(sg_to_cell)
            granule_properties[1]['protein'] = protein(i)
            granule_properties[1]['treatment'] = treatment(i)
            granule_properties[1]['field_view'] = i
            granule_properties[1]['time'] = t
            
            SG_properties.append(granule_properties[1])


 
#Concat list of dataframes into one single datafranme
cell_properties = pd.concat(cell_properties, axis=0)
nuclear_properties = pd.concat(nuclear_properties, axis=0)
SG_properties = pd.concat(SG_properties, axis=0)

#Merge cell and nuclear data
merge_properties = pd.merge(cell_properties, nuclear_properties, on = ['label', 'field_view', 'time'], how="outer", suffixes=('_cell', '_nuclear')).fillna(0)

merge_properties = merge_properties[merge_properties['label'] != 0] #Remove background label (0) from the merged properties dataframe

SG_count = pd.DataFrame({'label_cell': SG_properties["label_cell"],'field_view': SG_properties["field_view"],'time': SG_properties["time"], 'protein': SG_properties["protein"], 'treatment': SG_properties["treatment"]}).groupby(['label_cell','field_view', 'time', 'protein', 'treatment']).size().reset_index(name='SG_count_per_cell')
#Here I am counting stress granules per cell per frame.

merge_properties["label_cell"] = merge_properties["label"] #Create a new column in the merged properties dataframe to match the label of the cell for merging with SG count.

merge_properties = pd.merge(merge_properties, SG_count, on = ['label_cell', 'field_view', 'time', 'protein', 'treatment'], how="left").fillna(0)
#Here I am adding the stress granule count per cell to the merged properties dataframe.

#Save property tables into csv files
sg_path = os.path.join(directory_path, 'sg_properties.csv')
SG_properties.to_csv(sg_path, index=False)

cells_path = os.path.join(directory_path, 'cell_properties.csv')
merge_properties.to_csv(cells_path, index=False)

#Save overlays and segmented cells as numpy arrays
nuclear_overlays_array = np.array(nuclear_overlays)
nuclear_overlays_path = os.path.join(directory_path, 'nuclear_overlays.npy')
np.save(nuclear_overlays_path, nuclear_overlays_array)

cell_overlays_array = np.array(cell_overlays)
cell_overlays_path = os.path.join(directory_path, 'cell_overlays.npy')
np.save(cell_overlays_path, cell_overlays_array)

sg_overlays_array = np.array(sg_overlays)
sg_overlays_path = os.path.join(directory_path, 'sg_overlays.npy')
np.save(sg_overlays_path, sg_overlays_array)