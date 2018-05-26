
class SortMethod(object):

    # TODO: think about how we want to handle sorting efficiently
    # 

    @staticmethod
    def front_to_back(self, objs):
        # todo
        return objs

    @staticmethod
    def back_to_front(self, objs):
        # todo
        return objs

class RenderEngine(object):
    '''A simple, single-pass render engine that does not handle transparent meshes differently from opaque'''

    def __init__(self, shader, scene, sort_method=None):
        self.scene = scene
        self.shader = shader
        self.sort_method = sort_method

    def get_sorted_render_nodes(self):
        return self.sort_method(self.scene.flat_nodes['render'])

    def render(self):
        if self.sort_method:
            objs = self.get_sorted_render_nodes()
        else:
            objs = self.scene.flat_nodes['render']

        self.shader.bind()

        # TODO: this should be handled better to support multitexturing
        self.shader.uniform('PYGGEL_TexSampler', 0)
        if self.scene.camera:
            self.shader.uniform('PYGGEL_CameraPos', *self.scene.camera.world_position)

        #TODO: this should really only bind the N most influential lights for an obj
        # so we can have more than 4 of them
        for light_node in self.scene.flat_nodes['light']:
            light_node.light.bind(self.shader)

        for obj in objs:
            self.shader.uniform('PYGGEL_Transformation', 1, False, obj.render_matrix.representation)
            self.shader.uniform('PYGGEL_LocalTransformation', 1, False, obj.transform_matrix.representation)
            obj.mesh.render()
