
import numpy
# from .math3d import Vec3, Mat4
import math
from glm import vec3, vec4, mat4, translate, rotate, scale, perspective, ortho


class View(object):
    def __init__(self, fov, display_size, zNear, zFar):
        self._fov = fov
        self._display_size = display_size
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
        # return Mat4.from_identity()
        return mat4(1)

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
        # zNear = self._zNear
        # zFar = self._zFar
        aspect = 1.0 * self._display_size[0] / self._display_size[1]
        # zRange = zNear - zFar
        # halfFov = numpy.tan(numpy.radians(self._fov * 0.5))

        # self._matrix = Mat4(numpy.array(
        #     (
        #         (1.0 / halfFov * aspect, 0, 0, 0),
        #         (0, 1 / halfFov, 0, 0),
        #         (0, 0, (-zNear - zFar) / zRange, 2.0 * zFar * zNear / zRange),
        #         (0, 0, 1, 0)
        #     ),
        #     'f'
        # ))

        self._matrix = perspective(math.radians(self._fov), 1.0 * self._display_size[0] / self._display_size[1], self._zNear, self._zFar)

        # self._matrix = mat4(1.0 / halfFov * aspect, 0, 0, 0, 0, 1.0/halfFov, 0, 0, 0, 0, (-zNear-zFar)/zRange, 2.0*zFar*zNear/zRange, 0, 0, 1, 0)
        # self._matrix = mat4(
        #     vec4(1.0 / halfFov * aspect, 0, 0, 0),
        #     vec4(0, 1/halfFov, 0, 0),
        #     vec4(0, 0, (-zNear-zFar)/zRange, 2.0*zFar*zNear/zRange),
        #     vec4(0, 0, 1, 0)
        # )

        # self._matrix = Mat4.from_persepctive(self._fov, aspect, self._zNear, self._zFar)


class View2D(View):
    def __init__(self, display_size, depth=1):
        # depth is how many units in the z (positive) you want to allow, so we can use depth buffer (possibly)
        super(View2D, self).__init__(0, display_size, 0, depth)

    @property
    def depth(self):
        return self._zFar

    @depth.setter
    def depth(self, value):
        self._zFar = value
        self._dirty = True

    def _buildMatrix(self):
        # zFar = self._zFar
        # xMax = self._display_size[0] - 1
        # yMax = self._display_size[1] - 1
        # zRange = (-1.0 / zFar) if zFar else 0

        # self._matrix = Mat4(numpy.array(
        #     (
        #         (2.0 / xMax, 0, 0, -1),
        #         (0, -2.0 / yMax, 0, 1),
        #         (0, 0, zRange, 0),
        #         (0, 0, 0, 1)
        #     ),
        #     'f'
        # ))
        self._matrix = ortho(0, self._display_size[0], self._display_size[1], 0, self._zNear, self._zFar)
        # self._matrix = Mat4.from_ortho(self._display_size, self._zNear, self._zFar)

# TODO update each camera with data needed to billboard sprites properly


class Camera(object):
    def __init__(self, position=None, rotation=None):
        # todo should enforce vec3 for arguments
        # self._position = position or Vec3()
        self._position = position or vec3()
        # self._rotation = rotation or Vec3()
        self._rotation = rotation or vec3()

        self._dirty = True
        self._matrix = None

    def _buildMatrix(self):
        # self._matrix = Mat4.from_identity()
        self._matrix = mat4(1)

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

    @property
    def world_position(self):
        return self._position


class LookFromCamera(Camera):
    def _buildMatrix(self):
        # TODO: this can be optimized
        # mat4 = Mat4.from_identity()
        # mat4.rotate(self._rotation)
        # mat4.translate(self._position * -1)
        # self._matrix = mat4
        mat = mat4(1)
        mat = rotate(mat, self._rotation.x, vec3(1,0,0))
        mat = rotate(mat, self._rotation.y, vec3(0,1,0))
        mat = rotate(mat, self._rotation.z, vec3(0,0,1))
        mat = translate(mat, -self._position)
        self._matrix = mat


class LookAtCamera(Camera):
    def __init__(self, position=None, rotation=None, distance=0):
        super(LookAtCamera, self).__init__(position, rotation)
        self._distance = distance

    def _buildMatrix(self):
        # TODO: this can probably be optimized
        # mat4 = Mat4.from_identity()
        # mat4.translate(Vec3(0, 0, self._distance))
        # mat4.rotate(self._rotation)
        # mat4.translate(self._position * -1)
        # self._matrix = mat4
        mat = mat4(1)
        mat = translate(mat, vec3(0, 0, -self._distance))
        # mat = rotate(mat, self._rotation)
        mat = rotate(mat, self._rotation.x, vec3(1,0,0))
        mat = rotate(mat, self._rotation.y, vec3(0,1,0))
        mat = rotate(mat, self._rotation.z, vec3(0,0,1))
        mat = translate(mat, -self._position)
        self._matrix = mat

    @property
    def distance(self):
        return self._distance

    @distance.setter
    def distance(self, value):
        self.distance = value
        self._dirty = True

    @property
    def world_position(self):
        # return Vec3(0, 0, -self.distance) * self.matrix
        return (self.matrix * vec4(0, 0, self.distance, 1)).xyz


class Camera2D(Camera):
    def __init__(self, display_size, position=None, rotation=None):
        super(Camera2D, self).__init__(position, rotation)
        self._display_size = display_size
        # self._offset_position = Vec3(display_size[0] * 0.5, display_size[1] * 0.5, 0)
        self._offset_position = vec3(display_size[0] * 0.5, display_size[1] * 0.5, 0)

    @property
    def display_size(self):
        return self._display_size

    @display_size.setter
    def display_size(self, value):
        self._display_size = value
        # self._offset_position = Vec3(value[0] * 0.5, value[1] * 0.5, 0)
        self._offset_position = vec3(value[0] * 0.5, value[1] * 0.5, 0)
        self._dirty = True

    @property
    def world_position(self):
        return self._position + self._offset_position

    def _buildMatrix(self):
        # todo: this can be optimized
        # mat4 = Mat4.from_identity()
        # mat4.rotate(self._rotation)
        # mat4.translate(self._position * self._offset_position * -1)
        # self._matrix = mat4
        mat = mat4(1)
        # mat = rotate(mat, self._rotation)
        mat = rotate(mat, self._rotation.x, vec3(1,0,0))
        mat = rotate(mat, self._rotation.y, vec3(0,1,0))
        mat = rotate(mat, self._rotation.z, vec3(0,0,1))
        mat = translate(mat, self._position * self._offset_position * -1)
        self._matrix = mat
