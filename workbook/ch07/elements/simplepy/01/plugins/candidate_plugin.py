import os
import re
import logging

class CandidatePlugin:
    def __init__(self, config: dict):
        self._output_dir = config.get('output_dir', 'output')
        # Match \candidate{index}{text} or \candidate{index} (no text part)
        self._candidate_pattern = re.compile(r'\\candidate\{((?:\\[^ {][^{}]*\{[^}]*\}|[^}])*)\}(?:\{((?:\\[^ {][^{}]*\{[^}]*\}|[^}])*)\})?')
        self._index_pattern = re.compile(r'\\index\{((?:\\[^ {][^{}]*\{[^}]*\}|[^}])*)\}')
    
    def name(self) -> str:
        return "candidate_to_index"
    
    def get_priority(self) -> int:
        """Run candidate processing first (high priority)."""
        return 10
    
    def process(self, file_path: str, config: dict) -> bool:
        try:
            # Read the LaTeX file
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for existing \index commands to avoid duplicates
            existing_indexes = set(self._index_pattern.findall(content))
            
            # Find all \candidate commands
            candidates = self._candidate_pattern.findall(content)
            if not candidates:
                logging.info(f"No \\candidate commands found in {file_path}")
                # Even if no candidates found, we should create output file for pipeline
                # Only create output if we're supposed to write to a different location
                output_dir = config.get('output_dir', self._output_dir)
                if os.path.dirname(file_path) != output_dir:
                    os.makedirs(output_dir, exist_ok=True)
                    output_path = os.path.join(output_dir, os.path.basename(file_path))
                    with open(output_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    logging.info(f"Copied unchanged file to {output_path}")
                return True
            
            modified_content = content
            substitutions = 0
            
            # Process each \candidate case by case
            for candidate in candidates:
                index_term = candidate[0]  # First group: index term (e.g., demoscene)
                display_text = candidate[1] if candidate[1] else index_term  # Second group: display text (e.g., demos), or index_term if absent
                
                # Skip if the index term is already indexed
                if index_term in existing_indexes:
                    logging.info(f"Skipping index term '{index_term}' in {file_path}: already indexed")
                    continue
                
                # Prompt user for substitution decision
                prompt = f"Replace '\\candidate{{{index_term}}}' or '\\candidate{{{index_term}}}{{{display_text}}}' with '{display_text}' and '\\index{{{index_term}}}' in {file_path}? (y/n): "
                response = input(prompt).strip().lower()
                if response == 'y':
                    # Replace \candidate{index} or \candidate{index}{text} with display_text plus \index{index}
                    # Handle both cases: with and without display text
                    if candidate[1]:  # Has display text
                        old_pattern = f'\\candidate{{{index_term}}}{{{display_text}}}'
                    else:  # No display text
                        old_pattern = f'\\candidate{{{index_term}}}'
                    
                    replacement = f'{display_text}\\index{{{index_term}}}'
                    modified_content = modified_content.replace(old_pattern, replacement)
                    substitutions += 1
                    logging.info(f"Substituted '{old_pattern}' with '{replacement}'")
                else:
                    logging.info(f"Skipped substitution for '\\candidate{{{index_term}}}'")
            
            # Always write output file (for pipeline)
            output_dir = config.get('output_dir', self._output_dir)
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, os.path.basename(file_path))
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(modified_content)
            
            if substitutions > 0:
                logging.info(f"Wrote modified file to {output_path} with {substitutions} substitutions")
            else:
                logging.info(f"Wrote unchanged file to {output_path}")
            
            return True
        except Exception as e:
            logging.error(f"Failed to process {file_path}: {e}")
            return False

def register(config: dict, LatexProcessor) -> 'CandidatePlugin':
    class Plugin(CandidatePlugin, LatexProcessor):
        pass
    return Plugin(config)