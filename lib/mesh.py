
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.arrays import vbo

import numpy
from ctypes import c_void_p, sizeof, c_float

from .utils import calculate_normals_for_mesh

class Mesh(object):
    data_definition = {
        'vertices': {
            'index': 0,
            'num_components': 3
        },
        'normals': {
            'index': 1,
            'num_components': 3,
            'defaultFunc': calculate_normals_for_mesh
        },
        'texture_coords': {
            'index': 2,
            'num_components': 2,
            'defaultValue': (0, 0)
        },
        'colors': {
            'index': 3,
            'num_components': 4,
            'defaultValue': (1, 1, 1, 1)
        }
    }
    data_np_type = 'f'
    data_gl_type = GL_FLOAT
    data_size = sizeof(c_float)
    render_primitive = GL_TRIANGLES

    def __init__(self, vertices, normals=None, texture_coords=None, colors=None, texture=None, indices=None):
        self.initialize_values(vertices, normals, texture_coords, colors, texture, indices)
        self.build_arrays()

    def initialize_values(self, vertices=None, normals=None, texture_coords=None, colors=None, texture=None, indices=None):
        self.vertices = vertices
        if not indices:
            indices = [range(len(vertices))]
        self.indices = indices
        self.index_array = numpy.array(indices, dtype=numpy.int32)

        if 'normals' in self.data_definition:
            self.normals = self.default(normals, 'normals')
        if 'texture_coords' in self.data_definition:
            self.texture_coords = self.default(texture_coords, 'texture_coords')
        if 'colors' in self.data_definition:
            self.colors = self.default(colors, 'colors')

        self.texture = texture

    def default(self, value, _type):
        if value:
            return value
        ddef = self.data_definition[_type]
        if 'defaultValue' in ddef:
            return [ddef['defaultValue']] * len(self.vertices)
        if 'defaultFunc' in ddef:
            return ddef['defaultFunc'](self)
        raise AttributeError('Cannot default value for param "%s"'%_type)

    def build_arrays(self):
        # calculate stride and pointer offsets
        data_stride = 0 # how many values packed into a row
        next_offset = 0 # offset for next set of value in row
        data_defs = [] # list of (index, num_components, offset)
        for name in self.data_definition:
            if getattr(self, name):
                attrib = self.data_definition[name]
                data_stride += attrib['num_components']
                data_defs.append((attrib['index'], attrib['num_components'], next_offset))
                next_offset += attrib['num_components']

        # build data_defs as tuple of args for glVertexAttribPointer
        self.data_defs = [(d[0], d[1], self.data_gl_type, False, data_stride * self.data_size, c_void_p(d[2] * self.data_size)) for d in data_defs]
        
        # build data array
        vert_count = len(self.vertices)
        data = []
        for i in range(vert_count):
            for name in self.data_definition:
                val = getattr(self, name)
                if val:
                    data.extend(val[i])
        self.data_array = numpy.array(data, dtype=self.data_np_type)

        # build vbos
        self.data_buffer = vbo.VBO(self.data_array)
        self.index_buffer = vbo.VBO(self.index_array, target=GL_ELEMENT_ARRAY_BUFFER)

    def render(self):
        self.index_buffer.bind()
        self.data_buffer.bind()
        if self.texture:
            self.texture.bind()
        for data in self.data_defs:
            # each of these seems relativively expensive...
            # todo: good candidate for optimization
            # e.g.: with vert and texc we got ~1000 fps with two pyramids
            #       adding normals went down to ~925
            #       adding colors went down to ~850
            glEnableVertexAttribArray(data[0])
            glVertexAttribPointer(*data)
        glDrawElements(self.render_primitive, len(self.indices), GL_UNSIGNED_INT, None)
        for data in self.data_defs:
            glDisableVertexAttribArray(data[0])
        self.data_buffer.unbind()
        self.index_buffer.unbind()

# optimized classes if you don't need all functionality
# these run much faster if all objects are the same (have just color or just texture)
class ColoredMesh(Mesh):
    '''Mesh with no texture component'''

    data_definition = {
        'vertices': {
            'index': 0,
            'num_components': 3
        },
        'normals': {
            'index': 1,
            'num_components': 3,
            'defaultFunc': calculate_normals_for_mesh
        },
        'colors': {
            'index': 2,
            'num_components': 4,
            'defaultValue': (1, 1, 1, 1)
        }
    }

    def __init__(self, vertices, normals=None, colors=None, indices=None):
        # NOTE: I really don't like this - just haven't decided on an alternative I like more that lets me inject things when I need to
        self.initialize_values(vertices, normals, colors, indices)
        self.build_arrays()

    def initialize_values(self, vertices=None, normals=None, colors=None, indices=None):
        super(ColoredMesh, self).initialize_values(vertices, normals=normals, colors=colors, indices=indices)

class TexturedMesh(Mesh):
    '''Mesh with no color component'''

    data_definition = {
        'vertices': {
            'index': 0,
            'num_components': 3
        },
        'normals': {
            'index': 1,
            'num_components': 3,
            'defaultFunc': calculate_normals_for_mesh
        },
        'texture_coords': {
            'index': 2,
            'num_components': 2,
            'defaultValue': (0, 0)
        }
    }

    def __init__(self, vertices, normals=None, texture_coords=None, texture=None, indices=None):
        # NOTE: I really don't like this - just haven't decided on an alternative I like more that lets me inject things when I need to
        self.initialize_values(vertices, normals, texture_coords, texture, indices)
        self.build_arrays()

    def initialize_values(self, vertices=None, normals=None, texture_coords=None, texture=None, indices=None):
        super(TexturedMesh, self).initialize_values(vertices, normals=normals, texture_coords=texture_coords, texture=texture, indices=indices)
