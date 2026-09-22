import math


def circle_area(radius):
    """Return the area of a circle with the given radius."""
    if radius < 0:
        raise ValueError("radius must be non-negative")
    return math.pi * radius ** 2


if __name__ == "__main__":
    print("Hello from my clean environment!")
    print(circle_area(3))