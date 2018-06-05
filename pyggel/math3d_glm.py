
import math
import glm


class Vec3(object):
    def __init__(self, *args):
        self.representation = glm.vec3(*args)

    @property
    def gl_args(self):
        return (self.x, self.y, self.z)

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
        return glm.magnitude(self.representation)

    def dot(self, other):
        # just here for clarity if needed
        return Vec3(glm.dot(self.representation, other.representation))

    @property
    def normalized(self):
        return Vec3(glm.normalize(self.representation))

    def cross(self, other):
        return Vec3(glm.cross(self.representation, other.representation))

    def normalize(self):
        self.representation = glm.normalize(self.representation)
        return self

    # standard math operations
    def __add__(self, other):
        other = Vec3.cast(other)
        return Vec3(self.representation + other.representation)

    def __iadd__(self, other):
        other = Vec3.cast(other)
        self.representation = self.representation + other.representation
        return self

    def __sub__(self, other):
        other = Vec3.cast(other)
        return Vec3(self.representation - other.representation)

    def __isub__(self, other):
        other = Vec3.cast(other)
        self.representation = self.representation - other.representation
        return self

    def __mul__(self, other):
        if isinstance(other, Mat4):
            return Vec3((other.representation * glm.vec4(self.representation, 1)).xyz)
        other = Vec3.cast(other)
        return Vec3(glm.dot(self.representation, other.representation))

    def __imul__(self, other):
        if isinstance(other, Mat4):
            self.representation = (other.representation * glm.vec4(self.representation, 1)).xyz
            return self
        other = Vec3.cast(other)
        self.representation = glm.dot(self.representation, other.representation)
        return self

    def __truediv__(self, other):
        other = Vec3.cast(other)
        return Vec3(self.representation / other.representation)

    def __itruediv__(self, other):
        other = Vec3.cast(other)
        self.representation = self.representation / other.representation
        return self

    def __eq__(self, other):
        other = Vec3.cast(other)
        return glm.equal(self.representation, other.representation)

    def __ne__(self, other):
        other = Vec3.cast(other)
        return glm.notEqual(self.representation, other.representation)

    def __neg__(self):
        return Vec3(-self.representation)

    def __str__(self):
        return "Vec3 (x%6.2f, y%6.2f, z%6.2f)" % (self.representation.x, self.representation.y, self.representation.z)

    # helpers
    def __iter__(self):
        return iter(self.representation)

    @staticmethod
    def cast(thing):
        return thing if isinstance(thing, Vec3) else Vec3(thing)


class Mat4(object):
    def __init__(self, *args):
        # if nothing is passed just fall back to identity
        self.representation = glm.mat4(*args)

    @property
    def gl_args(self):
        return glm.value_ptr(self.representation)

    def translate(self, pos):
        self.representation = glm.translate(self.representation, Vec3.cast(pos).representation)
        return self

    def scale(self, size):
        self.representation = glm.scale(self.representation, Vec3.cast(size).representation)

        return self

    def rotate(self, angles):
        self.representation = glm.rotate(self.representation, angles.x, glm.vec3(1, 0, 0))
        self.representation = glm.rotate(self.representation, angles.y, glm.vec3(0, 1, 0))
        self.representation = glm.rotate(self.representation, angles.z, glm.vec3(0, 0, 1))

        return self

    def rotate_axis(self, angle, axis='x'):
        if axis == 'x':
            rot = glm.vec3(1, 0, 0)
        if axis == 'y':
            rot = glm.vec3(0, 1, 0)
        if axis == 'z':
            rot = glm.vec3(0, 0, 1)
        self.representation = glm.rotate(self.representation, angle, rot)
        return self

    def __mul__(self, other):
        if isinstance(other, Vec3):
            return Vec3((self.representation * glm.vec4(other.representation, 1)).xyz)
        return Mat4(self.representation * other.representation)

    def __imul__(self, other):
        self.representation = self.representation * other.representation
        return self

    def __str__(self):
        return str(self.representation)

    # builders
    @staticmethod
    def from_identity():
        return Mat4(1)

    @staticmethod
    def from_transform(position=None, rotation=None, scale=None):
        mat = Mat4(1)
        mat.translate(position or 0)
        mat.rotate(rotation or 0)
        mat.scale(scale or 1)

        return mat

    @staticmethod
    def from_perspective(fov, aspect, near, far):
        # return Mat4(glm.perspective(glm.radians(fov), aspect, near, far))
        mat1 = Mat4(glm.perspectiveLH_NO(glm.radians(fov), aspect, near, far))
        half_fov = math.tan(math.radians(fov * 0.5))
        z_range = near - far

        # return Mat4(
        mat2 = Mat4(
            (1.0 / half_fov * aspect, 0, 0, 0),
            (0, 1 / half_fov, 0, 0),
            (0, 0, (-near - far) / z_range, 2.0 * far * near / z_range),
            (0, 0, 1, 0)
        )

        print(mat1)
        print(mat2)
        return mat1

    @staticmethod
    def from_ortho(size, near, far):
        return Mat4(glm.ortho(size, near, far))
