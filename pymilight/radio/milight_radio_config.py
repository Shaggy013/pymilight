"""
Config for different remotes.
"""

class MiLightRadioConfig:

    def __init__(self, syncword0, syncword3, packetLength, channel0, channel1, channel2):
        self.syncword0 = syncword0
        self.syncword3 = syncword3
        self.packetLength = packetLength
        self.channels = [
            channel0,
            channel1,
            channel2,
        ]

MiLightRadioConfig.CONFIG_RGBW = MiLightRadioConfig(0x147A, 0x258B, 7, 9, 40, 71)
MiLightRadioConfig.CONFIG_CCT = MiLightRadioConfig(0x050A, 0x55AA, 7, 4, 39, 74)
MiLightRadioConfig.CONFIG_RGB_CCT = MiLightRadioConfig(0x7236, 0x1809, 9, 8, 39, 70)
MiLightRadioConfig.CONFIG_RGB = MiLightRadioConfig(0x9AAB, 0xBCCD, 6, 3, 38, 73)
MiLightRadioConfig.ALL_RADIOS = {
    'rgbw': MiLightRadioConfig.CONFIG_RGBW,
    'cct': MiLightRadioConfig.CONFIG_CCT,
    'rgb_cct': MiLightRadioConfig.CONFIG_RGB_CCT,
    'rgb': MiLightRadioConfig.CONFIG_RGB,
}
