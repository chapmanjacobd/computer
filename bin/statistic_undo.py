def p_inc(L, l, R, r):
    ratio = (l / L) / (r / R)
    return 100 * (ratio - 1)


def search(lower, upper, tot_students):
    for L in range(1, tot_students):
        R = tot_students - L
        for l in range(1, L):
            for r in range(1, R):
                if lower <= p_inc(L, l, R, r) < upper:
                    print(L, l, R, r)


search(5.676635, 5.67665, 446)

search(5.67655, 5.6767, 446)
