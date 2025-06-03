import os
import importlib.util
import sys
import json
import threading
import shutil
import tempfile
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Tuple
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Enhanced plugin interface
class LatexProcessor(ABC):
    @abstractmethod
    def name(self) -> str:
        pass
    
    @abstractmethod
    def process(self, file_path: str, config: Dict[str, Any]) -> bool:
        pass
    
    def get_priority(self) -> int:
        """Return processing priority (lower numbers = higher priority).
        Override in plugins to control execution order."""
        return 100

# Thread-safe registry with pipeline support
class PluginRegistry:
    def __init__(self):
        self._plugins: Dict[str, LatexProcessor] = {}
        self._lock = threading.Lock()
    
    def register(self, plugin: LatexProcessor) -> None:
        with self._lock:
            self._plugins[plugin.name()] = plugin
            logger.info(f"Registered plugin: {plugin.name()}")
    
    def get(self, name: str) -> Optional[LatexProcessor]:
        with self._lock:
            return self._plugins.get(name)
    
    def list_plugins(self) -> List[str]:
        with self._lock:
            return list(self._plugins.keys())
    
    def get_ordered_plugins(self) -> List[Tuple[str, LatexProcessor]]:
        """Return plugins sorted by priority for pipeline processing."""
        with self._lock:
            plugins = [(name, plugin) for name, plugin in self._plugins.items()]
            # Sort by priority (lower numbers first), then by name for consistency
            plugins.sort(key=lambda x: (x[1].get_priority(), x[0]))
            return plugins

# Pipeline processor for sequential plugin execution
class PipelineProcessor:
    def __init__(self, registry: PluginRegistry, config: Dict[str, Any]):
        self.registry = registry
        self.config = config
        self.temp_dir = None
    
    def __enter__(self):
        # Create temporary directory for intermediate files
        self.temp_dir = tempfile.mkdtemp(prefix='latex_pipeline_')
        logger.info(f"Created temporary directory: {self.temp_dir}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Clean up temporary directory
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            logger.info(f"Cleaned up temporary directory: {self.temp_dir}")
    
    def process_file(self, input_file: str, final_output_dir: str) -> bool:
        """Process a single file through the plugin pipeline."""
        if not os.path.isfile(input_file):
            logger.error(f"Input file not found: {input_file}")
            return False
        
        ordered_plugins = self.registry.get_ordered_plugins()
        if not ordered_plugins:
            logger.warning("No plugins registered")
            return False
        
        current_file = input_file
        filename = os.path.basename(input_file)
        
        logger.info(f"Processing {filename} through pipeline: {[name for name, _ in ordered_plugins]}")
        
        # Process through each plugin in sequence
        for i, (plugin_name, plugin) in enumerate(ordered_plugins):
            logger.info(f"Step {i+1}/{len(ordered_plugins)}: Processing with {plugin_name}")
            
            # Create temporary output directory for this step
            step_output_dir = os.path.join(self.temp_dir, f"step_{i+1}_{plugin_name}")
            os.makedirs(step_output_dir, exist_ok=True)
            
            # Temporarily modify plugin's output directory
            plugin_config = self.config.get(plugin_name, {}).copy()
            original_output_dir = plugin_config.get('output_dir', 'output')
            plugin_config['output_dir'] = step_output_dir
            
            try:
                # Process the file
                success = plugin.process(current_file, plugin_config)
                if not success:
                    logger.error(f"Plugin {plugin_name} failed to process {current_file}")
                    return False
                
                # Check if plugin created output (some plugins might skip files)
                step_output_file = os.path.join(step_output_dir, filename)
                if os.path.exists(step_output_file):
                    # Use the plugin's output as input for the next step
                    current_file = step_output_file
                    logger.info(f"Plugin {plugin_name} processed file -> {step_output_file}")
                else:
                    # Plugin didn't modify the file, continue with current file
                    logger.info(f"Plugin {plugin_name} didn't modify {filename}, continuing with original")
                
            except Exception as e:
                logger.error(f"Error in plugin {plugin_name} for {current_file}: {e}")
                return False
        
        # Copy final result to output directory
        if current_file != input_file:  # Only if file was actually modified
            os.makedirs(final_output_dir, exist_ok=True)
            final_output_path = os.path.join(final_output_dir, filename)
            shutil.copy2(current_file, final_output_path)
            logger.info(f"Final result saved to: {final_output_path}")
        else:
            logger.info(f"No plugins modified {filename}, no output file created")
        
        return True

# Load plugins from directory and config
def load_plugins(plugin_dir: str, config_file: str) -> PluginRegistry:
    registry = PluginRegistry()
    if not os.path.exists(plugin_dir):
        logger.error(f"Plugin directory '{plugin_dir}' not found!")
        return registry
    
    # Load config
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
    except Exception as e:
        logger.error(f"Failed to load config {config_file}: {e}")
        return registry
    
    # Load plugins
    for filename in os.listdir(plugin_dir):
        if filename.endswith("_plugin.py"):
            try:
                plugin_name = filename[:-3]
                logger.info(f"Attempting to load plugin: {plugin_name}")
                spec = importlib.util.spec_from_file_location(plugin_name, os.path.join(plugin_dir, filename))
                if spec is None:
                    logger.warning(f"Could not load spec for {filename}")
                    continue
                module = importlib.util.module_from_spec(spec)
                sys.modules[plugin_name] = module
                spec.loader.exec_module(module)
                if hasattr(module, 'register'):
                    plugin = module.register(config.get(plugin_name, {}), LatexProcessor)
                    if isinstance(plugin, LatexProcessor):
                        registry.register(plugin)
                        logger.info(f"Successfully loaded plugin: {plugin_name} (priority: {plugin.get_priority()})")
                    else:
                        logger.warning(f"Plugin {plugin_name} does not implement LatexProcessor")
                else:
                    logger.warning(f"No register function in {plugin_name}")
            except Exception as e:
                logger.error(f"Error loading plugin {filename}: {e}")
    return registry

# Process LaTeX files through pipeline
def process_files(registry: PluginRegistry, config_file: str, input_dir: str, output_dir: str = "output") -> None:
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
    except Exception as e:
        logger.error(f"Failed to load config {config_file}: {e}")
        return
    
    if not os.path.exists(input_dir):
        logger.error(f"Input directory '{input_dir}' not found!")
        return
    
    # Process each .tex file through the pipeline
    tex_files = [f for f in os.listdir(input_dir) if f.endswith('.tex')]
    if not tex_files:
        logger.warning(f"No .tex files found in {input_dir}")
        return
    
    logger.info(f"Found {len(tex_files)} .tex files to process")
    
    with PipelineProcessor(registry, config) as processor:
        for filename in tex_files:
            file_path = os.path.join(input_dir, filename)
            if os.path.isfile(file_path):
                logger.info(f"Starting pipeline for {filename}")
                success = processor.process_file(file_path, output_dir)
                if success:
                    logger.info(f"Successfully processed {filename}")
                else:
                    logger.error(f"Failed to process {filename}")

# Main
if __name__ == "__main__":
    PLUGIN_DIR = "plugins"
    CONFIG_FILE = "config.json"
    INPUT_DIR = "input"
    OUTPUT_DIR = "output"
    
    logger.info("Starting LaTeX processing pipeline")
    registry = load_plugins(PLUGIN_DIR, CONFIG_FILE)
    
    if registry.list_plugins():
        logger.info(f"Loaded plugins: {registry.list_plugins()}")
        process_files(registry, CONFIG_FILE, INPUT_DIR, OUTPUT_DIR)
    else:
        logger.error("No plugins loaded, exiting")