#!/usr/bin/env python

import sys
import unittest

if __name__ == "__main__":
    suite = unittest.TestLoader().discover('./python_translate/tests', pattern = "*.py")
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    sys.exit(not result.wasSuccessful())