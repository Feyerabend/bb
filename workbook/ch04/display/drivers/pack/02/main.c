#include <stdio.h>
#include "pico/stdlib.h"
#include "engine.h"
#include "display.h"

// Simple demo: Create a moving sprite and some particles
// WORKING?

int main() {
    // Initstdio for debugging (optional)
    stdio_init_all();
    printf("Starting graphics demo..\n");

    // Init engine
    engine_error_t init_result = engine_init();
    if (init_result != ENGINE_OK) {
        printf("Engine init failed: %s\n", engine_error_string(init_result));
        while (true) tight_loop_contents();
    }

    // Init buttons
    display_error_t button_result = buttons_init();
    if (button_result != DISPLAY_OK) {
        printf("Buttons init failed: %s\n", display_error_string(button_result));
    }

    // Create a solid color texture for the sprite (red square)
    texture_handle_t tex = texture_create_solid(ENGINE_COLOR_RED, 20, 20);
    if (tex == INVALID_HANDLE) {
        printf("Failed to create texture\n");
        engine_shutdown();
        while (true) tight_loop_contents();
    }

    // Create a sprite
    sprite_handle_t sprite = sprite_create(100.0f, 50.0f, tex);
    if (sprite == INVALID_HANDLE) {
        printf("Failed to create sprite\n");
        texture_destroy(tex);
        engine_shutdown();
        while (true) tight_loop_contents();
    }

    // Set sprite properties
    sprite_set_velocity(sprite, 1.0f, 0.5f);  // Move right and down
    sprite_set_visibility(sprite, true);
    sprite_set_layer(sprite, 1);

    // Create a particle system (blue particles at center)
    particle_system_handle_t particles = particles_create(120.0f, 67.0f, ENGINE_COLOR_BLUE);
    if (particles != INVALID_HANDLE) {
        particles_set_spawn_rate(particles, 100);  // Spawn every 100ms
        particles_set_lifetime(particles, 1000);   // 1 second lifetime
        particles_set_spawn_radius(particles, 5.0f);
        particles_emit_burst(particles, 5);        // Initial burst
    }

    // Main loop
    while (true) {
        // Update buttons
        buttons_update();

        // Simple movement logic: bounce sprite on screen edges
        float sx, sy;
        sprite_get_position(sprite, &sx, &sy);
        if (sx >= DISPLAY_WIDTH - 20 || sx <= 0) {
            float vx, vy;
            sprite_get_position(sprite, NULL, NULL);  // Actually get velocity
            sprite_set_velocity(sprite, -vx, vy);     // Reverse X
        }
        if (sy >= DISPLAY_HEIGHT - 20 || sy <= 0) {
            float vx, vy;
            sprite_get_position(sprite, NULL, NULL);  // Actually get velocity
            sprite_set_velocity(sprite, vx, -vy);     // Reverse Y
        }

        // Exit if button A is pressed (optional)
        if (button_pressed(BUTTON_A)) {
            break;
        }

        // Update and render
        engine_update();
        engine_render();
        engine_present();

        // Small delay for frame rate control (approx 60 FPS)
        sleep_ms(16);
    }

    // Cleanup
    particles_destroy(particles);
    sprite_destroy(sprite);
    texture_destroy(tex);
    engine_shutdown();
    display_cleanup();

    printf("Demo ended\n");
    return 0;
}
