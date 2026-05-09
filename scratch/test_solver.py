import sys
import os
# Add the root directory to sys.path to import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modules.hardy_cross import run_hardy_cross

def test_hardy_cross():
    inp_path = os.path.join(os.path.dirname(__file__), 'test.inp')
    print(f"Testing Hardy Cross with {inp_path}...")
    try:
        result = run_hardy_cross(inp_path)
        print("Success!")
        print(f"Iterations: {result['iterations']}")
        print(f"Converged: {result['converged']}")
        print(f"Loops Found: {result['loops_found']}")
        print("\nFinal Results:")
        print(result['final_df'])
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_hardy_cross()
