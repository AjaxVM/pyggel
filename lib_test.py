
import pygame
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GL import shaders
from OpenGL.GLU import *
from OpenGL.arrays import vbo
import numpy
import math

from ctypes import c_void_p, sizeof, c_float

from lib.data import Texture
from lib.math3d import Vec3
from lib.scene import Scene, TransformNode
from lib.view import PerspectiveView, LookAtCamera, LookFromCamera

class RenderThing(object):
    def __init__(self, verts, indices=None, texture=None, texcoords=None):
        self.verts = numpy.array(verts, 'f')
        self.vert_stride = 3

        self.vbo = vbo.VBO(self.verts)

        if not indices:
            indices = [range(verts.shape[0])]
        self.indices = numpy.array(indices, dtype=numpy.int32)
        self.indexBuffer = vbo.VBO(self.indices, target=GL_ELEMENT_ARRAY_BUFFER)

        self.texture = texture
        if texture:
            self.vert_stride = 5

        self.vbo.create_buffers()
        self.indexBuffer.create_buffers()
        self.buildShader()

    def buildShader(self):
        vert = shaders.compileShader("""
            #version 330
            layout (location = 0) in vec3 Position;
            layout (location = 1) in vec2 TexCoord;
            uniform mat4 worldLocation;
            out vec4 Color;
            out vec2 TexCoord0;

            void main() {
                Color = vec4(clamp(Position, 0.0, 1.0), 1.0);
                gl_Position = vec4(Position, 1.0) * worldLocation;
                TexCoord0 = TexCoord;
            }""", GL_VERTEX_SHADER)

        frag = shaders.compileShader("""
            #version 330
            in vec4 Color;
            in vec2 TexCoord0;
            uniform sampler2D gSampler;

            void main() {
                // gl_FragColor = Color;
                gl_FragColor = texture2D(gSampler, TexCoord0.st) * Color;
            }""", GL_FRAGMENT_SHADER)

        self.shader = shaders.compileProgram(vert,frag)
        self.shaderU = {
            'worldLocation': glGetUniformLocation(self.shader, 'worldLocation'),
            'gSampler': glGetUniformLocation(self.shader, 'gSampler')
        }

    def render(self, node):

        shaders.glUseProgram(self.shader)
        glUniformMatrix4fv(self.shaderU['worldLocation'], 1, False, node.render_matrix.representation)
        glUniform1i(self.shaderU['gSampler'], 0)

        self.indexBuffer.bind()
        self.vbo.bind()
        glEnableVertexAttribArray(0)
        if self.texture:
            glEnableVertexAttribArray(1)
        # verts have 3 points and are first index
        glVertexAttribPointer(0, 3, GL_FLOAT, False, sizeof(c_float)*self.vert_stride, None)
        # tex coords have 2 points and are second index - pointer to offset the first 3 float values
        if self.texture:
            glVertexAttribPointer(1, 2, GL_FLOAT, False, sizeof(c_float)*self.vert_stride, c_void_p(sizeof(c_float)*3))
            self.texture.bind()
        glDrawElements(GL_TRIANGLES, self.indices.shape[0], GL_UNSIGNED_INT, None)
        glDisableVertexAttribArray(0)
        if self.texture:
            glDisableVertexAttribArray(1)
        self.vbo.unbind()
        self.indexBuffer.unbind()
        shaders.glUseProgram(0)

def makeThing():

    verts = [
        -1, -1, 0.5, 0, 0,
        0, -1, -1, 0.5, 0.5,
        1, -1, 0.5, 1, 0.5,
        0, 1, 0, 0.5, 1
    ]

    indices = [
        0, 3, 1,
        1, 3, 2,
        2, 3, 0,
        0, 1, 2
    ]

    texture = Texture.from_file('data/wood-blocks.jpg')

    return RenderThing(verts, indices, texture)

def initDisplay(screen_size):
    pygame.display.set_mode(screen_size, OPENGL|DOUBLEBUF)

    glClearColor(0, 0, 0, 0)
    glEnable(GL_DEPTH_TEST)
    glFrontFace(GL_CW)
    glCullFace(GL_BACK)
    glEnable(GL_CULL_FACE)
    clear_screen()

def clear_screen():
    """Clear buffers."""
    glClear(GL_DEPTH_BUFFER_BIT | GL_COLOR_BUFFER_BIT)

def main():

    pygame.init()

    pygame.display.set_caption('Hello world!')

    screen_size = (640, 480)

    initDisplay(screen_size)

    view = PerspectiveView(45, screen_size, 1, 100)
    camera = LookAtCamera(Vec3(0, 0, 0), Vec3(0, 0, 0), 10)

    thing = makeThing()
    scene = Scene(view, camera)
    node1 = TransformNode(position=Vec3(0, 0, 0), parent=scene)
    node2 = TransformNode(position=Vec3(2, 0, 0), parent=node1, scale=Vec3(0.25))

    clock = pygame.time.Clock()
    ms_accum = 0
    ms_count = 0
    fps = 0

    objx = 0
    objScale = 0

    paused = False

    while 1:
        clock.tick(9999)
        frame_time = clock.get_time()
        ms_accum += frame_time
        ms_count += 1
        if ms_accum >= 1000:
            fps = int(1000 / (ms_accum / ms_count))
            ms_accum = 0
            ms_count = 0
        pygame.display.set_caption('Hello World! %s FPS'%fps)
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                return

            if event.type == KEYDOWN:
                if event.key == K_p:
                    paused = not paused
                    print(node2.transform_matrix)

        clear_screen()
        if not paused:
            objx += 0.001
            node1.position.x = math.sin(objx)
            # TODO: dirty only works on setting whole rotation :/
            camera.rotation += Vec3(0.002, 0, 0)
            node1.rotation.y += 0.001
            node2.position.y = math.sin(objx)
            # update node and children
            scene.update_node()
        thing.render(node1)
        thing.render(node2)
        pygame.display.flip()

main()
