# -*- coding: utf-8 -*-
"""
Created on Thu Nov 14 13:55:02 2019

@author: tinivella
"""

from __future__ import print_function

from desktopmagic.screengrab_win32 import (
	getDisplayRects, saveScreenToBmp, saveRectToBmp, getScreenAsImage,
	getRectAsImage, getDisplaysAsImages)

# Save the entire virtual screen as a BMP (no PIL required)
saveScreenToBmp('screencapture_entire.bmp')

# Save an arbitrary rectangle of the virtual screen as a BMP (no PIL required)
saveRectToBmp('screencapture_256_256.bmp', rect=(0, 0, 256, 256))

# Save the entire virtual screen as a PNG
entireScreen = getScreenAsImage()
entireScreen.save('screencapture_entire.png', format='png')

# Get bounding rectangles for all displays, in display order
print("Display rects are:", getDisplayRects())
# -> something like [(0, 0, 1280, 1024), (-1280, 0, 0, 1024), (1280, -176, 3200, 1024)]

# Capture an arbitrary rectangle of the virtual screen: (left, top, right, bottom)
rect256 = getRectAsImage((0, 0, 256, 256))
rect256.save('screencapture_256_256.png', format='png')

# Unsynchronized capture, one display at a time.
# If you need all displays, use getDisplaysAsImages() instead.
for displayNumber, rect in enumerate(getDisplayRects(), 1):
	imDisplay = getRectAsImage(rect)
	imDisplay.save('screencapture_unsync_display_%d.png' % (displayNumber,), format='png')

# Synchronized capture, entire virtual screen at once, cropped to one Image per display.
for displayNumber, im in enumerate(getDisplaysAsImages(), 1):
	im.save('screencapture_sync_display_%d.png' % (displayNumber,), format='png')