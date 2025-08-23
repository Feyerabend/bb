# In plugins/test_plugin.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from compiler import plugin

@plugin
def my_custom_function(ast, context, messages):
    messages.info("Running my custom plugin")
    return {"status": "executed"}
