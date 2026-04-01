#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep  6 18:12:22 2024

@author: joselito
"""

#Functions for calculating min and max sizes of nuclei

import numpy as np
from skimage.morphology import remove_small_objects

def remove_small(obj: np.array, min_size):
    """
    Remove objects smaller than the specified size.

    Expects obj to be an integer image array with labeled objects, and removes objects
    smaller than min_size.

    :param obj: np.array, 0-and-1
    :param min_size: int, optional (default: 10)
                The smallest allowable object size.
    :return: out: nd.array, 0-and-1, same shape and type as input obj

    """

    obj_bool = np.array(obj, bool)
    obj_mask = remove_small_objects(obj_bool, min_size)
    out = np.zeros_like(obj)
    out[obj_mask] = 1

    return out


def remove_large(obj: np.array, max_size):
    """
    Remove objects larger than the specified size.

    Expects ar to be an integer image array with labeled objects, and removes objects
    larger than max_size.

    :param obj: np.array, 0-and-1
    :param max_size: int, optional (default: 1000)
                The largest allowable object size.
    :return: out: np.array, 0-and-1, same shape and type as input obj
    """


    obj_bool = np.array(obj, bool)
    obj_mask = remove_small_objects(obj_bool, max_size)
    out = obj.copy()
    out[obj_mask] = 0

    return out