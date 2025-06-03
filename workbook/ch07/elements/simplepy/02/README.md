
## LaTeX Processing Pipeline Plugins

The pipeline processes `.tex` files sequentially through registered plugins, each performing specific transformations.
The pipeline system is designed to process LaTeX files using a modular, extensible plugin architecture.

- *PluginRegistry*: Manages plugin registration and ordering based on priority.
- *PipelineProcessor*: Executes plugins in sequence, handling intermediate files in a temporary directory and saving final output.
- *LatexProcessor*: Abstract base class defining the plugin interface.
- *Configuration*: Plugins are configured via a `config.json` file.

### 1. Comment Cleaner Plugin
- *Name*: `comment_cleaner`
- *Purpose*: Identifies and optionally removes LaTeX comments, particularly those matching a specified pattern (e.g., `% TODO`).
- *Priority*: 20 (runs after plugins with lower priority values).
- *Configuration* (in `config.json`):
  - `output_dir`: Directory for processed files (default: "temp_output").
  - `comment_logfile`: Log file for comment actions (default: "logs/comments.txt").
  - `auto_remove`: If `true`, removes matching comments automatically; if `false`, prompts user (default: `false`).
  - `comment_pattern`: Target pattern for comments to process (e.g., "% TODO").
- *Behaviour*:
  - Skips comments in `verbatim`, `lstlisting`, `minted`, or `Verbatim` environments and inline `\verb` commands.
  - Logs actions (removed or skipped) to the specified logfile.
  - Writes modified or unchanged files to the output directory.
- *Usage*:
  - Place `comment_cleaner_plugin.py` in the `plugins` directory.
  - Configure in `config.json` (see example below).
  - Run the pipeline; if `auto_remove` is `false`, respond to prompts to remove comments.

### 2. Candidate to Index Plugin
- *Name*: `candidate_to_index`
- *Purpose*: Used for ease of indexing, where candidates are picked out and can be replaced, or not, for real indexing.
- *Priority*: 10 (runs before plugins with higher priority values).
- *Configuration* (in `config.json`):
  - `output_dir`: Directory for processed files (default: "temp_output").
  - `priority`: Execution order (default: 10).
- *Behavior*:
  - Future implementation could convert candidate references to indexed more advanced entries or similar tasks.
- *Usage*:
  - Implement the plugin logic in `candidate_plugin.py`.
  - Place it in the `plugins` directory and configure in `config.json`.


### Configuration Example

The `config.json` file specifies plugin settings:

```json
{
    "candidate_to_index": {
        "output_dir": "temp_output",
        "priority": 10
    },
    "comment_cleaner": {
        "output_dir": "temp_output",
        "comment_logfile": "logs/comments.log",
        "auto_remove": false,
        "comment_pattern": "% TODO",
        "priority": 20
    }
}
```

- Keys match plugin names (e.g., `comment_cleaner`).
- Common fields: `output_dir` (output path), `priority` (execution order).
- Plugin-specific fields: e.g., `comment_pattern` for `comment_cleaner`.


### Using the Pipeline

1. *Setup*:
   - Place LaTeX files (`.tex`) in the `input` directory.
   - Store plugin files (e.g., `comment_cleaner_plugin.py`) in the `plugins` directory.
2. *Configure*:
   - Edit `config.json` to define plugin settings.
3. *Run*:
   - Execute `core.py`:
     ```bash
     python core.py
     ```
   - The pipeline loads plugins, processes each `.tex` file in `input`, and saves results to `output`.
4. *Interaction*:
   - For `comment_cleaner`, if `auto_remove` is `false`, respond to prompts (y/n) to remove comments.
5. *Output*:
   - Processed files appear in the `output` directory.
   - Logs (including comment actions) are written to specified paths (e.g., `logs/comments.log`).


### Adding a New Plugin

To extend the pipeline, create and register a new plugin:

1. *Create Plugin File*:
   - Name it `<plugin_name>_plugin.py` (e.g., `my_transform_plugin.py`).
   - Place it in the `plugins` directory.
2. *Implement the Plugin*:
   - Define a class implementing the `LatexProcessor` interface.
   - Required methods:
     - `name(self)`: Returns the plugin's name (string).
     - `process(self, file_path: str, config: dict) -> bool`: Processes the file; returns `True` on success, `False` on failure.
     - `get_priority(self) -> int`: (Optional) Returns priority (lower = earlier execution; default: 100).
   - Example:
     ```python
     import os
     from typing import Dict

     class MyTransform:
         def __init__(self, config: Dict[str, any]):
             self._output_dir = config.get('output_dir', 'output')
         
         def name(self) -> str:
             return "my_transform"
         
         def get_priority(self) -> int:
             return 15  # Runs between candidate_to_index (10) and comment_cleaner (20)
         
         def process(self, file_path: str, config: Dict[str, any]) -> bool:
             try:
                 with open(file_path, 'r', encoding='utf-8') as f:
                     content = f.read()
                 # Example transformation: replace "old" with "new"
                 modified_content = content.replace('old', 'new')
                 output_dir = config.get('output_dir', self._output_dir)
                 os.makedirs(output_dir, exist_ok=True)
                 output_path = os.path.join(output_dir, os.path.basename(file_path))
                 with open(output_path, 'w', encoding='utf-8') as f:
                     f.write(modified_content)
                 return True
             except Exception as e:
                 logging.error(f"Failed to process {file_path}: {e}")
                 return False

     def register(config: Dict[str, any], LatexProcessor) -> 'MyTransform':
         class Plugin(MyTransform, LatexProcessor):
             pass
         return Plugin(config)
     ```
3. *Configure*:
   - Add to `config.json`:
     ```json
     {
         "my_transform": {
             "output_dir": "temp_output",
             "priority": 15
         }
     }
     ```
4. *Run*:
   - The pipeline automatically loads the plugin from the `plugins` directory.
   - It executes in priority order (e.g., after `candidate_to_index` but before `comment_cleaner`).


### Notes

- *Priority*: Lower numbers run earlier. Use `get_priority` to control order.
- *Thread Safety*: The `PluginRegistry` uses a lock for safe plugin access.
- *Temporary Files*: The pipeline uses a temporary directory for intermediate results, cleaned up automatically.
- *Error Handling*: Plugins log errors and return `False` on failure, stopping the pipeline for that file.
- *Extensibility*: Add new plugins for custom LaTeX transformations (e.g., formatting, indexing, validation).

