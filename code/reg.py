names = list()
n = set()
with open("resources/full.txt", "rb") as file:
    for line in file.read().decode("utf-8").split("\r\n"):
        mas = line.split(" ")
        if mas[0] not in n:
            n.add(mas[0])
            names.append("{0} {1} {2}".format(mas[0],mas[1],mas[2]))
with open("resources/c2.txt", "rb") as file:
    for line in file.read().decode("utf-8").split("\r\n"):
        mas = line.split(" ")
        if mas[0] not in n:
            n.add(mas[0])
            names.append("{0} {1} {2}".format(mas[0], mas[1], mas[2]))
with open("resources/cities.txt", "w") as ff:
    for line in sorted(names):
        ff.write(line + "\n")
