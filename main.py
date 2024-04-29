from Board import Simulation
import sys

s = Simulation()
if len(sys.argv) > 1 and sys.argv[1] == '--playAI':
    s.run(True)
else:
    s.run(False)
