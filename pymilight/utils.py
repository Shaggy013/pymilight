# MiLight CCT bulbs range from 2700K-6500K, or ~370.3-153.8 mireds (warm to cool).
# Packets are sent with range 0-100.
# So we need to rescale 370 -> 153 onto 0 -> 100.
COLOR_TEMP_MAX_MIREDS = 370
COLOR_TEMP_MIN_MIREDS = 153
COLOR_TEMP_RANGE_MIREDS = COLOR_TEMP_MAX_MIREDS - COLOR_TEMP_MIN_MIREDS


def constrain(val, min_val, max_val):
    return min(max_val, max(min_val, val))


def rescale(val, new_max, old_max):
    return round(val * (new_max / float(old_max)))


def mireds_to_white_val(mireds):
    val = COLOR_TEMP_RANGE_MIREDS - (mireds - COLOR_TEMP_MIN_MIREDS)
    return int(round(val / float(COLOR_TEMP_RANGE_MIREDS) * 100.0, 0))


def white_val_to_mireds(value):
    val = (100 - value) / 100.0
    return int(round(COLOR_TEMP_RANGE_MIREDS * val + COLOR_TEMP_MIN_MIREDS, 0))


def kelvin_to_white_val(kelvin):
    return mireds_to_white_val(kelvin_to_mireds(kelvin))


def white_val_to_kelvin(value):
    return int(round(mireds_to_kelvin(white_val_to_mireds(value)), -1))


def kelvin_to_mireds(kelvin):
    return 1E6 / kelvin


def mireds_to_kelvin(mireds):
    return 1E6 / mireds