#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <float.h>
#include <math.h>
#include "rendering.h"
#include "rmath.h"
#include "model.h"

Framebuffer* create_framebuffer(int width, int height, int channels) {
    Framebuffer* fb = malloc(sizeof(Framebuffer));
    if (!fb) return NULL;
    
    fb->width = width;
    fb->height = height;
    fb->channels = channels;
    fb->pixels = calloc(width * height * channels, sizeof(unsigned char));
    
    if (!fb->pixels) {
        free(fb);
        return NULL;
    }
    
    return fb;
}

void free_framebuffer(Framebuffer* fb) {
    if (fb) {
        free(fb->pixels);
        free(fb);
    }
}

void clear_framebuffer(Framebuffer* fb, unsigned char value) {
    if (fb && fb->pixels) {
        memset(fb->pixels, value, fb->width * fb->height * fb->channels);
    }
}

void set_pixel(Framebuffer* fb, int x, int y, unsigned char r, unsigned char g, unsigned char b) {
    if (!fb || !fb->pixels) return;
    
    if (x >= 0 && x < fb->width && y >= 0 && y < fb->height) {
        int pixel_index = (y * fb->width + x) * fb->channels;
        if (fb->channels == 1) {
            fb->pixels[pixel_index] = (unsigned char)(0.299f * r + 0.587f * g + 0.114f * b);
        } else if (fb->channels == 3) {
            fb->pixels[pixel_index] = r;
            fb->pixels[pixel_index + 1] = g;
            fb->pixels[pixel_index + 2] = b;
        }
    }
}

Vec3 sample_texture(Model* model, float u, float v) {
    if (!model || !model->texture || model->tex_width <= 0 || model->tex_height <= 0) {
        return (Vec3){1.0f, 1.0f, 1.0f}; // Fallback to white if texture is invalid
    }
    
    // Check for invalid texture coordinates
    if (!isfinite(u) || !isfinite(v)) {
        return (Vec3){1.0f, 1.0f, 1.0f};
    }
    
    // Wrap texture coordinates instead of clamping for better tiling
    u = u - floorf(u); // Keep fractional part (0.0 to 1.0)
    v = v - floorf(v);
    if (u < 0) u += 1.0f;
    if (v < 0) v += 1.0f;
    
    // Clamp to [0, 1] range
    u = fmaxf(0.0f, fminf(1.0f, u));
    v = fmaxf(0.0f, fminf(1.0f, v));
    
    // Map to texture pixel coordinates
    int x = (int)(u * (model->tex_width - 1));
    int y = (int)(v * (model->tex_height - 1));
    
    // Ensure indices are within bounds
    x = fmaxf(0, fminf(model->tex_width - 1, x));
    y = fmaxf(0, fminf(model->tex_height - 1, y));
    
    int index = (y * model->tex_width + x) * 3;
    
    // Ensure index is within texture array bounds
    int max_index = model->tex_width * model->tex_height * 3;
    if (index >= max_index - 2 || index < 0) {
        return (Vec3){1.0f, 1.0f, 1.0f};
    }
    
    Vec3 color = {
        model->texture[index] / 255.0f,
        model->texture[index + 1] / 255.0f,
        model->texture[index + 2] / 255.0f
    };
    
    // Ensure color values are valid
    color.x = fmaxf(0.0f, fminf(1.0f, color.x));
    color.y = fmaxf(0.0f, fminf(1.0f, color.y));
    color.z = fmaxf(0.0f, fminf(1.0f, color.z));
    
    return color;
}

// Helper function to compute barycentric coordinates - CORRECTED VERSION
void compute_barycentric(Vec3 p, Vec3 a, Vec3 b, Vec3 c, float* u, float* v, float* w) {
    // Using area-based barycentric coordinates for better numerical stability
    Vec3 v0 = vec3_sub(c, a);
    Vec3 v1 = vec3_sub(b, a);
    Vec3 v2 = vec3_sub(p, a);
    
    float dot00 = vec3_dot(v0, v0);
    float dot01 = vec3_dot(v0, v1);
    float dot02 = vec3_dot(v0, v2);
    float dot11 = vec3_dot(v1, v1);
    float dot12 = vec3_dot(v1, v2);
    
    float denom = dot00 * dot11 - dot01 * dot01;
    if (fabsf(denom) < 1e-8f) {
        // Degenerate triangle
        *u = *v = *w = 0.0f;
        return;
    }
    
    float inv_denom = 1.0f / denom;
    
    *w = (dot11 * dot02 - dot01 * dot12) * inv_denom;  // weight for vertex c
    *v = (dot00 * dot12 - dot01 * dot02) * inv_denom;  // weight for vertex b
    *u = 1.0f - *v - *w;                                // weight for vertex a
    
    // Ensure barycentric coordinates are valid
    if (!isfinite(*u)) *u = 0.0f;
    if (!isfinite(*v)) *v = 0.0f;
    if (!isfinite(*w)) *w = 0.0f;
}

void fill_triangle_textured(Framebuffer* fb, Vec3 v1, Vec3 v2, Vec3 v3, 
                           TexCoord t1, TexCoord t2, TexCoord t3, Model* model, Light* light) {
    if (!fb || !fb->pixels || !model || !light) return;
    
    // Find bounding box of triangle
    int min_x = (int)fmaxf(0, fminf(fminf(v1.x, v2.x), v3.x));
    int max_x = (int)fminf(fb->width - 1, fmaxf(fmaxf(v1.x, v2.x), v3.x));
    int min_y = (int)fmaxf(0, fminf(fminf(v1.y, v2.y), v3.y));
    int max_y = (int)fminf(fb->height - 1, fmaxf(fmaxf(v1.y, v2.y), v3.y));
    
    if (min_x > max_x || min_y > max_y) return;
    
    // Check for degenerate triangle
    float area = (v2.x - v1.x) * (v3.y - v1.y) - (v3.x - v1.x) * (v2.y - v1.y);
    if (fabsf(area) < 1e-6f) return;
    
    // Compute triangle's normal
    Vec3 edge1 = vec3_sub(v2, v1);
    Vec3 edge2 = vec3_sub(v3, v1);
    Vec3 normal = vec3_normalize(vec3_cross(edge1, edge2));
    
    if (!isfinite(normal.x) || !isfinite(normal.y) || !isfinite(normal.z)) {
        normal = (Vec3){0.0f, 0.0f, 1.0f};
    }
    
    // FIXED: Use proper barycentric coordinate calculation
    float inv_area = 1.0f / area;
    
    for (int y = min_y; y <= max_y; y++) {
        for (int x = min_x; x <= max_x; x++) {
            // Calculate barycentric coordinates using cross products
            float px = (float)x + 0.5f;
            float py = (float)y + 0.5f;
            
            // Calculate areas of sub-triangles
            float area1 = ((v2.x - px) * (v3.y - py) - (v3.x - px) * (v2.y - py)) * inv_area;
            float area2 = ((v3.x - px) * (v1.y - py) - (v1.x - px) * (v3.y - py)) * inv_area;
            float area3 = 1.0f - area1 - area2;
            
            // Check if point is inside triangle
            if (area1 >= 0.0f && area2 >= 0.0f && area3 >= 0.0f) {
                // Interpolate texture coordinates
                float tex_u = area1 * t1.u + area2 * t2.u + area3 * t3.u;
                float tex_v = area1 * t1.v + area2 * t2.v + area3 * t3.v;
                
                // Clamp texture coordinates
                tex_u = fmaxf(0.0f, fminf(1.0f, tex_u));
                tex_v = fmaxf(0.0f, fminf(1.0f, tex_v));
                
                // Sample texture
                Vec3 tex_color = sample_texture(model, tex_u, tex_v);
                
                // Calculate lighting
                Vec3 lit_color = calculate_lighting(normal, tex_color, light);
                
                // Convert to pixel values
                unsigned char r = (unsigned char)fminf(255.0f, fmaxf(0.0f, lit_color.x * 255.0f + 0.5f));
                unsigned char g = (unsigned char)fminf(255.0f, fmaxf(0.0f, lit_color.y * 255.0f + 0.5f));
                unsigned char b = (unsigned char)fminf(255.0f, fmaxf(0.0f, lit_color.z * 255.0f + 0.5f));
                
                set_pixel(fb, x, y, r, g, b);
            }
        }
    }
}

void draw_line_fb(Framebuffer* fb, int x0, int y0, int x1, int y1, 
                  unsigned char r, unsigned char g, unsigned char b) {
    if (!fb || !fb->pixels) return;
    
    int dx = abs(x1 - x0);
    int dy = abs(y1 - y0);
    int sx = x0 < x1 ? 1 : -1;
    int sy = y0 < y1 ? 1 : -1;
    int err = dx - dy;

    while (1) {
        set_pixel(fb, x0, y0, r, g, b);
        
        if (x0 == x1 && y0 == y1) break;
        
        int e2 = 2 * err;
        if (e2 > -dy) {
            err -= dy;
            x0 += sx;
        }
        if (e2 < dx) {
            err += dx;
            y0 += sy;
        }
    }
}

void save_pam(Framebuffer* fb, const char* filename) {
    if (!fb || !fb->pixels || !filename) return;
    
    FILE* file = fopen(filename, "w");
    if (!file) {
        printf("Error: Cannot create file %s\n", filename);
        return;
    }

    fprintf(file, "P7\n");
    fprintf(file, "WIDTH %d\n", fb->width);
    fprintf(file, "HEIGHT %d\n", fb->height);
    fprintf(file, "DEPTH %d\n", fb->channels);
    fprintf(file, "MAXVAL 255\n");
    
    if (fb->channels == 1) {
        fprintf(file, "TUPLTYPE GRAYSCALE\n");
    } else if (fb->channels == 3) {
        fprintf(file, "TUPLTYPE RGB\n");
    }
    
    fprintf(file, "ENDHDR\n");

    for (int i = 0; i < fb->width * fb->height * fb->channels; i++) {
        fprintf(file, "%d", fb->pixels[i]);
        
        if ((i + 1) % 12 == 0) {
            fprintf(file, "\n");
        } else {
            fprintf(file, " ");
        }
    }
    
    if ((fb->width * fb->height * fb->channels) % 12 != 0) {
        fprintf(file, "\n");
    }
    
    fclose(file);
    printf("Saved %s (%dx%d, %d channels)\n", filename, fb->width, fb->height, fb->channels);
}

Vec3 world_to_screen(Vec3 world_pos, Camera* camera) {
    if (!camera) return world_pos;
    
    Vec3 screen;
    screen.x = (world_pos.x + 1.0f) * camera->screen_width * 0.5f;
    screen.y = (1.0f - world_pos.y) * camera->screen_height * 0.5f;
    screen.z = world_pos.z;
    
    // Validate screen coordinates
    if (!isfinite(screen.x)) screen.x = 0.0f;
    if (!isfinite(screen.y)) screen.y = 0.0f;
    if (!isfinite(screen.z)) screen.z = 0.0f;
    
    return screen;
}

Vec3 calculate_lighting(Vec3 surface_normal, Vec3 base_color, Light* light) {
    if (!light) return base_color;
    
    // Ensure we have a valid normal
    Vec3 normal = vec3_normalize(surface_normal);
    if (!isfinite(normal.x) || !isfinite(normal.y) || !isfinite(normal.z)) {
        normal = (Vec3){0.0f, 0.0f, 1.0f}; // Default normal
    }
    
    // Ensure light direction is normalized
    Vec3 light_dir = vec3_normalize(light->direction);
    if (!isfinite(light_dir.x) || !isfinite(light_dir.y) || !isfinite(light_dir.z)) {
        light_dir = (Vec3){0.0f, 0.0f, -1.0f}; // Default light direction
    }
    
    // Calculate ambient component
    Vec3 ambient = vec3_multiply(base_color, vec3_scale(light->ambient_color, light->ambient_intensity));
    
    // Calculate diffuse component
    float diffuse_factor = fmaxf(0.0f, vec3_dot(normal, light_dir));
    Vec3 diffuse = vec3_multiply(base_color, vec3_scale(vec3_scale(light->color, light->intensity), diffuse_factor));
    
    // Combine lighting components
    Vec3 final_color = vec3_add(ambient, diffuse);
    
    // Clamp final color and ensure it's valid
    final_color = vec3_clamp(final_color, 0.0f, 1.0f);
    
    // Validate final color components
    if (!isfinite(final_color.x)) final_color.x = base_color.x;
    if (!isfinite(final_color.y)) final_color.y = base_color.y;
    if (!isfinite(final_color.z)) final_color.z = base_color.z;
    
    return final_color;
}

int compare_triangles(const void *a, const void *b) {
    Triangle *ta = (Triangle*)a;
    Triangle *tb = (Triangle*)b;
    if (ta->avg_z < tb->avg_z) return -1;
    if (ta->avg_z > tb->avg_z) return 1;
    return 0;
}

TexCoord get_texture_coord(Model* model, Face* face, int vertex_index) {
    if (!model || !face) {
        return (TexCoord){0.5f, 0.5f};
    }
    
    // Get vertex index from face
    int vert_index = -1;
    if (vertex_index == 0) vert_index = face->v1;
    else if (vertex_index == 1) vert_index = face->v2;
    else if (vertex_index == 2) vert_index = face->v3;
    
    if (vert_index < 0 || vert_index >= model->vertex_count) {
        return (TexCoord){0.5f, 0.5f};
    }
    
    Vec3 vertex = model->vertices[vert_index];
    
    // FIXED: Generate proper cube face texture coordinates
    // Determine which face this vertex belongs to and generate appropriate UVs
    float abs_x = fabsf(vertex.x);
    float abs_y = fabsf(vertex.y);
    float abs_z = fabsf(vertex.z);
    
    // Use a small epsilon for floating point comparison
    const float epsilon = 0.9f;
    
    if (abs_x > epsilon) {
        // Left/Right face (X-dominant)
        if (vertex.x > 0) {
            // Right face (+X)
            return (TexCoord){
                (1.0f - vertex.z) * 0.5f + 0.5f,  // Map Z to U
                (vertex.y + 1.0f) * 0.5f           // Map Y to V
            };
        } else {
            // Left face (-X)
            return (TexCoord){
                (vertex.z + 1.0f) * 0.5f,          // Map Z to U
                (vertex.y + 1.0f) * 0.5f           // Map Y to V
            };
        }
    } else if (abs_y > epsilon) {
        // Top/Bottom face (Y-dominant)
        if (vertex.y > 0) {
            // Top face (+Y)
            return (TexCoord){
                (vertex.x + 1.0f) * 0.5f,          // Map X to U
                (1.0f - vertex.z) * 0.5f + 0.5f   // Map Z to V (flipped)
            };
        } else {
            // Bottom face (-Y)
            return (TexCoord){
                (vertex.x + 1.0f) * 0.5f,          // Map X to U
                (vertex.z + 1.0f) * 0.5f           // Map Z to V
            };
        }
    } else {
        // Front/Back face (Z-dominant)
        if (vertex.z > 0) {
            // Front face (+Z)
            return (TexCoord){
                (vertex.x + 1.0f) * 0.5f,          // Map X to U
                (1.0f - vertex.y) * 0.5f + 0.5f   // Map Y to V (flipped for screen space)
            };
        } else {
            // Back face (-Z)
            return (TexCoord){
                (1.0f - vertex.x) * 0.5f + 0.5f,  // Map X to U (flipped)
                (1.0f - vertex.y) * 0.5f + 0.5f   // Map Y to V (flipped)
            };
        }
    }
}

void render_solid_with_lighting(Model* model, Camera* camera, Vec3 object_position, 
                               Vec3 object_rotation, Framebuffer* fb, Light* light) {
    if (!model || !camera || !fb || !light) return;
    
    // Create transformation matrices
    Mat4 translation = mat4_translation(object_position.x, object_position.y, object_position.z);
    Mat4 rot_x = mat4_rotation_x(object_rotation.x);
    Mat4 rot_y = mat4_rotation_y(object_rotation.y);
    Mat4 rot_z = mat4_rotation_z(object_rotation.z);
    Mat4 rotation = mat4_multiply(mat4_multiply(rot_z, rot_y), rot_x);
    Mat4 model_matrix = mat4_multiply(translation, rotation);
    Mat4 view = mat4_translation(-camera->position.x, -camera->position.y, -camera->position.z);
    float aspect = (float)camera->screen_width / camera->screen_height;
    Mat4 projection = mat4_perspective(camera->fov, aspect, camera->near_plane, camera->far_plane);
    Mat4 mvp = mat4_multiply(mat4_multiply(projection, view), model_matrix);

    // Project all vertices
    Vec3* projected_vertices = malloc(model->vertex_count * sizeof(Vec3));
    if (!projected_vertices) return;
    
    for (int i = 0; i < model->vertex_count; i++) {
        projected_vertices[i] = mat4_transform_vec3(mvp, model->vertices[i]);
    }

    // Allocate triangle array
    Triangle* triangles = malloc(model->face_count * sizeof(Triangle));
    if (!triangles) {
        free(projected_vertices);
        return;
    }
    
    int triangle_count = 0;

    // Process faces
    for (int i = 0; i < model->face_count; i++) {
        Face face = model->faces[i];
        
        // Validate vertex indices
        if (face.v1 >= 0 && face.v1 < model->vertex_count &&
            face.v2 >= 0 && face.v2 < model->vertex_count &&
            face.v3 >= 0 && face.v3 < model->vertex_count) {
            
            Vec3 p1 = world_to_screen(projected_vertices[face.v1], camera);
            Vec3 p2 = world_to_screen(projected_vertices[face.v2], camera);
            Vec3 p3 = world_to_screen(projected_vertices[face.v3], camera);

            // Backface culling - compute normal in screen space
            Vec3 edge1 = vec3_sub(p2, p1);
            Vec3 edge2 = vec3_sub(p3, p1);
            Vec3 screen_normal = vec3_cross(edge1, edge2);
            
            if (screen_normal.z > 0) { // Front-facing triangle
                // Get texture coordinates properly
                TexCoord tc1 = get_texture_coord(model, &face, 0);
                TexCoord tc2 = get_texture_coord(model, &face, 1);
                TexCoord tc3 = get_texture_coord(model, &face, 2);
                
                // Validate texture coordinates
                if (!isfinite(tc1.u) || !isfinite(tc1.v)) tc1 = (TexCoord){0.0f, 0.0f};
                if (!isfinite(tc2.u) || !isfinite(tc2.v)) tc2 = (TexCoord){1.0f, 0.0f};
                if (!isfinite(tc3.u) || !isfinite(tc3.v)) tc3 = (TexCoord){0.5f, 1.0f};
                
                triangles[triangle_count].v1 = p1;
                triangles[triangle_count].v2 = p2;
                triangles[triangle_count].v3 = p3;
                triangles[triangle_count].t1 = tc1;
                triangles[triangle_count].t2 = tc2;
                triangles[triangle_count].t3 = tc3;
                
                // Use face color if available
                if (model->face_colors && i < model->face_count) {
                    triangles[triangle_count].color = model->face_colors[i];
                } else {
                    triangles[triangle_count].color = (Vec3){1.0f, 1.0f, 1.0f}; // Default white
                }
                
                float avg_z = (p1.z + p2.z + p3.z) / 3.0f;
                triangles[triangle_count].avg_z = isfinite(avg_z) ? avg_z : 0.0f;
                triangle_count++;
            }
        }
    }

    // Sort triangles front-to-back for better performance
    qsort(triangles, triangle_count, sizeof(Triangle), compare_triangles);

    // Render triangles
    for (int i = 0; i < triangle_count; i++) {
        Triangle t = triangles[i];
        fill_triangle_textured(fb, t.v1, t.v2, t.v3, t.t1, t.t2, t.t3, model, light);
    }

    free(projected_vertices);
    free(triangles);
}