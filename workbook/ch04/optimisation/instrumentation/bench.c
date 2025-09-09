/*
 * SPACE INVADERS BENCHMARKING INSTRUMENTATION
 * 
 * Add these functions to your existing C files, then compile to UF2 and deploy.
 * The Pico will output performance data via USB serial that you can collect.
 * 
 * Usage:
 * 1. Add this code to your inv.c and inv_opt.c files
 * 2. Compile with pico-sdk to generate UF2 files
 * 3. Deploy to Pico and collect serial output
 * 4. Use the Python collector script to analyze results
 */

#include "pico/stdlib.h"
#include <stdio.h>

// ============================================================================
// BENCHMARKING INSTRUMENTATION - ADD TO YOUR C FILES
// ============================================================================

// Benchmark data structure
typedef struct {
    uint32_t frame_start_time;
    uint32_t frame_end_time;
    uint32_t collision_start_time;
    uint32_t collision_end_time;
    uint32_t render_start_time;
    uint32_t render_end_time;
    uint32_t update_start_time;
    uint32_t update_end_time;
    
    // Counters
    uint32_t frame_count;
    uint32_t collision_checks;
    uint32_t objects_rendered;
    
    // Memory tracking (approximate)
    uint32_t active_bullets;
    uint32_t active_bombs; 
    uint32_t alive_invaders;
    
    // Performance stats
    uint32_t frame_time_us;
    uint32_t collision_time_us;
    uint32_t render_time_us;
    uint32_t update_time_us;
    
    // Running averages (simple)
    uint32_t avg_frame_time_us;
    uint32_t avg_collision_time_us;
    uint32_t avg_render_time_us;
    
    // Min/max tracking
    uint32_t min_frame_time_us;
    uint32_t max_frame_time_us;
    
} benchmark_data_t;

static benchmark_data_t bench_data = {0};
static bool benchmarking_enabled = true;
static uint32_t report_interval_frames = 60; // Report every 60 frames (1 second at 60fps)

// Timing macros - add these to your code
#define BENCH_FRAME_START() \
    if (benchmarking_enabled) { \
        bench_data.frame_start_time = time_us_32(); \
        bench_data.collision_checks = 0; \
        bench_data.objects_rendered = 0; \
    }

#define BENCH_FRAME_END() \
    if (benchmarking_enabled) { \
        bench_data.frame_end_time = time_us_32(); \
        bench_update_stats(); \
        if (bench_data.frame_count % report_interval_frames == 0) { \
            bench_report_stats(); \
        } \
    }

#define BENCH_COLLISION_START() \
    if (benchmarking_enabled) { \
        bench_data.collision_start_time = time_us_32(); \
    }

#define BENCH_COLLISION_END() \
    if (benchmarking_enabled) { \
        bench_data.collision_end_time = time_us_32(); \
        bench_data.collision_time_us = bench_data.collision_end_time - bench_data.collision_start_time; \
    }

#define BENCH_RENDER_START() \
    if (benchmarking_enabled) { \
        bench_data.render_start_time = time_us_32(); \
    }

#define BENCH_RENDER_END() \
    if (benchmarking_enabled) { \
        bench_data.render_end_time = time_us_32(); \
        bench_data.render_time_us = bench_data.render_end_time - bench_data.render_start_time; \
    }

#define BENCH_UPDATE_START() \
    if (benchmarking_enabled) { \
        bench_data.update_start_time = time_us_32(); \
    }

#define BENCH_UPDATE_END() \
    if (benchmarking_enabled) { \
        bench_data.update_end_time = time_us_32(); \
        bench_data.update_time_us = bench_data.update_end_time - bench_data.update_start_time; \
    }

#define BENCH_COUNT_COLLISION() \
    if (benchmarking_enabled) { \
        bench_data.collision_checks++; \
    }

#define BENCH_COUNT_RENDER_OBJECT() \
    if (benchmarking_enabled) { \
        bench_data.objects_rendered++; \
    }

// Update benchmark statistics
void bench_update_stats(void) {
    bench_data.frame_count++;
    bench_data.frame_time_us = bench_data.frame_end_time - bench_data.frame_start_time;
    
    // Update running averages (simple moving average)
    if (bench_data.frame_count == 1) {
        bench_data.avg_frame_time_us = bench_data.frame_time_us;
        bench_data.avg_collision_time_us = bench_data.collision_time_us;
        bench_data.avg_render_time_us = bench_data.render_time_us;
        bench_data.min_frame_time_us = bench_data.frame_time_us;
        bench_data.max_frame_time_us = bench_data.frame_time_us;
    } else {
        // Simple exponential moving average (alpha = 0.1)
        bench_data.avg_frame_time_us = (bench_data.avg_frame_time_us * 9 + bench_data.frame_time_us) / 10;
        bench_data.avg_collision_time_us = (bench_data.avg_collision_time_us * 9 + bench_data.collision_time_us) / 10;
        bench_data.avg_render_time_us = (bench_data.avg_render_time_us * 9 + bench_data.render_time_us) / 10;
        
        // Update min/max
        if (bench_data.frame_time_us < bench_data.min_frame_time_us) {
            bench_data.min_frame_time_us = bench_data.frame_time_us;
        }
        if (bench_data.frame_time_us > bench_data.max_frame_time_us) {
            bench_data.max_frame_time_us = bench_data.frame_time_us;
        }
    }
    
    // Count active objects (you'll need to update these based on your game state)
    bench_data.active_bullets = bullet_count;
    bench_data.active_bombs = bomb_count;
    bench_data.alive_invaders = 0;
    for (int i = 0; i < invader_count; i++) {
        if (invaders[i].alive) {
            bench_data.alive_invaders++;
        }
    }
}

// Output benchmark report via USB serial
void bench_report_stats(void) {
    // JSON format for easy parsing
    printf("{\"benchmark\":{");
    printf("\"frame\":%lu,", bench_data.frame_count);
    printf("\"timestamp\":%lu,", time_us_32());
    
    // Timing data (in microseconds)
    printf("\"frame_time_us\":%lu,", bench_data.frame_time_us);
    printf("\"avg_frame_time_us\":%lu,", bench_data.avg_frame_time_us);
    printf("\"min_frame_time_us\":%lu,", bench_data.min_frame_time_us);
    printf("\"max_frame_time_us\":%lu,", bench_data.max_frame_time_us);
    printf("\"collision_time_us\":%lu,", bench_data.collision_time_us);
    printf("\"avg_collision_time_us\":%lu,", bench_data.avg_collision_time_us);
    printf("\"render_time_us\":%lu,", bench_data.render_time_us);
    printf("\"avg_render_time_us\":%lu,", bench_data.avg_render_time_us);
    printf("\"update_time_us\":%lu,", bench_data.update_time_us);
    
    // Performance metrics
    printf("\"fps\":%.1f,", 1000000.0f / bench_data.avg_frame_time_us);
    printf("\"collision_checks\":%lu,", bench_data.collision_checks);
    printf("\"objects_rendered\":%lu,", bench_data.objects_rendered);
    
    // Game state
    printf("\"active_bullets\":%lu,", bench_data.active_bullets);
    printf("\"active_bombs\":%lu,", bench_data.active_bombs);
    printf("\"alive_invaders\":%lu", bench_data.alive_invaders);
    
    printf("}}\n");
}

// ============================================================================
// EXAMPLE: HOW TO INSTRUMENT YOUR EXISTING MAIN LOOP
// ============================================================================

/*
// In your main() function, replace your game loop with this instrumented version:

int main() {
    stdio_init_all();
    
    // Your existing initialization code...
    display.init();
    // ... etc
    
    init_game();
    
    printf("BENCHMARK_START: Space Invaders Performance Test\n");
    
    // Main game loop with instrumentation
    while (true) {
        BENCH_FRAME_START();
        
        if (!game_over && !win) {
            BENCH_UPDATE_START();
            handle_input();
            update_projectiles();
            update_invaders();
            BENCH_UPDATE_END();
            
            BENCH_COLLISION_START();
            optimized_collision_detection(); // or your collision function
            BENCH_COLLISION_END();
        }
        
        BENCH_RENDER_START();
        draw_game_optimized(); // or your draw function
        display.update(&graphics);
        BENCH_RENDER_END();
        
        BENCH_FRAME_END();
        
        sleep_ms(33); // Your target frame time
        
        // Reset game condition
        if ((game_over || win) && !gpio_get(BUTTON_X)) {
            sleep_ms(500);
            init_game();
        }
    }
    
    return 0;
}
*/
