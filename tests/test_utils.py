import unittest

from pymilight import utils


class UtilsTestCase(unittest.TestCase):
    def testKelvinToMireds(self):
        self.assertAlmostEqual(370.4, utils.kelvin_to_mireds(2700), 1)
        self.assertAlmostEqual(153.8, utils.kelvin_to_mireds(6500), 1)

    def testMiredsToKelvin(self):
        self.assertAlmostEqual(2700, utils.mireds_to_kelvin(370), -1)
        self.assertAlmostEqual(6500, utils.mireds_to_kelvin(153.828), -1)

    def testMiredsToWhite(self):
        self.assertAlmostEqual(100, utils.mireds_to_white_val(370))
        self.assertAlmostEqual(0, utils.mireds_to_white_val(153))

        self.assertAlmostEqual(50, utils.mireds_to_white_val(262))

    def testWhiteToMireds(self):
        self.assertAlmostEqual(370, utils.white_val_to_mireds(100))
        self.assertAlmostEqual(153, utils.white_val_to_mireds(0))

        self.assertAlmostEqual(262, utils.white_val_to_mireds(50))

    def testKelvinToWhite(self):
        self.assertAlmostEqual(100, utils.kelvin_to_white_val(2700))
        self.assertAlmostEqual(0, utils.kelvin_to_white_val(6500))

        self.assertAlmostEqual(50, utils.kelvin_to_white_val(3817))

    def testWhiteToKelvin(self):
        self.assertAlmostEqual(6500, utils.white_val_to_kelvin(0), -2)
        self.assertAlmostEqual(2700, utils.white_val_to_kelvin(99.8), -1)

        self.assertAlmostEqual(3820, utils.white_val_to_kelvin(50), 0)