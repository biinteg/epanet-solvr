from epyt import epanet
import os

def list_methods():
    inp_path = os.path.join(os.path.dirname(__file__), 'test.inp')
    d = epanet(inp_path)
    print("Methods in epyt.epanet:")
    for method in sorted(dir(d)):
        if not method.startswith('_'):
            print(method)
    d.unload()

if __name__ == "__main__":
    list_methods()
