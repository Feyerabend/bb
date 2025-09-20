#include <stdio.h>
#include <ctype.h>    // For toupper
#include <string.h>   // For memmove, strlen
#include <stdlib.h>
#include "pico/stdlib.h"
#include "display.h"

// Editor configurations
#define BUFFER_CAPACITY 4096  // Initial buffer size, can be resized if needed
#define FONT_WIDTH 6          // 5 pixels char + 1 spacing
#define FONT_HEIGHT 8
#define SCREEN_CHARS_WIDTH (DISPLAY_WIDTH / FONT_WIDTH)   // ~53 chars
#define SCREEN_LINES (DISPLAY_HEIGHT / FONT_HEIGHT)       // 30 lines
#define CURSOR_BLINK_MS 500   // Cursor blink interval

// Gap buffer structure
typedef struct {
    char* buffer;     // Dynamically allocated buffer
    size_t capacity;  // Total allocated size
    size_t gap_start; // Start of the gap (cursor position)
    size_t gap_end;   // End of the gap
    size_t text_size; // Total text length (excluding gap)
} GapBuffer;

// Editor state
typedef struct {
    GapBuffer gb;
    size_t cursor_x;       // Cursor column in current line (virtual)
    size_t cursor_y;       // Cursor row in view
    size_t view_top;       // Top line of the view (for scrolling)
    bool cursor_visible;   // For blinking
    uint32_t last_blink;   // Last blink time
    bool needs_redraw;     // Flag to trigger full redraw
} Editor;

// Function prototypes
display_error_t init_editor(Editor* editor);
void cleanup_editor(Editor* editor);
void insert_char(Editor* editor, char c);
void delete_char(Editor* editor);
void move_cursor_left(Editor* editor);
void move_cursor_right(Editor* editor);
void move_cursor_up(Editor* editor);
void move_cursor_down(Editor* editor);
void handle_enter(Editor* editor);
void render_screen(Editor* editor);
size_t get_line_start(const Editor* editor, size_t line);
size_t get_line_length(const Editor* editor, size_t line_start);
void get_cursor_pos(Editor* editor, size_t* abs_pos, size_t* line, size_t* col);
void set_cursor_from_pos(Editor* editor, size_t abs_pos);

// Gap buffer functions
static void gb_init(GapBuffer* gb, size_t capacity) {
    gb->buffer = malloc(capacity);
    gb->capacity = capacity;
    gb->gap_start = 0;
    gb->gap_end = capacity;
    gb->text_size = 0;
}

static void gb_cleanup(GapBuffer* gb) {
    free(gb->buffer);
    gb->buffer = NULL;
    gb->capacity = 0;
    gb->gap_start = 0;
    gb->gap_end = 0;
    gb->text_size = 0;
}

static size_t gb_gap_size(const GapBuffer* gb) {
    return gb->gap_end - gb->gap_start;
}

static void gb_move_gap(GapBuffer* gb, size_t new_pos) {
    if (new_pos == gb->gap_start) return;

    if (new_pos < gb->gap_start) {
        // Move gap left: move text from new_pos to gap_start to after gap
        size_t move_size = gb->gap_start - new_pos;
        memmove(gb->buffer + gb->gap_end, gb->buffer + new_pos, move_size);
        gb->gap_start = new_pos;
        gb->gap_end = gb->gap_start + gb_gap_size(gb);
    } else {
        // Move gap right: move text from gap_end to new_pos to before gap
        size_t move_size = new_pos - gb->gap_start;
        memmove(gb->buffer + new_pos - move_size, gb->buffer + gb->gap_end, move_size);
        gb->gap_end += move_size;
        gb->gap_start = new_pos;
    }
}

static void gb_insert(GapBuffer* gb, char c) {
    if (gb_gap_size(gb) == 0) {
        // Resize buffer (double capacity)
        size_t new_capacity = gb->capacity * 2;
        char* new_buffer = realloc(gb->buffer, new_capacity);
        if (!new_buffer) return; // Out of memory, ignore insert
        // Adjust gap_end after realloc
        gb->gap_end += (new_buffer - gb->buffer);
        gb->buffer = new_buffer;
        gb->capacity = new_capacity;
    }
    gb->buffer[gb->gap_start++] = c;
    gb->text_size++;
}

static void gb_delete(GapBuffer* gb) {
    if (gb->gap_start > 0) {
        gb->gap_start--;
        gb->text_size--;
    }
}

static char gb_get(const GapBuffer* gb, size_t pos) {
    if (pos < gb->gap_start) {
        return gb->buffer[pos];
    } else {
        return gb->buffer[pos + (gb->gap_end - gb->gap_start)];
    }
}

static size_t gb_length(const GapBuffer* gb) {
    return gb->text_size;
}

// Editor initialization
display_error_t init_editor(Editor* editor) {
    memset(editor, 0, sizeof(Editor));
    gb_init(&editor->gb, BUFFER_CAPACITY);
    editor->cursor_visible = true;
    editor->last_blink = get_time_ms();
    editor->needs_redraw = true;
    return DISPLAY_OK;
}

// Cleanup
void cleanup_editor(Editor* editor) {
    gb_cleanup(&editor->gb);
}

// Insert character (handle lowercase to uppercase for display, but store as is)
void insert_char(Editor* editor, char c) {
    gb_insert(&editor->gb, c);
    editor->cursor_x++;
    if (editor->cursor_x >= SCREEN_CHARS_WIDTH) {
        editor->cursor_x = 0;
        editor->cursor_y++;
        if (editor->cursor_y >= SCREEN_LINES) {
            editor->view_top++;
            editor->cursor_y = SCREEN_LINES - 1;
        }
    }
    editor->needs_redraw = true;
}

// Delete character (backspace)
void delete_char(Editor* editor) {
    if (editor->gb.gap_start > 0) {
        gb_delete(&editor->gb);
        if (editor->cursor_x > 0) {
            editor->cursor_x--;
        } else if (editor->cursor_y > 0) {
            editor->cursor_y--;
            // Find end of previous line
            size_t prev_line_start = get_line_start(editor, editor->view_top + editor->cursor_y);
            editor->cursor_x = get_line_length(editor, prev_line_start);
        } else if (editor->view_top > 0) {
            editor->view_top--;
        }
        editor->needs_redraw = true;
    }
}

// Move cursor left
void move_cursor_left(Editor* editor) {
    size_t abs_pos, line, col;
    get_cursor_pos(editor, &abs_pos, &line, &col);
    if (col > 0) {
        gb_move_gap(&editor->gb, abs_pos - 1);
        editor->cursor_x--;
    } else if (line > 0) {
        size_t prev_line = line - 1;
        size_t prev_start = get_line_start(editor, prev_line);
        size_t prev_len = get_line_length(editor, prev_start);
        gb_move_gap(&editor->gb, prev_start + prev_len);
        editor->cursor_y--;
        editor->cursor_x = prev_len;
        if (editor->cursor_y < 0 && editor->view_top > 0) {
            editor->view_top--;
            editor->cursor_y = 0;
        }
    }
    editor->needs_redraw = true;
}

// Move cursor right
void move_cursor_right(Editor* editor) {
    size_t abs_pos, line, col;
    get_cursor_pos(editor, &abs_pos, &line, &col);
    if (abs_pos < gb_length(&editor->gb)) {
        gb_move_gap(&editor->gb, abs_pos + 1);
        editor->cursor_x++;
        if (editor->cursor_x >= SCREEN_CHARS_WIDTH) {
            editor->cursor_x = 0;
            editor->cursor_y++;
            if (editor->cursor_y >= SCREEN_LINES) {
                editor->view_top++;
                editor->cursor_y = SCREEN_LINES - 1;
            }
        }
    }
    editor->needs_redraw = true;
}

// Move cursor up
void move_cursor_up(Editor* editor) {
    if (editor->cursor_y > 0) {
        editor->cursor_y--;
    } else if (editor->view_top > 0) {
        editor->view_top--;
    } else {
        return; // Top of file
    }
    // Adjust cursor x to fit line length
    size_t line_start = get_line_start(editor, editor->view_top + editor->cursor_y);
    size_t line_len = get_line_length(editor, line_start);
    if (editor->cursor_x > line_len) {
        editor->cursor_x = line_len;
    }
    set_cursor_from_pos(editor, line_start + editor->cursor_x);
    editor->needs_redraw = true;
}

// Move cursor down
void move_cursor_down(Editor* editor) {
    // Check if there's a next line
    size_t next_line = editor->view_top + editor->cursor_y + 1;
    size_t next_start = get_line_start(editor, next_line);
    if (next_start < gb_length(&editor->gb)) {
        editor->cursor_y++;
        if (editor->cursor_y >= SCREEN_LINES) {
            editor->view_top++;
            editor->cursor_y = SCREEN_LINES - 1;
        }
        // Adjust cursor x
        size_t line_len = get_line_length(editor, next_start);
        if (editor->cursor_x > line_len) {
            editor->cursor_x = line_len;
        }
        set_cursor_from_pos(editor, next_start + editor->cursor_x);
    }
    editor->needs_redraw = true;
}

// Handle enter (new line)
void handle_enter(Editor* editor) {
    insert_char(editor, '\n');
}

// Get start position of a line (0-based)
size_t get_line_start(const Editor* editor, size_t line) {
    size_t pos = 0;
    size_t current_line = 0;
    while (pos < gb_length(&editor->gb) && current_line < line) {
        if (gb_get(&editor->gb, pos) == '\n') {
            current_line++;
        }
        pos++;
    }
    return pos;
}

// Get length of a line starting at pos (excluding \n)
size_t get_line_length(const Editor* editor, size_t line_start) {
    size_t len = 0;
    size_t pos = line_start;
    while (pos < gb_length(&editor->gb)) {
        char c = gb_get(&editor->gb, pos);
        if (c == '\n') break;
        len++;
        pos++;
    }
    return len;
}

// Get absolute position, line, col from cursor
void get_cursor_pos(Editor* editor, size_t* abs_pos, size_t* line, size_t* col) {
    *line = editor->view_top + editor->cursor_y;
    size_t line_start = get_line_start(editor, *line);
    *col = editor->cursor_x;
    *abs_pos = line_start + *col;
}

// Set gap and cursor from absolute pos
void set_cursor_from_pos(Editor* editor, size_t abs_pos) {
    gb_move_gap(&editor->gb, abs_pos);
}

// Render the screen
void render_screen(Editor* editor) {
    display_clear(COLOR_BLACK);

    for (size_t screen_line = 0; screen_line < SCREEN_LINES; screen_line++) {
        size_t file_line = editor->view_top + screen_line;
        size_t line_start = get_line_start(editor, file_line);
        size_t line_len = get_line_length(editor, line_start);

        char line_buf[SCREEN_CHARS_WIDTH + 1];
        size_t draw_len = line_len > SCREEN_CHARS_WIDTH ? SCREEN_CHARS_WIDTH : line_len;
        for (size_t i = 0; i < draw_len; i++) {
            char c = gb_get(&editor->gb, line_start + i);
            line_buf[i] = isprint(c) ? toupper(c) : ' ';  // Translate to upper for display
        }
        line_buf[draw_len] = '\0';

        display_draw_string(0, screen_line * FONT_HEIGHT, line_buf, COLOR_WHITE, COLOR_BLACK);
    }

    // Draw cursor if visible
    if (editor->cursor_visible) {
        uint16_t cur_x = editor->cursor_x * FONT_WIDTH;
        uint16_t cur_y = editor->cursor_y * FONT_HEIGHT;
        display_fill_rect(cur_x, cur_y, FONT_WIDTH, FONT_HEIGHT, COLOR_WHITE);  // Invert as cursor
    }

    editor->needs_redraw = false;
}

// Handle input (parse ANSI for arrows)
static void handle_input(Editor* editor) {
    int c = getchar_timeout_us(0);
    if (c == PICO_ERROR_GENERIC) return;

    if (c == 0x1B) {  // Escape
        int next1 = getchar_timeout_us(10000);  // Timeout for sequence
        if (next1 == '[') {
            int next2 = getchar_timeout_us(10000);
            switch (next2) {
                case 'A': move_cursor_up(editor); break;    // Up
                case 'B': move_cursor_down(editor); break;  // Down
                case 'C': move_cursor_right(editor); break; // Right
                case 'D': move_cursor_left(editor); break;  // Left
            }
        }
    } else if (c == 0x7F || c == 0x08) {  // Backspace/Delete
        delete_char(editor);
    } else if (c == '\r' || c == '\n') {  // Enter
        handle_enter(editor);
    } else if (isprint(c)) {
        insert_char(editor, c);
    }
}

// Main function
int main() {
    stdio_init_all();  // Enable USB CDC for input/output

    if (display_pack_init() != DISPLAY_OK) {
        printf("Display init failed\n");
        return 1;
    }

    if (buttons_init() != DISPLAY_OK) {
        printf("Buttons init failed\n");
        return 1;
    }

    // Note: Buttons are initialized but not used for editor controls in this version
    // You could add callbacks for e.g., save/exit if needed

    Editor editor;
    if (init_editor(&editor) != DISPLAY_OK) {
        printf("Editor init failed\n");
        return 1;
    }

    printf("Full Screen Editor Started. Use keyboard via USB serial.\n");
    printf("Arrow keys for navigation, backspace to delete, enter for new line.\n");

    while (true) {
        buttons_update();  // Keep button handling if needed

        handle_input(&editor);

        uint32_t now = get_time_ms();
        if (now - editor.last_blink > CURSOR_BLINK_MS) {
            editor.cursor_visible = !editor.cursor_visible;
            editor.last_blink = now;
            editor.needs_redraw = true;
        }

        if (editor.needs_redraw) {
            render_screen(&editor);
        }

        if (display_dma_busy()) {
            display_wait_for_dma();
        }

        sleep_ms(10);
    }

    cleanup_editor(&editor);
    display_cleanup();
    return 0;
}
