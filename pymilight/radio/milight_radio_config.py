"""
Config for different remotes.
"""

class MiLightRadioConfig:
    CONFIG_RGBW = MiLightRadioConfig(0x147A, 0x258B, 7, 9, 40, 71)
    CONFIG_CCT = MiLightRadioConfig(0x050A, 0x55AA, 7, 4, 39, 74)
    CONFIG_RGB_CCT = MiLightRadioConfig(0x7236, 0x1809, 9, 8, 39, 70)
    CONFIG_RGB = MiLightRadioConfig(0x9AAB, 0xBCCD, 6, 3, 38, 73)

    def __init__(self, syncword0, syncword3, packetLength, channel0, channel1, channel2):
        self.syncword0 = syncword0
        self.syncword3 = syncword3
        self.packetLength = packetLength
        self.channels = [
            channel0,
            channel1,
            channel2,
        ]
