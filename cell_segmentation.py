#Segmentation of cells

'''Segmentation of cells based on edge (i.e. membrane) signal.
For this segmentation pipeline, it is recommended to have a strong membrane marker. 
It uses nulcear labels as seeds for a watershed segmentation'''
def edge_segment(cyto, label_nuclei):
    # Rescaling data
    from skimage.exposure import rescale_intensity
    rescaled_cyto = rescale_intensity(cyto)

    # Convert an image to unsigned byte format, with values in [0, 255].
    from bit_depth import convert
    import numpy as np
    cyto_int8 = convert(rescaled_cyto, 0, 255, target_type=np.uint8)
    
    import napari_segment_blobs_and_things_with_membranes as nsbatwm
    cell_labels = nsbatwm.seeded_watershed(cyto_int8, label_nuclei)
    
    return cell_labels


'''Segmentation of cells based on cytoplasmic signal plus nuclear signal'''
def cyto_segment(cytoplasm, label_nuclei, gaussian_sigma, min_cell_size, max_cell_size, closing_radius):
    import numpy as np
    # Convert an image to unsigned byte format, with values in [0, 255].
    from bit_depth import convert
    cyto_int8 = convert(cytoplasm, 0, 255, target_type=np.uint8)
    
    # Rescaling data
    from skimage.exposure import rescale_intensity
    #rescaled_cyto = rescale_intensity(cyto_int8)  # Stretching image on the full range of pixel intensitites.
    #rescaled_cyto = cyto_int8*50
    rescaled_cyto = cyto_int8
    
    from skimage.morphology import white_tophat, disk
    # Top-hat filter to subtract background
    #bg_substract = white_tophat(rescaled_cyto)
    
    # Applying a gaussian filter and thresholding
    from skimage.filters import threshold_li, threshold_otsu, gaussian, threshold_sauvola, threshold_minimum
    transformed_cyto = gaussian(rescaled_cyto, sigma=gaussian_sigma)
    
    from skimage.restoration import denoise_bilateral
    #transformed_cyto = denoise_bilateral(transformed_cyto, sigma_color=None, sigma_spatial=5)
    threshold_cyto = threshold_li(transformed_cyto)  # Calculate a threshold value
    
    # Thresholding and masking
    mask_cyto = np.zeros(transformed_cyto.shape)
    mask_cyto[transformed_cyto > threshold_cyto] = 255
    
    # Dilate cells, fill holes, and remove objects touching the border
    from skimage.morphology import binary_dilation, binary_closing, closing, isotropic_closing
    from scipy import ndimage as ndi
    #dilated_mask = binary_dilation(filtered_mask, mode='max')
    #filled_mask = ndi.binary_fill_holes(filtered_mask)
    closed_mask = isotropic_closing(mask_cyto, radius = closing_radius)
    
    # apply watershed
    from skimage.segmentation import watershed
    from skimage.feature import peak_local_max
    markers = label_nuclei
    cell_labels = watershed(-transformed_cyto, markers=markers, mask=closed_mask, connectivity=2, watershed_line=True)
    
    # Filter cells based on size
    from size_filter import remove_small, remove_large
    filtered_mask = remove_small(cell_labels, min_cell_size)
    filtered_mask = remove_large(filtered_mask, max_cell_size)
    
    from skimage.measure import label
    filtered_mask = label(filtered_mask)

    return filtered_mask


'''Segmentation of cells based on whole cell signal.
For this segmentation pipeline, it is recommended to have a homogenous and strong cell signal.'''
def cell_segment(cyto):
    import numpy as np
    # Rescaling data
    from skimage.exposure import rescale_intensity
    rescaled_cyto = rescale_intensity(cyto)  # Stretching image on the full range of pixel intensitites.

    # Convert an image to unsigned byte format, with values in [0, 255].
    from bit_depth import convert
    cyto_int8 = convert(rescaled_cyto, 0, 255, target_type=np.uint8)

    # Applying a gaussian filter and thresholding
    from skimage.filters import threshold_li, threshold_otsu, gaussian
    transformed_cyto = gaussian(cyto_int8, sigma=2)
    threshold_cyto = threshold_li(transformed_cyto)  # Calculate a threshold value

    # Thresholding and masking
    mask_cyto = np.zeros(transformed_cyto.shape)
    mask_cyto[transformed_cyto > threshold_cyto] = 255

    # Filter cells based on size
    from size_filter import remove_small, remove_large
    min_cell_size = 1000 #Arbitrary. it will depend on the data.
    filtered_mask = remove_small(mask_cyto, min_cell_size)

    # Dilate cells, fill holes, and remove objects touching the border
    from skimage.morphology import binary_dilation, binary_closing
    from scipy import ndimage as ndi
    # filtered_mask = binary_closing(filtered_mask)
    filtered_mask = binary_dilation(filtered_mask)
    filtered_mask = ndi.binary_fill_holes(filtered_mask)

    # apply watershed
    from skimage.segmentation import watershed
    from skimage.feature import peak_local_max
    distance = ndi.distance_transform_edt(filtered_mask)  # compute the distance image
    coords = peak_local_max(distance, min_distance=40, labels=filtered_mask)  # use the distance image to find local maxima
    _, inds = np.unique(distance[coords[:, 0], coords[:, 1]], return_index=True)  # make sure they are unique
    coords = coords[inds, :]
    mask = np.zeros(distance.shape, dtype=bool)
    mask[tuple(coords.T)] = True  # make an image with 1's where local maxima are
    markers, _ = ndi.label(mask)
    cell_labels = watershed(-distance, markers, mask=filtered_mask, watershed_line=True)  # perform watershed
    return cell_labels


'''Segmentation of cells with ML model Cellpose.'''
def cellpose_segment(cyto):
    from cellpose import models
    from cellpose import plot

    # DEFINE CELLPOSE MODEL
    model = models.Cellpose(model_type='cyto')  # model_type='cyto' or model_type='nuclei'

    # Running the models
    masks, flows, styles, diams = model.eval(cyto, diameter=100, flow_threshold=None, channels=[0, 0])
    #channels=[0, 0] for grayscale images
    return masks


