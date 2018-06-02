
from OpenGL.GL import *
from OpenGL.GL import shaders

class Shader(object):
    __bound_shader = None

    def __init__(self, vert_shader, frag_shader, uniforms=None):
        self.vs_source = vert_shader
        self.fs_source = frag_shader
        self.uf_source = uniforms

        self._shader = None
        self._uniform_map = None

    def compile(self):
        vert = shaders.compileShader(self.vs_source, GL_VERTEX_SHADER)
        frag = shaders.compileShader(self.fs_source, GL_FRAGMENT_SHADER)

        _shader = shaders.compileProgram(vert, frag)
        if self.uf_source:
            _map = {}
            _funcs = {}
            for uniform in self.uf_source:
                _map[uniform] = glGetUniformLocation(_shader, uniform)
                _funcs[uniform] = self.uf_source[uniform]
            self._uniform_map = _map
            self._uniform_funcs = _funcs

        self._shader = _shader

    def bind(self):
        if self.__bound_shader is self:
            return
        shaders.glUseProgram(self._shader)
        self.__bound_shader = self

    def unbind(self):
        #note: this should not be done unless needed
        # took fps from ~1000 to ~900 when rendering two objects and binding/unbinding each render
        shaders.glUseProgram(0)

    def uniform(self, name, *args):
        # TODO: cache what values were last set so we don't reset when the same
        if not (self._uniform_map and name in self._uniform_map):
            raise AttributeError("Invalid uniform %s"%name)
        self._uniform_funcs[name](self._uniform_map[name], *args)

    # TODO: some helpers to pass variables to shader without needing to define the uniform func
    # like, if I want to pass (0.1, 0.2, 0.3) it would figure out that is glUniform3f, etc.

# TODO: make default shaders based on the types of input that can come in
