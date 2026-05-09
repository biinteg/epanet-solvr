from epyt import epanet
import os

# Create a dummy .inp file
with open("dummy.inp", "w") as f:
    f.write("[TITLE]\n\n[JUNCTIONS]\n1 0 0\n2 10 0\n\n[PIPES]\n1 1 2 1000 100 0\n\n[REPORT]\nSTATUS YES\n")

d = epanet("dummy.inp")
print("Methods in epanet object:")
print([m for m in dir(d) if "LinkNodes" in m])
d.unload()
os.remove("dummy.inp")
