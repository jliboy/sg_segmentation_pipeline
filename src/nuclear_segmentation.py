#Segmentation of nuclei via thresholding and watershed
def nuclear_segment(nuclei, min_nuclear_size, min_distance, gaussian_nuclei, dilation_radius):
    import numpy as np
    # Rescaling data
    from skimage.exposure import rescale_intensity
    #rescaled_nuclei = rescale_intensity(nuclei)  # Stretching image on the full range of pixel intensitites.
    #rescaled_nuclei = nuclei*50
    rescaled_nuclei = nuclei
    
    # Convert an image to unsigned byte format, with values in [0, 255].
    from bit_depth import convert
    nuclei_int8 = convert(rescaled_nuclei, 0, 255, target_type=np.uint8)

    # Applying a gaussian filter
    from skimage.filters import gaussian, threshold_otsu, threshold_li
    transformed_nuclei = gaussian(nuclei_int8, sigma=gaussian_nuclei)

    # Li threshold
    threshold_nuclei = threshold_li(transformed_nuclei)  # Calculate a threshold value. Choose a method that fits best for your data

    # Thresholding and masking
    mask_nuclei = np.zeros(transformed_nuclei.shape)
    mask_nuclei[transformed_nuclei > threshold_nuclei] = 255

    # Dilate nuclei, fill holes, and remove objects touching the border
    from skimage.morphology import binary_dilation, binary_closing, isotropic_dilation
    from scipy import ndimage
    from skimage.segmentation import clear_border
    from skimage.measure import label

    mask_nuclei = isotropic_dilation(mask_nuclei, radius=dilation_radius)
    mask_nuclei = ndimage.binary_fill_holes(mask_nuclei)
    #mask_nuclei = clear_border(mask_nuclei)

    # Filter nuclei based on size
    from size_filter import remove_small, remove_large
    filtered_nuclei = remove_small(mask_nuclei, min_nuclear_size)

    # apply watershed
    from skimage.segmentation import watershed
    from skimage.feature import peak_local_max
    distance = ndimage.distance_transform_edt(filtered_nuclei)  # compute the distance image
    coords = peak_local_max(distance, min_distance=min_distance, labels=filtered_nuclei)  # use the distance image to find local maxima
    mask = np.zeros(distance.shape, dtype=bool)
    mask[tuple(coords.T)] = True  # make an image with 1's where local maxima are
    markers, _ = ndimage.label(mask)
    label_nuclei = watershed(-distance, markers, mask=filtered_nuclei, watershed_line=True)  # perform watershed

    return label_nuclei