# plugins/comment_cleaner_plugin.py
import os
import re
import logging
from datetime import datetime

class CommentCleaner:
    def __init__(self, config: dict):
        self._output_dir = config.get('output_dir', 'output')
        self._comment_logfile = config.get('comment_logfile', 'logs/comments.txt')
        self._auto_remove = config.get('auto_remove', False)
        self._target_pattern = config.get('comment_pattern', None)  # Fixed: was 'target_pattern'
        # Match comments: % not preceded by \, capture content until newline or EOF
        self._comment_pattern = re.compile(r'(?<!\\)%.*', re.MULTILINE)
    
    def name(self) -> str:
        return "comment_cleaner"
    
    def get_priority(self) -> int:
        """Run comment cleaning after candidate processing (lower priority)."""
        return 20
    
    def _log_comment_action(self, file_path: str, line_number: int, comment: str, action: str) -> None:
        """Log comment action to the specified logfile."""
        try:
            os.makedirs(os.path.dirname(self._comment_logfile), exist_ok=True)
            with open(self._comment_logfile, 'a', encoding='utf-8') as f:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                f.write(f"[{timestamp}] File: {file_path}, Line: {line_number}, Action: {action}, Comment: {comment}\n")
        except Exception as e:
            logging.error(f"Failed to write to comment logfile {self._comment_logfile}: {e}")
    
    def process(self, file_path: str, config: dict) -> bool:
        try:
            # Read the LaTeX file
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            logging.debug(f"Processing {len(lines)} lines in {file_path}")
            
            modified_lines = []
            removals = 0
            in_verbatim = False
            in_verb_env = False
            
            # Get updated config values
            comment_logfile = config.get('comment_logfile', self._comment_logfile)
            auto_remove = config.get('auto_remove', self._auto_remove)
            target_pattern = config.get('comment_pattern', self._target_pattern)
            
            # Process line by line
            for i, line in enumerate(lines, start=1):
                logging.debug(f"Line {i}: {line.rstrip()}")
                
                # Check for verbatim-like environments (more comprehensive)
                if re.search(r'\\begin\{(verbatim|lstlisting|minted|Verbatim)\}', line):
                    in_verbatim = True
                    logging.debug(f"Entered verbatim-like environment at line {i}")
                elif re.search(r'\\end\{(verbatim|lstlisting|minted|Verbatim)\}', line):
                    in_verbatim = False
                    logging.debug(f"Exited verbatim-like environment at line {i}")
                
                # Check for inline verb commands
                if re.search(r'\\verb[^a-zA-Z]', line):
                    in_verb_env = True
                    logging.debug(f"Found inline verb at line {i}")
                
                if in_verbatim or in_verb_env:
                    modified_lines.append(line)
                    in_verb_env = False  # Reset inline verb flag
                    continue
                
                # Find comment in the line
                comment_match = self._comment_pattern.search(line)
                if not comment_match:
                    modified_lines.append(line)
                    continue
                
                # Extract comment parts
                comment_full = comment_match.group(0)  # Full match including %
                comment_content = comment_full[1:].strip()  # Content after % (remove % and strip)
                start_pos = comment_match.start()
                
                logging.debug(f"Found comment at line {i}, pos {start_pos}: '{comment_full}' (content: '{comment_content}')")
                
                # Skip if comment doesn't match target pattern
                # Note: target_pattern might include %, but comment_content has % stripped
                if target_pattern:
                    # Remove % from target_pattern for comparison with stripped comment_content
                    pattern_to_check = target_pattern[1:].strip() if target_pattern.startswith('%') else target_pattern
                    if pattern_to_check not in comment_content:
                        logging.debug(f"Skipping comment (no '{pattern_to_check}' match): {comment_content}")
                        modified_lines.append(line)
                        continue
                
                # Decide whether to remove
                should_remove = auto_remove
                if not should_remove:
                    # Show context
                    context = lines[max(0, i-2)].strip() if i > 1 else "<start of file>"
                    prompt = f"Remove comment '{comment_content}' at line {i} in {file_path}?\nContext: {context}\n(y/n): "
                    response = input(prompt).strip().lower()
                    should_remove = response == 'y'
                
                if should_remove:
                    # Remove comment by slicing up to start_pos and strip trailing whitespace
                    before_comment = line[:start_pos].rstrip()
                    if before_comment:  # If there's content before the comment
                        modified_line = before_comment + '\n'
                    else:  # If the entire line is just a comment
                        modified_line = ''  # Remove the entire line
                    
                    logging.debug(f"Original line: {repr(line)}")
                    logging.debug(f"Modified line: {repr(modified_line)}")
                    
                    modified_lines.append(modified_line)
                    removals += 1
                    logging.info(f"Removed comment '{comment_content}' at line {i}, pos {start_pos} in {file_path}")
                    self._log_comment_action(file_path, i, comment_content, "Removed")
                else:
                    logging.info(f"Skipped comment '{comment_content}' at line {i}, pos {start_pos} in {file_path}")
                    self._log_comment_action(file_path, i, comment_content, "Skipped")
                    modified_lines.append(line)
            
            # Always write output file (for pipeline)
            output_dir = config.get('output_dir', self._output_dir)
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, os.path.basename(file_path))
            with open(output_path, 'w', encoding='utf-8') as f:
                f.writelines(modified_lines)
            
            if removals > 0:
                logging.info(f"Wrote modified file to {output_path} with {removals} comments removed")
            else:
                logging.info(f"Wrote unchanged file to {output_path}")
            
            return True
            
        except Exception as e:
            logging.error(f"Failed to process {file_path}: {e}")
            return False

def register(config: dict, LatexProcessor) -> 'CommentCleaner':
    class Plugin(CommentCleaner, LatexProcessor):
        pass
    return Plugin(config)