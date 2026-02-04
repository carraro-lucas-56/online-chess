def is_light_square(t: tuple[int,int]) -> bool:
    return (t[0]+t[1]) % 2 == 0

def in_bound(x: int, y: int) -> bool:
        """
        helper function to check if a coordinate in valid
        """
        return x >= 0 and y >= 0 and x <= 7 and y <= 7

def flip_and_negate(pst):
    flipped = []
    for r in range(8):
        flipped.extend(pst[(7 - r) * 8 : (8 - r) * 8])
    return [-v for v in flipped]
