class TaggsonomyError(Exception):
    pass

class NoSuchTagError(TaggsonomyError):
    pass

class SelfExclusionError(TaggsonomyError):
    pass
