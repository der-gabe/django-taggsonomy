class TaggsonomyError(Exception):
    pass

class MutualExclusionError(TaggsonomyError):
    pass

class NoSuchTagError(TaggsonomyError):
    pass

class SelfExclusionError(TaggsonomyError):
    pass

class SimultaneousInclusionExclusionError(TaggsonomyError):
    pass

class CircularInclusionError(TaggsonomyError):
    pass

class CommonSubtagExclusionError(TaggsonomyError):
    pass
