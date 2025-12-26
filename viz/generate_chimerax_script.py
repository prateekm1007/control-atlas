import csv, sys

edges = sys.argv[1]
outfile = sys.argv[2]

with open(outfile, "w") as f:
    f.write("lighting soft\n")
    f.write("surface transparency 80 color #444444\n")

    with open(edges) as e:
        for r in csv.reader(e):
            i, j, v = int(r[0]), int(r[1]), float(r[2])
            radius = max(0.2, v * 0.5)
            f.write(
                f"shape cylinder start #1:{i}@CA end #1:{j}@CA "
                f"radius {radius:.2f} color #ff0033 caps true\n"
            )
