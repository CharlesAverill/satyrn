# Introduction to Satyrn
Code in Satyrn is executed in "Cells", which are small blocks of code that should perform a few small functions, 
but share variables, functions, imports, etc. Splitting code into these Cells allows users to run lots of "setup" 
cells and then play around with a cell that depends on the setup to function. This prevents users from having to run 
lengthy code over and over again. A similar application is Jupyter's Notebook.


Most code is executed as a list of instructions,
```python
print(1)
print(2)
print(3)
```
However, Satyrn's code execution is different. Code inside of cells still executes normally, but cells are not 
necessarily linked linearly. 

![Graph Example](media/graph.png?raw=true)

In the graph above, cell `root` is what's called a "parent cell", with `a` and `b` being its children, and `c` 
being the child of `b`. This is how Satyrn Graphs, or `.SATX` files, are structured. Satyrn performs a breadth-first 
traversal on its graph to execute the code within the cells. This means that while cell `root` will executet before all 
other cells, cells `a` and `b` will run their code <b>simultaneously</b>. This is particularly useful in situations like data analysis, where lots of data 
must be preprocessed before they can be used. If you have multiple sets of data to preprocess, why not preprocess them 
simultaneously instead of waiting for them to finish 1-by-1?

Satyrn is also a great tool for collaboration. While using the UI, the graph state is shared over your local network 
via a CherryPy WSGI server. This allows machines on your local network to edit the same code you're working on by 
navigating to your IP address in their browser, no Python/Satyrn installations required. If you desire more security, 
the `--hidden` command line argument will hide your Satyrn instance from the network. <b>Use caution when working with 
Satyrn on public networks.</b>