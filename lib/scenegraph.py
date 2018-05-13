
import numpy
import operator

class Vec3(object):
    def cast(thing):
        return thing if isinstance(thing, Vec3) else Vec3(thing)

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

    def __combine(self, other, op):
        f = getattr(operator, op)
        other = Vec3.cast(other)
        return Vec3(f(self.x, other.x), f(self.y, other.y), f(self.z, other.z))

    def __add__(self, other):
        return self.__combine(other, 'add')

    def __sub__(self, other):
        return self.__combine(other, 'sub')

    def __mul__(self, other):
        return self.__combine(other, 'mul')

    def __truediv__(self, other):
        return self.__combine(other, 'truediv')

    def __eq__(self, other):
        other = Vec3.cast(other)
        return self.x == other.x and self.y == other.y and self.z == other.z

    def __ne__(self, other):
        other = Vec3.cast(other)
        return self.x != other.x or self.y != other.y or self.z != other.z

    def __str__(self):
        return "Vec3 (x%d, y%d, z%d)"%(self.x, self.y, self.z)

# todo this needs to be more fleshed out
# and should probably be like a subclass of numpy.array or something
# so we can pass it to uniform

class Mat4(object):
    def __init__(self, representation):
        # if nothing is passed just fall back to identity
        self.representation = representation

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

    def rotate(self, angles):
        xc = numpy.cos(angles.x)
        xs = numpy.sin(angles.x)

        yc = numpy.cos(angles.y)
        ys = numpy.sin(angles.y)

        zc = numpy.cos(angles.z)
        zs = numpy.sin(angles.z)

        self.representation = numpy.matmul(self.representation, numpy.array(
            (
                (yc*zc, zs, -ys, 0),
                (-zs, xc*zc, xs, 0),
                (ys, -xs, xc*yc, 0),
                (0, 0, 0, 1)
            ),
            'f'
        ))

        return self

    def rotateAxis(self, radianAngle, axis='x'):
        c = numpy.cos(radianAngle)
        s = numpy.sin(radianAngle)

        self.representation = numpy.matmul(self.representation, numpy.array(
            (
                # (1 if axis == 'x' else c, s if axis == 'z' else 0, -s if axis == 'y' else 0, 0),
                ((c, 1)[axis=='x'], (0, s)[axis=='z'], (0, -s)[axis=='y'], 0),
                ((0, -s)[axis=='z'], (c, 1)[axis=='y'], (0, s)[axis=='x'], 0),
                ((0, s)[axis=='y'], (0, -s)[axis=='x'], (c, 1)[axis=='z'], 0),
                (0, 0, 0, 1)
            )
        ))
        return self

    # builders
    def identity():
        return Mat4(numpy.array(
            (
                (1, 0, 0, 0),
                (0, 1, 0, 0),
                (0, 0, 1, 0),
                (0, 0, 0, 1)
            )
        ))

    def fromTransform(position=None, rotation=None, scale=None):
        position = position or Vec3(0)
        rotation = rotation or Vec3(0)
        scale = scale or Vec3(1)

        xc = numpy.cos(rotation.x)
        xs = numpy.sin(rotation.x)

        yc = numpy.cos(rotation.y)
        ys = numpy.sin(rotation.y)

        zc = numpy.cos(rotation.z)
        zs = numpy.sin(rotation.z)

        return Mat4(numpy.array(
            (
                (yc*zc*scale.x, zs*scale.x, -ys*scale.x, position.x),
                (-zs*scale.y, xc*zc*scale.y, xs*scale.y, position.y),
                (ys*scale.z, -xs*scale.z, xc*yc*scale.z, position.z),
                (0, 0, 0, 1)
            ),
            'f'
        ))

    def __mul__(self, other):
        return Mat4(numpy.matmul(self.representation, other.representation))

class Node(object):
    def __init__(self, position=None, rotation=None, scale=None, parent=None, view=None):

        self.position = position or Vec3()
        self.rotation = rotation or Vec3()
        self.scale = scale or Vec3(1)

        self.parent = parent
        self._view = view

    def get_matrix(self, transOnly=False):
        mat4 = Mat4.fromTransform(self.position, self.rotation, self.scale)

        if self.parent and not isinstance(self.parent, ViewNode):
            mat4 = self.parent.get_matrix(True) * mat4

        if not transOnly:
            view = self.view
            if view:
                return view.get_view_matrix() * mat4
        return mat4

    @property
    def view(self):
        # return self._view or (self.parent and self.parent.view)
        return (isinstance(self.parent, ViewNode) and self.parent) or (self.parent and self.parent.view)

class ViewNode(object):
    def __init__(self, view=None, camera=None):
        self.view = view
        self.camera = camera

    def get_view_matrix(self):
        if self.view:
            if self.camera:
                return self.view.matrix * self.camera.matrix
            return self.view.matrix
        elif self.camera:
            return self.camera.matrix
