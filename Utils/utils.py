def is_light_square(t: tuple[int,int]) -> bool:
    return (t[0]+t[1]) % 2 == 0

def in_bound(x: int, y: int) -> bool:
        """
        helper function to check if a coordinate in valid
        """
        return x >= 0 and y >= 0 and x <= 7 and y <= 7
