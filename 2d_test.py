
import pygame
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *
import numpy
import math
import random

from pyggel.data import Texture
from pyggel.light import AmbientLight, DirectionalLight, PointLight
from pyggel.math3d import Vec3
from pyggel.mesh import Mesh
from pyggel.render_engine import RenderEngine, SortMethod
from pyggel.scene import Scene, TransformNode, RenderNode, LightNode
from pyggel.shader import Shader
from pyggel.view import PerspectiveView, LookAtCamera, LookFromCamera, View2D, Camera2D

def makeThing():
    vertices = (
        (0, 0, 0),
        (100, 0, 0),
        (100, 100, 0),
        (0, 100, 0),
    )

    texcs = (
        (0, 0),
        (1, 0),
        (1, 1),
        (0, 1)
    )

    colors = (
        (1,1,1,1),
        (1,0,0,1),
        (0,1,0,1),
        (0,0,1,1)
    )

    indices = (
        2, 1, 0,
        0, 3, 2
    )

    texture = Texture.from_file('data/wood-blocks.jpg')

    mesh = Mesh(vertices, texture_coords=texcs, colors = colors, texture=texture, indices=indices)

    return mesh

def makeShader():
    vs = """
        #version 330
        layout (location = 0) in vec3 PYGGEL_Position;
        layout (location = 1) in vec3 PYGGEL_Normal;
        layout (location = 2) in vec2 PYGGEL_TexCoord;
        layout (location = 3) in vec4 PYGGEL_Color;
        // TODO: make this a material and pack values into a vec4?
        layout (location = 4) in float PYGGEL_SpecularIntensity;

        uniform mat4 PYGGEL_Transformation;
        uniform mat4 PYGGEL_LocalTransformation;

        out vec4 Color;
        out vec2 TexCoord;
        out vec4 Normal;

        out mat4 LocalTransformation;
        out vec3 CameraPos;
        out vec3 LocalPosition;
        out float SpecularIntensity;

        void main() {
            Color = PYGGEL_Color;
            vec4 tempPosition = vec4(PYGGEL_Position, 1.0f);
            gl_Position = tempPosition * PYGGEL_Transformation;
            LocalPosition = (tempPosition * PYGGEL_LocalTransformation).xyz;
            TexCoord = PYGGEL_TexCoord;
            Normal = vec4(PYGGEL_Normal, 0.0f);
            LocalTransformation = PYGGEL_LocalTransformation;
            SpecularIntensity = PYGGEL_SpecularIntensity;
        }"""
    fs = """
        #version 330
        in vec4 Color;
        in vec2 TexCoord;
        in vec4 Normal;
        in mat4 LocalTransformation;
        in vec3 LocalPosition;
        in float SpecularIntensity;

        // TODO: light definitions should come in from a uniform buffer so we don't have to ship all this data in
        //const int MAX_POINT_LIGHTS = 16;
        const int MAX_POINT_LIGHTS = 4;
        // NOTE: this is a maximum number of lights that may be active for a single fragment - to allow cheaper/easier switching
        //const int MAX_ACTIVE_POINT_LIGHTS = 4;
        const float MIN_POINT_LIGHT_ATTENUATION = 0.0f;

        struct AmbientLight {
            vec3 color;
            float intensity;
        };

        struct DirectionalLight {
            vec3 color;
            float intensity;
            vec3 normal;
            float specularPower;
        };

        struct PointLight {
            vec3 color;
            float intensity;
            vec3 position;
            float specularPower;
            float attenuationConstant;
            float attenuationLinear;
            float attenuationExponent;
        };

        vec4 calculate_ambient_light(AmbientLight light) {
            return vec4(light.color, 1.0f) * light.intensity;
        }

        vec4 calculate_directional_light(DirectionalLight light, vec3 vertexToEye) {
            vec4 transNormal = normalize(Normal * LocalTransformation);

            float diffuseNormalIntensity = dot(transNormal, vec4(-light.normal, 1.0f));
            vec4 diffuse = vec4(0,0,0,0);
            vec4 specular = vec4(0,0,0,0);

            if (diffuseNormalIntensity > 0) {
                diffuse = vec4(light.color, 1.0f) * light.intensity * diffuseNormalIntensity;
            }
            if (diffuseNormalIntensity > 0.1) {
                vec3 lightReflect = normalize(reflect(light.normal, transNormal.xyz));
                float specularFactor = dot(vertexToEye, lightReflect);
                if (specularFactor > 0){
                    specularFactor = pow(specularFactor, light.specularPower);
                    specular = vec4(light.color * SpecularIntensity * specularFactor, 1.0f);
                }
            }

            return diffuse + specular;
        }

        vec4 calculate_point_light(PointLight light, vec3 vertexToEye) {
            vec3 lightDirection = LocalPosition - light.position;
            float distance = length(lightDirection);
            float attenuation = light.attenuationConstant +
                                (light.attenuationLinear * distance) +
                                (light.attenuationExponent * distance * distance);

            if (attenuation <= MIN_POINT_LIGHT_ATTENUATION) {
                // basically no effect on this object so skip the more expensive stuff
                return vec4(0,0,0,0);
            } else {
                DirectionalLight dlight = DirectionalLight(light.color, light.intensity, normalize(lightDirection), light.specularPower);
                return calculate_directional_light(dlight, vertexToEye) / attenuation;
            }
        }

        uniform vec3 PYGGEL_CameraPos;
        uniform sampler2D PYGGEL_TexSampler;
        uniform AmbientLight PYGGEL_AmbientLight;
        uniform DirectionalLight PYGGEL_DirectionalLight;
        uniform PointLight PYGGEL_PointLights[MAX_POINT_LIGHTS];
        //uniform int PYGGEL_ActivePointLights[MAX_ACTIVE_POINT_LIGHTS];


        out vec4 FragColor;

        void main() {
            vec4 baseColor = texture2D(PYGGEL_TexSampler, TexCoord.st) * Color;

            vec3 vertexToEye = normalize(PYGGEL_CameraPos - LocalPosition);

            vec4 lightColor = calculate_ambient_light(PYGGEL_AmbientLight) +
                              calculate_directional_light(PYGGEL_DirectionalLight, vertexToEye);

            //for (int i = 0; i<MAX_ACTIVE_POINT_LIGHTS; i++) {
            for (int i = 0; i<MAX_POINT_LIGHTS; i++) {
                //lightColor += calculate_point_light(PYGGEL_PointLights[PYGGEL_ActivePointLights[i]], vertexToEye); 
                lightColor += calculate_point_light(PYGGEL_PointLights[i], vertexToEye); 
            }

            FragColor = baseColor * vec4(lightColor.xyz, 1.0f);
            FragColor = baseColor;
        }"""

    # build point light attrs
    pl_params = {}
    for i in range(4):
        pl_params['PYGGEL_PointLights[%s].color'%i] = glUniform3f
        pl_params['PYGGEL_PointLights[%s].intensity'%i] = glUniform1f
        pl_params['PYGGEL_PointLights[%s].position'%i] = glUniform3f
        pl_params['PYGGEL_PointLights[%s].specularPower'%i] = glUniform1f
        pl_params['PYGGEL_PointLights[%s].attenuationConstant'%i] = glUniform1f
        pl_params['PYGGEL_PointLights[%s].attenuationLinear'%i] = glUniform1f
        pl_params['PYGGEL_PointLights[%s].attenuationExponent'%i] = glUniform1f

    shader = Shader(vs, fs, {
        'PYGGEL_Transformation': glUniformMatrix4fv,
        'PYGGEL_LocalTransformation': glUniformMatrix4fv,
        'PYGGEL_CameraPos': glUniform3f,
        'PYGGEL_TexSampler': glUniform1i,
        'PYGGEL_AmbientLight.color': glUniform3f,
        'PYGGEL_AmbientLight.intensity': glUniform1f,
        'PYGGEL_DirectionalLight.color': glUniform3f,
        'PYGGEL_DirectionalLight.intensity': glUniform1f,
        'PYGGEL_DirectionalLight.normal': glUniform3f,
        'PYGGEL_DirectionalLight.specularPower': glUniform1f,
        **pl_params
    })
    shader.compile()
    return shader

def initDisplay(screen_size):
    pygame.display.set_mode(screen_size, OPENGL|DOUBLEBUF)

    glClearColor(0, 0, 0, 0)
    glEnable(GL_DEPTH_TEST)
    glFrontFace(GL_CW)
    glCullFace(GL_BACK)
    # glEnable(GL_CULL_FACE)
    # glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)
    glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA)
    glEnable(GL_BLEND)
    clear_screen()

def clear_screen():
    glClear(GL_DEPTH_BUFFER_BIT | GL_COLOR_BUFFER_BIT)

def main():
    pygame.init()

    pygame.display.set_caption('Hello world!')

    screen_size = (640, 480)

    initDisplay(screen_size)

    # create our world
    thing = makeThing()
    shader = makeShader()
    view = View2D(screen_size)
    camera = Camera2D(screen_size, Vec3(0,0,0))
    scene = Scene(view, camera)
    renderEngine = RenderEngine(shader, scene)


    # populate our scene
    node1 = TransformNode(position=Vec3(100, 0, 0), parent=scene)
    RenderNode(thing, parent=node1)

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

        if not paused:
            objx += 0.001

            # node1.position.x = math.sin(objx)
            # node1.rotation.y += 0.001

            # update node and children
            scene.update()

        clear_screen()
        renderEngine.render()
        pygame.display.flip()

main()
