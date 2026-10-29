"""H043: Workbook schema comparison. Safe standalone wrapper around shared offline tools."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _shared.core import main

if __name__ == '__main__':
    main(['--mode', 'compare_headers', *sys.argv[1:]])
