
from .math3d import Vec3
from OpenGL.GL import GL_TRIANGLES


def calculate_normals_for_mesh(mesh):
    if not mesh.render_primitive == GL_TRIANGLES:
        # TODO: handle more.../all???
        raise Exception('Cannot calculate normals for non-triangle render types')

    normals = [Vec3(0)] * len(mesh.vertices)

    indices = mesh.indices
    verts = mesh.vertices

    # a triangle (with face) is 3 verts (so 3 indices)
    for i in range(0, len(indices), 3):
        ind1 = indices[i]
        ind2 = indices[i + 1]
        ind3 = indices[i + 2]
        vert1 = Vec3(verts[ind1])
        vert2 = Vec3(verts[ind2])
        vert3 = Vec3(verts[ind3])
        u = vert2 - vert1
        v = vert3 - vert1
        normal = u.cross(v).normalize()
        # have to make sure we set new instances instead of adding in place
        normals[ind1] = normals[ind1] + normal
        normals[ind2] = normals[ind2] + normal
        normals[ind3] = normals[ind3] + normal

    n = tuple(tuple(n.normalize()) for n in normals)
    return n
