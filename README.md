# MineSolver

This is a solution for the Decode Demcon challenge #3.
The solver class can be instantiated with a field settings dict.
On the instance, the newGame method will create a MineField and output a list of x,y locations (NamedTuple).





## Authors

- [@Matthijsvs]()


## Usage/Examples

```python
from main import Solver

#play 10 games
s = Solver(BEGINNER_FIELD)
	for i in range(10):
		print(s.newGame())

Solver(EXPERT_FIELD).newGame()
#etc
```


