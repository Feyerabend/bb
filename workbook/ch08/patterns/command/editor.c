/**
 * Command Pattern Implementation - Line Editor
 * This example as editor is quite underwhelming, but that is not the point.
 * This example demonstrates the Command pattern with a simple line editor.
 * The Command pattern encapsulates actions as objects, allowing for:
 * - Parameterization of clients with different requests
 * - Queuing of commands (implemented as a command queue)
 * - Logging of commands (implemented with file logging)
 * - Undo/redo operations
 */

 #include <stdio.h>
 #include <stdlib.h>
 #include <string.h>
 #include <time.h>  // For logging timestamps
 
 #define MAX_LINE_LENGTH 100
 #define MAX_LINES 100
 #define MAX_COMMAND_HISTORY 20
 #define MAX_QUEUED_COMMANDS 50
 
 // Document structure - represents our text buffer
 typedef struct {
     char lines[MAX_LINES][MAX_LINE_LENGTH];
     int lineCount;
 } Document;
 
 // Forward declaration of Command
 typedef struct Command Command;
 
 // Command interface
 struct Command {
     void (*execute)(Command* self);
     void (*undo)(Command* self);
     void (*log)(Command* self, const char* action);  // New function for logging
     void* data;  // For command-specific data
 };
 
 // Command Manager to handle undo/redo
 typedef struct {
     Command* history[MAX_COMMAND_HISTORY];
     int historyCount;
     int currentPos;
 } CommandManager;
 
 // Command Queue for deferred execution
 typedef struct {
     Command* queue[MAX_QUEUED_COMMANDS];
     int queueCount;
 } CommandQueue;
 
 // Global instances
 Document doc;
 CommandManager cmdManager;
 CommandQueue cmdQueue;
 
 // Initialize document
 void initDocument() {
     doc.lineCount = 0;
     for (int i = 0; i < MAX_LINES; i++) {
         doc.lines[i][0] = '\0';
     }
 }
 
 // Initialize command manager
 void initCommandManager() {
     cmdManager.historyCount = 0;
     cmdManager.currentPos = 0;
 }
 
 // Initialize command queue
 void initCommandQueue() {
     cmdQueue.queueCount = 0;
 }
 
 // Logging function
 void logToFile(const char* commandType, const char* details) {
     FILE* logFile = fopen("editor_log.txt", "a");
     if (logFile != NULL) {
         time_t now = time(NULL);
         char timeStr[26];
         ctime_r(&now, timeStr);
         timeStr[strcspn(timeStr, "\n")] = '\0';  // Remove trailing newline
         
         fprintf(logFile, "[%s] %s: %s\n", timeStr, commandType, details);
         fclose(logFile);
     }
 }
 
 // Add a command to history
 void addToHistory(Command* cmd) {
     // If we're in the middle of the history, remove everything after current position
     if (cmdManager.currentPos < cmdManager.historyCount) {
         for (int i = cmdManager.currentPos; i < cmdManager.historyCount; i++) {
             free(cmdManager.history[i]->data);
             free(cmdManager.history[i]);
         }
         cmdManager.historyCount = cmdManager.currentPos;
     }
     
     // Check if history is full
     if (cmdManager.historyCount >= MAX_COMMAND_HISTORY) {
         // Shift history to make room
         free(cmdManager.history[0]->data);
         free(cmdManager.history[0]);
         for (int i = 0; i < cmdManager.historyCount - 1; i++) {
             cmdManager.history[i] = cmdManager.history[i + 1];
         }
         cmdManager.historyCount--;
     }
     
     // Add new command
     cmdManager.history[cmdManager.historyCount++] = cmd;
     cmdManager.currentPos = cmdManager.historyCount;
 }
 
 // Display document content
 void displayDocument() {
     printf("\n--- Document Content ---\n");
     for (int i = 0; i < doc.lineCount; i++) {
         printf("%d: %s\n", i + 1, doc.lines[i]);
     }
     printf("----------------------\n");
 }
 
 // InsertLine Command
 typedef struct {
     int lineNum;
     char text[MAX_LINE_LENGTH];
 } InsertLineData;
 
 void executeInsertLine(Command* self) {
     InsertLineData* data = (InsertLineData*)self->data;
     
     // Ensure valid line position
     if (data->lineNum < 0 || data->lineNum > doc.lineCount) {
         printf("Invalid line position for insertion\n");
         return;
     }
     
     // Shift lines down to make room
     for (int i = doc.lineCount; i > data->lineNum; i--) {
         strcpy(doc.lines[i], doc.lines[i - 1]);
     }
     
     // Insert the new line
     strcpy(doc.lines[data->lineNum], data->text);
     doc.lineCount++;
     
     // Log the action
     self->log(self, "EXECUTE");
     
     printf("Line inserted at position %d\n", data->lineNum + 1);
 }
 
 void undoInsertLine(Command* self) {
     InsertLineData* data = (InsertLineData*)self->data;
     
     // Shift lines up to remove the inserted line
     for (int i = data->lineNum; i < doc.lineCount - 1; i++) {
         strcpy(doc.lines[i], doc.lines[i + 1]);
     }
     
     doc.lineCount--;
     
     // Log the action
     self->log(self, "UNDO");
     
     printf("Insertion at line %d undone\n", data->lineNum + 1);
 }
 
 void logInsertLine(Command* self, const char* action) {
     InsertLineData* data = (InsertLineData*)self->data;
     char details[MAX_LINE_LENGTH + 50];
     
     if (strcmp(action, "EXECUTE") == 0) {
         sprintf(details, "Line inserted at position %d: \"%s\"", data->lineNum + 1, data->text);
     } else if (strcmp(action, "UNDO") == 0) {
         sprintf(details, "Undid insertion at line %d", data->lineNum + 1);
     }
     
     logToFile("INSERT", details);
 }
 
 Command* createInsertLineCommand(int lineNum, const char* text) {
     Command* cmd = (Command*)malloc(sizeof(Command));
     InsertLineData* data = (InsertLineData*)malloc(sizeof(InsertLineData));
 
     data->lineNum = lineNum;
     strncpy(data->text, text, MAX_LINE_LENGTH - 1);
     data->text[MAX_LINE_LENGTH - 1] = '\0';
 
     cmd->execute = executeInsertLine;
     cmd->undo = undoInsertLine;
     cmd->log = logInsertLine;
     cmd->data = data;
 
     return cmd;
 }
 
 // DeleteLine Command
 typedef struct {
     int lineNum;
     char deletedText[MAX_LINE_LENGTH];
 } DeleteLineData;
 
 void executeDeleteLine(Command* self) {
     DeleteLineData* data = (DeleteLineData*)self->data;
     
     // Ensure valid line position
     if (data->lineNum < 0 || data->lineNum >= doc.lineCount) {
         printf("Invalid line position for deletion\n");
         return;
     }
     
     // Save deleted line for undo
     strcpy(data->deletedText, doc.lines[data->lineNum]);
     
     // Shift lines up to remove the line
     for (int i = data->lineNum; i < doc.lineCount - 1; i++) {
         strcpy(doc.lines[i], doc.lines[i + 1]);
     }
     
     doc.lineCount--;
     
     // Log the action
     self->log(self, "EXECUTE");
     
     printf("Line %d deleted\n", data->lineNum + 1);
 }
 
 void undoDeleteLine(Command* self) {
     DeleteLineData* data = (DeleteLineData*)self->data;
     
     // Shift lines down to make room
     for (int i = doc.lineCount; i > data->lineNum; i--) {
         strcpy(doc.lines[i], doc.lines[i - 1]);
     }
     
     // Restore the deleted line
     strcpy(doc.lines[data->lineNum], data->deletedText);
     doc.lineCount++;
     
     // Log the action
     self->log(self, "UNDO");
     
     printf("Deletion of line %d undone\n", data->lineNum + 1);
 }
 
 void logDeleteLine(Command* self, const char* action) {
     DeleteLineData* data = (DeleteLineData*)self->data;
     char details[MAX_LINE_LENGTH + 50];
     
     if (strcmp(action, "EXECUTE") == 0) {
         sprintf(details, "Line %d deleted: \"%s\"", data->lineNum + 1, data->deletedText);
     } else if (strcmp(action, "UNDO") == 0) {
         sprintf(details, "Restored deleted line %d: \"%s\"", data->lineNum + 1, data->deletedText);
     }
     
     logToFile("DELETE", details);
 }
 
 Command* createDeleteLineCommand(int lineNum) {
     Command* cmd = (Command*)malloc(sizeof(Command));
     DeleteLineData* data = (DeleteLineData*)malloc(sizeof(DeleteLineData));
 
     data->lineNum = lineNum;
     data->deletedText[0] = '\0';  // Will be filled during execution
 
     cmd->execute = executeDeleteLine;
     cmd->undo = undoDeleteLine;
     cmd->log = logDeleteLine;
     cmd->data = data;
 
     return cmd;
 }
 
 // EditLine Command
 typedef struct {
     int lineNum;
     char oldText[MAX_LINE_LENGTH];
     char newText[MAX_LINE_LENGTH];
 } EditLineData;
 
 void executeEditLine(Command* self) {
     EditLineData* data = (EditLineData*)self->data;
     
     // Ensure valid line position
     if (data->lineNum < 0 || data->lineNum >= doc.lineCount) {
         printf("Invalid line position for editing\n");
         return;
     }
     
     // Save old line for undo
     strcpy(data->oldText, doc.lines[data->lineNum]);
     
     // Replace with new text
     strcpy(doc.lines[data->lineNum], data->newText);
     
     // Log the action
     self->log(self, "EXECUTE");
     
     printf("Line %d edited\n", data->lineNum + 1);
 }
 
 void undoEditLine(Command* self) {
     EditLineData* data = (EditLineData*)self->data;
     
     // Restore old text
     strcpy(doc.lines[data->lineNum], data->oldText);
     
     // Log the action
     self->log(self, "UNDO");
     
     printf("Edit of line %d undone\n", data->lineNum + 1);
 }
 
 void logEditLine(Command* self, const char* action) {
     EditLineData* data = (EditLineData*)self->data;
     char details[MAX_LINE_LENGTH * 2 + 50];
     
     if (strcmp(action, "EXECUTE") == 0) {
         sprintf(details, "Line %d changed from \"%s\" to \"%s\"", 
                 data->lineNum + 1, data->oldText, data->newText);
     } else if (strcmp(action, "UNDO") == 0) {
         sprintf(details, "Reverted line %d from \"%s\" to \"%s\"", 
                 data->lineNum + 1, data->newText, data->oldText);
     }
     
     logToFile("EDIT", details);
 }
 
 Command* createEditLineCommand(int lineNum, const char* newText) {
     Command* cmd = (Command*)malloc(sizeof(Command));
     EditLineData* data = (EditLineData*)malloc(sizeof(EditLineData));
 
     data->lineNum = lineNum;
     data->oldText[0] = '\0';  // Will be filled during execution
     strncpy(data->newText, newText, MAX_LINE_LENGTH - 1);
     data->newText[MAX_LINE_LENGTH - 1] = '\0';
 
     cmd->execute = executeEditLine;
     cmd->undo = undoEditLine;
     cmd->log = logEditLine;
     cmd->data = data;
 
     return cmd;
 }
 
 // Perform undo operation
 void undo() {
     if (cmdManager.currentPos <= 0) {
         printf("Nothing to undo\n");
         return;
     }
     
     Command* cmd = cmdManager.history[--cmdManager.currentPos];
     cmd->undo(cmd);
     
     logToFile("SYSTEM", "Undo operation performed");
 }
 
 // Perform redo operation
 void redo() {
     if (cmdManager.currentPos >= cmdManager.historyCount) {
         printf("Nothing to redo\n");
         return;
     }
     
     Command* cmd = cmdManager.history[cmdManager.currentPos++];
     cmd->execute(cmd);
     
     logToFile("SYSTEM", "Redo operation performed");
 }
 
 // Helper function to execute a command and add it to history
 void executeCommand(Command* cmd) {
     cmd->execute(cmd);
     addToHistory(cmd);
 }
 
 // Command Queue operations
 void enqueueCommand(Command* cmd) {
     if (cmdQueue.queueCount < MAX_QUEUED_COMMANDS) {
         cmdQueue.queue[cmdQueue.queueCount++] = cmd;
         logToFile("QUEUE", "Command added to queue");
         printf("Command added to queue. Queue size: %d\n", cmdQueue.queueCount);
     } else {
         printf("Command queue is full\n");
     }
 }
 
 void executeNextQueuedCommand() {
     if (cmdQueue.queueCount <= 0) {
         printf("Command queue is empty\n");
         return;
     }
     
     Command* cmd = cmdQueue.queue[0];
     
     // Shift queue
     for (int i = 0; i < cmdQueue.queueCount - 1; i++) {
         cmdQueue.queue[i] = cmdQueue.queue[i + 1];
     }
     cmdQueue.queueCount--;
     
     // Execute and add to history
     logToFile("QUEUE", "Executing command from queue");
     executeCommand(cmd);
     printf("Executed command from queue. Remaining: %d\n", cmdQueue.queueCount);
 }
 
 void executeAllQueuedCommands() {
     if (cmdQueue.queueCount <= 0) {
         printf("Command queue is empty\n");
         return;
     }
     
     logToFile("QUEUE", "Executing all queued commands");
     printf("Executing %d command(s) from queue\n", cmdQueue.queueCount);
     
     while (cmdQueue.queueCount > 0) {
         executeNextQueuedCommand();
     }
     
     printf("All queued commands executed\n");
 }
 
 // Main function
 int main() {
     char input[MAX_LINE_LENGTH];
     char text[MAX_LINE_LENGTH];
     int lineNum;
     
     // Initialize
     initDocument();
     initCommandManager();
     initCommandQueue();
     
     // Create a new log file or clear existing one
     FILE* logFile = fopen("editor_log.txt", "w");
     if (logFile != NULL) {
         fprintf(logFile, "--- Line Editor Session Log ---\n");
         fclose(logFile);
     }
     
     printf("Simple Line Editor (Command Pattern Implementation)\n");
     printf("Commands: insert, delete, edit, undo, redo, display, queue, next, run-all, exit\n");
     
     while (1) {
         printf("\n> ");
         scanf("%s", input);
         
         if (strcmp(input, "exit") == 0) {
             break;
         } else if (strcmp(input, "display") == 0) {
             displayDocument();
         } else if (strcmp(input, "insert") == 0) {
             printf("Line number: ");
             scanf("%d", &lineNum);
             printf("Text: ");
             getchar();  // Consume newline
             fgets(text, MAX_LINE_LENGTH, stdin);
             text[strcspn(text, "\n")] = '\0';  // Remove trailing newline
             
             Command* cmd = createInsertLineCommand(lineNum - 1, text);
             executeCommand(cmd);
         } else if (strcmp(input, "delete") == 0) {
             printf("Line number: ");
             scanf("%d", &lineNum);
             
             Command* cmd = createDeleteLineCommand(lineNum - 1);
             executeCommand(cmd);
         } else if (strcmp(input, "edit") == 0) {
             printf("Line number: ");
             scanf("%d", &lineNum);
             printf("New text: ");
             getchar();  // Consume newline
             fgets(text, MAX_LINE_LENGTH, stdin);
             text[strcspn(text, "\n")] = '\0';  // Remove trailing newline
             
             Command* cmd = createEditLineCommand(lineNum - 1, text);
             executeCommand(cmd);
         } else if (strcmp(input, "queue") == 0) {
             // Queue a command for later execution
             printf("Command to queue (insert/delete/edit): ");
             char cmdType[20];
             scanf("%s", cmdType);
             
             Command* cmd = NULL;
             
             if (strcmp(cmdType, "insert") == 0) {
                 printf("Line number: ");
                 scanf("%d", &lineNum);
                 printf("Text: ");
                 getchar();  // Consume newline
                 fgets(text, MAX_LINE_LENGTH, stdin);
                 text[strcspn(text, "\n")] = '\0';  // Remove trailing newline
                 
                 cmd = createInsertLineCommand(lineNum - 1, text);
             } else if (strcmp(cmdType, "delete") == 0) {
                 printf("Line number: ");
                 scanf("%d", &lineNum);
                 
                 cmd = createDeleteLineCommand(lineNum - 1);
             } else if (strcmp(cmdType, "edit") == 0) {
                 printf("Line number: ");
                 scanf("%d", &lineNum);
                 printf("New text: ");
                 getchar();  // Consume newline
                 fgets(text, MAX_LINE_LENGTH, stdin);
                 text[strcspn(text, "\n")] = '\0';  // Remove trailing newline
                 
                 cmd = createEditLineCommand(lineNum - 1, text);
             } else {
                 printf("Unknown command type for queueing\n");
                 continue;
             }
             
             if (cmd != NULL) {
                 enqueueCommand(cmd);
             }
         } else if (strcmp(input, "next") == 0) {
             executeNextQueuedCommand();
         } else if (strcmp(input, "run-all") == 0) {
             executeAllQueuedCommands();
         } else if (strcmp(input, "undo") == 0) {
             undo();
         } else if (strcmp(input, "redo") == 0) {
             redo();
         } else {
             printf("Unknown command: %s\n", input);
         }
     }
     
     // Clean up (in a real application, we would free all allocated memory)
     for (int i = 0; i < cmdManager.historyCount; i++) {
         free(cmdManager.history[i]->data);
         free(cmdManager.history[i]);
     }
     
     // Clean up any remaining queued commands
     for (int i = 0; i < cmdQueue.queueCount; i++) {
         free(cmdQueue.queue[i]->data);
         free(cmdQueue.queue[i]);
     }
     
     printf("Editor closed\n");
     return 0;
 }
 