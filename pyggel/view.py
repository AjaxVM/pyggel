
from .math3d import Vec3, Mat4


class View(object):
    def __init__(self, fov, display_size, z_near, z_far):
        self._fov = fov
        self._display_size = display_size
        self._z_near = z_near
        self._z_far = z_far

        self._dirty = True
        self._matrix = None

    def dirty(self):
        self._dirty = True

    @property
    def matrix(self):
        if self._dirty:
            self._build_matrix()
            self._dirty = False

        return self._matrix

    def _build_matrix(self):
        return Mat4.from_identity()

    @property
    def fov(self):
        return self._fov

    @fov.setter
    def fov(self, value):
        self._fov = value
        self._dirty = True

    @property
    def display_size(self):
        return self._display_size

    @display_size.setter
    def display_size(self, value):
        self._display_size = value
        self._dirty = True

    @property
    def z_near(self):
        return self._z_near

    @z_near.setter
    def z_near(self, value):
        self._z_near = value
        self._dirty = True

    @property
    def z_far(self):
        return self._z_far

    @z_far.setter
    def z_far(self, value):
        self._z_far = value
        self._dirty = True


class PerspectiveView(View):

    def _build_matrix(self):
        aspect = 1.0 * self._display_size[0] / self._display_size[1]
        self._matrix = Mat4.from_perspective(self._fov, aspect, self._z_near, self._z_far)


class View2D(View):
    def __init__(self, display_size, depth=1):
        # depth is how many units in the z (positive) you want to allow, so we can use depth buffer (possibly)
        super(View2D, self).__init__(0, display_size, 0, depth)

    @property
    def depth(self):
        return self._z_far

    @depth.setter
    def depth(self, value):
        self._z_far = value
        self._dirty = True

    def _build_matrix(self):
        self._matrix = Mat4.from_ortho(self._display_size, self._z_near, self._z_far)

# TODO update each camera with data needed to billboard sprites properly


class Camera(object):
    def __init__(self, position=None, rotation=None):
        # todo should enforce vec3 for arguments
        self._position = position or Vec3()
        self._rotation = rotation or Vec3()

        self._dirty = True
        self._matrix = None

    def _build_matrix(self):
        self._matrix = Mat4.from_identity()

    @property
    def matrix(self):
        if self._dirty:
            self._build_matrix()
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

    @property
    def world_position(self):
        return self._position


class LookFromCamera(Camera):
    def _build_matrix(self):
        # TODO: this can be optimized
        mat4 = Mat4.from_identity()
        mat4.rotate(self._rotation)
        mat4.translate(self._position * -1)
        self._matrix = mat4


class LookAtCamera(Camera):
    def __init__(self, position=None, rotation=None, distance=0):
        super(LookAtCamera, self).__init__(position, rotation)
        self._distance = distance

    def _build_matrix(self):
        # TODO: this can probably be optimized
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

    @property
    def world_position(self):
        return self.matrix * Vec3(0, 0, self.distance)


class Camera2D(Camera):
    def __init__(self, display_size, position=None, rotation=None):
        super(Camera2D, self).__init__(position, rotation)
        self._display_size = display_size
        self._offset_position = Vec3(display_size[0] * 0.5, display_size[1] * 0.5, 0)

    @property
    def display_size(self):
        return self._display_size

    @display_size.setter
    def display_size(self, value):
        self._display_size = value
        self._offset_position = Vec3(value[0] * 0.5, value[1] * 0.5, 0)
        self._dirty = True

    @property
    def world_position(self):
        return self._position + self._offset_position

    def _build_matrix(self):
        # todo: this can be optimized
        mat4 = Mat4.from_identity()
        mat4.rotate(self._rotation)
        mat4.translate(self._position * self._offset_position * -1)
        self._matrix = mat4
