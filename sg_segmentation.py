'''Segmentation of stress granules'''
def sg_segment(cyto, blob_threshold, min_sigma, max_sigma, min_sg_size, max_sg_size):
    import numpy as np
    
    # Rescaling data
    from skimage.exposure import rescale_intensity
    rescaled_cyto = rescale_intensity(cyto)  # Stretching image on the full range of pixel intensitites.

    # Convert an image to unsigned byte format, with values in [0, 255].
    from bit_depth import convert
    cyto_int8 = convert(rescaled_cyto, 0, 255, target_type=np.uint8)

    # Applying a gaussian filter and thresholding
    from skimage.filters import gaussian
    from skimage.feature import blob_log
    from skimage.draw import disk
    transformed_cyto = gaussian(cyto_int8, sigma=2)
    
    blobs = blob_log(transformed_cyto, min_sigma=min_sigma, max_sigma=max_sigma, threshold=blob_threshold)
    # min_sigma - keep low to detect small blobs (i.e. 1)
    # max_sigma - keep high to detect bigger blobs (i.e 50)
    
    # Each blob is (y, x, radius)
    # You can convert radius to diameter: diameter ≈ sqrt(2) * sigma

    # Create empty mask
    mask_sg = np.zeros_like(transformed_cyto, dtype=bool)

    # Fill mask with disks at blob positions
    for y, x, r in blobs:
        rr, cc = disk((y, x), radius=r*np.sqrt(2), shape=transformed_cyto.shape)
        mask_sg[rr, cc] = True

    # Filter SGs based on size
    from size_filter import remove_small, remove_large
    filtered_sg = remove_small(mask_sg, min_sg_size)
    filtered_sg = remove_large(filtered_sg, max_sg_size)
    
    from skimage.measure import label
    sg_labeled = label(filtered_sg)
    
    return sg_labeled