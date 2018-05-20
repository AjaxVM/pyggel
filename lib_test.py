
import pygame
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *
import numpy
import math

# from ctypes import c_void_p, sizeof, c_float

from lib.data import Texture
from lib.math3d import Vec3
from lib.mesh import Mesh
from lib.scene import Scene, TransformNode, RenderNode, LightNode
from lib.shader import Shader
from lib.light import AmbientLight, DirectionalLight
from lib.view import PerspectiveView, LookAtCamera, LookFromCamera

def makeThing():
    vertices = (
        (-1, -1, 0.5),
        (0, -1, -1),
        (1, -1, 0.5),
        (0, 1, 0),
    )

    texcs = (
        (0, 0),
        (0.5, 0.5),
        (1, 0.5),
        (0.5, 1)
    )

    indices = (
        0, 3, 1,
        1, 3, 2,
        2, 3, 0,
        0, 1, 2
    )

    texture = Texture.from_file('data/wood-blocks.jpg')

    mesh = Mesh(vertices, texture_coords=texcs, texture=texture, indices=indices)

    return mesh

def makeShader():
    vs = """
        #version 330
        layout (location = 0) in vec3 PYGGEL_Position;
        layout (location = 1) in vec3 PYGGEL_Normal;
        layout (location = 2) in vec2 PYGGEL_TexCoord;
        layout (location = 3) in vec4 PYGGEL_Color;

        uniform mat4 PYGGEL_Transformation;
        uniform mat4 PYGGEL_LocalTransformation;

        out vec4 Color;
        out vec2 TexCoord;
        out vec4 Normal;

        out mat4 LocalTransformation;

        void main() {
            Color = PYGGEL_Color;
            gl_Position = vec4(PYGGEL_Position, 1.0f) * PYGGEL_Transformation;
            TexCoord = PYGGEL_TexCoord;
            Normal = vec4(PYGGEL_Normal, 0.0f);
            LocalTransformation = PYGGEL_LocalTransformation;
        }"""
    fs = """
        #version 330
        in vec4 Color;
        in vec2 TexCoord;
        in vec4 Normal;
        in mat4 LocalTransformation;

        uniform sampler2D PYGGEL_TexSampler;
        uniform vec3 PYGGEL_AmbientColor;
        uniform float PYGGEL_AmbientIntensity;
        uniform vec3 PYGGEL_DirectionalColor;
        uniform float PYGGEL_DirectionalIntensity;
        uniform vec3 PYGGEL_DirectionalNormal; // direction

        out vec4 FragColor;

        void main() {
            vec4 baseColor = texture2D(PYGGEL_TexSampler, TexCoord.st) * Color;

            vec4 ambient = baseColor * vec4(PYGGEL_AmbientColor, 1.0f) * PYGGEL_AmbientIntensity;

            float diffuseNormalIntensity = dot(normalize(Normal * LocalTransformation), vec4(-PYGGEL_DirectionalNormal, 1.0f));
            vec4 diffuse;
            if (diffuseNormalIntensity > 0) {
                diffuse = baseColor * vec4(PYGGEL_DirectionalColor, 1.0f) * PYGGEL_DirectionalIntensity * diffuseNormalIntensity;
            } else {
                diffuse = vec4(0,0,0,0);
            }

            FragColor = ambient + diffuse;
        }"""

    shader = Shader(vs, fs, {
        'PYGGEL_Transformation': glUniformMatrix4fv,
        'PYGGEL_LocalTransformation': glUniformMatrix4fv,
        'PYGGEL_TexSampler': glUniform1i,
        'PYGGEL_AmbientColor': glUniform3f,
        'PYGGEL_AmbientIntensity': glUniform1f,
        'PYGGEL_DirectionalColor': glUniform3f,
        'PYGGEL_DirectionalIntensity': glUniform1f,
        'PYGGEL_DirectionalNormal': glUniform3f
    })
    shader.compile()
    return shader

def initDisplay(screen_size):
    pygame.display.set_mode(screen_size, OPENGL|DOUBLEBUF)

    glClearColor(0, 0, 0, 0)
    glEnable(GL_DEPTH_TEST)
    glFrontFace(GL_CW)
    glCullFace(GL_BACK)
    glEnable(GL_CULL_FACE)
    clear_screen()

def clear_screen():
    glClear(GL_DEPTH_BUFFER_BIT | GL_COLOR_BUFFER_BIT)

def main():
    pygame.init()

    pygame.display.set_caption('Hello world!')

    screen_size = (640, 480)

    initDisplay(screen_size)

    view = PerspectiveView(45, screen_size, 1, 100)
    camera = LookAtCamera(Vec3(0, 0, 0), Vec3(0, 0, 0), 10)

    thing = makeThing()
    shader = makeShader()
    scene = Scene(view, camera, shader)
    light1 = AmbientLight((1, 0.5, 0.5), 0.1)
    LightNode(light1, parent=scene)
    light2 = DirectionalLight((1, 1, 0.75), 0.5)
    LightNode(light2, parent=scene)
    node1 = TransformNode(position=Vec3(0, 0, 0), parent=scene)
    RenderNode(thing, parent=node1)
    node2 = TransformNode(position=Vec3(2, 0, 0), parent=node1, scale=Vec3(0.25))
    RenderNode(thing, parent=node2)

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
            scene.update()
        scene.render()
        pygame.display.flip()

main()
