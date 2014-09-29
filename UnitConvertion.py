def UnitConvertionToMeters(value, unit_from):
    if unit_from.lower() == "millimeters":
        return value * 0.001
    elif unit_from.lower() == "centimeters":
        return value * 0.01
    elif unit_from.lower() == "decimeters":
        return value * 0.1
    elif unit_from.lower() == "meters":
        return value * 1.0
    elif unit_from.lower() == "kilometers":
        return value * 1000.0
    elif unit_from.lower() == "inches":
        return value * 0.0254
    elif unit_from.lower() == "feet":
        return value * 0.0254 * 12
    elif unit_from.lower() == "yards":
        return value * 0.0254 * 36
    elif unit_from.lower() == "miles":
        return value * 0.0254 * 63360

def UnitConvertionFromMeters(value, unit_to):
    if unit_to.lower() == "millimeters":
        return value * 1000.0
    elif unit_to.lower() == "centimeters":
        return value * 100.0
    elif unit_to.lower() == "decimeters":
        return value * 10.0
    elif unit_to.lower() == "meters":
        return value * 1.0
    elif unit_to.lower() == "kilometers":
        return value * 0.001
    elif unit_to.lower() == "inches":
        return value * 39.3701
    elif unit_to.lower() == "feet":
        return value * 39.3701 / 12
    elif unit_to.lower() == "yards":
        return value * 39.3701 / 36
    elif unit_to.lower() == "miles":
        return value * 39.3701 / 63360

def UnitConvertion(value, unit_from, unit_to):
    if unit_from.lower() == unit_to.lower():
        return value
    else:
        return UnitConvertionFromMeters(UnitConvertionToMeters(value, unit_from), unit_to)
