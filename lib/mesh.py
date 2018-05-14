
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.arrays import vbo

import numpy
from ctypes import c_void_p, sizeof, c_float

class Mesh(object):
    def __init__(self, verts, texcoords=None, colors=None, texture=None, indices=None):

        # data vbo parts
        self._verts = verts
        self._texcs = texcoords
        self._colors = colors

        self._texture = texture
        self._indices = indices

        self.build_arrays()

    def build_arrays(self):
        # calculate stride and pointer offsets
        data_stride = 3 # how many data points in a row - vert is 3
        next_offset = 3 # offset for next set of values (if any)
        data_defs = [
            # (name, index, num components, pointer offset)
            ('vert', 0, 3, None)
        ]
        next_data_index = 1 # where to start the next data range (if any)
        if self._texcs:
            data_stride += 2
            data_defs.append(('texcs', next_data_index, 2, c_void_p(sizeof(c_float)*next_offset)))
            next_offset += 2
            next_data_index += 1
        if self._colors:
            data_stride += 3
            data_defs.append(('colors', next_data_index, 3, c_void_p(sizeof(c_float)*next_offset)))
            next_offset += 3
            next_data_index += 1
        self.data_stride = sizeof(c_float)*data_stride
        self.data_defs = data_defs
        
        # build data array
        vert_count = len(self._verts)
        data = []
        for i in range(vert_count):
            data.extend(self._verts[i])
            if self._texcs:
                data.extend(self._texcs[i])
            if self._colors:
                data.extend(self._colors[i])
        self.data_array = numpy.array(data, 'f')

        # build index array
        # TODO: maybe better to just not build index_array without indices so we don't bind that stuff?
        if not self._indices:
            self._indices = [range(vert_count)]
        self.index_array = numpy.array(self._indices, dtype=numpy.int32)

        # build vbos
        self.data_buffer = vbo.VBO(self.data_array)
        self.index_buffer = vbo.VBO(self.index_array, target=GL_ELEMENT_ARRAY_BUFFER)

    def render(self):
        self.index_buffer.bind()
        self.data_buffer.bind()
        if self._texture:
            self._texture.bind()
        for data in self.data_defs:
            glEnableVertexAttribArray(data[1])
            glVertexAttribPointer(data[1], data[2], GL_FLOAT, False, self.data_stride, data[3])
        glDrawElements(GL_TRIANGLES, len(self._indices), GL_UNSIGNED_INT, None)
        for data in self.data_defs:
            glDisableVertexAttribArray(data[1])
        self.data_buffer.unbind()
        self.index_buffer.unbind()
