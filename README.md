# py_datastrucure

《算法导论（原书第3版）》（CLRS）数据结构与图算法章节的 Python 分节实现 demo。

覆盖范围：**第6章 堆**、**第三部分 数据结构（第10~14章）**、**第五部分 高级数据结构（第18~21章）**、**第六部分 图算法（第22~26章）**，共 13 章 39 个可运行文件。每章两类文件：
- **实现 demo**（`chXX_YY_*.py`）：结构/算法本体，带中文注释、复杂度标注与运行时自校验（不变量检查 / 与暴力法对拍）
- **应用 demo**（`chXX_app_*.py`）：配真实应用场景 + 正确性对拍 + 效率基准（与朴素做法/工业实现同台计时）

## 目录（实现 demo）

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
| 6.1~6.5 | `ch06_heaps/ch06_01_heap.py` | 二叉堆：MAX-HEAPIFY / BUILD-MAX-HEAP O(n) / HEAPSORT / 优先队列接口（EXTRACT-MAX、INCREASE-KEY） |
| 22.1~22.3 | `ch22_graph_algorithms/ch22_01_bfs_dfs.py` | 邻接表、BFS 最短路、DFS 时间戳/括号化定理/边四分类 |
| 22.4~22.5 | `ch22_graph_algorithms/ch22_02_topological_scc.py` | 拓扑排序（DFS 版 + Kahn 版对拍）、Kosaraju SCC（vs 传递闭包参照） |
| 23.2 | `ch23_mst/ch23_mst.py` | Kruskal（并查集）+ Prim（小顶堆）双实现互检 + 树性校验 |
| 24.1~24.2 | `ch24_shortest_paths/ch24_bellman_ford.py` | Bellman-Ford（负环检测）+ DAG-SHORTEST-PATHS；vs Dijkstra 三方对拍 |
| 25.2 | `ch25_all_pairs_shortest_paths/ch25_floyd_warshall.py` | Floyd-Warshall O(V³) + 传递闭包；vs V次Dijkstra 全矩阵互检 |
| 26.2 | `ch26_max_flow/ch26_max_flow.py` | Edmonds-Karp O(VE²)（BFS 增广）；最大流=最小割验证；二分图匹配建模 |

## 运行

```bash
# 单个运行（Python 3.8+，无第三方依赖）
python ch13_red_black_trees/ch13_01_rb_insert.py

# 全量运行
for f in $(find . -name "*.py" -not -path "./.git/*" | sort); do python "$f"; done
```

## 目录（应用 demo：真实场景 + 正确性对拍 + 效率基准）

| 章节 | 文件 | 应用场景 | 效率读数（实测） |
|---|---|---|---|
| 10 | `ch10_basic_data_structures/ch10_app_stack_queue_app.py` | 括号匹配 + RPN 求值；LRU 缓存（对拍 OrderedDict） | 环形队列比 list.pop(0) 反例快 **235×** |
| 11 | `ch11_hash_tables/ch11_app_hash_app.py` | 词频统计（对拍 Counter）；Two-Sum；拼写检查器 | 哈希 Two-Sum 比暴力快 **746×**；查词快 78× |
| 12 | `ch12_binary_search_trees/ch12_app_bst_app.py` | 动态电话簿 vs 排序数组；范围查询剪枝 vs 全表扫；顺序插入退化实验 | 范围查询快 17×；顺序插入树高=n（4000 个→高 4000）实证 BST 退化 |
| 13 | `ch13_red_black_trees/ch13_app_rb_app.py` | 有序集合 fuzz 对拍；BST vs RBT 顺序插入对抗；事件调度器 ceil 查询 | RBT 搜索比退化 BST 快 **208×**（树高 23 vs 8000） |
| 14 | `ch14_augmenting_data_structures/ch14_app_augment_app.py` | 会议室冲突检测（区间树）；实时排行榜 rank/kth（顺序统计树） | 冲突查询快 28×；rank 查询快 37× |
| 18 | `ch18_b_trees/ch18_app_btree_app.py` | 磁盘页 I/O 计数模拟；范围扫描（range scan）；阶数 t 调参 | B树页读比 BST 少 **5.9×**（2.99 vs 17.56 页/查询） |
| 19 | `ch19_fibonacci_heaps/ch19_app_dijkstra_app.py` | Dijkstra 三实现同台：朴素/二叉堆/斐波那契堆（10 组三方逐点对拍） | V=4000：朴素 461ms vs heapq 4.2ms；理论账 O(E+VlgV) 详解 |
| 20 | `ch20_van_emde_boas/ch20_app_port_allocator.py` | TCP 端口池分配器 allocate/allocate_at/release（对拍 bitmap 版） | 高密度下 vEB 比 linear probing 快 **25×** |
| 21 | `ch21_disjoint_sets/ch21_app_disjoint_app.py` | 图像连通域（对拍 BFS）；渗流相变蒙特卡洛（p*≈0.59 复现）；Kruskal 迷宫生成+ASCII 渲染；路径压缩微基准 | 渗流率 0.55→0.65 从 18.7%→85.7% 相变清晰；压缩后链深 3 vs 7 |
| 6 | `ch06_heaps/ch06_app_heap_app.py` | Top-K 流式守门员（四方对拍）；任务调度器（10 万任务 vs heapq）；heapsort vs Timsort | BUILD 比逐插入快 1.9×；纯 Python 堆与 heapq 常数差 6×（同阶） |
| 22 | `ch22_graph_algorithms/ch22_app_graph_app.py` | 社交网络六度分隔（BFS 平均 5.83 跳）；构建系统拓扑序；网页 SCC 集团；大图遍历基准 | BFS/递归DFS/栈DFS 三方同台；SCC 集团结构即分量图 DAG |

## 实现说明

- **NIL 哨兵**：红黑树按 CLRS 原生 sentinel 模式实现（`demo_utils.py`），使 RB-TRANSPLANT 与删除修复无需处理 None 特例——这是删除修复正确性的关键。
- **vEB 树**：delete 在 CLRS 假定 x ∈ 树的前提下定义；本实现加了成员护栏使其成为全集字典语义（删不存在元素返回 False），压力测试方可与 Python set 对拍。
- **B树/红黑树/斐波那契堆** 的 demo 均含**运行时不变量校验**（堆序、黑高、size/max 字段、度数、min 指针等），随机操作序列下全程 0 破坏。

## 来源

章节与目录结构依据迈越 RAGFlow 知识库《算法导论（原书第3版）》第三部分 + 第五部分。
