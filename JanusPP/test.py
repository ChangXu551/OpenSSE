abinary = lambda x: "".join(reversed(
    [i + j for i, j in zip(*[["{0:04b}".format(int(c, 16)) for c in reversed("0" + x)][n::2] for n in [1, 0]])]))

print(abinary('79d6'))