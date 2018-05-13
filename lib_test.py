
import pygame
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GL import shaders
from OpenGL.GLU import *
from OpenGL.arrays import vbo
import numpy
import math

from lib.math3d import Vec3
from lib.scenegraph import Scene, TransformNode
from lib.view import PerspectiveView, LookAtCamera, LookFromCamera

class RenderThing(object):
    def __init__(self, verts, indices=None):

        self.verts = verts

        self.vbo = vbo.VBO(verts)

        if not indices:
            indices = [range(verts.shape[0])]
        self.indices = numpy.array(indices, dtype=numpy.int32)
        self.indexBuffer = vbo.VBO(self.indices, target=GL_ELEMENT_ARRAY_BUFFER)

        self.vbo.create_buffers()
        self.indexBuffer.create_buffers()
        self.buildShader()

    def buildShader(self):
        vert = shaders.compileShader("""
            #version 330
            layout (location = 0) in vec3 Position;
            uniform mat4 worldLocation;
            out vec4 Color;

            void main() {
                Color = vec4(clamp(Position, 0.0, 1.0), 1.0);
                gl_Position = vec4(Position, 1.0) * worldLocation;
                gl_Position = gl_ModelViewProjectionMatrix * gl_Position;
            }""", GL_VERTEX_SHADER)

        frag = shaders.compileShader("""
            #version 330
            in vec4 Color;
            void main() {
                //gl_FragColor = vec4( 0, 1, 0, 1 );
                gl_FragColor = Color;
            }""", GL_FRAGMENT_SHADER)

        self.shader = shaders.compileProgram(vert,frag)
        self.shaderU = {
            'worldLocation': glGetUniformLocation(self.shader, 'worldLocation')
        }

    def render(self, node):

        shaders.glUseProgram(self.shader)
        glUniformMatrix4fv(self.shaderU['worldLocation'], 1, False, node.render_matrix.representation)

        self.indexBuffer.bind()
        self.vbo.bind()
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, self.verts.shape[1], GL_FLOAT, False, 0, None)
        glDrawElements(GL_TRIANGLES, self.indices.shape[0], GL_UNSIGNED_INT, None)
        glDisableVertexAttribArray(0)
        self.vbo.unbind()
        self.indexBuffer.unbind()
        shaders.glUseProgram(0)

def makeThing():

    verts = numpy.array([
        [-1, -1, 0],
        [0, -1, 1],
        [1, -1, 0],
        [0, 1, 0]
    ], 'f')

    indices = [
        0, 3, 1,
        1, 3, 2,
        2, 3, 0,
        0, 1, 2
    ]

    return RenderThing(verts, indices)

def initDisplay(screen_size):
    pygame.display.set_mode(screen_size, OPENGL|DOUBLEBUF)

    glClearColor(0, 0, 0, 0)
    glEnable(GL_DEPTH_TEST)
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
                    print(node2.get_matrix())

        clear_screen()
        if not paused:
            objx += 0.001
            node1.position.x = math.sin(objx)
            # TODO: dirty only works on setting whole rotation :/
            camera.rotation = camera.rotation + Vec3(0, 0.002, 0)
            node1.rotation.y += 0.001
            node2.position.y = math.sin(objx)
            node2.rotation.z += 0.001
            # update node and children
            scene.update_node()
        thing.render(node1)
        thing.render(node2)
        pygame.display.flip()

main()
