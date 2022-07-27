import os,sys
import numpy as np
import matplotlib.pyplot as plt
import pyregion

from astropy.io import fits
from astropy.table import Table
import astropy.wcs as wcs
from astropy.wcs.utils import pixel_to_skycoord
from astropy.wcs import WCS

def add_source(file_cat, id, mag_auto=None, ext=1, file_out=None, f_phot=True, 
    copy_flux=True, id_orig=0, sky=[None,None]):
    '''
    '''
    if file_out == None:
        file_out = 'tmp_cat.fits'

    hdu = fits.open(file_cat)
    keys = []
    for key in hdu[ext].data.columns:
        keys.append(key)
        # Get original info;
        if id_orig > 0:
            if key.name == 'NUMBER' or key.name == 'ID' or key.name == 'id':
                iix = np.where(hdu[ext].data[key.name] == id_orig)
                if len(iix[0])==0:
                    id_orig = 0
    
    if id_orig > 0:
        print('Original id is %d'%id_orig)

    hdu_new = hdu.copy()
    new_row = []
    for key in keys:
        if key.name == 'NUMBER' or key.name == 'ID' or key.name == 'id':
            new_row.append(id)
        elif key.name == 'X_WORLD' and sky[0] != None:
            new_row.append(sky[0])
        elif key.name == 'Y_WORLD' and sky[1] != None:
            new_row.append(sky[1])
        else:
            if id_orig > 0:
                new_row.append(hdu[ext].data[key.name][iix])
            else:
                new_row.append(0)

    t = Table(hdu[ext].data)
    t.add_row(new_row)

    file_tmp = 'tmp.fits'
    t.write(file_tmp, format='fits',overwrite=True)
    fd_data = fits.open(file_tmp)[1]

    prihdu = fits.PrimaryHDU(header=hdu[0].header)
    prihdu.writeto(file_out, overwrite=True)
    # Add data;
    fits.append(file_out, fd_data.data, fd_data.header)
    # Add wcs;
    if not f_phot:
        fits.append(file_out, hdu_new[2].data, hdu_new[2].header)

    # Remove temp files;
    os.system('rm %s'%file_tmp)

    return file_out


def create_circular_mask(h, w, center=None, radius=None):
    '''
    This provides a circular aperture mask for a given shape.

    Parameters
    ----------
    h : float
        height, in pixel
    w : float
        width, in pixel
    center : list
        contains (x,y) (!not y,x!)
    '''
    if center is None: # use the middle of the image
        center = (int(w/2), int(h/2))
    if radius is None: # use the smallest distance between the center and image walls
        radius = min(center[0], center[1], w-center[0], h-center[1])

    Y, X = np.ogrid[:h, :w]
    dist_from_center = np.sqrt((X - center[0])**2 + (Y-center[1])**2)

    mask = dist_from_center <= radius
    return mask


def save_segmap(fd_seg, file_output, hdr=None):
    '''
    '''
    if file_output == None:
        file_output = 'test_seg.fits'

    fits.writeto(filename=file_output, data=fd_seg, header=hdr, overwrite=True)
    return True


def extend_segmap(fd_seg, id_targ, radius=5, coords=None, override=True, 
    file_region=None, hd_seg=None, file_cat=None, mag_auto=20, file_cat_out=None):
    '''
    Purpose
    -------
    Expand segmentation of a specific source to the input radius from the source center. 
    If radius does not exceed segmap, nothing will happen. 

    Parameters
    ----------
    fd_seg : float 2d array. 
        seg data array. E.g. fd_seg = fits.open(file)['seg'].data

    override : bool
        if True, the script will override any pixels that belong other sources within the new region.

    '''
    id_orig = None
    if file_region==None:
        pos = np.where(fd_seg == id_targ)
        if len(pos[0]) == 0 and coords == None:
            print('%d is not found in the input segmap nor coords are specified. Exiting.'%id_targ)
            sys.exit()

        # Get segment center if not provided;
        if coords == None:
            xcen,ycen = np.median(pos[1]),np.median(pos[0])
        else:
            xcen,ycen = coords

        h, w = fd_seg.shape
        circle_mask = create_circular_mask(h, w, center=[xcen,ycen], radius=radius)
        new_mask = (circle_mask)
        id_orig = np.max(fd_seg[new_mask])

        # Then fill the pixel with id;
        fd_seg_new = fd_seg.copy()
        if override:
            print('Overriding is on.')
            new_mask = (circle_mask)
            fd_seg_new[new_mask] = id_targ
        else:
            new_mask = np.where( (circle_mask) & ((fd_seg == id_targ) | (fd_seg == 0))) 
            fd_seg_new[new_mask] = id_targ

    else:
        print('Polygon is provided.')
        fd_seg_new = fd_seg.copy()
        fd_region = pyregion.open(file_region)
        mask = fd_region.get_mask(shape=(np.shape(fd_seg)), header=hd_seg)
        region_mask = np.where(mask == True)
        id_orig = np.max(fd_seg[new_mask])
        
        # Then fill the pixel with id;
        if override:
            print('Overriding is on.')
            new_mask = (region_mask)
            fd_seg_new[new_mask] = id_targ
        else:
            new_mask = np.where( (mask) & ((fd_seg == id_targ) | (fd_seg == 0))) 
            fd_seg_new[new_mask] = id_targ

        xcen,ycen = np.median(region_mask[1]),np.median(region_mask[0])

    # Calculate RADEC;
    w = WCS(hd_seg)
    sky = w.pixel_to_world(xcen,ycen)

    # Catalog part;
    if not file_cat == None:
        file_cat_new = add_source(file_cat, id_targ, mag_auto=mag_auto, file_out=file_cat_out, 
            id_orig=id_orig, sky=sky)
        return fd_seg_new,file_cat_new
    else:
        return fd_seg_new, None

