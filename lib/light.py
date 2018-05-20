

class Light(object):
    shader_params = {}

    def __init__(self, color, intensity=1.0):
        # TODO: enforce correct type(s) for color (vec3/tuple(3))
        self.color = color
        self.intensity = intensity

    def bind(self, shader):
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
        'normal': 'PYGGEL_DirectionalNormal'
    }

    def __init__(self, color, intensity=1.0, normal=(1, 1, 1)):
        self.color = color
        self.intensity = intensity
        self.normal = normal

    def bind(self, shader):
        super(DirectionalLight, self).bind(shader)
        shader.uniform(self.shader_params['normal'], *self.normal)
