import json
import unittest

from pymilight.rgb_converter import hsv_to_rgb, rgb_to_hsv


class RgbConverterTestCase(unittest.TestCase):
    def test_rgb_to_hsv(self):
        hue, saturation, value = rgb_to_hsv(255, 255, 255)
        self.assertEqual(0, hue)
        self.assertEqual(0, saturation)
        self.assertEqual(1, value)

        hue, saturation, value = rgb_to_hsv(255, 0, 0)
        self.assertEqual(0, hue)
        self.assertEqual(1, saturation)
        self.assertEqual(1, value)

        hue, saturation, value = rgb_to_hsv(0, 255, 0)
        self.assertAlmostEqual(0.33333333, hue)
        self.assertEqual(1, saturation)
        self.assertEqual(1, value)

        hue, saturation, value = rgb_to_hsv(0, 10, 255)
        self.assertAlmostEqual(0.66013071895, hue)
        self.assertEqual(1, saturation)
        self.assertEqual(1, value)

    def test_hsv_to_rgb(self):
        rgb = hsv_to_rgb(0, 0, 1)
        self.assertEqual((255, 255, 255), rgb)

        rgb = hsv_to_rgb(0, 1, 1)
        self.assertEqual((255, 0, 0), rgb)

        rgb = hsv_to_rgb(1 / 3.0, 1, 1)
        self.assertEqual((0, 255, 0), rgb)

        rgb = hsv_to_rgb(0.66013071895, 1, 1)
        self.assertEqual((0, 9, 255), rgb)