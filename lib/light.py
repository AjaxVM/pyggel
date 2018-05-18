

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
