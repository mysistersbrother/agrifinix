from dataclasses import dataclass, is_dataclass, asdict, fields
import json


SETTINGS_FILENAME = "settings.json"


def encode_value(val):
    if is_dataclass(val):
        return asdict(val)

    raise TypeError(f"Unknown value of type: {type(val)}")


def serialize(val):
    return json.dumps(val, default=encode_value, indent=4)


class JSONObject:
    @classmethod
    def deserialize(cls, dct):
        if isinstance(dct, str):
            dct = json.loads(dct)

        flds = fields(cls)
        args = []
        for field in flds:
            val = dct[field.name]
            if issubclass(field.type, JSONObject):
                args.append(field.type.deserialize(val))
            else:
                args.append(val)

        return cls(*args)


    def serialize(self):
        return serialize(self)


@dataclass
class Point(JSONObject):
    x: int
    y: int


@dataclass
class WindowInfo(JSONObject):
    top_left: Point
    bottom_right: Point
#    maximised: bool


@dataclass
class IndicatorInfo(JSONObject):
    top_box: int
    bottom_box: int
    fish_eye: Point
    bar_top: int
    bar_bottom: int
    fish_text: Point


@dataclass
class Settings(JSONObject):
    window: WindowInfo
    indicators: IndicatorInfo


if __name__ == "__main__":
    window = WindowInfo(Point(50, 50), Point(100, 100))
    indicators = IndicatorInfo(1000, 300, Point(3, 3))

    settings = Settings(window, indicators)

    serialized = settings.serialize()
    des = Settings.deserialize(json.loads(serialized))

    print(des.window)
    print(des.indicators)
    print(des.window.top_left)

    print(serialize(des))
