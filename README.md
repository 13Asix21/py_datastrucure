# py_datastrucure

《算法导论（原书第3版）》（CLRS）数据结构章节的 Python 分节实现 demo。

覆盖范围：**第三部分 数据结构（第10~14章）** 与 **第五部分 高级数据结构（第18~21章）**，共 9 章 21 个可运行文件，每个 demo 独立运行（`python <file>`），带中文注释、操作复杂度标注与运行时自校验（不变量检查 / 与暴力法对拍）。

## 目录

| 章节 | 文件 | 内容 |
|---|---|---|
| 10.1 | `ch10_basic_data_structures/ch10_01_stack_and_queue.py` | 数组栈（PUSH/POP）、环形队列（ENQUEUE/DEQUEUE） |
| 10.2 | `ch10_basic_data_structures/ch10_02_linked_list.py` | 单链表 / 双向链表 / 带哨兵循环双向链表（LIST-INSERT'/DELETE'/SEARCH'） |
| 10.3 | `ch10_basic_data_structures/ch10_03_array_object_representation.py` | 无指针语言模拟对象：多数组表示 + 单数组表示 + 空闲表 ALLOCATE/FREE |
| 10.4 | `ch10_basic_data_structures/ch10_04_rooted_tree.py` | 二叉树 left/right 表示、多叉树 left-child/right-sibling 表示 |
| 11.1 | `ch11_hash_tables/ch11_01_direct_addressing.py` | 直接寻址表 O(1) 与其空间缺陷 |
| 11.2 | `ch11_hash_tables/ch11_02_chained_hash.py` | 链接法散列表（CHAINED-HASH-INSERT/SEARCH/DELETE）+ rehash、2的幂 vs 质数分布实验 |
| 11.3 | `ch11_hash_tables/ch11_03_hash_functions.py` | 除法/乘法/字符串多项式/全域散列函数族 |
| 11.4 | `ch11_hash_tables/ch11_04_open_addressing.py` | 开放寻址：线性/二次/双重探查、墓碑 DELETED、群集实验 |
| 12.1 | `ch12_binary_search_trees/ch12_01_bst_basics.py` | BST 性质、中序遍历=升序、性质自检器 |
| 12.2 | `ch12_binary_search_trees/ch12_02_bst_queries.py` | SEARCH / MINIMUM / MAXIMUM / SUCCESSOR / PREDECESSOR |
| 12.3 | `ch12_binary_search_trees/ch12_03_bst_insert_delete.py` | TREE-INSERT / TRANSPLANT / TREE-DELETE 三情形 |
| 13.1~13.3 | `ch13_red_black_trees/ch13_01_rb_insert.py` | 红黑性质5条、LEFT/RIGHT-ROTATE、RB-INSERT-FIXUP 3 case |
| 13.4 | `ch13_red_black_trees/ch13_02_rb_delete.py` | RB-DELETE / RB-DELETE-FIXUP 4 case（NIL 哨兵版在 `demo_utils.py`），6000 次随机插删全程校验 |
| 14.1 | `ch14_augmenting_data_structures/ch14_01_order_statistic_tree.py` | 顺序统计树：size 扩张、OS-SELECT / OS-RANK |
| 14.3 | `ch14_augmenting_data_structures/ch14_03_interval_tree.py` | 区间树：max 扩张、INTERVAL-SEARCH、全部重叠查找 |
| 18.1~18.2 | `ch18_b_trees/ch18_01_btree_insert.py` | B树定义、B-TREE-SPLIT-CHILD / INSERT（t=3，叶等深/key界校验） |
| 18.3 | `ch18_b_trees/ch18_02_btree_delete.py` | B-TREE-DELETE 全 case（前驱/后继替换、借键、2t-1 合并），乱序全删校验 |
| 19.1~19.3 | `ch19_fibonacci_heaps/ch19_fib_heap.py` | 斐波那契堆全操作：INSERT/UNION/EXTRACT-MIN（consolidate）/DECREASE-KEY（cut+级联切割）/DELETE，不变量校验 + 300 步混战 |
| 20.1~20.3 | `ch20_van_emde_boas/ch20_veb_tree.py` | van Emde Boas 树：summary/cluster/min/max 冗余、MEMBER/INSERT/SUCCESSOR/PREDECESSOR/DELETE，与 Python set 2000 次操作对拍 |
| 21.1~21.4 | `ch21_disjoint_sets/ch21_disjoint_set.py` | 链表表示 + 按秩合并/路径压缩森林；应用：连通分量、Kruskal 环检测，路径压缩步数实验 |

## 运行

```bash
# 单个运行（Python 3.8+，无第三方依赖）
python ch13_red_black_trees/ch13_01_rb_insert.py

# 全量运行
for f in $(find . -name "*.py" -not -path "./.git/*" | sort); do python "$f"; done
```

## 实现说明

- **NIL 哨兵**：红黑树按 CLRS 原生 sentinel 模式实现（`demo_utils.py`），使 RB-TRANSPLANT 与删除修复无需处理 None 特例——这是删除修复正确性的关键。
- **vEB 树**：delete 在 CLRS 假定 x ∈ 树的前提下定义；本实现加了成员护栏使其成为全集字典语义（删不存在元素返回 False），压力测试方可与 Python set 对拍。
- **B树/红黑树/斐波那契堆** 的 demo 均含**运行时不变量校验**（堆序、黑高、size/max 字段、度数、min 指针等），随机操作序列下全程 0 破坏。

## 来源

章节与目录结构依据迈越 RAGFlow 知识库《算法导论（原书第3版）》第三部分 + 第五部分。
