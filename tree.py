# Tree structure of indices for generating mirror table
# Good implementation of tree structure, getting less time complexity
from __future__ import annotations

class Tree:
    def __init__(self, root:TreeNode):
        self.root = root
    
    @staticmethod
    def find_mtable_tree(cushion_amt):
        tree = Tree(TreeNode((cushion_amt, cushion_amt), [], 0))
        root = tree.root
        # q is for traversing mtable tree in order
        q = []
        q.append(root)
        
        # appeared_set is for detecting repeated indices
        appeared_indices_set = {root.index}
        
        while len(q) > 0:
            current_node = q.pop(0)
            current_index = current_node.index
            x = current_index[0]
            y = current_index[1]
            current_level = current_node.level

            child_index_list = [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]

            to_be_removed_list = []
            for child_index in child_index_list:
                # print(child_index)
                if child_index in appeared_indices_set:
                    # we cannot remove appeared child in this section
                    # it may be wild when a loop ends
                    to_be_removed_list.append(child_index)
                else:
                    appeared_indices_set.add(child_index)

            for removed in to_be_removed_list:
                child_index_list.remove(removed)

            child_level = current_level + 1

            if child_level == cushion_amt:
                break

            for child_index in child_index_list:
                child_node = TreeNode(child_index, [], child_level)
                current_node.child.append(child_node)
                q.append(child_node)
            
        return tree

class TreeNode:
    def __init__(self, index, child, level):
        self.index = index
        self.child = child
        self.level = level
    
# node = TreeNode.find_mtable_tree(5)
# q = []
# q.append(node)
# count = 0
# while len(q) > 0:
#     n = q.pop(0)
#     child_list = []
#     for child in n.child:
#         child_list.append(child.index)
#     print(n.index, child_list)
#     for child in n.child:
#         q.append(child)
#     count = count + 1
# print(count)