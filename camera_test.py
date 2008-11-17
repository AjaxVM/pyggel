import pyggel
from pyggel import *

def main():
    pyggel.init()

    pyggel.view.set_lighting(False)

    camera1 = pyggel.camera.LookFromCamera((0,0,10))
    camera2 = pyggel.camera.LookAtCamera((0,0,0), distance=10)
    camera = camera1
    font = pyggel.font.Font()
    img = font.make_text_image3D("Hello World: 3D", (255, 255, 0))
    print img._pimage2.get_at((0,0))
    img.scale = 5
    img2 = font.make_text_image3D("Hello World: 3D X2!!!", (0, 255, 255))
    img2.pos = (0, 1, 0)
    img3 = img2.copy()
    img3.pos = (0, 0, 0)
    img4 = font.make_text_image3D("Testy...123...", (0, 255, 0))
    img4.pos = (0, -1, 0)

    text = font.make_text_image("ARG!!!!", (255, 0, 0))
    text.scale = 10

    box = pyggel.geometry.Cube(5)
    box.pos=(0,0,-5)

    mscene = pyggel.scene.Scene()
    mscene.add_3d_image(img)
    mscene.add_3d_image(img2)
    mscene.add_3d(box)
    mscene.add_3d_image(img3)
    mscene.add_3d_image(img4)
    mscene.add_2d(text)

    clock = pygame.time.Clock()

    while 1:
        clock.tick(999)
        print clock.get_fps()

        for event in pyggel.get_events():
            if event.type == QUIT:
                pyggel.quit()
                return None

            if event.type == KEYDOWN and event.key == K_RETURN:
                if camera == camera1:
                    camera = camera2
                else:
                    camera = camera1

        key = pygame.key.get_pressed()
        if key[K_m]:
            if key[K_LEFT]:
                camera.posx -= .1
            if key[K_RIGHT]:
                camera.posx += .1
            if key[K_UP]:
                camera.posy += .1
            if key[K_DOWN]:
                camera.posy -= .1
            if key[K_MINUS]:
                camera.posz += .1
            if key[K_EQUALS]:
                camera.posz -= .1
        elif key[K_r]:
            if key[K_LEFT]:
                camera.roty -= .25
            if key[K_RIGHT]:
                camera.roty += .25
            if key[K_UP]:
                camera.rotx -= .25
            if key[K_DOWN]:
                camera.rotx += .25
            if key[K_MINUS]:
                camera.rotz -= .25
            if key[K_EQUALS]:
                camera.rotz += .25

        pyggel.view.clear_screen()
        mscene.render(camera)
        pyggel.view.refresh_screen()

main()
