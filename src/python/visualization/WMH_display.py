import gl
import sys
print(sys.version)
print(gl.version())
gl.resetdefaults()

gl.loadimage(r'E:\Projects\WMH_segmentation\derivatives\Population\vessels\MNI152_T1_1mm.nii')

gl.overlayload(r'E:\Projects\WMH_segmentation\derivatives\Population\vessels\sum_PWMH.nii.gz')
gl.colorname (1,"6warm")

gl.overlayload(r'E:\Projects\WMH_segmentation\derivatives\Population\vessels\sum_DWMH.nii.gz')
gl.colorname (2,"2green")

gl.mosaic("A L H 0 V 0.2 16 40");
