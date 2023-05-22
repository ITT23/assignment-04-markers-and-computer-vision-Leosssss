## Liu (11/15P)

### 1 Perspecitve Transformation (2/5P)

 * load and display image
   * there is delay on startup, but then the image is displayed (+1)
 * corner selection
   * works (+1)
 * perspective transformation works
   * worked after I fixed a few things (+1)
   * red dots from selection process are still in the image (-1)
 * command line parameters and shortcuts
   * those are not command line parameters (-1)

The submitted version of the program did not work as it crashed because of the `cv2.destroyAllWindows()` in `mouse_callback()`. (-1)

### 2 AR Game (9/10P)

 * ROI extraction
   * works
 * reliable object tracking
   * no pixel-perfect collision (-1)
   * otherwise fine
 * game mechanics
   * ok
 * performance
   * ok
 * does not crash
   * ok
