

class Light(object):
    shader_params = {}

    def __init__(self, color, intensity=1.0):
        # TODO: enforce correct type(s) for color (vec3/tuple(3))
        self.color = color
        self.intensity = intensity

    def bind(self, shader):
        # TODO: add a param to shader_params so this can be auto-generated
        shader.uniform(self.shader_params['color'], *self.color)
        shader.uniform(self.shader_params['intensity'], self.intensity)

class AmbientLight(Light):
    shader_params = {
        'color': 'PYGGEL_AmbientColor',
        'intensity': 'PYGGEL_AmbientIntensity'
    }

class DirectionalLight(Light):
    shader_params = {
        'color': 'PYGGEL_DirectionalColor',
        'intensity': 'PYGGEL_DirectionalIntensity',
        'normal': 'PYGGEL_DirectionalNormal',
        'specular_power': 'PYGGEL_SpecularPower'
    }

    def __init__(self, color, intensity=1.0, normal=(1, 1, 1), specular_power=32):
        self.color = color
        self.intensity = intensity
        self.normal = normal
        self.specular_power = specular_power

    def bind(self, shader):
        super(DirectionalLight, self).bind(shader)
        shader.uniform(self.shader_params['normal'], *self.normal)
        shader.uniform(self.shader_params['specular_power'], self.specular_power)
