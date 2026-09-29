from graphviz import Digraph

dot = Digraph()


dot.node('A', 'Start')
dot.node('B', 'nterms = 10')
dot.node('C', 'nterms <= 0 ?')
dot.node('D', 'Print Error')
dot.node('E', 'Print Fibonacci')
dot.node('F', 'Loop i in range(nterms)')
dot.node('G', 'Call recur_fibo(i)')
dot.node('H', 'Print result')
dot.node('I', 'End')


dot.edge('A', 'B')
dot.edge('B', 'C')
dot.edge('C', 'D', label='Yes')
dot.edge('C', 'E', label='No')
dot.edge('D', 'I')
dot.edge('E', 'F')
dot.edge('F', 'G')
dot.edge('G', 'H')
dot.edge('H', 'F')
dot.edge('F', 'I')


dot.render('cfg', format='png', cleanup=True)

print("CFG created!")