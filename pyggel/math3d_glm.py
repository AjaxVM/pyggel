
import glm


class Vec3(object):
    def __init__(self, *args):
        self.representation = glm.vec3(*args)

    @property
    def x(self):
        return self.representation.x

    @property
    def y(self):
        return self.representation.y

    @property
    def z(self):
        return self.representation.z
    

    # math functions/properties
    @property
    def magnitude(self):
        # return math.sqrt(self.x**2 + self.y**2 + self.z**2)
        return glm.magnitude(self.representation)

    def dot(self, other):
        # just here for clarity if needed
        # return self * other
        return Vec3(glm.dot(self.representation, other.representation))

    @property
    def normalized(self):
        # mag = self.magnitude
        # return Vec3(
        #     self.x / mag if self.x else 0,
        #     self.y / mag if self.y else 0,
        #     self.z / mag if self.z else 0
        # )
        return Vec3(glm.normalize(self.representation))

    def cross(self, other):
        # return Vec3(
        #     self.y * other.z - self.z * other.y,
        #     self.z * other.x - self.x * other.z,
        #     self.x * other.y - self.y * other.x
        # )
        return Vec3(glm.cross(self.representation, other.representation))

    def normalize(self):
        # mag = self.magnitude
        # if self.x:
        #     self.x = self.x / mag
        # if self.y:
        #     self.y = self.y / mag
        # if self.z:
        #     self.z = self.z / mag
        # return self
        self.representation = glm.normalize(self.representation)

    # standard math operations
    def __add__(self, other):
        other = Vec3.cast(other)
        # return Vec3(self.x + other.x, self.y + other.y, self.z + other.z)
        return Vec3(self.representation + other.representation)

    def __iadd__(self, other):
        other = Vec3.cast(other)
        # self.x += other.x
        # self.y += other.y
        # self.z += other.z
        self.representation = self.representation + other.representation
        return self

    def __sub__(self, other):
        other = Vec3.cast(other)
        # return Vec3(self.x - other.x, self.y - other.y, self.z - other.z)
        return Vec3(self.representation - other.representation)

    def __isub__(self, other):
        other = Vec3.cast(other)
        # self.x -= other.x
        # self.y -= other.y
        # self.z -= other.z
        self.representation = self.representation - other.representation
        return self

    def __mul__(self, other):
        if isinstance(other, Mat4):
            # # todo
            # x = self.x
            # y = self.y
            # z = self.z

            # m = other.representation

            # ox = x * m[0][0] + y * m[1][0] + z * m[2][0] + m[3][0]
            # oy = x * m[0][1] + y * m[1][1] + z * m[2][1] + m[3][1]
            # oz = x * m[0][2] + y * m[1][2] + z * m[2][2] + m[3][2]
            # return Vec3(ox, oy, oz)
            return Vec3((other.representation * glm.vec4(self.representation, 1)).xyz)
        other = Vec3.cast(other)
        # return Vec3(self.x * other.x, self.y * other.y, self.z * other.z)
        return Vec3(glm.dot(self.representation, other.representation))

    def __imul__(self, other):
        if isinstance(other, Mat4):
            # self.x, self.y, self.z = tuple(self * other)
            self.representation = (other.representation * glm.vec4(self.representation, 1)).xyz
            return self
        other = Vec3.cast(other)
        # self.x *= other.x
        # self.y *= other.y
        # self.z *= other.z
        self.representation = glm.dot(self.representation, other.representation)
        return self

    def __truediv__(self, other):
        other = Vec3.cast(other)
        # return Vec3(self.x / other.x, self.y / other.y, self.z / other.z)
        return Vec3(self.representation / other.representation)

    def __itruediv__(self, other):
        other = Vec3.cast(other)
        # self.x /= other.x
        # self.y /= other.y
        # self.z /= other.z
        self.representation = self.representation / other.representation
        return self

    def __eq__(self, other):
        other = Vec3.cast(other)
        # return self.x == other.x and self.y == other.y and self.z == other.z
        return glm.equal(self.representation, other.representation)

    def __ne__(self, other):
        other = Vec3.cast(other)
        # return self.x != other.x or self.y != other.y or self.z != other.z
        return glm.notEqual(self.representation, other.representation)

    def __neg__(self):
        # return Vec3(self.x * -1, self.y * -1, self.z * -1)
        return Vec3(-self.representation)

    def __str__(self):
        # return "Vec3 (x%6.2f, y%6.2f, z%6.2f)" % (self.x, self.y, self.z)
        return "Vec3 (x%6.2f, y%6.2f, z%6.2f)" % (self.representation.x, self.representation.y, self.representation.z)

    # helpers
    def __iter__(self):
        # yield self.x
        # yield self.y
        # yield self.z
        return iter(self.representation)

    @staticmethod
    def cast(thing):
        return thing if isinstance(thing, Vec3) else Vec3(thing)


class Mat4(object):
    def __init__(self, *args):
        # if nothing is passed just fall back to identity
        self.representation = glm.mat4(*args)

    def translate(self, pos):
        # self.representation = numpy.matmul(self.representation, numpy.array(
        #     (
        #         (1, 0, 0, pos.x),
        #         (0, 1, 0, pos.y),
        #         (0, 0, 1, pos.z),
        #         (0, 0, 0, 1)
        #     )
        # ))

        self.representation = glm.translate(self.representation, pos)
        return self

    def scale(self, size):
        # self.representation = numpy.matmul(self.representation, numpy.array(
        #     (
        #         (size.x, 0, 0, 0),
        #         (0, size.y, 0, 0),
        #         (0, 0, size.z, 0),
        #         (0, 0, 0, 1)
        #     )
        # ))

        self.representation = glm.scale(self.representation, size)

        return self

    def rotate(self, angles):
        # xc = math.cos(angles.x)
        # xs = math.sin(angles.x)

        # yc = math.cos(angles.y)
        # ys = math.sin(angles.y)

        # zc = math.cos(angles.z)
        # zs = math.sin(angles.z)

        # self.representation = numpy.matmul(self.representation, numpy.array(
        #     (
        #         (yc * zc, -zs,     ys,      0),
        #         (zs,      xc * zc, -xs,     0),
        #         (-ys,     xs,      xc * yc, 0),
        #         (0,       0,       0,       1)
        #     ),
        #     'f'
        # ))

        # rep = self.representation
        # rot = Vec3(angles)

        # if rot.x:
        #     c = math.cos(rot.x)
        #     s = math.sin(rot.x)
        #     rep = numpy.matmul(rep, numpy.array(
        #         (
        #             (1, 0, 0, 0),
        #             (0, c, -s, 0),
        #             (0, s, c, 0),
        #             (0, 0, 0, 1)
        #         ),
        #         'f'
        #     ))

        # if rot.y:
        #     c = math.cos(rot.y)
        #     s = math.sin(rot.y)
        #     rep = numpy.matmul(rep, numpy.array(
        #         (
        #             (c, 0, s, 0),
        #             (0, 1, 0, 0),
        #             (-s, 0, c, 0),
        #             (0, 0, 0, 1)
        #         ),
        #         'f'
        #     ))

        # if rot.z:
        #     c = math.cos(rot.z)
        #     s = math.sin(rot.z)
        #     rep = numpy.matmul(rep, numpy.array(
        #         (
        #             (c, -s, 0, 0),
        #             (s, c, 0, 0),
        #             (0, 0, 1, 0),
        #             (0, 0, 0, 1)
        #         ),
        #         'f'
        #     ))

        # self.representation = rep

        self.representation = glm.rotate(self.rotation, angles.x, glm.vec3(1, 0, 0))
        self.representation = glm.rotate(self.rotation, angles.y, glm.vec3(0, 1, 0))
        self.representation = glm.rotate(self.rotation, angles.z, glm.vec3(0, 0, 1))

        return self

    def rotate_axis(self, radianAngle, axis='x'):
        # c = math.cos(radianAngle)
        # s = math.sin(radianAngle)

        # x = axis == 'x'
        # y = axis == 'y'
        # z = axis == 'z'

        # self.representation = numpy.matmul(self.representation, numpy.array(
        #     (
        #         (1 if x else c, -s if z else 0, s if y else 0, 0),
        #         (s if z else 0, 1 if y else c, -s if x else 0, 0),
        #         (-s if y else 0, s if x else 0, 1 if z else c, 0),
        #         (0, 0, 0, 1)
        #     ),
        #     'f'
        # ))

        if axis == 'x':
            rot = vec3(1, 0, 0)
        if axis == 'y':
            rot = vec3(0, 1, 0)
        if axis == 'z':
            rot = vec3(0, 0, 1)
        self.representation = glm.rotate(self.representation, radianAngle, rot)
        return self

    def __mul__(self, other):
        if isinstance(other, Vec3):
            # return other * self
            return Vec3(self.representation * other.representation)
        # return Mat4(numpy.matmul(self.representation, other.representation))
        return Mat4(self.representation * other.representation)

    def __imul__(self, other):
        # self.representation = numpy.matmul(
        #     self.representation, other.representation)
        self.representation = self.representation * other.representation
        return self

    # builders
    @staticmethod
    def from_identity():
        # return Mat4(numpy.identity(4))
        return Mat4(1)

    @staticmethod
    def from_transform(position=None, rotation=None, scale=None):
        # position = position or Vec3(0)
        # rotation = rotation or Vec3(0)
        # scale = scale or Vec3(1)

        # xc = math.cos(rotation.x)
        # xs = math.sin(rotation.x)

        # yc = math.cos(rotation.y)
        # ys = math.sin(rotation.y)

        # zc = math.cos(rotation.z)
        # zs = math.sin(rotation.z)

        # return Mat4(numpy.array(
        #     (
        #         (yc * zc * scale.x, zs * scale.x, -ys * scale.x, position.x),
        #         (-zs * scale.y, xc * zc * scale.y, xs * scale.y, position.y),
        #         (ys * scale.z, -xs * scale.z, xc * yc * scale.z, position.z),
        #         (0, 0, 0, 1)
        #     ),
        #     'f'
        # ))
        # return Mat4(numpy.array(
        #     (
        #         (scale.x, 0, 0, position.x),
        #         (0, scale.y, 0, position.y),
        #         (0, 0, scale.z, position.z),
        #         (0, 0, 0, 1)
        #     ),
        #     'f'
        # )).rotate(rotation)

        mat = Mat4(1)
        mat.translate(glm.vec3(position or 0))
        mat.rotate(glm.vec3(rotation or 0))
        mat.scale(glm.vec3(scale or 1))

        return mat

    @staticmethod
    def from_perspective(fov, aspect, near, far):
        # half_fov = math.tan(math.radians(fov * 0.5))
        # z_range = near - far

        # return Mat4(numpy.array(
        #     (
        #         (1.0 / half_fov * aspect, 0, 0, 0),
        #         (0, 1 / half_fov, 0, 0),
        #         (0, 0, (-near - far) / z_range, 2.0 * far * near / z_range),
        #         (0, 0, 1, 0)
        #     ),
        #     'f'
        # ))
        return Mat4(glm.perspective(math.radians(fov), aspect, near, far))

    @staticmethod
    def from_ortho(size, near, far):
        # x_max = size[0] - 1
        # y_max = size[1] - 1
        # z_range = (-1.0 / far) if far else 0

        # return Mat4(numpy.array(
        #     (
        #         (2.0 / x_max, 0, 0, -1),
        #         (0, -2.0 / y_max, 0, 1),
        #         (0, 0, z_range, 0),
        #         (0, 0, 0, 1)
        #     ),
        #     'f'
        # ))
        return Mat4(glm.ortho(size, near, far))
