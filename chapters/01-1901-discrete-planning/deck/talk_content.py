# -*- coding: utf-8 -*-
"""Single source of truth for the Discrete Planning lecture deck: slide
content + speaker notes, curated from DiscretePlanning.ipynb.

Long tutorial-value code (BFS/DFS/Dijkstra/A*) is kept as short, trimmed
snippets. Long/low-tutorial-value code (Maze plotting/animation utilities,
PItem/PriorityQueueUpdatable boilerplate) is left out of slides and pointed
at via COLAB_URL instead. "demo" slides mark points to switch from slides
to the live notebook.
"""

import os
MEDIA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "imgs")

COLAB_URL = ("https://colab.research.google.com/github/wecacuee/ECE417-F26-Mobile-Robots/"
             "blob/main/chapters/01-1901-discrete-planning/exports-DiscretePlanningColab.ipynb")

SLIDES = [

dict(
    type="title",
    title="Discrete Planning in Robotics",
    subtitle="Graphs, BFS, DFS, Dijkstra's algorithm, and A*",
    footer="ECE 417 — Mobile Robots  ·  Vikas Dhiman  ·  University of Maine",
    notes="""Today we're covering discrete planning: how to turn a robot's
motion-planning problem into a graph search problem, and the four classic
search algorithms — breadth-first search, depth-first search, Dijkstra's
algorithm, and A* — that we can run on that graph. We'll also cover the
computational-complexity tools (Big-O notation, heaps) needed to reason
about how fast these algorithms are, and finish with how continuous
(non-grid) spaces get converted into graphs, as a bridge to RRT next."""
),

dict(
    type="content",
    title="Required readings",
    bullets=[
        "[Ch 7 and 23, Carmen's Intro to Algorithms](https://drive.google.com/file/d/1XoJtB9LVAn7zq5RulNDWCUQv4eOtppoq/view?usp=sharing)",
        "[Breadth-first search and its uses — Khan Academy](https://www.khanacademy.org/computing/computer-science/algorithms/breadth-first-search/a/breadth-first-search-and-its-uses)",
        "[PythonRobotics/dijkstra.py](https://github.com/AtsushiSakai/PythonRobotics/tree/master#path-planning)",
        "[Discrete Planning — LaValle](https://lavalle.pl/planning/node35.html)",
        "[3.5.2, Russell & Norvig: Artificial Intelligence](https://drive.google.com/file/d/1rOimmdudiyqI98VkkqDEHoclJUMCxJi0/view?usp=sharing)",
    ],
    notes="""These are the assigned readings backing today's lecture — Carmen's
chapters on graphs and heaps, a Khan Academy primer on BFS, the PythonRobotics
reference implementation of Dijkstra, LaValle's planning notes, and the A*
section of Russell & Norvig. Skim these before the next class."""
),

dict(
    type="image_full",
    title="A planning problem, visually",
    img=f"{MEDIA}/maze.png",
    caption="Find a path from the start to the goal without crossing a wall — the running example for today.",
    notes="""Here's the running example for the whole lecture: a maze. The
robot has to find a path from a start cell to a goal cell without passing
through a wall. Every algorithm we cover today — BFS, DFS, Dijkstra, A* —
will be demonstrated on a maze just like this one, once we show how to turn
a maze into a graph."""
),

dict(
    type="content",
    title="Abstraction of a planning problem",
    bullets=[
        "State s_t ∈ S — everything needed to predict the future (Markov property), e.g. (x, y), or (x, y, θ) if orientation matters",
        "Action space U(s) — the choices available at a state, e.g. up/down/left/right = {(0,-1), (0,1), (1,0), (-1,0)}",
        "Transition function s_{t+1} = f(s_t, u_t) — e.g. s_{t+1} = s_t + u_t. Stochastic version: P(s_{t+1} | s_t, u_t)",
        "Initial state s_I ∈ S, goal states s_G ⊆ S",
    ],
    notes="""A planning problem is defined by five pieces. First, the state
space: whatever property of the robot changes over time and captures
everything needed for future planning — the Markov property means the state
alone is enough, we don't need the full history. A 2D grid position (x, y) is
the simplest example; if orientation matters — a car that has to turn before
it can move sideways — the state becomes (x, y, theta). Something worth
thinking about: what would the state be for a drone or a plane that can fly
and rotate in full 3D? Second, the action space per state, the choices the
robot can make — for grid movement that's up/down/left/right. Third, the
state transition function, how an action changes the state — for grid
movement that's just vector addition, s_{t+1} = s_t + u_t; when the system is
stochastic this becomes a transition probability P(s_{t+1} | s_t, u_t), which
in control theory is called the system dynamics. Fourth and fifth, the
initial state and the set of goal states."""
),

dict(
    type="content",
    title="A Graph",
    bullets=[
        "A graph G = (V, E): a set of vertices V and a set of edges E",
        "Each edge e = (v_s, v_e) has a start vertex v_s = start(e) and an end vertex v_e = end(e)",
        "Planning → graph: vertices are states (V = S); the action space at a state is its outgoing edges; the transition function is just \"follow the edge to its other end\"",
    ],
    notes="""A graph is a set of vertices V and a set of edges E, where each
edge is an ordered pair of a start vertex and an end vertex. Any discrete
planning problem converts into a graph search problem this way: the state
space becomes the vertex set, V = S. The action space at a state becomes the
set of edges leaving that vertex — U(s_t) is exactly the edges (s_t, s_j) in
E. And the transition function becomes trivial: the next state is just
whatever vertex is at the other end of the edge you took, s_{t+1} =
end(u_t) where s_t = start(u_t). Once you see planning this way, "find a
plan" becomes "find a path through a graph" — which is exactly what BFS,
DFS, Dijkstra, and A* do."""
),

dict(
    type="code",
    title="Representations of graphs",
    kicker="Chapter 23, Carmen, Intro to Algorithms (1990)",
    bullets=[
        "Adjacency list — a dict mapping each node to its neighbors (most common; what we use below)",
        "Adjacency matrix — an |V|×|V| 0/1 (or weighted) array; simple, but wastes memory on sparse graphs",
        "Edge list — a flat list of (start, end) pairs; compact, but slow to query a node's neighbors",
    ],
    code="""G_adjacency_list = {
    1: [2, 5],           # node: list of neighbors
    2: [1, 5, 3, 4],
    3: [2, 4],
    4: [2, 5, 3],
    5: [4, 1, 2],
}

G_adjacency_matrix = np.array([
    [0, 1, 0, 0, 1],
    [1, 0, 1, 1, 1],
    [0, 1, 0, 1, 0],
    [0, 1, 1, 0, 1],
    [1, 1, 0, 1, 0],
])

G_edge_list = [(1, 2), (1, 5), (2, 1), (2, 5), ...]""",
    img=f"{MEDIA}/undirected-graph-rep.png",
    colab_note="Directed-graph version (edges only go one way) — same three representations, in the notebook.",
    notes="""Three standard ways to represent a graph in code, all equivalent.
An adjacency list — a dictionary from each node to the list of its neighbors
— is what we'll use for the rest of the lecture; Python lists here are
arrays, not linked lists, so lookups are O(1) by key but O(n) to scan. An
adjacency matrix is an n-by-n array where a 1 at (i, j) means an edge from i
to j; simple, and easy to check "is there an edge?" in O(1), but wastes
O(n^2) memory on a sparse graph. An edge list is just the flat list of
(start, end) pairs; compact to store, but you have to scan the whole list to
find one node's neighbors. Directed graphs use exactly these same three
representations — the only difference is edges aren't assumed symmetric; the
adjacency-list code for that is a two-line change and is in the notebook."""
),

dict(
    type="section",
    title="Graph Search Algorithms",
    subtitle="Breadth-first search & Depth-first search",
    notes="""Now that we can represent a graph, let's search it. We'll start
with the two simplest, uninformed search strategies: breadth-first search and
depth-first search. They differ in exactly one thing — the data structure
used for the frontier."""
),

dict(
    type="content_img",
    title="Breadth-first search (BFS)",
    img=f"{MEDIA}/bfs-step-by-step.png",
    bullets=[
        "“BFS expands the frontier uniformly across its breadth” — Carmen, Intro to Algorithms (1990)",
        "Frontier = FIFO queue: the vertex that has been waiting longest gets processed next",
        "Three vertex states: unseen (white), frontier (gray), processed (black)",
        "dist[u] = dist[m] + 1 — distance grows by exactly one hop per frontier layer",
    ],
    notes="""Breadth-first search keeps track of three kinds of vertices:
unseen (white, dist = infinity), frontier (gray, currently waiting to be
processed) and processed/seen (black, already expanded). The frontier is a
First-In-First-Out queue — whichever vertex has been in the frontier longest
gets processed next. The algorithm: while the frontier isn't empty, pop the
oldest vertex m, mark it processed, then for every unseen neighbor u of m,
mark it as frontier, push it, and set dist[u] = dist[m] + 1. Because the
frontier is FIFO, BFS explores the graph in layers — everything at distance k
from the start is fully processed before anything at distance k+1 is even
looked at. That's exactly why BFS finds the *shortest path by hop count* on
an unweighted graph."""
),

dict(
    type="code",
    title="BFS implementation",
    code="""def bfs(graph, start):
    seen = {start}           # seen = frontier + processed
    frontier = Queue()       # FIFO -> level-by-level order
    dist = {start: 0}
    frontier.put(start)
    search_order = []

    while not frontier.empty():
        m = frontier.get()   # oldest addition, first out
        search_order.append(m)
        for u in graph.get(m, []):
            if u not in seen:
                seen.add(u)
                frontier.put(u)
                dist[u] = dist[m] + 1
    return search_order, dist""",
    colab_note="Full version with a debug trace: notebook cells 21-22.",
    notes="""This is the whole algorithm. seen tracks anything already in the
frontier or already processed, so we never revisit a vertex. frontier is a
FIFO Queue — that's the one line that makes this breadth-first rather than
depth-first. Every neighbor discovered for the first time gets a distance one
more than its parent. On the six-node example graph in the notebook, this
produces the search order ['s', 'w', 'r', 't', 'x', 'v', 'u', 'y'] with
distances growing 0, 1, 1, 2, 2, 2, 3, 3 — visibly layer by layer."""
),

dict(
    type="content_img",
    title="Depth-first search (DFS)",
    img=f"{MEDIA}/dfs-step-by-step.png",
    bullets=[
        "Frontier = LIFO stack: the most recently discovered vertex is explored next",
        "Dives down one branch as deep as possible before backtracking",
        "Much simpler to write recursively — the call stack *is* the LIFO frontier",
    ],
    notes="""Depth-first search is identical to BFS except for one line: the
frontier is a LIFO stack instead of a FIFO queue. That single change means
the most recently discovered vertex is explored next, so the search dives
down one path as far as it can before backtracking — very different
exploration shape from BFS's uniform layer-by-layer spread. DFS is also much
more natural to write recursively, since the function call stack already
behaves like a LIFO frontier for free — see dfs_recursive in the notebook,
which is about half the line count of the iterative version."""
),

dict(
    type="code",
    title="DFS implementation",
    code="""def dfs(graph, start):
    seen = {start}
    frontier = LifoQueue()   # LIFO -> depth-first order
    frontier.put(start)
    search_order = []

    while not frontier.empty():
        m = frontier.get()   # most recent addition, first out
        search_order.append(m)
        for u in graph.get(m, []):
            if u not in seen:
                seen.add(u)
                frontier.put(u)
    return search_order""",
    colab_note="Recursive version (dfs_recursive): notebook cells 27-29.",
    notes="""Same shape as bfs() — only the frontier's data structure changed,
from Queue to LifoQueue. On the same six-node graph, DFS produces the order
['s', 'r', 'v', 'w', 'x', 'y', 't', 'u'] — compare that to BFS's
['s', 'w', 'r', 't', 'x', 'v', 'u', 'y'] on the exact same graph, same start
node. Same algorithm skeleton, very different traversal."""
),

dict(
    type="demo",
    title="Live demo — BFS vs. DFS search order",
    bullets=[
        "Run bfs(graph, 's', debug=True) and dfs(graph, 's', debug=True) on the same 6-node graph",
        "Watch the frontier (printed each step) grow breadth-first vs. depth-first",
        "Compare the two final search orders side by side",
    ],
    colab_url=COLAB_URL,
    notes="""Switch to the notebook now (cells 21-29). Run both searches with
debug=True so the frontier prints at every step. Point out how BFS's frontier
grows wide (multiple siblings queued before any grandchild) while DFS's
frontier stays a thin, deep stack. This is the moment to take questions on
the difference before moving to weighted graphs."""
),

dict(
    type="content",
    title="Search order: BFS vs. DFS vs. Dijkstra",
    bullets=[
        "BFS — FIFO frontier → explores in order of hop count (levels)",
        "DFS — LIFO frontier → explores in order of discovery depth",
        "Dijkstra — priority-queue frontier → explores in order of path *cost*, not hop count or depth",
        "On an unweighted graph (every edge cost = 1), Dijkstra's order matches BFS exactly",
    ],
    notes="""The three algorithms are really one algorithm skeleton with
three different frontier data structures: FIFO for BFS, LIFO for DFS, and a
min-priority-queue keyed on path cost for Dijkstra. That reframing is the
single most important idea to take away from today — once you see it, A*
next is just "Dijkstra's priority queue with an extra term added to the
key". Also worth noting: if every edge has cost 1, Dijkstra reduces to
exactly BFS, since path cost and hop count become the same thing."""
),

dict(
    type="content",
    title="From a maze to a graph",
    bullets=[
        "Every free (non-wall) cell becomes a vertex",
        "4-connected: up/down/left/right neighbors become edges (cost 1 each)",
        "8-connected: add the four diagonal neighbors (cost √2 each)",
        "Once the maze is a graph, BFS / Dijkstra / A* all run on it unchanged",
    ],
    notes="""To run any of today's algorithms on the maze image from the
start of the lecture, we don't need new algorithms — we just need to define
what "graph" means for a maze. Each open cell is a vertex; a cell is
connected to its free neighbors. The notebook's Maze class implements this
as a get(node) method that returns the free neighbors of a cell, so it can
be dropped straight into the same bfs()/dijkstra()/astar() functions we just
wrote — no changes needed to the search algorithms themselves. That
maze-to-graph plumbing (Maze, plotting, animation) is utility code, not
algorithmic content — it's in the notebook/Colab if you want to read it."""
),

dict(
    type="section",
    title="Dijkstra's Algorithm",
    subtitle="Shortest paths on a weighted graph",
    notes="""BFS and DFS both assume every edge is equally costly. Dijkstra's
algorithm removes that assumption — edges can have arbitrary non-negative
weights, and the algorithm still finds the minimum-cost path."""
),

dict(
    type="content_img",
    title="Dijkstra's algorithm",
    img=f"{MEDIA}/dijkstra-step-by-step.png",
    bullets=[
        "Same skeleton as BFS, but the frontier is a PriorityQueue keyed on path cost, not arrival order",
        "“Relaxation”: whenever a shorter path to a neighbor is found, update its distance",
        "Finds the minimum-cost path in a graph with non-negative edge weights",
    ],
    notes="""Dijkstra's algorithm looks almost identical to BFS, with one
change: the frontier is a priority queue ordered by cumulative path cost
(node2dist), not a FIFO queue ordered by discovery time. Every time we look
at an edge to a neighbor, we check whether going through the current node
gives a cheaper path than whatever we'd previously found — this check-and-
update step is called relaxation. As long as edge weights are non-negative,
this greedy strategy is provably optimal: the first time we pop a node off
the priority queue, we've found its true shortest distance."""
),

dict(
    type="code",
    title="Dijkstra implementation",
    code="""def dijkstra(graph, start, goal):
    seen = {start}
    frontier = PriorityQueue()      # ordered by dist, not arrival
    frontier.put(PItem(0, start))
    node2parent = {start: None}
    node2dist = {start: 0}

    while not frontier.empty():
        m = frontier.get().node
        if m == goal:
            return True, node2parent, node2dist

        for neighbor, edge_cost in graph.get(m, []):
            new_dist = node2dist[m] + edge_cost
            if neighbor not in seen or new_dist < node2dist[neighbor]:
                seen.add(neighbor)                # relax
                node2parent[neighbor] = m
                node2dist[neighbor] = new_dist
                frontier.put(PItem(new_dist, neighbor))
    return False, {}, node2dist""",
    colab_note="Full version (in-place priority-queue updates via PItem/PriorityQueueUpdatable): notebook cells 42-43.",
    notes="""This is the pedagogical core of Dijkstra, simplified slightly
from the notebook version for slide space — the notebook's version updates a
stale priority-queue entry in place when a shorter path is relaxed after the
node is already queued (Python's stdlib PriorityQueue can't do that
directly, so it uses a small PriorityQueueUpdatable helper). The idea is
identical either way: pop the cheapest frontier node, and relax every
outgoing edge."""
),

dict(
    type="content_img",
    title="Dijkstra on an 8-connected maze",
    img=f"{MEDIA}/dijkstra-8conn-small-demo.png",
    bullets=[
        "Diagonal moves cost √2 instead of 1 — Dijkstra correctly prefers a diagonal shortcut over two orthogonal steps",
        "Same dijkstra() function as the graph example — only graph.get() changed, to return 8 weighted neighbors instead of a fixed dict",
    ],
    notes="""Here Dijkstra runs on the maze from the start of the lecture,
using an 8-connected neighborhood (MazeD/Maze8 in the notebook) so diagonal
moves are allowed at cost sqrt(2). Nothing about dijkstra() itself changed —
only what graph.get(node) returns. This is the payoff of the "planning is
graph search" abstraction: the same four-line relaxation loop works on a
hand-drawn 6-node graph and on a 40-row image-based maze."""
),

dict(
    type="demo",
    title="Live demo — Dijkstra on a big maze",
    img=f"{MEDIA}/dijkstra-path-result.png",
    bullets=[
        "61×39 maze, 8-connected, start and goal on opposite sides",
        "Watch the frontier grow outward as an expanding cost “wavefront”",
        "Trace the final shortest path back through node2parent",
    ],
    colab_url=COLAB_URL,
    notes="""Switch to the notebook (cells 44-48) for the full-size maze
demo. The animation shows the frontier expanding roughly circularly (by
cost, not by hop count) until it reaches the goal — a good visual for why
Dijkstra explores in every direction equally, which motivates the next
section: A* uses a heuristic to bias that expansion toward the goal instead
of wasting time exploring away from it."""
),

dict(
    type="section",
    title="Computational Complexity",
    subtitle="Big-O notation, and how fast BFS and Dijkstra really are",
    notes="""Before A*, a short detour: how do we talk precisely about how
fast these algorithms are? That's Big-O (and Theta and Omega) notation, and
we'll use it to derive the running time of BFS and Dijkstra."""
),

dict(
    type="content_img",
    title="Asymptotic notation",
    img=f"{MEDIA}/bigO-notation.png",
    bullets=[
        "Θ(g(n)) — tight bound: f(n) is sandwiched between c1·g(n) and c2·g(n) for large n",
        "O(g(n)) — upper bound: f(n) grows no faster than c·g(n)",
        "Ω(g(n)) — lower bound: f(n) grows at least as fast as c·g(n)",
    ],
    notes="""Three related but distinct notations, from Chapter 23. Big-Theta
is a two-sided, tight bound — f(n) is sandwiched between two constant
multiples of g(n) for all sufficiently large n. Big-O is one-sided: an upper
bound only, f(n) grows no faster than g(n) up to a constant factor. Big-Omega
is the mirror image, a lower bound only. In casual usage people often say
"O(n)" when they really mean the tighter "Θ(n)" — worth being precise about
which one you actually mean when analyzing an algorithm."""
),

dict(
    type="code",
    title="Complexity of BFS",
    code="""def bfs_barebones(graph, start):
    seen = {start}                          # O(1)
    frontier = Queue()                      # O(1)
    frontier.put(start)                     # O(1)

    while not frontier.empty():             # O(|V|) iterations
        m = frontier.get()                  # O(|V| * 1)
        for neighbor in graph.get(m, []):   # O(|V| * |E|/|V|) = O(|E|)
            if neighbor not in seen:        # O(|E| * 1)
                seen.add(neighbor)          # O(|E| * 1)
                frontier.put(neighbor)      # O(|E| * 1)

# Total: O(|V| + |E|)""",
    notes="""Line-by-line: the while loop runs once per vertex, O(|V|)
iterations. The inner for-loop, summed *across all iterations of the outer
loop*, touches each edge at most once — so summed over the whole run it's
O(|E|), not O(|V| * |E|). Set membership/insertion are O(1) on average. Add
it up: O(|V| + |E|) total — linear in the size of the graph, which is why
BFS is considered a very efficient algorithm."""
),

dict(
    type="code",
    title="Complexity of Dijkstra",
    code="""def dijkstra_barebones(graph, start):
    seen = {start}
    frontier = PriorityQueue()
    frontier.put(PItem(0, start))
    node2dist = {start: 0}

    while not frontier.empty():
        m = frontier.get()                       # O(|V| log|V|) total (heap)
        for neighbor, w in graph.get(m, []):      # O(|E|) total
            if neighbor not in seen:
                seen.add(neighbor)
                frontier.put(PItem(node2dist[m]+w, neighbor))  # O(|E| log|V|)
                node2dist[neighbor] = node2dist[m] + w

# Total: O(|V| log|V| + |E| log|V|) = O(|E| log|V|) with a binary heap
# O(|V| log|V| + |E|) with a Fibonacci heap""",
    notes="""Same skeleton as BFS, but now every priority-queue get() and
put() costs O(log|V|) instead of O(1), because a binary heap has to sift the
new smallest element to the top. Summed over the run: O(|V| log|V|) for the
gets, O(|E| log|V|) for the puts — combined, O(|E| log|V|), since |E| >=
|V|-1 for a connected graph. A Fibonacci heap can do the decrease-key
operation in amortized O(1), improving this to O(|V| log|V| + |E|) — better
for very dense graphs, but rarely used in practice because of a large
constant factor."""
),

dict(
    type="content_img",
    title="PriorityQueue (Heaps)",
    kicker="Chapter 7, Carmen, Intro to Algorithms (1990)",
    img=f"{MEDIA}/heap.png",
    bullets=[
        "H[Parent(i)] ≥ H[i] — the max-heap property",
        "Parent(i) = ceil(i/2), LeftChild(i) = 2i, RightChild(i) = 2i+1",
        "A binary heap gives O(log n) insert / extract-max, and O(1) peek",
    ],
    notes="""A heap is a nearly-complete binary tree stored flat in an array,
with the heap property: every parent is at least as large as its children
(for a max-heap; flip the inequality for a min-heap, which is what a
priority queue keyed on distance actually needs). The parent/child index
arithmetic — parent = ceil(i/2), children = 2i and 2i+1 — is what lets a heap
live in a plain array with no pointers. This is exactly the data structure
Python's queue.PriorityQueue uses internally, and it's why priority-queue
operations cost O(log n) instead of O(n)."""
),

dict(
    type="gallery",
    title="Heapify → Insert → Extract-Max",
    kicker="Chapter 7, Carmen, Intro to Algorithms (1990)",
    images=[
        (f"{MEDIA}/heapify.png", "Heapify: sift a node down until the heap property holds"),
        (f"{MEDIA}/heapify-pseudocode.png", "Heapify — pseudocode"),
        (f"{MEDIA}/heap-insert.png", "Insert: append, then sift up"),
        (f"{MEDIA}/heap-extract-max.png", "Extract-max: swap root with last, pop, heapify"),
    ],
    notes="""The three operations that keep a heap valid. Heapify repairs a
single violation by sifting a node down past its larger child, recursively,
until the property holds again — that's the O(log n) at the core of every
other operation. Insert appends the new element at the end of the array
(keeping it a complete tree), then sifts it *up* past any smaller parent.
Extract-max swaps the root with the last element, removes what is now the
last element (the old max), and heapifies from the root to restore the
property. Every one of these does at most O(log n) swaps, since a heap's
height is O(log n) by construction."""
),

dict(
    type="image_full",
    title="Heap runtimes",
    kicker="Chapter 7, Carmen, Intro to Algorithms (1990)",
    img=f"{MEDIA}/heap-runtimes.png",
    caption="Build-heap is O(n), not O(n log n) — the sum telescopes because most nodes are near the bottom, already almost-valid.",
    notes="""A summary table of heap operation costs. The one that surprises
people: building a heap from n arbitrary elements is O(n), not O(n log n) —
even though each heapify call is O(log n) and you might call it n times, the
sum telescopes because the vast majority of nodes are near the bottom of the
tree, where a heapify call only costs O(1) or O(2), not O(log n). Insert and
extract-max/extract-min are each O(log n); peek at the min/max is O(1)."""
),

dict(
    type="section",
    title="A* Algorithm",
    subtitle="Dijkstra + a heuristic",
    notes="""Required reading: section 3.5.2 of Russell & Norvig. A* is the
single most important algorithm in this lecture for robotics — it's the one
you'll actually reach for in a real planner."""
),

dict(
    type="content_img",
    title="A* search",
    kicker="Russell & Norvig, Artificial Intelligence, §3.5.2 — Romania map figure",
    img=f"{MEDIA}/romania-nodes.png",
    bullets=[
        "Priority = g(n) + h(n): cost-so-far, plus a heuristic estimate of cost-to-goal",
        "Identical to Dijkstra, except the priority-queue key gets the extra + h(n) term",
        "The heuristic biases the search toward the goal instead of expanding equally in every direction",
    ],
    notes="""A* is Dijkstra with one addition: instead of ordering the
frontier purely by cost-so-far g(n), it orders by g(n) + h(n), where h(n) is
a heuristic estimate of the remaining cost to the goal. The classic textbook
example (Russell & Norvig) is finding a route across this map of Romania,
using straight-line distance to Bucharest as h(n). The heuristic doesn't
change correctness (under conditions we'll cover next) — it changes *which
order* nodes get explored in, biasing the search toward the goal instead of
Dijkstra's uniform circular expansion."""
),

dict(
    type="code",
    title="A* implementation",
    code="""def astar(graph, h, start, goal):
    seen = {start}
    frontier = PriorityQueue()          # ordered by g(n) + h(n)
    frontier.put(PItem(h(start, goal), start))
    node2parent = {start: None}
    node2dist = {start: 0}              # g(n): cost-so-far

    while not frontier.empty():
        m = frontier.get().node
        if m == goal:
            return True, node2parent, node2dist

        for neighbor, edge_cost in graph.get(m, []):
            new_dist = node2dist[m] + edge_cost
            if neighbor not in seen or new_dist < node2dist[neighbor]:
                seen.add(neighbor)
                node2parent[neighbor] = m
                node2dist[neighbor] = new_dist
                priority = new_dist + h(neighbor, goal)  # <- only diff vs. Dijkstra
                frontier.put(PItem(priority, neighbor))
    return False, {}, node2dist""",
    colab_note="Full version + Euclidean heuristic: notebook cells 64-65.",
    notes="""Diff this against the dijkstra() slide from earlier — every line
is identical except the priority put into the frontier gets + h(neighbor,
goal) added. That's the entire algorithmic difference between Dijkstra and
A*. The heuristic used in the notebook is Euclidean distance to the goal,
optionally scaled: euclidean_heurist_dist(node, goal, scale)."""
),

dict(
    type="content",
    title="Admissibility and consistency of h(n)",
    bullets=[
        "Admissible: h(n) never overestimates the true cost to the goal",
        "Consistent (triangle inequality): h(s_t) ≤ c(s_t, s_{t+1}) + h(s_{t+1})",
        "Consistent ⟹ admissible; A* with a consistent heuristic is guaranteed to find the optimal path",
    ],
    notes="""Two conditions on the heuristic, from weakest to strongest. A
heuristic is admissible if it never overestimates the true remaining cost —
this alone is enough to guarantee A* finds an optimal path when a node is
first *expanded* off the goal, but with re-expansions possible. A heuristic
is consistent if it satisfies a triangle-inequality-like condition: the
estimated cost from a state is never more than one edge's real cost plus the
estimate from the state on the other side of that edge. Consistency is
strictly stronger than admissibility, and it's the condition that gives you
the clean guarantee we rely on in practice: the first time A* pops a node off
the frontier, its distance is already final, exactly like Dijkstra."""
),

dict(
    type="demo",
    title="Live demo — A* with different heuristic weights",
    img=f"{MEDIA}/astar-demo-euclidean.png",
    bullets=[
        "scale = 0  →  h(n) = 0 everywhere  →  A* becomes exactly Dijkstra (circular expansion)",
        "scale = 0.1  →  weak heuristic  →  mild bias toward the goal",
        "scale = 1.0  →  full Euclidean distance  →  narrow, goal-directed search cone",
        "Compare how many nodes each setting expands before reaching the goal",
    ],
    colab_url=COLAB_URL,
    notes="""Switch to the notebook (cells 66-71) — it runs A* on the same
maze three times with heuristic scale 0, 0.1, and 1.0, so you can watch the
explored region (shown in cyan) shrink from Dijkstra's full circle down to a
narrow cone pointed straight at the goal. This is the most convincing
"why does A* matter" demo in the whole lecture — leave time for it."""
),

dict(
    type="content",
    title="From continuous space to a graph",
    bullets=[
        "Grids and mazes: cells → vertices, adjacency → edges (what we've been doing all lecture)",
        "Two-step recipe for a general continuous space: (1) build a graph over the space, (2) run A*/Dijkstra on that graph",
    ],
    notes="""Everything so far assumed a grid or a maze, where "turn it into
a graph" was obvious: one vertex per free cell. The general recipe for any
continuous space is the same two steps in the abstract: first turn the
space into a graph somehow, then run exactly the same search algorithms
we've already built on it. The next two slides cover two different ways to
do step one, depending on what you know about the obstacles."""
),

dict(
    type="content_img",
    title="Continuous space → graph: polygon obstacles",
    img=f"{MEDIA}/polygon-obstacles.png",
    bullets=[
        "If obstacles are convex polygons: use their corners as graph vertices",
        "Add an edge between two corners only if the straight segment between them stays entirely outside every obstacle",
        "Convex polygon: any segment between two of its vertices lies entirely inside the polygon",
    ],
    notes="""When obstacles are convex polygons, there's a clean way to build
the graph: the vertices are the polygon corners (plus start and goal), and
you connect two corners with an edge exactly when the straight line segment
between them doesn't pass through any obstacle. This is sometimes called a
visibility graph. It relies on convexity — a polygon where every segment
between two of its own vertices stays inside the polygon — which is what
makes "corners are enough" a valid simplification; you don't need to sample
along the polygon's edges, just its vertices."""
),

dict(
    type="content_img",
    title="Sampling-based planning: RRT",
    img=f"{MEDIA}/RRT-vis.png",
    bullets=[
        "No polygon obstacles? Only a point-in-obstacle test → need a sampling-based method",
        "Rapidly-exploring Random Trees (RRT), RRT*, PRM (Probabilistic Roadmaps)",
        "Build the graph by randomly sampling points and connecting nearby, collision-free ones — next lecture",
    ],
    notes="""Sometimes you don't have an explicit polygon description of the
obstacles — only a black-box collision-check function that tells you if one
point is free or not. Corners-as-vertices doesn't work anymore, since there
are no corners to use. This is exactly the setting for sampling-based
planners: RRT, RRT*, and probabilistic roadmaps (PRM) all build a graph by
randomly sampling points in the free space and connecting nearby ones with a
local collision-checked edge. That's the subject of the next lecture, with
its own notebook (RRT.ipynb / RRTstar.ipynb / PRM.ipynb) in this repo."""
),

dict(
    type="end",
    title="Next up: RRT, RRT*, PRM",
    subtitle="Sampling-based planning for continuous spaces",
    contact="Vikas Dhiman  –  vikas.dhiman@maine.edu  –  ECE 417, University of Maine",
    notes="""That's discrete planning. Next lecture picks up exactly where we
left off — sampling-based planning for spaces without explicit polygon
obstacles, in RRT.ipynb, RRTstar.ipynb, and PRM.ipynb. Questions?"""
),

]
