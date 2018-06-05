
import math
import numpy

class Vec3(object):
    def __init__(self, *args):
        if len(args) == 0:
            self.x = self.y = self.z = 0
        elif len(args) == 3:
            self.x, self.y, self.z = args
        elif len(args) == 1:
            other = args[0]
            if isinstance(other, Vec3):
                self.x = other.x
                self.y = other.y
                self.z = other.z
            elif isinstance(other, (list, tuple)):
                self.x, self.y, self.z = other
            elif isinstance(other, (int, float)):
                self.x = self.y = self.z = other
        else:
            raise TypeError('Invalid arguments for Vec3')

    @property
    def gl_args(self):
        return (self.x, self.y, self.z)

    # math functions/properties
    @property
    def magnitude(self):
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)

    def dot(self, other):
        # just here for clarity if needed
        return self * other

    @property
    def normalized(self):
        mag = self.magnitude
        return Vec3(
            self.x / mag if self.x else 0,
            self.y / mag if self.y else 0,
            self.z / mag if self.z else 0
        )

    def cross(self, other):
        return Vec3(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x
        )

    def normalize(self):
        mag = self.magnitude
        if self.x:
            self.x = self.x / mag
        if self.y:
            self.y = self.y / mag
        if self.z:
            self.z = self.z / mag
        return self

    # standard math operations
    def __add__(self, other):
        other = Vec3.cast(other)
        return Vec3(self.x + other.x, self.y + other.y, self.z + other.z)

    def __iadd__(self, other):
        other = Vec3.cast(other)
        self.x += other.x
        self.y += other.y
        self.z += other.z
        return self

    def __sub__(self, other):
        other = Vec3.cast(other)
        return Vec3(self.x - other.x, self.y - other.y, self.z - other.z)

    def __isub__(self, other):
        other = Vec3.cast(other)
        self.x -= other.x
        self.y -= other.y
        self.z -= other.z
        return self

    def __mul__(self, other):
        if isinstance(other, Mat4):
            # todo
            x = self.x
            y = self.y
            z = self.z

            m = other.representation

            ox = x * m[0][0] + y * m[1][0] + z * m[2][0] + m[3][0]
            oy = x * m[0][1] + y * m[1][1] + z * m[2][1] + m[3][1]
            oz = x * m[0][2] + y * m[1][2] + z * m[2][2] + m[3][2]
            return Vec3(ox, oy, oz)
        other = Vec3.cast(other)
        return Vec3(self.x * other.x, self.y * other.y, self.z * other.z)

    def __imul__(self, other):
        if isinstance(other, Mat4):
            self.x, self.y, self.z = tuple(self * other)
            return self
        other = Vec3.cast(other)
        self.x *= other.x
        self.y *= other.y
        self.z *= other.z
        return self

    def __truediv__(self, other):
        other = Vec3.cast(other)
        return Vec3(self.x / other.x, self.y / other.y, self.z / other.z)

    def __itruediv__(self, other):
        other = Vec3.cast(other)
        self.x /= other.x
        self.y /= other.y
        self.z /= other.z
        return self

    def __eq__(self, other):
        other = Vec3.cast(other)
        return self.x == other.x and self.y == other.y and self.z == other.z

    def __ne__(self, other):
        other = Vec3.cast(other)
        return self.x != other.x or self.y != other.y or self.z != other.z

    def __neg__(self):
        return Vec3(self.x * -1, self.y * -1, self.z * -1)

    def __str__(self):
        return "Vec3 (x%6.2f, y%6.2f, z%6.2f)" % (self.x, self.y, self.z)

    # helpers
    def __iter__(self):
        yield self.x
        yield self.y
        yield self.z

    @staticmethod
    def cast(thing):
        return thing if isinstance(thing, Vec3) else Vec3(thing)

# todo this needs to be more fleshed out
# and should probably be like a subclass of numpy.array or something
# so we can pass it to uniform

class Mat4(object):
    def __init__(self, representation):
        # if nothing is passed just fall back to identity
        self.representation = representation

    @property
    def gl_args(self):
        return self.representation

    def translate(self, pos):
        self.representation = numpy.matmul(self.representation, numpy.array(
            (
                (1, 0, 0, pos.x),
                (0, 1, 0, pos.y),
                (0, 0, 1, pos.z),
                (0, 0, 0, 1)
            )
        ))

        return self

    def scale(self, size):
        self.representation = numpy.matmul(self.representation, numpy.array(
            (
                (size.x, 0, 0, 0),
                (0, size.y, 0, 0),
                (0, 0, size.z, 0),
                (0, 0, 0, 1)
            )
        ))

        return self

    def rotate(self, angles, reverse=False):
        rep = self.representation
        rot = Vec3.cast(angles)

        xrot = yrot = zrot = None

        _x, _y, _z = rot

        if _x:
            c = math.cos(_x)
            s = math.sin(_x)
            xrot = numpy.array(
                (
                    (1, 0, 0, 0),
                    (0, c, -s, 0),
                    (0, s, c, 0),
                    (0, 0, 0, 1)
                ),
                'f'
            )

        if _y:
            c = math.cos(_y)
            s = math.sin(_y)
            yrot = numpy.array(
                (
                    (c, 0, s, 0),
                    (0, 1, 0, 0),
                    (-s, 0, c, 0),
                    (0, 0, 0, 1)
                ),
                'f'
            )

        if _z:
            c = math.cos(_z)
            s = math.sin(_z)
            zrot = numpy.array(
                (
                    (c, -s, 0, 0),
                    (s, c, 0, 0),
                    (0, 0, 1, 0),
                    (0, 0, 0, 1)
                ),
                'f'
            )

        if reverse:
            if _z: rep = numpy.matmul(rep, zrot)
            if _y: rep = numpy.matmul(rep, yrot)
            if _x: rep = numpy.matmul(rep, xrot)
        else:
            if _x: rep = numpy.matmul(rep, xrot)
            if _y: rep = numpy.matmul(rep, yrot)
            if _z: rep = numpy.matmul(rep, zrot)

        self.representation = rep

        return self

    def __mul__(self, other):
        if isinstance(other, Vec3):
            return other * self
        return Mat4(numpy.matmul(self.representation, other.representation))

    def __imul__(self, other):
        self.representation = numpy.matmul(
            self.representation, other.representation)
        return self

    def __str__(self):
        return str(self.representation)

    # builders
    @staticmethod
    def from_identity():
        return Mat4(numpy.identity(4))

    @staticmethod
    def from_transform(position=None, rotation=None, scale=None):
        position = position or Vec3(0)
        rotation = rotation or Vec3(0)
        scale = scale or Vec3(1)

        return Mat4(numpy.array(
            (
                (scale.x, 0, 0, position.x),
                (0, scale.y, 0, position.y),
                (0, 0, scale.z, position.z),
                (0, 0, 0, 1)
            ),
            'f'
        )).rotate(rotation)

    @staticmethod
    def from_perspective(fov, aspect, near, far):
        half_fov = math.tan(math.radians(fov * 0.5))
        z_range = near - far

        return Mat4(numpy.array(
            (
                (1.0 / half_fov * aspect, 0, 0, 0),
                (0, 1 / half_fov, 0, 0),
                (0, 0, (-near - far) / z_range, 2.0 * far * near / z_range),
                (0, 0, 1, 0)
            ),
            'f'
        ))

        return mat1

    @staticmethod
    def from_ortho(size, near, far):
        x_max = size[0] - 1
        y_max = size[1] - 1
        z_range = (-1.0 / far) if far else 0

        return Mat4(numpy.array(
            (
                (2.0 / x_max, 0, 0, -1),
                (0, -2.0 / y_max, 0, 1),
                (0, 0, z_range, 0),
                (0, 0, 0, 1)
            ),
            'f'
        ))
