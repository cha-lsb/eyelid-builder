"""
Miscellaneous methods and functions used in the project
"""

import maya.cmds as cmds
import functools

def undo_chunk(func):
    """
    A decorator that wraps a Maya command or function within a single undo chunk.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        chunk_name = func.__name__.replace('_', ' ').title()
        cmds.undoInfo(openChunk=True, chunkName=chunk_name)
        result = None
        try:
            result = func(*args, **kwargs)
        finally:
            cmds.undoInfo(closeChunk=True)
        return result
    return wrapper
