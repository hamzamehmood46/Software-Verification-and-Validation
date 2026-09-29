from graphviz import Digraph

dot = Digraph()


dot.node('A', 'nterms = 10')
dot.node('B', 'Check nterms <= 0')
dot.node('C', 'Loop variable i')
dot.node('D', 'Call recur_fibo(i)')
dot.node('E', 'Input n')
dot.node('F', 'Check n <= 1')
dot.node('G', 'Return n')
dot.node('H', 'n - 1')
dot.node('I', 'recur_fibo(n-1)')
dot.node('J', 'n - 2')
dot.node('K', 'recur_fibo(n-2)')
dot.node('L', 'Add results')
dot.node('M', 'Return result')
dot.node('N', 'Print result')


dot.edge('A', 'B')
dot.edge('A', 'C')
dot.edge('C', 'D')
dot.edge('D', 'E')
dot.edge('E', 'F')
dot.edge('F', 'G', label='True')
dot.edge('E', 'H', label='False')
dot.edge('H', 'I')
dot.edge('E', 'J')
dot.edge('J', 'K')
dot.edge('I', 'L')
dot.edge('K', 'L')
dot.edge('L', 'M')
dot.edge('G', 'N')
dot.edge('M', 'N')


dot.render('dfg', format='png', cleanup=True)

print("DFG created!")