
class SortMethod(object):

    # TODO: think about how we want to handle sorting efficiently
    #       the default method below is very slow

    @staticmethod
    def default(opaque, transparent=None):
        opaque = sorted(opaque, key=lambda a: a.get_render_position().z)
        if transparent:
            transparent = sorted(transparent, key=lambda a: -a.get_render_position().z)
        return opaque, transparent

class RenderEngine(object):
    '''A simple, single-pass render engine that does not handle transparent meshes differently from opaque'''

    def __init__(self, shader, scene, sort_method=None):
        self.scene = scene
        self.shader = shader
        self.sort_method = sort_method

    def get_sorted_render_nodes(self):
        oObjs = self.scene.flat_nodes['render_opaque']
        tObjs = self.scene.flat_nodes['render_transparent']
        if self.sort_method:
            return self.sort_method(oObjs, tObjs)
        return oObjs, tObjs

    def render(self):
        oObjs, tObjs = self.get_sorted_render_nodes()

        self.shader.bind()

        # TODO: this should be handled better to support multitexturing
        # this should really be a part of binding the texture or something... but how?
        self.shader.uniform('PYGGEL_TexSampler', 0)
        if self.scene.camera:
            self.shader.uniform('PYGGEL_CameraPos', *self.scene.camera.world_position)

        #TODO: this should really only bind the N most influential lights for an obj
        # so we can have more than 4 of them
        for light_node in self.scene.flat_nodes['light']:
            light_node.light.bind(self.shader)

        for obj in oObjs:
            self.shader.uniform('PYGGEL_Transformation', 1, False, obj.render_matrix.representation)
            self.shader.uniform('PYGGEL_LocalTransformation', 1, False, obj.transform_matrix.representation)
            obj.mesh.render()

        if tObjs:
            for obj in tObjs:
                self.shader.uniform('PYGGEL_Transformation', 1, False, obj.render_matrix.representation)
                self.shader.uniform('PYGGEL_LocalTransformation', 1, False, obj.transform_matrix.representation)
                obj.mesh.render()
