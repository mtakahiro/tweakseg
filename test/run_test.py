from tweakseg.tweakseg import add_source,save_segmap,extend_segmap    
from astropy.io import fits
import matplotlib.pyplot as plt


if __name__ == "__main__":
    '''
    '''
    # Testing;
    # !! Assumng that input files are from Grizli !!
    file_seg = 'jw01324001001-ir_seg.fits'
    file_cat = 'jw01324001001-ir.cat.fits'

    fd_seg = fits.open(file_seg)[0].data
    hd_seg = fits.open(file_seg)[0].header
    fd_cat = fits.open(file_cat)[1].data

    # Output file;
    file_output = 'test_seg.fits'
    file_cat_output = 'test_cat.fits'

    # 1. case where you want to expand your segmap of a specific source;
    if True:
        print('1. Expanding existing segmap;')
        plt.imshow(fd_seg)
        plt.xlim(1240,1280)
        plt.ylim(1220,1260)
        plt.title('Original segment')
        plt.show()

        id_targ = 3132
        radius = 15

        # You don't want to touch catalog in this case;
        fd_seg_new, _ = extend_segmap(fd_seg, id_targ, radius=radius, coords=None, override=True, file_cat=None)
        plt.imshow(fd_seg_new)
        plt.xlim(1240,1280)
        plt.ylim(1220,1260)
        plt.title('Updated segment')
        plt.show()
        plt.close()

    # 2. case where you want to inject a new circular segmap of a specific source;
    if True:
        print('2. Adding new segmap;')
        id_targ = 30000
        radius = 5

        # Should be
        coords = [1216, 1244]
        plt.imshow(fd_seg)
        plt.xlim(1200,1230)
        plt.ylim(1220,1260)
        plt.title('Original segment')
        plt.show()

        fd_seg_new, file_cat_new = extend_segmap(fd_seg_new, id_targ, radius=radius, coords=coords, override=True, file_cat=file_cat, file_cat_out=file_cat_output)
        plt.imshow(fd_seg_new)
        plt.xlim(1200,1230)
        plt.ylim(1220,1260)
        plt.title('Updated segment')
        plt.show()
        plt.close()


    # 3. Case where you want to add specific regions by an input polygon files    
    # !! Make sure to have one region file per object; 
    if True:
        file_polygon = 'targets_ds9.reg'
        id_targ = 50000

        # Should be
        plt.imshow(fd_seg)
        plt.xlim(1540,1800)
        plt.ylim(1082,1280)
        plt.title('Original segment')
        plt.show()

        fd_seg_new, file_cat_new = extend_segmap(fd_seg_new, id_targ, coords=None, override=True, file_region=file_polygon, 
            hd_seg=hd_seg, file_cat=file_cat_new, file_cat_out=file_cat_output)

        plt.imshow(fd_seg_new)
        plt.xlim(1540,1800)
        plt.ylim(1082,1280)
        plt.title('Updated segment')
        plt.show()

    save_segmap(fd_seg_new, file_output=file_output, hdr=hd_seg)
    #save_catalog(fd_cat_new, file_output=file_cat_output, hdr=hd_seg)
