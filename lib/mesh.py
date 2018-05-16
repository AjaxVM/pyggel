
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.arrays import vbo

import numpy
from ctypes import c_void_p, sizeof, c_float

class Mesh(object):
    data_definition = (
        {
            'name': 'vertices',
            'index': 0,
            'num_components': 3
        },
        {
            'name': 'texture_coords',
            'index': 1,
            'num_components': 2
        },
        {
            'name': 'colors',
            'index': 2,
            'num_components': 4
        }
    )
    data_np_type = 'f'
    data_gl_type = GL_FLOAT
    data_size = sizeof(c_float)

    def __init__(self, vertices, texture_coords=None, colors=None, texture=None, indices=None):

        # data vbo parts
        self.vertices = vertices
        self.texture_coords = texture_coords
        self.colors = colors

        self._texture = texture
        self.indices = indices

        self.build_arrays()

    def build_arrays(self):
        # calculate stride and pointer offsets
        data_stride = 0 # how many values packed into a row
        next_offset = 0 # offset for next set of value in row
        data_defs = [] # list of (index, num_components, offset)
        for attrib in self.data_definition:
            if getattr(self, attrib['name']):
                data_stride += attrib['num_components']
                data_defs.append((attrib['index'], attrib['num_components'], next_offset))
                next_offset += attrib['num_components']

        # build data_defs as tuple of args for glVertexAttribPointer
        self.data_defs = [(d[0], d[1], self.data_gl_type, False, data_stride * self.data_size, c_void_p(d[2] * self.data_size)) for d in data_defs]
        
        # build data array
        vert_count = len(self.vertices)
        data = []
        for i in range(vert_count):
            for attrib in self.data_definition:
                val = getattr(self, attrib['name'])
                if val:
                    data.extend(val[i])
        self.data_array = numpy.array(data, dtype=self.data_np_type)

        # build index array
        if not self.indices:
            self.indices = [range(vert_count)]
        self.index_array = numpy.array(self.indices, dtype=numpy.int32)

        # build vbos
        self.data_buffer = vbo.VBO(self.data_array)
        self.index_buffer = vbo.VBO(self.index_array, target=GL_ELEMENT_ARRAY_BUFFER)

    def render(self):
        self.index_buffer.bind()
        self.data_buffer.bind()
        if self._texture:
            self._texture.bind()
        for data in self.data_defs:
            glEnableVertexAttribArray(data[0])
            glVertexAttribPointer(*data)
        glDrawElements(GL_TRIANGLES, len(self.indices), GL_UNSIGNED_INT, None)
        for data in self.data_defs:
            glDisableVertexAttribArray(data[0])
        self.data_buffer.unbind()
        self.index_buffer.unbind()
