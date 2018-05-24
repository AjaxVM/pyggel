

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
        'color': 'PYGGEL_AmbientLight.color',
        'intensity': 'PYGGEL_AmbientLight.intensity'
    }

class DirectionalLight(Light):
    shader_params = {
        'color': 'PYGGEL_DirectionalLight.color',
        'intensity': 'PYGGEL_DirectionalLight.intensity',
        'normal': 'PYGGEL_DirectionalLight.normal',
        'specular_power': 'PYGGEL_DirectionalLight.specularPower'
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

# TODO: implement max active
MAX_POINT_LIGHTS = 4

class PointLight(Light):

    _bound_lights = []

    shader_params = {
        'color': 'PYGGEL_PointLights[%d].color',
        'intensity': 'PYGGEL_PointLights[%d].intensity',
        'position': 'PYGGEL_PointLights[%d].position',
        'specular_power': 'PYGGEL_PointLights[%d].specularPower',
        'attenuation_constant': 'PYGGEL_PointLights[%d].attenuationConstant',
        'attenuation_linear': 'PYGGEL_PointLights[%d].attenuationLinear',
        'attenuation_exponent': 'PYGGEL_PointLights[%d].attenuationExponent'
    }

    def __init__(self, color, intensity=1.0, position=(0, 0, 0), specular_power=32, attenuation_params=(1, 0.5, 0.1)):
        self.color = color
        self.intensity = intensity
        self.position = position
        self.specular_power = specular_power
        self.attenuation_params = attenuation_params

        self._current_id = -1 # not bound

    def bind(self, shader):
        # if self in self._bound_lights:
        #     return
        # TODO: this needs to be smarter... - possibly an attribute of shader derived from getting the value or something?
        # or it is a uniform set by shader, I dunno
        if self not in self._bound_lights and len(self._bound_lights) > MAX_POINT_LIGHTS:
            raise Exception('Too many point lights active - max %s'%MAX_POINT_LIGHTS)

        if not self in self._bound_lights:
            self._bound_lights.append(self)
            self._current_id = -1
        if self._current_id == -1:
            self._current_id = self._get_id()
        shader.uniform(self.shader_params['color']%self._current_id, *self.color)
        shader.uniform(self.shader_params['intensity']%self._current_id, self.intensity)
        shader.uniform(self.shader_params['position']%self._current_id, *self.position)
        shader.uniform(self.shader_params['specular_power']%self._current_id, self.specular_power)
        shader.uniform(self.shader_params['attenuation_constant']%self._current_id, self.attenuation_params[0])
        shader.uniform(self.shader_params['attenuation_linear']%self._current_id, self.attenuation_params[1])
        shader.uniform(self.shader_params['attenuation_exponent']%self._current_id, self.attenuation_params[2])

    def unbind(self):
        if self in self._bound_lights:
            self._bound_lights.remove(self)
            self._current_id = -1

    def _get_id(self):
        # free = list(range(MAX_POINT_LIGHTS))
        used = map(lambda light: light._current_id, self._bound_lights)

        for _id in range(MAX_POINT_LIGHTS):
            if _id not in used:
                return _id

        raise Exception('Cannot get id for point light - too many bound - max %s'%MAX_POINT_LIGHTS)

