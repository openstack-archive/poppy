# -*- coding: utf-8 -*-

#    Copyright (C) 2014 Yahoo! Inc. All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import networkx as nx
from six.moves import cPickle as pickle

from taskflow import test
from taskflow.types import graph
from taskflow.types import sets
from taskflow.types import tree


class GraphTest(test.TestCase):
    def test_no_successors_no_predecessors(self):
        g = graph.DiGraph()
        g.add_node("a")
        g.add_node("b")
        g.add_node("c")
        g.add_edge("b", "c")
        self.assertEqual(set(['a', 'b']),
                         set(g.no_predecessors_iter()))
        self.assertEqual(set(['a', 'c']),
                         set(g.no_successors_iter()))

    def test_directed(self):
        g = graph.DiGraph()
        g.add_node("a")
        g.add_node("b")
        g.add_edge("a", "b")
        self.assertTrue(g.is_directed_acyclic())
        g.add_edge("b", "a")
        self.assertFalse(g.is_directed_acyclic())

    def test_frozen(self):
        g = graph.DiGraph()
        self.assertFalse(g.frozen)
        g.add_node("b")
        g.freeze()
        self.assertRaises(nx.NetworkXError, g.add_node, "c")

    def test_merge(self):
        g = graph.DiGraph()
        g.add_node("a")
        g.add_node("b")

        g2 = graph.DiGraph()
        g2.add_node('c')

        g3 = graph.merge_graphs(g, g2)
        self.assertEqual(3, len(g3))

    def test_merge_edges(self):
        g = graph.DiGraph()
        g.add_node("a")
        g.add_node("b")
        g.add_edge('a', 'b')

        g2 = graph.DiGraph()
        g2.add_node('c')
        g2.add_node('d')
        g2.add_edge('c', 'd')

        g3 = graph.merge_graphs(g, g2)
        self.assertEqual(4, len(g3))
        self.assertTrue(g3.has_edge('c', 'd'))
        self.assertTrue(g3.has_edge('a', 'b'))

    def test_overlap_detector(self):
        g = graph.DiGraph()
        g.add_node("a")
        g.add_node("b")
        g.add_edge('a', 'b')

        g2 = graph.DiGraph()
        g2.add_node('a')
        g2.add_node('d')
        g2.add_edge('a', 'd')

        self.assertRaises(ValueError,
                          graph.merge_graphs, g, g2)

        def occurence_detector(to_graph, from_graph):
            return sum(1 for node in from_graph.nodes_iter()
                       if node in to_graph)

        self.assertRaises(ValueError,
                          graph.merge_graphs, g, g2,
                          overlap_detector=occurence_detector)

        g3 = graph.merge_graphs(g, g2, allow_overlaps=True)
        self.assertEqual(3, len(g3))
        self.assertTrue(g3.has_edge('a', 'b'))
        self.assertTrue(g3.has_edge('a', 'd'))

    def test_invalid_detector(self):
        g = graph.DiGraph()
        g.add_node("a")

        g2 = graph.DiGraph()
        g2.add_node('c')

        self.assertRaises(ValueError,
                          graph.merge_graphs, g, g2,
                          overlap_detector='b')


class TreeTest(test.TestCase):
    def _make_species(self):
        # This is the following tree:
        #
        # animal
        # |__mammal
        # |  |__horse
        # |  |__primate
        # |     |__monkey
        # |     |__human
        # |__reptile
        a = tree.Node("animal")
        m = tree.Node("mammal")
        r = tree.Node("reptile")
        a.add(m)
        a.add(r)
        m.add(tree.Node("horse"))
        p = tree.Node("primate")
        m.add(p)
        p.add(tree.Node("monkey"))
        p.add(tree.Node("human"))
        return a

    def test_pformat_species(self):
        root = self._make_species()
        expected = """
animal
|__mammal
|  |__horse
|  |__primate
|     |__monkey
|     |__human
|__reptile
"""
        self.assertEqual(expected.strip(), root.pformat())

    def test_pformat_flat(self):
        root = tree.Node("josh")
        root.add(tree.Node("josh.1"))
        expected = """
josh
|__josh.1
"""
        self.assertEqual(expected.strip(), root.pformat())

        root[0].add(tree.Node("josh.1.1"))
        expected = """
josh
|__josh.1
   |__josh.1.1
"""
        self.assertEqual(expected.strip(), root.pformat())

        root[0][0].add(tree.Node("josh.1.1.1"))
        expected = """
josh
|__josh.1
   |__josh.1.1
      |__josh.1.1.1
"""
        self.assertEqual(expected.strip(), root.pformat())

        root[0][0][0].add(tree.Node("josh.1.1.1.1"))
        expected = """
josh
|__josh.1
   |__josh.1.1
      |__josh.1.1.1
         |__josh.1.1.1.1
"""
        self.assertEqual(expected.strip(), root.pformat())

    def test_pformat_partial_species(self):
        root = self._make_species()

        expected = """
reptile
"""
        self.assertEqual(expected.strip(), root[1].pformat())

        expected = """
mammal
|__horse
|__primate
   |__monkey
   |__human
"""
        self.assertEqual(expected.strip(), root[0].pformat())

        expected = """
primate
|__monkey
|__human
"""
        self.assertEqual(expected.strip(), root[0][1].pformat())

        expected = """
monkey
"""
        self.assertEqual(expected.strip(), root[0][1][0].pformat())

    def test_pformat(self):

        root = tree.Node("CEO")

        expected = """
CEO
"""

        self.assertEqual(expected.strip(), root.pformat())

        root.add(tree.Node("Infra"))

        expected = """
CEO
|__Infra
"""
        self.assertEqual(expected.strip(), root.pformat())

        root[0].add(tree.Node("Infra.1"))
        expected = """
CEO
|__Infra
   |__Infra.1
"""
        self.assertEqual(expected.strip(), root.pformat())

        root.add(tree.Node("Mail"))
        expected = """
CEO
|__Infra
|  |__Infra.1
|__Mail
"""
        self.assertEqual(expected.strip(), root.pformat())

        root.add(tree.Node("Search"))
        expected = """
CEO
|__Infra
|  |__Infra.1
|__Mail
|__Search
"""
        self.assertEqual(expected.strip(), root.pformat())

        root[-1].add(tree.Node("Search.1"))
        expected = """
CEO
|__Infra
|  |__Infra.1
|__Mail
|__Search
   |__Search.1
"""
        self.assertEqual(expected.strip(), root.pformat())

        root[-1].add(tree.Node("Search.2"))
        expected = """
CEO
|__Infra
|  |__Infra.1
|__Mail
|__Search
   |__Search.1
   |__Search.2
"""
        self.assertEqual(expected.strip(), root.pformat())

        root[0].add(tree.Node("Infra.2"))
        expected = """
CEO
|__Infra
|  |__Infra.1
|  |__Infra.2
|__Mail
|__Search
   |__Search.1
   |__Search.2
"""
        self.assertEqual(expected.strip(), root.pformat())

        root[0].add(tree.Node("Infra.3"))
        expected = """
CEO
|__Infra
|  |__Infra.1
|  |__Infra.2
|  |__Infra.3
|__Mail
|__Search
   |__Search.1
   |__Search.2
"""
        self.assertEqual(expected.strip(), root.pformat())

        root[0][-1].add(tree.Node("Infra.3.1"))
        expected = """
CEO
|__Infra
|  |__Infra.1
|  |__Infra.2
|  |__Infra.3
|     |__Infra.3.1
|__Mail
|__Search
   |__Search.1
   |__Search.2
"""
        self.assertEqual(expected.strip(), root.pformat())

        root[-1][0].add(tree.Node("Search.1.1"))
        expected = """
CEO
|__Infra
|  |__Infra.1
|  |__Infra.2
|  |__Infra.3
|     |__Infra.3.1
|__Mail
|__Search
   |__Search.1
   |  |__Search.1.1
   |__Search.2
"""
        self.assertEqual(expected.strip(), root.pformat())

        root[1].add(tree.Node("Mail.1"))
        expected = """
CEO
|__Infra
|  |__Infra.1
|  |__Infra.2
|  |__Infra.3
|     |__Infra.3.1
|__Mail
|  |__Mail.1
|__Search
   |__Search.1
   |  |__Search.1.1
   |__Search.2
"""
        self.assertEqual(expected.strip(), root.pformat())

        root[1][0].add(tree.Node("Mail.1.1"))
        expected = """
CEO
|__Infra
|  |__Infra.1
|  |__Infra.2
|  |__Infra.3
|     |__Infra.3.1
|__Mail
|  |__Mail.1
|     |__Mail.1.1
|__Search
   |__Search.1
   |  |__Search.1.1
   |__Search.2
"""
        self.assertEqual(expected.strip(), root.pformat())

    def test_path(self):
        root = self._make_species()
        human = root.find("human")
        self.assertIsNotNone(human)
        p = list([n.item for n in human.path_iter()])
        self.assertEqual(['human', 'primate', 'mammal', 'animal'], p)

    def test_empty(self):
        root = tree.Node("josh")
        self.assertTrue(root.empty())

    def test_removal(self):
        root = self._make_species()
        self.assertIsNotNone(root.remove('reptile'))
        self.assertRaises(ValueError, root.remove, 'reptile')
        self.assertIsNone(root.find('reptile'))

    def test_removal_direct(self):
        root = self._make_species()
        self.assertRaises(ValueError, root.remove, 'human',
                          only_direct=True)

    def test_removal_self(self):
        root = self._make_species()
        n = root.find('horse')
        self.assertIsNotNone(n.parent)
        n.remove('horse', include_self=True)
        self.assertIsNone(n.parent)
        self.assertIsNone(root.find('horse'))

    def test_disassociate(self):
        root = self._make_species()
        n = root.find('horse')
        self.assertIsNotNone(n.parent)
        c = n.disassociate()
        self.assertEqual(1, c)
        self.assertIsNone(n.parent)
        self.assertIsNone(root.find('horse'))

    def test_disassociate_many(self):
        root = self._make_species()
        n = root.find('horse')
        n.parent.add(n)
        n.parent.add(n)
        c = n.disassociate()
        self.assertEqual(3, c)
        self.assertIsNone(n.parent)
        self.assertIsNone(root.find('horse'))

    def test_not_empty(self):
        root = self._make_species()
        self.assertFalse(root.empty())

    def test_node_count(self):
        root = self._make_species()
        self.assertEqual(7, 1 + root.child_count(only_direct=False))

    def test_index(self):
        root = self._make_species()
        self.assertEqual(0, root.index("mammal"))
        self.assertEqual(1, root.index("reptile"))

    def test_contains(self):
        root = self._make_species()
        self.assertIn("monkey", root)
        self.assertNotIn("bird", root)

    def test_freeze(self):
        root = self._make_species()
        root.freeze()
        self.assertRaises(tree.FrozenNode, root.add, "bird")

    def test_find(self):
        root = self._make_species()
        self.assertIsNone(root.find('monkey', only_direct=True))
        self.assertIsNotNone(root.find('monkey', only_direct=False))
        self.assertIsNotNone(root.find('animal', only_direct=True))
        self.assertIsNotNone(root.find('reptile', only_direct=True))
        self.assertIsNone(root.find('animal', include_self=False))
        self.assertIsNone(root.find('animal',
                                    include_self=False, only_direct=True))

    def test_dfs_itr(self):
        root = self._make_species()
        things = list([n.item for n in root.dfs_iter(include_self=True)])
        self.assertEqual(set(['animal', 'reptile', 'mammal', 'horse',
                              'primate', 'monkey', 'human']), set(things))

    def test_dfs_itr_left_to_right(self):
        root = self._make_species()
        it = root.dfs_iter(include_self=False, right_to_left=False)
        things = list([n.item for n in it])
        self.assertEqual(['reptile', 'mammal', 'primate',
                          'human', 'monkey', 'horse'], things)

    def test_dfs_itr_no_self(self):
        root = self._make_species()
        things = list([n.item for n in root.dfs_iter(include_self=False)])
        self.assertEqual(['mammal', 'horse', 'primate',
                          'monkey', 'human', 'reptile'], things)

    def test_bfs_itr(self):
        root = self._make_species()
        things = list([n.item for n in root.bfs_iter(include_self=True)])
        self.assertEqual(['animal', 'reptile', 'mammal', 'primate',
                          'horse', 'human', 'monkey'], things)

    def test_bfs_itr_no_self(self):
        root = self._make_species()
        things = list([n.item for n in root.bfs_iter(include_self=False)])
        self.assertEqual(['reptile', 'mammal', 'primate',
                          'horse', 'human', 'monkey'], things)

    def test_bfs_itr_right_to_left(self):
        root = self._make_species()
        it = root.bfs_iter(include_self=False, right_to_left=True)
        things = list([n.item for n in it])
        self.assertEqual(['mammal', 'reptile', 'horse',
                          'primate', 'monkey', 'human'], things)


class OrderedSetTest(test.TestCase):

    def test_pickleable(self):
        items = [10, 9, 8, 7]
        s = sets.OrderedSet(items)
        self.assertEqual(items, list(s))
        s_bin = pickle.dumps(s)
        s2 = pickle.loads(s_bin)
        self.assertEqual(s, s2)
        self.assertEqual(items, list(s2))

    def test_retain_ordering(self):
        items = [10, 9, 8, 7]
        s = sets.OrderedSet(iter(items))
        self.assertEqual(items, list(s))

    def test_retain_duplicate_ordering(self):
        items = [10, 9, 10, 8, 9, 7, 8]
        s = sets.OrderedSet(iter(items))
        self.assertEqual([10, 9, 8, 7], list(s))

    def test_length(self):
        items = [10, 9, 8, 7]
        s = sets.OrderedSet(iter(items))
        self.assertEqual(4, len(s))

    def test_duplicate_length(self):
        items = [10, 9, 10, 8, 9, 7, 8]
        s = sets.OrderedSet(iter(items))
        self.assertEqual(4, len(s))

    def test_contains(self):
        items = [10, 9, 8, 7]
        s = sets.OrderedSet(iter(items))
        for i in items:
            self.assertIn(i, s)

    def test_copy(self):
        items = [10, 9, 8, 7]
        s = sets.OrderedSet(iter(items))
        s2 = s.copy()
        self.assertEqual(s, s2)
        self.assertEqual(items, list(s2))

    def test_empty_intersection(self):
        s = sets.OrderedSet([1, 2, 3])

        es = set(s)

        self.assertEqual(es.intersection(), s.intersection())

    def test_intersection(self):
        s = sets.OrderedSet([1, 2, 3])
        s2 = sets.OrderedSet([2, 3, 4, 5])

        es = set(s)
        es2 = set(s2)

        self.assertEqual(es.intersection(es2), s.intersection(s2))
        self.assertEqual(es2.intersection(s), s2.intersection(s))

    def test_multi_intersection(self):
        s = sets.OrderedSet([1, 2, 3])
        s2 = sets.OrderedSet([2, 3, 4, 5])
        s3 = sets.OrderedSet([1, 2])

        es = set(s)
        es2 = set(s2)
        es3 = set(s3)

        self.assertEqual(es.intersection(s2, s3), s.intersection(s2, s3))
        self.assertEqual(es2.intersection(es3), s2.intersection(s3))

    def test_superset(self):
        s = sets.OrderedSet([1, 2, 3])
        s2 = sets.OrderedSet([2, 3])
        self.assertTrue(s.issuperset(s2))
        self.assertFalse(s.issubset(s2))

    def test_subset(self):
        s = sets.OrderedSet([1, 2, 3])
        s2 = sets.OrderedSet([2, 3])
        self.assertTrue(s2.issubset(s))
        self.assertFalse(s2.issuperset(s))

    def test_empty_difference(self):
        s = sets.OrderedSet([1, 2, 3])

        es = set(s)

        self.assertEqual(es.difference(), s.difference())

    def test_difference(self):
        s = sets.OrderedSet([1, 2, 3])
        s2 = sets.OrderedSet([2, 3])

        es = set(s)
        es2 = set(s2)

        self.assertEqual(es.difference(es2), s.difference(s2))
        self.assertEqual(es2.difference(es), s2.difference(s))

    def test_multi_difference(self):
        s = sets.OrderedSet([1, 2, 3])
        s2 = sets.OrderedSet([2, 3])
        s3 = sets.OrderedSet([3, 4, 5])

        es = set(s)
        es2 = set(s2)
        es3 = set(s3)

        self.assertEqual(es3.difference(es), s3.difference(s))
        self.assertEqual(es.difference(es3), s.difference(s3))
        self.assertEqual(es2.difference(es, es3), s2.difference(s, s3))

    def test_empty_union(self):
        s = sets.OrderedSet([1, 2, 3])

        es = set(s)

        self.assertEqual(es.union(), s.union())

    def test_union(self):
        s = sets.OrderedSet([1, 2, 3])
        s2 = sets.OrderedSet([2, 3, 4])

        es = set(s)
        es2 = set(s2)

        self.assertEqual(es.union(es2), s.union(s2))
        self.assertEqual(es2.union(es), s2.union(s))

    def test_multi_union(self):
        s = sets.OrderedSet([1, 2, 3])
        s2 = sets.OrderedSet([2, 3, 4])
        s3 = sets.OrderedSet([4, 5, 6])

        es = set(s)
        es2 = set(s2)
        es3 = set(s3)

        self.assertEqual(es.union(es2, es3), s.union(s2, s3))
