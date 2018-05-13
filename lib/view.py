
import numpy
from .math3d import Vec3, Mat4

class View(object):
    def __init__(self, fov, displaySize, zNear, zFar):
        self._fov = fov
        self._displaySize = displaySize
        self._zNear = zNear
        self._zFar = zFar

        self._dirty = True
        self._matrix = None

    def dirty(self):
        self._dirty = True

    @property
    def matrix(self):
        if self._dirty:
            self._buildMatrix()
            self._dirty = False

        return self._matrix

    def _buildMatrix(self):
        return Mat4.from_identity()

    @property
    def fov(self):
        return self._fov

    @fov.setter
    def fov(self, value):
        self._fov = value
        self._dirty = True

    @property
    def displaySize(self):
        return self._displaySize

    @displaySize.setter
    def displaySize(self, value):
        self._displaySize = value
        self._dirty = True

    @property
    def zNear(self):
        return self._zNear

    @zNear.setter
    def zNear(self, value):
        self._zNear = value
        self._dirty = True

    @property
    def zFar(self):
        return self._zFar

    @zFar.setter
    def zFar(self, value):
        self._zFar = value
        self._dirty = True

class PerspectiveView(View):

    def _buildMatrix(self):
        zNear = self._zNear
        zFar = self._zFar
        aspect = 1.0*self._displaySize[0]/self._displaySize[1]
        zRange = zNear-zFar
        halfFov = numpy.tan(numpy.radians(self._fov * 0.5))

        self._matrix = Mat4(numpy.array(
            (
                (1.0 / halfFov * aspect, 0, 0, 0),
                (0, 1 / halfFov, 0, 0),
                (0, 0, (-zNear - zFar) / zRange, 2.0 * zFar * zNear / zRange),
                (0, 0, 1, 0)
            ),
            'f'
        ))

#TODO update each camera with data needed to billboard sprites properly

class Camera(object):
    def __init__(self, position=None, rotation=None):
        # todo should enforce vec3 for arguments
        self._position = position or Vec3()
        self._rotation = rotation or Vec3()

        self._dirty = True
        self._matrix = None

    def _buildMatrix(self):
        self._matrix = Mat4.from_identity()

    @property
    def matrix(self):
        if self._dirty:
            self._buildMatrix()
            self._dirty = False

        return self._matrix

    @property
    def position(self):
        return self._position
    @position.setter
    def position(self, value):
        self._position = value
        self._dirty = True

    @property
    def rotation(self):
        return self._rotation
    @rotation.setter
    def rotation(self, value):
        self._rotation = value
        self._dirty = True

class LookFromCamera(Camera):
    def _buildMatrix(self):
        mat4 = Mat4.fromIdentity()
        mat4.rotate(self._rotation)
        mat4.translate(self._position * -1)
        self._matrix = mat4

class LookAtCamera(Camera):
    def __init__(self, position=None, rotation=None, distance=0):
        super(LookAtCamera, self).__init__(position, rotation)
        self._distance = distance

    def _buildMatrix(self):
        mat4 = Mat4.from_identity()
        mat4.translate(Vec3(0, 0, self._distance))
        mat4.rotate(self._rotation)
        mat4.translate(self._position * -1)
        self._matrix = mat4

    @property
    def distance(self):
        return self._distance
    @distance.setter
    def distance(self, value):
        self.distance = value
        self._dirty = True

