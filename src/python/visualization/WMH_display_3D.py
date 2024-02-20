import gl
import sys
print(sys.version)
print(gl.version())
gl.resetdefaults()

#gl.loadimage(r'F:\Projects\WMH_segmentation\derivatives\Population\vessels\MNI152_T1_1mm.nii')
gl.loadimage('spm152')

gl.overlayload(r'E:\Projects\WMH_segmentation\derivatives\Population\sum_PWMH.nii.gz')
gl.colorname (1,"6warm")

gl.overlayload(r'E:\Projects\WMH_segmentation\derivatives\Population\sum_DWMH.nii.gz')
gl.colorname (2,"7cool")

gl.cutout(0.0, 0.45, 0.5, 0.75, 1.0, 1.0)

gl.savebmp(r'E:\Projects\WMH_segmentation\derivatives\Population\WMH_segmentation_display_3D.png')
