class DependentTagSet(object):
    """
    Base class for tagsets that depend on a single tag,
    such as exclusion, sub- and supertagsets.
    """
    def __init__(self, tag):
        self.tag = tag


class ExclusionTagSet(DependentTagSet):
    """
    Set of tags excluded by the `Tag` instance passed to the contructor.
    """
    pass


class SubTagSet(DependentTagSet):
    """
    Set of subtags of the `Tag` instance passed to the contructor.
    """
    pass


class SuperTagSet(DependentTagSet):
    """
    Set of supertags of the `Tag` instance passed to the contructor.
    """
    pass
