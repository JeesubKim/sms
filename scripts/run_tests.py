"""CI-friendly test runner."""

import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(__file__))
SRC = os.path.join(ROOT, "src")

if SRC not in sys.path:
    sys.path.insert(0, SRC)

loader = unittest.TestLoader()

suite = loader.discover(
    start_dir=os.path.join(SRC, "server", "core", "tests"),
    top_level_dir=SRC,
)

runner = unittest.TextTestRunner(verbosity=2)
result = runner.run(suite)

sys.exit(0 if result.wasSuccessful() else 1)
