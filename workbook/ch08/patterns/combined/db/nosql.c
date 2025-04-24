
/*
* Design Patterns used:
* - Command: Encapsulates insert/update/delete actions
* - Observer: Allows real-time event notifications
* - Factory/Builder: Creates Command and Document structs
* - Strategy (light): Swap logic using function pointers in Command
*/


#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_COLLECTIONS 10
#define MAX_DOCUMENTS 100
#define MAX_FIELDS 10
#define MAX_FIELD_NAME 50
#define MAX_FIELD_VALUE 50
#define MAX_OBSERVERS 10

typedef struct {
    char field_names[MAX_FIELDS][MAX_FIELD_NAME];
    char field_values[MAX_FIELDS][MAX_FIELD_VALUE];
    int field_count;
} Document;

typedef struct {
    char name[MAX_FIELD_NAME];
    Document documents[MAX_DOCUMENTS];
    int document_count;
} Collection;

typedef struct {
    Collection collections[MAX_COLLECTIONS];
    int collection_count;
} NoSQLDatabase;

typedef enum {
    EVENT_INSERT,
    EVENT_UPDATE,
    EVENT_DELETE
} EventType;

typedef struct {
    EventType type;
    const char* collection_name;
    Document* document;
} Event;

typedef void (*Observer)(Event* event);

typedef struct {
    Observer observers[MAX_OBSERVERS];
    int count;
} ObserverList;

ObserverList observer_list = { .count = 0 };

void register_observer(Observer o) {
    if (observer_list.count < MAX_OBSERVERS) {
        observer_list.observers[observer_list.count++] = o;
    }
}

void notify_observers(Event* event) {
    for (int i = 0; i < observer_list.count; i++) {
        observer_list.observers[i](event);
    }
}



typedef struct Command {
    void (*execute)(struct Command* self, NoSQLDatabase* db);
    char collection_name[MAX_FIELD_NAME];
    Document document;
    Document query;
    Document update;
} Command;

Collection* get_collection(NoSQLDatabase* db, const char* name) {
    for (int i = 0; i < db->collection_count; i++) {
        if (strcmp(db->collections[i].name, name) == 0)
            return &db->collections[i];
    }
    return NULL;
}

int match_document(Document* doc, Document* query) {
    for (int i = 0; i < query->field_count; i++) {
        int found = 0;
        for (int j = 0; j < doc->field_count; j++) {
            if (strcmp(query->field_names[i], doc->field_names[j]) == 0 &&
                strcmp(query->field_values[i], doc->field_values[j]) == 0) {
                found = 1;
                break;
            }
        }
        if (!found) return 0;
    }
    return 1;
}


void insert_execute(Command* self, NoSQLDatabase* db) {
    Collection* col = get_collection(db, self->collection_name);
    if (!col || col->document_count >= MAX_DOCUMENTS) return;
    col->documents[col->document_count++] = self->document;

    Event e = { EVENT_INSERT, self->collection_name, &self->document };
    notify_observers(&e);
}


void update_execute(Command* self, NoSQLDatabase* db) {
    Collection* col = get_collection(db, self->collection_name);
    if (!col) return;

    for (int i = 0; i < col->document_count; i++) {
        if (match_document(&col->documents[i], &self->query)) {
            for (int j = 0; j < self->update.field_count; j++) {
                int updated = 0;
                for (int k = 0; k < col->documents[i].field_count; k++) {
                    if (strcmp(col->documents[i].field_names[k], self->update.field_names[j]) == 0) {
                        strcpy(col->documents[i].field_values[k], self->update.field_values[j]);
                        updated = 1;
                        break;
                    }
                }
                if (!updated && col->documents[i].field_count < MAX_FIELDS) {
                    strcpy(col->documents[i].field_names[col->documents[i].field_count], self->update.field_names[j]);
                    strcpy(col->documents[i].field_values[col->documents[i].field_count], self->update.field_values[j]);
                    col->documents[i].field_count++;
                }
            }
            Event e = { EVENT_UPDATE, self->collection_name, &col->documents[i] };
            notify_observers(&e);
        }
    }
}


void delete_execute(Command* self, NoSQLDatabase* db) {
    Collection* col = get_collection(db, self->collection_name);
    if (!col) return;
    int i = 0;
    while (i < col->document_count) {
        if (match_document(&col->documents[i], &self->query)) {
            Event e = { EVENT_DELETE, self->collection_name, &col->documents[i] };
            notify_observers(&e);
            for (int j = i; j < col->document_count - 1; j++) {
                col->documents[j] = col->documents[j + 1];
            }
            col->document_count--;
        } else {
            i++;
        }
    }
}

Command create_insert_command(const char* collection, Document doc) {
    Command cmd = { .execute = insert_execute };
    strcpy(cmd.collection_name, collection);
    cmd.document = doc;
    return cmd;
}

Command create_update_command(const char* collection, Document query, Document update) {
    Command cmd = { .execute = update_execute };
    strcpy(cmd.collection_name, collection);
    cmd.query = query;
    cmd.update = update;
    return cmd;
}

Command create_delete_command(const char* collection, Document query) {
    Command cmd = { .execute = delete_execute };
    strcpy(cmd.collection_name, collection);
    cmd.query = query;
    return cmd;
}

Document create_document(char field_names[][MAX_FIELD_NAME], char field_values[][MAX_FIELD_VALUE], int field_count) {
    Document doc;
    doc.field_count = field_count;
    for (int i = 0; i < field_count; i++) {
        strcpy(doc.field_names[i], field_names[i]);
        strcpy(doc.field_values[i], field_values[i]);
    }
    return doc;
}

void print_event(Event* e) {
    const char* type = e->type == EVENT_INSERT ? "Insert" :
                       e->type == EVENT_UPDATE ? "Update" : "Delete";
    printf("Event: %s in collection '%s'\n", type, e->collection_name);
    for (int i = 0; i < e->document->field_count; i++) {
        printf("  %s: %s\n", e->document->field_names[i], e->document->field_values[i]);
    }
}


int main() {
    NoSQLDatabase db = { .collection_count = 1 };
    strcpy(db.collections[0].name, "users");
    db.collections[0].document_count = 0;

    register_observer(print_event);

    // insert Alice
    char field_names1[][MAX_FIELD_NAME] = { "id", "name", "age" };
    char field_values1[][MAX_FIELD_VALUE] = { "1", "Alice", "25" };
    Document doc1 = create_document(field_names1, field_values1, 3);
    Command insert1 = create_insert_command("users", doc1);
    insert1.execute(&insert1, &db);

    // insert Bob
    char field_names2[][MAX_FIELD_NAME] = { "id", "name", "age" };
    char field_values2[][MAX_FIELD_VALUE] = { "2", "Bob", "30" };
    Document doc2 = create_document(field_names2, field_values2, 3);
    Command insert2 = create_insert_command("users", doc2);
    insert2.execute(&insert2, &db);

    // update Alice's age
    char query_names[][MAX_FIELD_NAME] = { "name" };
    char query_values[][MAX_FIELD_VALUE] = { "Alice" };
    Document query = create_document(query_names, query_values, 1);

    char update_names[][MAX_FIELD_NAME] = { "age" };
    char update_values[][MAX_FIELD_VALUE] = { "26" };
    Document update = create_document(update_names, update_values, 1);
    Command update_cmd = create_update_command("users", query, update);
    update_cmd.execute(&update_cmd, &db);

    // delete Bob
    char delete_names[][MAX_FIELD_NAME] = { "name" };
    char delete_values[][MAX_FIELD_VALUE] = { "Bob" };
    Document delete_query = create_document(delete_names, delete_values, 1);
    Command delete_cmd = create_delete_command("users", delete_query);
    delete_cmd.execute(&delete_cmd, &db);

    return 0;
}
