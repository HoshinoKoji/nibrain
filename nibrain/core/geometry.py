#!/usr/bin/env python
from nibabel.streamlines import tck
from dipy.segment.clustering import QuickBundle
import numpy as np

class Points(object):
    """Points represent a collection of spatial ponits
    
    Attributes
    ----------
    coords:  Nx3 numpy array, points coordinates
    id: Nx1 numpy array,tuple or list, id for each point
    src: source image or surface obejct which the coords were dervied
    """
    def __init__(self, coords, id=None):
        """
        Parameters
        ----------
        coords:  Nx3 numpy array, points coordinates
        id: Nx1 numpy array, id for each point
        src: source image or surface obejct which the coords were dervied
        """

        self._coords  = coords
        if id is None:
            id = range(coords.shape[0])
        elif np.asarray(id).shape[0] != coords.shape[0]:
            raise ValueError("id length is not equal to the length of the coords")

        self._id = id

    @property
    def coords(self):
        return self._coords

    @coords.setter
    def coords(self, coords):
        assert coords.ndim == 2 and coords.shape[1] == 3, "coords should be N x 3 np array."
        self._coords = coords

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, id):
        self._id = id

    def merge(self, other):
        """ Merge other Points object into self
        
        Parameters
        ----------
        other: Points object to be merged

        Returns
        -------
        self: the merged object

        """
        assert isinstance(other, Points), "other should be a Points object"
        self.coords = np.vstack((self.coords, other.coords))
        self.id = np.vstack((self.id, other.id))
        self.id, idx = np.unique(self.id, return_index=True)
        self.coords = self.coords[idx,:]
        return self

    def intersect(self,other):
        """ Intersect with other Points object

        Parameters
        ----------
        other: Points object to be intersectd with this object

        Returns
        -------
        self: the intersected object

        """
        assert isinstance(other, Points), "other should be a Points object"
        idx = np.in1d(self.id, other.id)
        self.id = self.id[idx]
        self.coords = self.coords[idx,:]
        return self

    def exclude(self, other):
        """ Exclude other Points object from this object

        Parameters
        ----------
        other: Points object to be merged

        Returns
        -------
        self: the object after excluding others

        """
        assert isinstance(other, Points), "other should be a Points object"

        idx = np.logical_not(np.in1d(self.id, other.id))
        self.id = self.id[idx]
        self.coords = self.coords[idx,:]
        return self

    def get_center(self):
        """ Get the center of the points set
        
        Parameters
        ----------

        Returns
        -------
        center: 1x3 numpy array, the center coordinates

        """
        
        return np.mean(self.coords,axis=0)

class Lines(object):
    def __init__(self, coords, id=None):
        """
        Parameters
        ----------
        coords: geometry coords, a sequence of array.
        id: the id for each array.
        """
        if isinstance(coords, tck.ArraySequence):
            self._coords = coords
        elif coords.data.shape[1] == 3:
            self._coords = coords
        else:
            raise ValueError("Data dimension is false.")
        self._coords = coords
        if id is None:
            id = range(len(coords))
        elif np.asarray(id).shape[0] != len(coords):
            raise ValueError("id length is not equal to the length of the coords")
        self._id = id

    @property
    def coords(self):
        return self._coords

    @coords.setter
    def coords(self, coords):
        if isinstance(coords, tck.ArraySequence):
            self._coords = coords
        elif coords.data.shape[1] == 3:
            self._coords = coords
        else:
            raise ValueError("Data dimension is false.")

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, id):
        self._id = id

    def get_toi_data(self, toi=None):
        """Get the coordinates of the node within a toi

        Parameters
        ----------
        toi, a toi include the fiber id of interest
        if toi == None, return data from all vertices on the surface
        Returns
        -------
        data: NxT numpy array, scalar value from the toi
        """
        pass

    def get_toi_lines(self, toi=None):
        """ Get the coordinates of the node within a toi

        Parameters
        ----------
        toi, a toi include the fiber id of interest

        Returns
        -------
        lines: arraysequence, streamline from the toi
        """
        if toi == None:
            toi_lines = self.lines.streamlines
        else:
            toi_lines = [self.lines.streamlines[i] for i in toi]
        return toi_lines

    def merge(self, other):
        """ Merge other Lines into the Lines based on the line id.

        Parameters
        ----------
        other: Lines object, another lines
    axis: integer, 0 or 1

        Return
        ----------
        self: merged Lines
        """
        assert isinstance(other, Lines), "other should be a Lines object"
        self.coords = np.vstack((self.coords, other.coords))
        self.id = np.vstack((self.id, other.id))
        self.id, idx = np.unique(self.id, return_index=True)
        self.coords = self.coords[idx,:]
        pass

    def intersect(self,other):
        """ Intersect with other Lines based on the line id.

        Parameters
        ----------
        other: Lines object, another Lines 

        Return
        ----------
        self with intersection from two Lines
        """
        idx = np.in1d(self.id, other.id)
        self.id = self.id(idx)
        del self.coords[np.nonzero(np.logical_not(idx))]

    def exclude(self, other):
        """ Exclude other Lines from the current Lines based on the line id.

        Parameters
        ----------
        other: Lines object, another Lines 

        Return
        ----------
        self:  The Lines after excluding other Lines
        """
        idx = np.in1d(self.id, other.id)
        self.id = self.id(np.logical_not(idx))
        del self.coords[np.nonzero(idx)]

    def equidistant_resample(self, num_segment):
        """ Resample the Lines with eistantance points
        
        Parameters
        ----------
        num_segment: int, number of segment to be sampled

        Returns
        -------
        resample_result: N x num x 3 list of array,num is num_segment.
        """
        num_lines = range(len(self.coords))
        resample_result = []
        # Resample every fiber to num_segment points
        for i in num_lines:
            i_lines = self.coords[i]
            i_lines_len = len(i_lines)
            interval = (i_lines_len - 1) / (num_segment - 1)          #calculate the interval of every points
            resample_index = [int(round(num * interval)) for num in range(num_segment)]
            i_resample_result = [self.coords[i][point][:] for point in resample_index]
            resample_result.append(i_resample_result)
        return resample_result

    def skeleton(self,dis=500):
        """Find the skeletion of the line set

        Paraments:
        -------
        dis: the threshold of distance between two fiber,
             it controls whether the fibers will be clustering into one line set.
             default value = 500
        Returns
        -------
        fiber_skeleton: a centroid of fiber,a Line object
        """
        qb_streamline = QuickBundles(dis)
        fiber_clusters = qb_streamline.cluster(self.coords)
        fiber_skeleton = fiber_clusters.centroid
        return fiber_skeleton

class Mesh(object):
    """Mesh class represents geometry mesh
    
        Attributes
        ----------
        vertices
        faces

    """
    def __init__(self, vertices, faces):
        self.vertices = vertices
        self.faces = faces

    def __eq__(self, other):
        return  np.array_equal(self.vertices, self.vertices)