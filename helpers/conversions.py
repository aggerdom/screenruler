from fractions import Fraction
from functools import reduce

CONVERSIONS = {
    'px': {},  # Pixels
    'pt': {},  # Points
    'em': {},  # Em
    'in': {},  # inches
    'mm': {},  # millimeter
    'pi': {},  # pica
}

CONVERSIONS['px']['in'] = lambda x: x * Fraction(1, 96)
CONVERSIONS['in']['pt'] = lambda x: x * Fraction(72, 1)
CONVERSIONS['in']['mm'] = lambda x: x * Fraction(254, 10)
CONVERSIONS['pt']['em'] = lambda x: x * Fraction(1, 12)
CONVERSIONS['in']['pi'] = lambda x: x * Fraction(6, 1)

def float_to_frac(x, precision=100):
    return Fraction(round(x * precision), precision)

def define_conversions():
    """
    Based upon the conversions that are presently defined,
    define all possible conversions.
    """
    graph = {
        k: [v for v in CONVERSIONS[k]]
        for k in CONVERSIONS
    }

    def find_path(a, b, path=None):
        """
        DFS to find a path from unit a to unit b.

        :param a: Unit we want a conversion from
        :param b: Unit we want a conversion to
        :param path: Path so far in the current search
        :return: Path as a list of (direction, node1, node2) tuples.
                Direction will be '+' if node2 is defined in terms of node1 (CONVERSIONS[node1][node2] is defined)
                Direction will be '-' if node2 is defined in terms of node1 (CONVERSIONS[node2][node1] is defined)
        """
        if path is None:
            path = []
        # Case: Node has been visited
        if a in [p[1] for p in path]:
            return None
        # Case: We have a path from a to b or b to a
        if b in graph[a]:
            return path + [("+", a, b)]
        elif a in graph[b]:
            return path + [('-', a, b)]

        # Case: There's an outbound path from a that works
        for c in graph[a]:
            res = find_path(c, b, path=path + [("+", a, c)])
            if res:
                return res

        # Case: There's an inbound path to a that works
        for c in graph:
            if a in graph[c]:
                res = find_path(c, b, path=path + [("-", a, c)])
                if res:
                    return res

    # Note: This is defined the way it is so the resulting function will have path in it's closure
    def get_conversion(a, b):
        """
        Get a function to convert between two provided measurements
        :param a: Unit we want a conversion from
        :param b: Unit we want a conversion to
        :return: Function that converts from a to b
        """
        path = find_path(a, b)
        path = [CONVERSIONS[a][b](1) if (d == '+') else (CONVERSIONS[b][a](1) ** -1)
                for (d, a, b) in path]
        return lambda x: x * reduce(lambda a, b: a * b, path)

    for a in graph:
        for b in graph:
            if a == b:
                continue
            if CONVERSIONS[a].get(b):
                continue
            CONVERSIONS[a][b] = get_conversion(a, b)
    for k in CONVERSIONS:
        CONVERSIONS[k][k] = lambda x: x

define_conversions()

def test_inverses():
    # Test that all
    for a in CONVERSIONS:
        for b in CONVERSIONS:
            for i in range(0, 100):
                inner = CONVERSIONS[a][b](i)
                outer = CONVERSIONS[b][a](inner)
                assert outer == i, f"c[{a}][{b}](c[{b}][{a}]({i})) != {i}"


if __name__ == '__main__':
    test_inverses()
