#! /usr/bin/python
import unittest
import coverage

COV = coverage.coverage(branch=True, include='app/*')
COV.start()

suite = unittest.TestLoader().discover('tests')
unittest.TextTestRunner(verbosity=2).run(suite)

COV.stop()
COV.report()
