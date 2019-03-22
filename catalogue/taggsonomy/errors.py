class TaggsonomyError(Exception):
    pass

class MutualExclusionError(TaggsonomyError):
    pass

class NoSuchTagError(TaggsonomyError):
    pass

class SelfExclusionError(TaggsonomyError):
    pass
