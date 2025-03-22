import math
def check(n):
    if n == 2:
        return True
    else:
        for i in range(2, math.sqrt(n)):
            if n % i == 0:
                return False
    return True
