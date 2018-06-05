
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
        },
        # TODO: this needs to be a material that is packed in a vec4 probably...
        'specular_power': {
            'index': 4,
            'num_components': 1,
            'defaultValue': (1,)
        }
    }
    data_np_type = 'f'
    data_gl_type = GL_FLOAT
    data_size = sizeof(c_float)
    render_primitive = GL_TRIANGLES

    def __init__(self, vertices, normals=None, texture_coords=None, colors=None, specular_power=None, texture=None, indices=None):
        # TODO: can we make this initialize smarter???
        self.initialize_values(vertices, normals, texture_coords, colors, specular_power, texture, indices)
        self.build_arrays()

    def initialize_values(self, vertices=None, normals=None, texture_coords=None, colors=None, specular_power=None, texture=None, indices=None):
        # TODO: now that things are optimized enough to have one class - might want to revisit if we really want to default everything
        #       ie, texture_coords and colors can probably be omitted if we don't want to use them or something?
        #       or maybe we go back to having some models not have that stuff... hmm
        self.vertices = vertices
        if not indices:
            indices = [range(len(vertices))]
        self.indices = indices
        self.index_array = numpy.array(indices, dtype=numpy.int32)

        # this is mainly to support subclasses that don't have all of these
        # to avoid reimplementation
        # TODO: just loop over data_definition and set things?
        if 'normals' in self.data_definition:
            self.normals = self.default(normals, 'normals')
        if 'texture_coords' in self.data_definition:
            self.texture_coords = self.default(texture_coords, 'texture_coords')
        if 'colors' in self.data_definition:
            self.colors = self.default(colors, 'colors')
        if 'specular_power' in self.data_definition:
            self.specular_power = self.default(specular_power, 'specular_power')

        self.texture = texture

    def default(self, value, _type):
        if value:
            return value
        ddef = self.data_definition[_type]
        if 'defaultValue' in ddef:
            return [ddef['defaultValue']] * len(self.vertices)
        if 'defaultFunc' in ddef:
            return ddef['defaultFunc'](self)
        raise AttributeError('Cannot default value for param "%s"' % _type)

    def build_arrays(self):
        # calculate stride and pointer offsets
        data_stride = 0  # how many values packed into a row
        next_offset = 0  # offset for next set of value in row
        data_defs = []  # list of (index, num_components, offset)
        for name in self.data_definition:
            if getattr(self, name):
                attrib = self.data_definition[name]
                data_stride += attrib['num_components']
                data_defs.append((attrib['index'], attrib['num_components'], next_offset))
                next_offset += attrib['num_components']

        # store in case we need to reference our definitions
        self.data_defs = data_defs

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
        self.vao = glGenVertexArrays(1)

        # set data format
        glBindVertexArray(self.vao)
        self.data_buffer.bind()
        for data in data_defs:
            glEnableVertexAttribArray(data[0])
            glVertexAttribPointer(data[0], data[1], self.data_gl_type, False,
                                  data_stride * self.data_size, c_void_p(data[2] * self.data_size))
        self.data_buffer.unbind()
        glBindVertexArray(0)

    def render(self):
        # TODO: this should probably be passed the currently active shader to make this work
        glBindVertexArray(self.vao)
        self.index_buffer.bind()
        self.data_buffer.bind()
        if self.texture:
            self.texture.bind()
        glDrawElements(self.render_primitive, len(self.indices), GL_UNSIGNED_INT, None)
        self.data_buffer.unbind()
        self.index_buffer.unbind()
        glBindVertexArray(0)
