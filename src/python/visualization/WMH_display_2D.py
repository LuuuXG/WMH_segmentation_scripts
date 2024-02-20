import gl
import sys
print(sys.version)
print(gl.version())
gl.resetdefaults()

gl.loadimage('spm152')

gl.overlayload(r'E:\Projects\WMH_segmentation\derivatives\Population\sum_PWMH.nii.gz')
gl.colorname (1,"6warm")

gl.overlayload(r'E:\Projects\WMH_segmentation\derivatives\Population\sum_DWMH.nii.gz')
gl.colorname (2,"7cool")

gl.mosaic(" H 0 V 0 A 16 18 20 22 24 26; 28 30 32 34 36 38; 40 42 44 46 46 48");

gl.savebmp(r'E:\Projects\WMH_segmentation\derivatives\Population\WMH_segmentation_display_2D')
