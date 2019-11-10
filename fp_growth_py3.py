# encoding: utf-8
"""
"""
from collections import defaultdict, namedtuple

def find_frequent_itemsets(transactions, minimum_support, include_support=False):
    """
使用FP growth查找给定事务中的频繁项集。这个函数返回生成器，而不是填充的项列表。

“transactions”参数可以是iterables of items的任意iterable。

`minimum_support`应该是一个整数，指定要接受的项集的出现次数。

每个项必须是散列的（即它必须作为字典）。

如果“include_support”为true，则放弃（itemset，support）对。
    """
    items = defaultdict(lambda: 0)  # 从项映射到支持度

    # 加载传入事务并计算
    for transaction in transactions:
        for item in transaction:
            items[item] += 1

    # 从项支持词典中删除不常用的项；
    items = dict((item, support) for item, support in items.items()
        if support >= minimum_support)

    # 建立我们的FP树
    # 必须去除不常见的物品，并且其幸存物品必须按频率的降序排序。
    def clean_transaction(transaction):
        transaction = filter(lambda v: v in items, transaction)
        transaction_list = list(transaction)   # 为了防止变量在其他部分调用，这里引入临时变量transaction_list
        transaction_list.sort(key=lambda v: items[v], reverse=True)
        return transaction_list

    master = FPTree()
    for transaction in map(clean_transaction, transactions):
        master.add(transaction)

    def find_with_suffix(tree, suffix):
        if len(suffix) <= 1:  # 优化点，设置后缀长度<=1，即生成的频繁项长度<=2，去掉频繁项集长度小于等于1的部分
            for item, nodes in tree.items():
                support = sum(n.count for n in nodes)
                if support >= minimum_support and item not in suffix:
                    found_set = [item] + suffix
                    yield (found_set, support) if include_support else found_set

                    # 建立条件树并递归搜索
                    # 项目集
                    cond_tree = conditional_tree_from_paths(tree.prefix_paths(item))
                    for s in find_with_suffix(cond_tree, found_set):
                        yield s

    # 搜索频繁项集，并生成找到的结果。
    for itemset in find_with_suffix(master, []):
        yield itemset

class FPTree(object):
    """
一棵FP树
此对象只能存储可哈希的事务项
所有项必须作为字典键或集合成员
    """

    Route = namedtuple('Route', 'head tail')

    def __init__(self):
        # 树的根节点.
        self._root = FPNode(self, None, None)

        # 将项目映射到路径的头和尾的字典
        # “neighbor”将命中包含该项的每个节点。
        self._routes = {}

    @property
    def root(self):
        """树的根节点"""
        return self._root

    def add(self, transaction):
        """向树中添加事务"""
        point = self._root

        for item in transaction:
            next_point = point.search(item)
            if next_point:
                # 此树中已存在当前事务项重新调用它。
                next_point.increment()
            else:
                # 创建一个新点并将其添加为
                # 正在查看。
                next_point = FPNode(self, item)
                point.add(next_point)

                # 更新包含此项的节点的路由以包括新节点。
                self._update_route(next_point)

            point = next_point

    def _update_route(self, point):
        """将给定节点添加到通过其项的所有节点的路由中。"""
        assert self is point.tree

        try:
            route = self._routes[point.item]
            route[1].neighbor = point
            self._routes[point.item] = self.Route(route[0], point)
        except KeyError:

            self._routes[point.item] = self.Route(point, point)

    def items(self):
        """
        为树中表示的每个项生成一个2元组。第一次元组的元素是项本身，第二个元素是生成树中属于项的节点的生成器。
        """
        for item in self._routes.keys():
            yield (item, self.nodes(item))

    def nodes(self, item):
        """
        生成包含给定项的节点序列。
        """

        try:
            node = self._routes[item][0]
        except KeyError:
            return

        while node:
            yield node
            node = node.neighbor

    def prefix_paths(self, item):
        """生成以给定项结尾的前缀路径。"""

        def collect_path(node):
            path = []
            while node and not node.root:
                path.append(node)
                node = node.parent
            path.reverse()
            return path

        return (collect_path(node) for node in self.nodes(item))

    def inspect(self):
        print('Tree:')
        self.root.inspect(1)

        print
        print('Routes:')
        for item, nodes in self.items():
            print('  %r' % item)
            for node in nodes:
                print('    %r' % node)

def conditional_tree_from_paths(paths):
    """从给定的前缀路径构建条件FP树。"""
    tree = FPTree()
    condition_item = None
    items = set()

    # 将路径中的节点导入到新树中。
    # 叶数很重要；剩余的计数将从叶数开始。
    for path in paths:
        if condition_item is None:
            condition_item = path[-1].item

        point = tree.root
        for node in path:
            next_point = point.search(node.item)
            if not next_point:
                items.add(node.item)
                count = node.count if node.item == condition_item else 0
                next_point = FPNode(tree, node.item, count)
                point.add(next_point)
                tree._update_route(next_point)
            point = next_point

    assert condition_item is not None

    # 计算非叶节点的计数。
    for path in tree.prefix_paths(condition_item):
        count = path[-1].count
        for node in reversed(path[:-1]):
            node._count += count

    return tree

class FPNode(object):

    def __init__(self, tree, item, count=1):
        self._tree = tree
        self._item = item
        self._count = count
        self._parent = None
        self._children = {}
        self._neighbor = None

    def add(self, child):

        if not isinstance(child, FPNode):
            raise TypeError("Can only add other FPNodes as children")

        if not child.item in self._children:
            self._children[child.item] = child
            child.parent = self

    def search(self, item):

        try:
            return self._children[item]
        except KeyError:
            return None

    def __contains__(self, item):
        return item in self._children

    @property
    def tree(self):

        return self._tree

    @property
    def item(self):

        return self._item

    @property
    def count(self):

        return self._count

    def increment(self):

        if self._count is None:
            raise ValueError("Root nodes have no associated count.")
        self._count += 1

    @property
    def root(self):

        return self._item is None and self._count is None

    @property
    def leaf(self):

        return len(self._children) == 0

    @property
    def parent(self):

        return self._parent

    @parent.setter
    def parent(self, value):
        if value is not None and not isinstance(value, FPNode):
            raise TypeError("A node must have an FPNode as a parent.")
        if value and value.tree is not self.tree:
            raise ValueError("Cannot have a parent from another tree.")
        self._parent = value

    @property
    def neighbor(self):

        return self._neighbor

    @neighbor.setter
    def neighbor(self, value):
        if value is not None and not isinstance(value, FPNode):
            raise TypeError("A node must have an FPNode as a neighbor.")
        if value and value.tree is not self.tree:
            raise ValueError("Cannot have a neighbor from another tree.")
        self._neighbor = value

    @property
    def children(self):

        return tuple(self._children.itervalues())

    def inspect(self, depth=0):
        print(('  ' * depth) + repr(self))
        for child in self.children:
            child.inspect(depth + 1)

    def __repr__(self):
        if self.root:
            return "<%s (root)>" % type(self).__name__
        return "<%s %r (%r)>" % (type(self).__name__, self.item, self.count)


if __name__ == '__main__':
    from optparse import OptionParser
    import csv

    p = OptionParser(usage='/Users/apple/PycharmProjects/Apriori/python3-fp-growth-master/课程出勤详情.csv')
    p.add_option('-s', '--minimum-support', dest='minsup', type='int',
        help='Minimum itemset support (default: 2)')
    p.add_option('-n', '--numeric', dest='numeric', action='store_true',
        help='Convert the values in datasets to numerals (default: false)')
    p.set_defaults(minsup=2)
    p.set_defaults(numeric=False)

    options, args = p.parse_args()
    if len(args) < 1:
        p.error('must provide the path to a CSV file to read')

    transactions = []
    with open(args[0]) as database:
        for row in csv.reader(database):
            if options.numeric:
                transaction = []
                for item in row:
                    transaction.append(long(item))
                transactions.append(transaction)
            else:
                transactions.append(row)

    result = []
    for itemset, support in find_frequent_itemsets(transactions, options.minsup, True):
        result.append((itemset, support))

    result = sorted(result, key=lambda i: i[0])
    for itemset, support in result:
        print(str(itemset) + ' ' + str(support))
