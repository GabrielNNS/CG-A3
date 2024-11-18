import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import numpy as np

# Função para carregar um modelo .obj
def load_obj(file_path):
    vertices = []
    faces = []

    with open(file_path, 'r') as file:
        for line in file:
            if line.startswith('v '):  # Vértices
                parts = line.split()
                vertices.append([float(parts[1]), float(parts[2]), float(parts[3])])
            elif line.startswith('f '):  # Faces
                parts = line.split()
                face = [int(i.split('/')[0]) - 1 for i in parts[1:]]
                faces.append(face)
    
    return np.array(vertices), faces

# Função para desenhar o modelo
def draw_obj(vertices, faces):
    glBegin(GL_TRIANGLES)
    for face in faces:
        for vertex in face:
            glVertex3fv(vertices[vertex])
    glEnd()

def main():
    pygame.init()
    display = (800, 600)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)

    gluPerspective(45, (display[0] / display[1]), 0.1, 50.0)
    glTranslatef(0.0, 0.0, -5)  # Posição inicial

    # Carregar modelo .obj
    obj_path = "/objects/objeto.obj"  # Certifique-se de ter um arquivo model.obj no mesmo diretório
    vertices, faces = load_obj(obj_path)

    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        # Controles de movimento
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            glRotatef(1, 0, 1, 0)
        if keys[pygame.K_RIGHT]:
            glRotatef(-1, 0, 1, 0)
        if keys[pygame.K_UP]:
            glRotatef(1, 1, 0, 0)
        if keys[pygame.K_DOWN]:
            glRotatef(-1, 1, 0, 0)

        # Renderização
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        draw_obj(vertices, faces)
        pygame.display.flip()

        # Limitar FPS
        clock.tick(60)

if __name__ == "__main__":
    main()