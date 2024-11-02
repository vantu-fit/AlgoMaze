a*:
	python algorithm/ASTAR.py maze/input-01.txt algorithm/a_start_output/output-01.txt

test ucs:
	python algorithm/UCS.py algorithm/input.txt algorithm/UCS_output.txt

test bfs:
	python algorithm/DFS_BFS.py algorithm/input.txt algorithm/BFS_output.txt BFS

test dfs:
	python algorithm/DFS_BFS.py algorithm/input.txt algorithm/DFS_output.txt DFS