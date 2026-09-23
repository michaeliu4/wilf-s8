"""Explicit primitive-return catalogue and the Ray--West j statistic.

The mathematical justification is in Section 6 of manuscript/main.pdf.  These routines inspect the
input permutation only; they do not enumerate larger permutations.
Python 3.10+, standard library only.
"""
from __future__ import annotations
from collections.abc import Iterable, Iterator

Perm = tuple[int, ...]
Parameters = tuple[int, int, int, int]


def validate(p: Perm) -> None:
    if sorted(p) != list(range(1, len(p) + 1)):
        raise ValueError("Expected a permutation of 1,...,n.")


def return_word(a: int, b: int, t: int, s: int) -> Perm:
    """Construct Z(a,b;t,s); raise ValueError for inadmissible parameters."""
    if a < 2 or b < 2 or t < 0 or s < 0:
        raise ValueError("Require a,b >= 2 and t,s >= 0.")
    n = a + b + t + s - 2
    q, v = b - 1 + 2*t, a - 1 + 2*s
    if q >= n or v >= n:
        raise ValueError("Require b-1+2t < n and a-1+2s < n.")
    w: list[int | None] = [None] * (n + 1)
    w[1], w[b] = a, 1
    for i in range(1, n + 1):
        if i in (q, n):
            continue
        target = i + (2 if b - 1 <= i < q else 1)
        value = w[i]
        if value is None:
            raise AssertionError("An increasing path has no assigned root.")
        image = value + 1 + int(a - 1 <= value < v)
        if w[target] is not None and w[target] != image:
            raise AssertionError("The two paths collided.")
        w[target] = image
    if any(x is None for x in w[1:]):
        raise AssertionError("The paths did not cover all positions.")
    p = tuple(int(x) for x in w[1:])
    validate(p)
    return p


def primitive_parameters(word: Iterable[int], *, check_input: bool = True
                         ) -> Parameters | None:
    """Recognize a primitive return in linear time after input validation.

    Returns the unique (a,b,t,s), or None.  Validation sorts the input and
    therefore takes O(n log n); set check_input=False for a known permutation.
    """
    w = tuple(word)
    if check_input:
        validate(w)
    n = len(w)
    if n < 2:
        return None
    a, b = w[0], w.index(1) + 1
    if a < 2 or b < 2 or w[-1] == n:
        return None
    q, v = w.index(n) + 1, w[-1]
    k, l = q - b + 1, v - a + 1
    if k < 0 or l < 0 or k % 2 or l % 2:
        return None
    t, s = k // 2, l // 2
    if n != a + b + t + s - 2:
        return None
    if a == b == 2 and t == s and t >= 1:
        return None
    # Compare path equations directly rather than reconstructing and sorting.
    for i in range(1, n + 1):
        if i in (q, n):
            continue
        target = i + (2 if b - 1 <= i < q else 1)
        value = w[i - 1]
        if target > n or w[target - 1] != value + 1 + int(a - 1 <= value < v):
            return None
    return a, b, t, s


def catalogue(n: int) -> Iterator[tuple[Parameters, Perm]]:
    """Generate all primitive return words of a given length, without repeats."""
    if n < 0:
        raise ValueError("Length must be nonnegative.")
    for a in range(2, n + 1):
        for b in range(2, n + 1):
            for t in range(max(0, n + 3 - a - b)):
                s = n + 2 - a - b - t
                if s < 0 or b - 1 + 2*t >= n or a - 1 + 2*s >= n:
                    continue
                if a == b == 2 and t == s and t >= 1:
                    continue
                yield (a, b, t, s), return_word(a, b, t, s)


def catalogue_size(n: int) -> int:
    if n < 2:
        return 0
    if n % 2:
        return (n**3 - n) // 12
    return (n**3 + 2*n) // 12 - int(n >= 4)


def j_statistic(word: Iterable[int]) -> int:
    """Count oriented primitive-return intervals in O(n^3) arithmetic work."""
    p = tuple(word)
    validate(p)
    total = 0
    for left in range(len(p)):
        lo = hi = p[left]
        for right in range(left + 1, len(p)):
            lo, hi = min(lo, p[right]), max(hi, p[right])
            if hi - lo != right - left:
                continue
            w = tuple(x - lo + 1 for x in p[left:right+1])
            total += primitive_parameters(w, check_input=False) is not None
            total += primitive_parameters(w[::-1], check_input=False) is not None
    return total


def g2(word: Iterable[int]) -> int:
    p = tuple(word)
    validate(p)
    m = len(p)
    if m == 0:
        return 2
    return (m**4 + 2*m**3 + m*m + 4*m + 4) // 2 - j_statistic(p)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("permutation", nargs="*", type=int,
                        help="Entries separated by spaces, e.g. 2 4 1 5 3")
    args = parser.parse_args()
    p = tuple(args.permutation)
    print({"permutation": p, "j": j_statistic(p), "g2": g2(p),
           "primitive_parameters": primitive_parameters(p)})
