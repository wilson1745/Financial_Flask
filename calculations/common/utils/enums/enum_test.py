from aenum import Enum


class Fingers(Enum):
    _init_ = 'value string string'

    THUMB = "1", 'two thumbs', 'www'
    INDEX = "2", 'offset location', 'vvv'
    MIDDLE = "3", 'average is not median', 'ddd'
    RING = "4", 'round or finger', 'qqq'
    PINKY = "5", 'wee wee wee', 'rrr'

    def __str__(self):
        return self.string

    def __repr__(self):
        return self

    @classmethod
    def _missing_value_(cls, value):
        for member in cls:
            if member.string == value:
                return member
