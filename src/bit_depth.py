# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

#Function for converting images with a different bit depth.
def convert(img, target_type_min, target_type_max, target_type):
    '''
    This function is inteded to normalize img and change the image to the specified target_type
      img: numpy array
      target_type_min: int
      target_type_max: int
      target_type: str, optins are: np.uint
    '''
    imin = img.min()
    imax = img.max()
    a = (target_type_max - target_type_min) / (imax - imin)
    b = target_type_max - a * imax
    new_img = (a * img + b).astype(target_type)
    return new_img