#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep  8 15:46:01 2024

@author: joselito
"""
import numpy as np 
import pandas as pd
from skimage.measure import label, regionprops_table

#Function for calculating properties of objects in image
def object_count(label_obj: np.array, obj_intensity: np.array):
    """
    Count the number of objects in given image.

    :param obj: np.array, 0-and-1
    :return: count_obj: number of objects.
    """
    obj_prop = regionprops_table(label_obj, obj_intensity, properties=('label', 'area', 'area_bbox', 'area_convex', 
                                                                       'area_filled', 'axis_major_length', 'axis_minor_length',
                                                                       'eccentricity', 'equivalent_diameter_area', 'extent', 'feret_diameter_max',
                                                                       'intensity_max', 'intensity_mean', 'intensity_min', 'intensity_std',
                                                                      'num_pixels', 'orientation', 'perimeter', 'perimeter_crofton', 'solidity'))
    obj_prop = pd.DataFrame.from_dict(obj_prop, orient='columns')
    count_obj = len(obj_prop)
    
    return count_obj, obj_prop
