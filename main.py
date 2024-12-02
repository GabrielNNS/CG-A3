import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import math

display = [1366, 768]
obj_path = "Objects/rocket.obj"
tex_path = "Objects/rocket.png"
flying_move = 0.05

def compute_normal(v1, v2, v3): # Calcula a normal para uma face a partir de 3 vértices
    u = np.subtract(v2, v1)
    v = np.subtract(v3, v1)
    normal = np.cross(u, v)  # Produto vetorial
    normal = normal / np.linalg.norm(normal)  # Normalização
    return normal

def load_obj(file_path): # Carrega o objeto com os vértices, coordenadas de textura e as faces
    vertices = []
    tex_coords = []
    faces = []
    normals = []

    with open(file_path, 'r') as obj_file:
        for line in obj_file:
            parts = line.split()
            if not parts:
                continue

            if parts[0] == 'v':  # Lê vértices
                vertices.append([float(x) for x in parts[1:4]])
            elif parts[0] == 'vt':  # Lê coordenadas de textura
                tex_coords.append([float(x) for x in parts[1:3]])
            elif parts[0] == 'f':  # Lê faces
                face = []
                for vertex in parts[1:]:
                    indices = vertex.split('/')
                    v_idx = int(indices[0]) - 1  # Índice do vértice
                    vt_idx = int(indices[1]) - 1 if len(indices) > 1 and indices[1] else None  # Índice da textura
                    face.append((v_idx, vt_idx))
                faces.append(face)

                # Calcular normal para cada face
                v1 = np.array(vertices[face[0][0]])
                v2 = np.array(vertices[face[1][0]])
                v3 = np.array(vertices[face[2][0]])
                normal = compute_normal(v1, v2, v3)
                normals.append(normal)

    return vertices, tex_coords, faces, normals

def setup_lighting():
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)

    # Configurar a luz
    light_position = [5.0, 5.0, 5.0, 1.0]  # Posição da luz
    light_ambient = [0.2, 0.2, 0.2, 1.0]  # Luz ambiente
    light_diffuse = [0.8, 0.8, 0.8, 1.0]  # Luz difusa
    light_specular = [1.0, 1.0, 1.0, 1.0]  # Luz especular

    glLightfv(GL_LIGHT0, GL_POSITION, light_position)
    glLightfv(GL_LIGHT0, GL_AMBIENT, light_ambient)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, light_diffuse)
    glLightfv(GL_LIGHT0, GL_SPECULAR, light_specular)

    # Configurar material
    material_specular = [1.0, 1.0, 1.0, 1.0]
    material_shininess = [50.0]
    glMaterialfv(GL_FRONT, GL_SPECULAR, material_specular)
    glMaterialfv(GL_FRONT, GL_SHININESS, material_shininess)

def render_model(vertices, tex_coords, faces, normals):
    glBegin(GL_TRIANGLES)
    for i, face in enumerate(faces):
        for vertex in face:
            v_idx, vt_idx = vertex
            if vt_idx is not None and vt_idx < len(tex_coords):  # Verifique se o índice de textura é válido
                glTexCoord2f(*tex_coords[vt_idx])
            glNormal3f(*normals[i])  # Usar normal para cada face
            glVertex3f(*vertices[v_idx])  # Usar vértice para cada face
    glEnd()

def move_object(x, y, z):
    glTranslatef(x, y, z)
    
def rotate_object(rotate_x, rotate_y):
    glRotatef(rotate_x, 1, 0, 0)  
    glRotatef(rotate_y, 0, 1, 0)
    
def reset():
    glLoadIdentity()
    gluPerspective(20, (display[0] / display[1]), 0.1, 50.0)
    glTranslatef(0.0, 0.0, -3)
    glScale(0.1, 0.1, 0.1)

def main():
    pygame.init()
    screen = pygame.display.set_mode(display, pygame.DOUBLEBUF | pygame.OPENGL)
    gluPerspective(20, (display[0] / display[1]), 0.1, 50.0)
    glTranslatef(0.0, 0.0, -3)
    glScale(0.1, 0.1, 0.1)
    glClearColor(0.1, 0.1, 0.1, 1.0)

    vertices, tex_coords, faces, normals = load_obj(obj_path)
    
    setup_lighting()

    print("Vértices carregados:", len(vertices))
    print("Coordenadas de textura carregadas:", len(tex_coords))
    print("Faces carregadas:", len(faces))

    texture_surface = pygame.image.load(tex_path)
    texture_data = pygame.image.tostring(texture_surface, "RGB", True)
    width, height = texture_surface.get_size()

    rocket_texture_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, rocket_texture_id)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, texture_data)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    glEnable(GL_TEXTURE_2D)
    glEnable(GL_CULL_FACE)  
    glCullFace(GL_BACK) 
    glFrontFace(GL_CCW)
    glEnable(GL_DEPTH_TEST) 
    glDepthFunc(GL_LEQUAL)
    
    time_elapsed = 0  # Tempo acumulado para a animação do voo
    flying_offset = 0  # Deslocamento no eixo Y devido à animação

    clock = pygame.time.Clock()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

        y_move = 0  
        x_move = 0 
        z_move = 0
        
        rotate_x = 0
        rotate_y = 0
        
        teclas = pygame.key.get_pressed()
        if teclas[K_w]:
            y_move += 0.5  # Mover para cima
        if teclas[K_s]:
            y_move -= 0.5  # Mover para baixo
        if teclas[K_a]:
            x_move -= 0.5  # Mover para a esquerda
        if teclas[K_d]:
            x_move += 0.5  # Mover para a direita
        if teclas[K_q]:
            z_move += 5  # Zoom      
        if teclas[K_e]:
            z_move -= 5  # Zoom         
                        
        if teclas[K_LEFT]:
            rotate_y -= 4  # Girar para a esquerda
        if teclas[K_RIGHT]:
            rotate_y += 4  # Girar para a direita
        if teclas[K_UP]:
            rotate_x -= 4  # Girar para cima
        if teclas[K_DOWN]:
            rotate_x += 4  # Girar para baixo
            
        if teclas[K_r]: # Reseta tudo :3
            reset()

        time_elapsed += clock.get_time() / 1000.0  # Atualizar tempo acumulado
        flying_offset = math.sin(time_elapsed) * 0.01  # Oscilação suave (frequência e amplitude ajustáveis)
        y_move += flying_offset

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        move_object(x_move, y_move, z_move)
        rotate_object(rotate_x, rotate_y)
        glBindTexture(GL_TEXTURE_2D, rocket_texture_id)
        render_model(vertices, tex_coords, faces, normals)
        
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()