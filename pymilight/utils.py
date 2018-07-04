# MiLight CCT bulbs range from 2700K-6500K, or ~370.3-153.8 mireds.
COLOR_TEMP_MAX_MIREDS = 370
COLOR_TEMP_MIN_MIREDS = 153


def constrain(val, min_val, max_val):
    return min(max_val, max(min_val, val))


def rescale(val, new_max, old_max):
    return round(val * (new_max / float(old_max)))


def mireds_to_white_val(mireds, max_val=255):
    return int(round(1000000 / mireds, 0))


def white_val_to_mireds(value, max_val=255):
    return int(round(1000000 / value, 0))