import btrack
from skimage.io import imread

# load your segmentation data
segmentation = imread(r"C:\Users\jamel\Downloads\B3-5 moco good.tif")

# create btrack objects (with properties) from the segmentation data
# (you can also calculate properties, based on scikit-image regionprops)
objects = btrack.utils.segmentation_to_objects(
  segmentation, properties=('area', )
)

# initialise a tracker session using a context manager
with btrack.BayesianTracker() as tracker:

  # configure the tracker using a config file
  tracker.configure('/path/to/your/models/cell_config.json')

  # append the objects to be tracked
  tracker.append(objects)

  # set the volume (Z axis volume limits default to [-1e5, 1e5] for 2D data)
  tracker.volume = ((0, 1200), (0, 1600))

  # track them (in interactive mode)
  tracker.track_interactive(step_size=100)

  # generate hypotheses and run the global optimizer
  tracker.optimize()

  # store the data in an HDF5 file
  tracker.export('/path/to/tracks.h5', obj_type='obj_type_1')

  # get the tracks as a python list
  tracks = tracker.tracks

  # optional: get the data in a format for napari
  data, properties, graph = tracker.to_napari()