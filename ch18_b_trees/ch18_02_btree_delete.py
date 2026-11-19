# -*- coding: utf-8 -*-
"""
第18章 B树 —— 18.3 从 B树中删除关键字
《算法导论（原书第3版）》CLRS

删除比插

入复杂：一路下行"预支"，保证删除发生在叶上或降到 t-1 也不违约：
  case 1: k 在叶 x 且 x 有 ≥ t 个 key → 直接删
  case 2: k 在内部 x：
      2a: k 左孩子 ≥ t keys → 用前驱（左子树最大）替换后递归删
      2b: k 右孩子 ≥ t keys → 用后继替换后递归删
      2c: 两孩子都 t-1 → 合并两孩+k 成一个 2t-1 结点，递归删
  case 3: k 不在 x：保证所进孩子有 ≥ t keys；
      3a: 兄弟够借 → 借一个 key+孩子
      3b: 兄弟都 t-1 → 与某兄弟合并，吸收父 key
删除后若根空且非叶 → 根下沉一层。
"""


class BTreeNode:
    __slots__ = ("leaf", "keys", "children", "n")

    def __init__(self, leaf=True):
        self.leaf = leaf
        self.keys = []
        self.children = []
        self.n = 0

    def _sync(self):
        self.n = len(self.keys)


class BTree:
    def __init__(self, t=3):
        assert t >= 2
        self.t = t
        self.root = BTreeNode(leaf=True)

    # ---------- 查 ----------
    def _find_key_index_in_node(self, x, k):
        i = 0
        while i < x.n and k > x.keys[i]:
            i += 1
        return i

    def search(self, k, x=None):
        if x is None:
            x = self.root
        i = self._find_key_index_in_node(x, k)
        if i < x.n and k == x.keys[i]:
            return (x, i)
        if x.leaf:
            return None
        return self.search(k, x.children[i])

    # ---------- 18.2 复用：分裂与插入 ----------
    def split_child(self, x, i):
        t = self.t
        z = BTreeNode()
        y = x.children[i]
        z.leaf = y.leaf
        z.keys = y.keys[t:]
        median = y.keys[t - 1]
        y.keys = y.keys[:t - 1]
        if not y.leaf:
            z.children = y.children[t:]
            y.children = y.children[:t]
        x.keys.insert(i, median)
        x.children.insert(i + 1, z)
        y._sync(); z._sync(); x._sync()

    def insert(self, k):
        r = self.root
        if r.n == 2 * self.t - 1:
            s = BTreeNode(leaf=False)
            s.children = [r]
            self.root = s
            self.split_child(s, 0)
            self._insert_nonfull(s, k)
        else:
            self._insert_nonfull(r, k)

    def _insert_nonfull(self, x, k):
        if x.leaf:
            i = x.n - 1
            x.keys.append(None)
            while i >= 0 and k < x.keys[i]:
                x.keys[i + 1] = x.keys[i]
                i -= 1
            x.keys[i + 1] = k
            x._sync()
        else:
            i = x.n - 1
            while i >= 0 and k < x.keys[i]:
                i -= 1
            i += 1
            if x.children[i].n == 2 * self.t - 1:
                self.split_child(x, i)
                if k > x.keys[i]:
                    i += 1
            self._insert_nonfull(x.children[i], k)

    # ---------- 18.3 删除 ----------
    def delete(self, k):
        """B-TREE-DELETE 主入口：包装 _delete(root, k) + 根收缩。"""
        self._delete(self.root, k)
        if self.root.n == 0 and not self.root.leaf:
            self.root = self.root.children[0]
        elif self.root.n == 0 and self.root.leaf:
            pass  # 空树，保持

    def _delete(self, x, k):
        t = self.t
        i = self._find_key_index_in_node(x, k)

        # case 1：k 就在本结点 x（叶或内部）
        if i < x.n and x.keys[i] == k:
            if x.leaf:
                x.keys.pop(i)
                x._sync()
                return
            # ——— 内部结点：case 2 ———
            left = x.children[i]
            right = x.children[i + 1]
            if left.n >= t:
                # 2a：前驱替换
                pred = self._max_key_node(left)
                kp = pred.keys[-1]
                x.keys[i] = kp
                self._delete(left, kp)
            elif right.n >= t:
                # 2b：后继替换
                suc = self._min_key_node(right)
                kp = suc.keys[0]
                x.keys[i] = kp
                self._delete(right, kp)
            else:
                # 2c：合并
                self._merge_children(x, i)
                self._delete(left, k)      # 合并后 left 有 2t-1 keys

        else:
            # ——— case 3：k 不在 x，递归往孩子走 ———
            if x.leaf:
                return                      # k 不在树中
            child = x.children[i]
            if child.n >= t:
                self._delete(child, k)
            else:
                # 3a/3b：先保证 child 有 ≥ t keys
                # 左兄弟
                if i > 0 and x.children[i - 1].n >= t:
                    self._borrow_from_left(x, i)
                elif i < x.n and x.children[i + 1].n >= t:
                    self._borrow_from_right(x, i)
                else:
                    # 3b：与相邻兄弟合并
                    if i > 0:
                        self._merge_children(x, i - 1)
                        child = x.children[i - 1]
                    else:
                        self._merge_children(x, i)
                        child = x.children[i]
                    # 根收缩提前处理
                    if x is self.root and x.n == 0:
                        self.root = child
                self._delete(child, k)

    # ---- 辅助 ----
    def _max_key_node(self, x):
        while not x.leaf:
            x = x.children[-1]
        return x

    def _min_key_node(self, x):
        while not x.leaf:
            x = x.children[0]
        return x

    def _borrow_from_left(self, x, i):
        """case 3a：x.children[i] 从左兄弟借一个。"""
        child = x.children[i]
        left = x.children[i - 1]
        child.keys.insert(0, x.keys[i - 1])
        x.keys[i - 1] = left.keys.pop()
        if not child.leaf:
            child.children.insert(0, left.children.pop())
        child._sync(); left._sync()

    def _borrow_from_right(self, x, i):
        child = x.children[i]
        right = x.children[i + 1]
        child.keys.append(x.keys[i])
        x.keys[i] = right.keys.pop(0)
        if not child.leaf:
            child.children.append(right.children.pop(0))
        child._sync(); right._sync()

    def _merge_children(self, x, i):
        """把 x.children[i] + x.keys[i] + x.children[i+1] 合成一个 2t-1 结点。"""
        t = self.t
        left = x.children[i]
        right = x.children[i + 1]
        left.keys += [x.keys[i]] + right.keys
        if not left.leaf:
            left.children += right.children
        x.keys.pop(i)
        x.children.pop(i + 1)
        left._sync(); x._sync()

    # ---------- 校验/展示（同 ch18_01）----------
    def verify(self):
        errs = []
        t = self.t
        leaf_depths = []

        def chk(x, depth, is_root):
            if x.n != len(x.keys):
                errs.append(f"n 不同步 @ {x.keys}")
            if not x.leaf and len(x.children) != x.n + 1:
                errs.append(f"孩子数错 @ keys={x.keys}")
            if is_root:
                pass
            else:
                if x.n < t - 1 or x.n > 2 * t - 1:
                    errs.append(f"key 数越界 @ {x.keys}: {x.n}")
            if x.keys != sorted(x.keys):
                errs.append(f"key 不升序 @ {x.keys}")
            if x.leaf:
                leaf_depths.append(depth)
            for c in x.children:
                chk(c, depth + 1, False)

        chk(self.root, 0, True)
        if len(set(leaf_depths)) > 1:
            errs.append(f"叶不等深: {sorted(set(leaf_depths))}")
        return len(errs) == 0, errs

    def inorder(self):
        out = []
        def walk(x):
            for i in range(x.n):
                if not x.leaf:
                    walk(x.children[i])
                out.append(x.keys[i])
            if not x.leaf:
                walk(x.children[x.n])
        walk(self.root)
        return out

    def height(self):
        h, x = 0, self.root
        while not x.leaf:
            h += 1
            x = x.children[0]
        return h

    def print_tree(self):
        def dump(x, depth=0):
            print("  " * depth + f"[{' '.join(map(str, x.keys))}]")
            for c in x.children:
                dump(c, depth + 1)
        dump(self.root)


def demo():
    print("=" * 60)
    print("18.3 B树删除（t=3）：插入 25 个 key 后乱序全删")
    import random
    t = BTree(t=3)
    keys = [10, 20, 5, 6, 12, 30, 7, 17, 3, 22, 40, 50, 60, 70, 80, 90, 100, 55, 65, 35, 45, 1, 2, 3, 4]
    keys = list(set(keys))
    for k in keys:
        t.insert(k)
    ok, _ = t.verify()
    print(f"插入 {len(keys)} 个去重 key，校验 {'✓' if ok else '✗'}")
    t.print_tree()

    random.seed(5)
    order = keys[:]
    random.shuffle(order)
    bad = 0
    for k in order:
        t.delete(k)
        ok, errs = t.verify()
        if not ok:
            bad += 1
            print(f"  ✗ 删 {k} 后: {errs[:2]}")
            if bad >= 3:
                t.print_tree()
                break
        if t.search(k) is not None:
            print(f"  ✗ 删 {k} 后仍能搜到")
            bad += 1
    remaining = t.inorder()
    print("乱序删除完成；剩余:", len(remaining), "（应为 0）")
    print("全程结构破坏次数:", bad, "次", "✓" if bad == 0 else "✗")
    print("删除后树高:", t.height(), "（根收缩正常）")


if __name__ == "__main__":
    demo()
