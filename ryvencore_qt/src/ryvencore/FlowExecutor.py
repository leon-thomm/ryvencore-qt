

class DataFlowOptimized:
    """
    A special flow executor with implements some node functions to optimise flow execution.
    Whenever a new execution is invoked somewhere (some node or output is updated), it
    analyses the graph and create a few data structure to reverse engineer how many input
    updates every node possibly receives in this execution. A node's outputs are then only
    propagated when no input can still received new data from a predecessor node.
    Therefore, while a node gets updated every time an input receives some data,
    every OUTPUT is only updated ONCE.
    This implies that every connection is activated at most once in an execution.
    This can result in asymptotic speedup in large data flows compared to normal data flow
    execution where any two executed branches which merge again in the future result in two
    complete executions of everything that comes after the merge, which quickly produces
    performance issues.
    """

    def __init__(self, flow):
        self.flow = flow
        self.output_updated = {}
        self.waiting_count = {}
        self.num_conns_from_predecessors = None
        self.last_execution_root = None     # for reuse when a same execution is invoked many times consecutively
        self.execution_root = None          # can be Node or NodeOutput
        self.execution_root_node = None     # the updated Node or the updated NodeOutput's Node
        self.flow_changed = True

    def node_output_added(self, out):
        self.output_updated[out] = False

    def node_output_removed(self, out):
        del self.output_updated[out]

    def start_execution(self, root_node=None, root_output=None):

        # reset cached output values
        self.output_updated = {}
        for n in self.flow.nodes:
            for out in n.outputs:
                self.output_updated[out] = False

        if root_node is not None:
            self.execution_root = root_node
            self.execution_root_node = root_node
            self.waiting_count = self.generate_waiting_count(root_node=root_node)

        elif root_output is not None:
            self.execution_root = root_output
            self.execution_root_node = root_output.node
            self.waiting_count = self.generate_waiting_count(root_output=root_output)

    def stop_execution(self):
        self.execution_root_node = None
        self.last_execution_root = self.execution_root
        self.execution_root = None

    def generate_waiting_count(self, root_node=None, root_output=None):
        if not self.flow_changed and self.execution_root is self.last_execution_root:
            return self.num_conns_from_predecessors.copy()
        self.flow_changed = False

        nodes = self.flow.nodes
        node_successors = self.flow.node_successors

        # DP TABLE
        self.num_conns_from_predecessors = {
            n: 0
            for n in nodes
        }

        successors = set()
        visited = {
            n: False
            for n in nodes
        }

        # BC
        if root_node is not None:
            successors.add(root_node)
        elif root_output is not None:
            for c in root_output.connections:
                connected_node = c.inp.node
                self.num_conns_from_predecessors[connected_node] += 1
                successors.add(connected_node)

        # ITERATION
        while len(successors) > 0:
            n = successors.pop()
            if visited[n]:
                continue

            for s in node_successors[n]:
                self.num_conns_from_predecessors[s] += 1
                successors.add(s)
            visited[n] = True

        return self.num_conns_from_predecessors.copy()

    def invoke_node_update_event(self, node, inp):
        try:
            node.update_event(inp)
        except Exception:
            pass


    # ----------------------------------------------------------

    # NODE FUNCTIONS

    # Node.update() =>
    def update_node(self, node, inp=-1):
        if self.execution_root_node is None:  # execution starter!
            self.start_execution(root_node=node)
            self.invoke_node_update_event(node, inp)
            self.propagate_outputs(node)
            self.stop_execution()
        else:
            self.invoke_node_update_event(node, inp)

    # Node.set_output_val() =>
    def set_output_val(self, node, index, val):
        out = node.outputs[index]

        if self.execution_root_node is None:  # execution starter!
            self.start_execution(root_output=out)

            out.val = val
            self.output_updated[out] = True
            self.propagate_output(out)

            self.stop_execution()

        else:
            out.val = val
            self.output_updated[out] = True

    # Node.exec_output() =>
    def exec_output(self, node, index):
        out = node.outputs[index]

        if self.execution_root_node is None:  # execution starter!
            self.start_execution(root_output=out)

            self.output_updated[out] = True
            self.propagate_output(out)

            self.stop_execution()

        else:
            self.output_updated[out] = True

    # ----------------------------------------------------------

    def decrease_wait(self, node):
        """decreases the wait count of the node;
        if the count reaches zero, which means there is no other input waiting for data,
        the output values get propagated"""

        self.waiting_count[node] -= 1
        if self.waiting_count[node] == 0:
            self.propagate_outputs(node)

    def propagate_outputs(self, node):
        """propagates all outputs of node"""

        for out in node.outputs:
            self.propagate_output(out)

    def propagate_output(self, out):
        """pushes an output's value to successors if it has been changed in the execution"""

        if self.output_updated[out]:

            if out.type_ == 'data':         # data output updated
                for c in out.connections:
                    c.activate(out.val)

            else:                           # exec output executed
                for c in out.connections:
                    c.activate()

        # decrease wait count of successors
        for c in out.connections:
            self.decrease_wait(c.inp.node)
