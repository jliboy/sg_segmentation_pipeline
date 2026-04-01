import numpy as np 
from skimage.measure import regionprops, label

def matching_parent(parent_obj, child_obj):
    # Matching cells to parent nuclei
    # Get region properties
    parent_props = regionprops(parent_obj)
    child_props = regionprops(child_obj)
    
    # Create a dictionary to hold parent-child relationships
    child_to_parent = {}
    
    # For each granule, find which cell it belongs to
    for child in child_props:
        # Get coordinates of the pixels in this granule
        child_label = child.label
        coords = child.coords
        # Find cell labels at those coordinates
        overlapping_parents = parent_obj[coords[:, 0], coords[:, 1]]
        # Most common overlapping cell label is the parent
        overlapping_parents = overlapping_parents[overlapping_parents > 0]
        
        if len(overlapping_parents) == 0:
            parent_cell = None  # granule outside any cell
        else:
            parent_cell = np.bincount(overlapping_parents).argmax()
    
        child_to_parent[child_label] = parent_cell

    return child_to_parent