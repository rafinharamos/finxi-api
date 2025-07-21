#!/usr/bin/env python
import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner

if __name__ == "__main__":
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'finxi.settings')
    
    # Add the finxi directory to the Python path
    sys.path.insert(0, '/workspace/finxi-api/finxi')
    
    django.setup()
    
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(["core.tests"])
    
    if failures:
        sys.exit(1)