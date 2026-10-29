"""H022: PDF collection and copy planning. Safe standalone wrapper around shared offline tools."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _shared.core import main

if __name__ == '__main__':
    main(['--mode', 'copy_pdfs', *sys.argv[1:]])
