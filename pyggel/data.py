
from PIL import Image
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy


class Texture(object):
    def __init__(self, texture_id=None, repeat=False):

        self.texture_id = texture_id or Texture.gen_texture_id()
        self.repeat = repeat

    def bind(self):
        glBindTexture(GL_TEXTURE_2D, self.texture_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        if self.repeat:
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_R, GL_REPEAT)
        else:
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_R, GL_CLAMP_TO_EDGE)

    @staticmethod
    def from_file(filename, repeat=False):
        # todo need a system to handle non-power-of-2 textures

        image = Image.open(filename)
        image_data = numpy.array(list(image.getdata()), numpy.uint8)

        _id = Texture.gen_texture_id()
        glBindTexture(GL_TEXTURE_2D, _id)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, image.size[0], image.size[1],
                     0, GL_RGB, GL_UNSIGNED_BYTE, image_data)

        image.close()
        return Texture(_id, repeat)

    @staticmethod
    def gen_texture_id():
        # todo track "deleted" textures and reuse those ids
        return glGenTextures(1)
