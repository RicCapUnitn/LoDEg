import unittest
import sys
import os
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../../src/lodegML')
import auto_plot
from exceptions import AutoPlotException


class TestAutoplot(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.test_output_folder = './test/unit/test_output/'
        cls.autoplot = auto_plot.AutoPlot(target='default')
        cls.test_coverage = {
            'session_coverage': [
                [0.0, 60.0], [70.0, 100.0], [130.0, 150.0]]
        }
        cls.test_lesson_duration = 300

    def test_saveNextFigure_valid_path(self):
        path = 'valid_image.png'
        self.autoplot.saveNextFigure(path, self.test_output_folder).printSessionCoverage(
            self.test_coverage, self.test_lesson_duration)
        self.assertTrue(os.path.isfile(self.test_output_folder + path))

    def test_saveNextFigure_invalid_path(self):
        path = 'boh/boh.png'
        with self.assertRaisesRegex(AutoPlotException, 'Error while saving figure'):
            self.autoplot.saveNextFigure(path, self.test_output_folder).printSessionCoverage(
                self.test_coverage, self.test_lesson_duration)

    def test_saveNextFigure_invalid_file_extension(self):
        path = 'invalid_file_extension.mp3'
        with self.assertRaisesRegex(AutoPlotException, 'Error while saving figure'):
            self.autoplot.saveNextFigure(path, self.test_output_folder).printSessionCoverage(
                self.test_coverage, self.test_lesson_duration)
