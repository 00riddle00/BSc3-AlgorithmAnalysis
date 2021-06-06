/* 
 * This code was borrowed from 
 * https://www.techiedelight.com/travelling-salesman-problem-using-branch-and-bound/
 * [accessed on 2021-05-25]
 * to compare test outputs.
 */

#include <iostream>
#include <vector>
#include <queue>
#include <utility>
#include <cstring>
#include <climits>
using namespace std;

// `N` is the total number of total nodes on the graph or cities on the map
#define N 5

// Sentinel value for representing `INFINITY`
#define INF INT_MAX

int iterations = 0;

// State Space Tree nodes
struct Node
{
    // stores edges of the state-space tree
    // help in tracing the path when the answer is found
    vector<pair<int, int>> path;

    // stores the reduced matrix
    int reducedMatrix[N][N];

    // stores the lower bound
    int cost;

    // stores the current city number
    int vertex;

    // stores the total number of cities visited so far
    int level;
};

// Function to allocate a new node `(i, j)` corresponds to visiting city `j`
// from city `i`
Node* newNode(int parentMatrix[N][N], vector<pair<int, int>> const &path,
            int level, int i, int j)
{
    Node* node = new Node;

    // stores ancestors edges of the state-space tree
    node->path = path;
    // skip for the root node
    if (level != 0)
    {
        // add a current edge to the path
        node->path.push_back(make_pair(i, j));
    }

    // copy data from the parent node to the current node
    memcpy(node->reducedMatrix, parentMatrix,
        sizeof node->reducedMatrix);

    // Change all entries of row `i` and column `j` to `INFINITY`
    // skip for the root node
    for (int k = 0; level != 0 && k < N; k++)
    {
        // set outgoing edges for the city `i` to `INFINITY`
        node->reducedMatrix[i][k] = INF;

        // set incoming edges to city `j` to `INFINITY`
        node->reducedMatrix[k][j] = INF;
    }

    // Set `(j, 0)` to `INFINITY`
    // here start node is 0
    node->reducedMatrix[j][0] = INF;

    // set number of cities visited so far
    node->level = level;

    // assign current city number
    node->vertex = j;

    // return node
    return node;
}

// Function to reduce each row so that there must be at least one zero in each row
int rowReduction(int reducedMatrix[N][N], int row[N])
{
    // initialize row array to `INFINITY`
    fill_n(row, N, INF);

    // `row[i]` contains minimum in row `i`
    for (int i = 0; i < N; i++)
    {
        for (int j = 0; j < N; j++)
        {
            if (reducedMatrix[i][j] < row[i]) {
                row[i] = reducedMatrix[i][j];
            }
        }
    }

    // reduce the minimum value from each element in each row
    for (int i = 0; i < N; i++)
    {
        for (int j = 0; j < N; j++)
        {
            if (reducedMatrix[i][j] != INF && row[i] != INF) {
                reducedMatrix[i][j] -= row[i];
            }
        }
    }
}

// Function to reduce each column so that there must be at least one zero
// in each column
int columnReduction(int reducedMatrix[N][N], int col[N])
{
    // initialize all elements of array `col` with `INFINITY`
    fill_n(col, N, INF);

    // `col[j]` contains minimum in col `j`
    for (int i = 0; i < N; i++)
    {
        for (int j = 0; j < N; j++)
        {
            if (reducedMatrix[i][j] < col[j]) {
                col[j] = reducedMatrix[i][j];
            }
        }
    }

    // reduce the minimum value from each element in each column
    for (int i = 0; i < N; i++)
    {
        for (int j = 0; j < N; j++)
        {
            if (reducedMatrix[i][j] != INF && col[j] != INF) {
                reducedMatrix[i][j] -= col[j];
            }
        }
    }
}

// Function to get the lower bound on the path starting at the current minimum node
int calculateCost(int reducedMatrix[N][N])
{
    // initialize cost to 0
    int cost = 0;

    // Row Reduction
    int row[N];
    rowReduction(reducedMatrix, row);

    // Column Reduction
    int col[N];
    columnReduction(reducedMatrix, col);

    // the total expected cost is the sum of all reductions
    for (int i = 0; i < N; i++)
    {
        cost += (row[i] != INT_MAX) ? row[i] : 0,
            cost += (col[i] != INT_MAX) ? col[i] : 0;
    }

    return cost;
}

// Function to print list of cities visited following least cost
void printPath(vector<pair<int, int>> const &list)
{
    for (int i = 0; i < list.size(); i++) {
        cout << list[i].first + 1 << " —> " << list[i].second + 1 << endl;
    }
}

// Comparison object to be used to order the heap
struct comp
{
    bool operator()(const Node* lhs, const Node* rhs) const {
        return lhs->cost > rhs->cost;
    }
};

// Function to solve the traveling salesman problem using Branch and Bound
int solve(int costMatrix[N][N])
{
    // Create a priority queue to store live nodes of the search tree
    priority_queue<Node*, vector<Node*>, comp> pq;

    vector<pair<int, int>> v;

    // create a root node and calculate its cost.
    // The TSP starts from the first city, i.e., node 0
    Node* root = newNode(costMatrix, v, 0, -1, 0);

    // get the lower bound of the path starting at node 0
    root->cost = calculateCost(root->reducedMatrix);

    // Add root to the list of live nodes
    pq.push(root);

    // Finds a live node with the least cost, adds its children to the list of
    // live nodes, and finally deletes it from the list

    while (!pq.empty())
    {
        iterations++;

        // Find a live node with the least estimated cost
        Node* min = pq.top();

        // The found node is deleted from the list of live nodes
        pq.pop();

        // `i` stores the current city number
        int i = min->vertex;

        // if all cities are visited
        if (min->level == N - 1)
        {
            // return to starting city
            min->path.push_back(make_pair(i, 0));

            // print list of cities visited
            printPath(min->path);

            // return optimal cost
            return min->cost;
        }

        // do for each child of min
        // `(i, j)` forms an edge in a space tree
        for (int j = 0; j < N; j++)
        {
            if (min->reducedMatrix[i][j] != INF)
            {
                // create a child node and calculate its cost
                Node* child = newNode(min->reducedMatrix, min->path,
                    min->level + 1, i, j);

                /* Cost of the child =
                    cost of the parent node +
                    cost of the edge(i, j) +
                    lower bound of the path starting at node j
                */

                child->cost = min->cost + min->reducedMatrix[i][j]
                            + calculateCost(child->reducedMatrix);

                // Add a child to the list of live nodes
                pq.push(child);
            }
        }

        // free node as we have already stored edges `(i, j)` in vector.
        // So no need for a parent node while printing the solution.
        delete min;
    }
}

int main()
{
    // cost matrix for traveling salesman problem.
    // change `N` constant to matrix size accordingly
    
    /*  Test 01
     *         
     *  cost = 8 
     *  1 -> 2 -> 4 -> 3 -> 1 */
    /*
    int costMatrix[N][N] =
    {
        {INF, 2, 1, INF},
        {2, INF, 4, 3},
        {1, 4, INF, 2},
        {INF, 3, 2, INF}
    };
    */

    /* Test 02
     *
     * cost = 16
     * 1 -> 3 -> 5 -> 4 -> 2 -> 1 */
    /*
    int costMatrix[N][N] =
    {
        {INF, INF, 1, 5, 8},
        {3, INF, 6, 7, 9},
        {1, 6, INF, 4, 2},
        {5, 7, 4, INF, 3},
        {8, 9, 2, 3, INF}
    };
    */

    /* Test 03
     *
     * cost = 34
     * 1 -> 3 -> 4 -> 2 -> 5 -> 1 */
    
    int costMatrix[N][N] =
    {
        { INF, 10, 8, 9, 7 },
        { 10, INF, 10, 5, 6 },
        { 8, 10, INF, 8, 9 },
        { 9, 5, 8, INF, 6 },
        { 7, 6, 9, 6, INF }
    };

    /* Test 04
     *
     * cost = 50 
     * 1 -> 2 -> 3 -> 5 -> 4 -> 1 */
    /*
    int costMatrix[N][N] =
    {
        {INF, 1, 21, 27, 5},
        {30, INF, 18, 23, 23},
        {27, 29, INF, 20, 10},
        {15, 2, 27, INF, 14},
        {28, 9, 15, 6, INF}
    };
    */

    /* Test 05
     *
     * cost = 62
     * 1 -> 2 -> 3 -> 5 -> 4 -> 1 */
    /*
    int costMatrix[N][N] =
    {
        {INF, 25, 40, 31, 27 },
        {5, INF, 17, 30, 25 },
        {19, 15, INF, 6, 1 },
        {9, 50, 24, INF, 6 },
        {22, 8, 7, 10, INF }
    };
    */

    /* Test 06
     *
     * only one tour possible
     * cost = 15 
     * 1 -> 2 -> 3 -> 4 -> 5 -> 1 */
    /*
    int costMatrix[N][N] =
    {
        {INF, 1, INF, INF, INF},
        {INF, INF, 2, INF, INF},
        {INF, INF, INF, 3, INF},
        {INF, INF, INF, INF, 4},
        {5, INF, INF, INF, INF}
    };
    */

    /* Test 07
     *
     * cost = 19
     * 1 -> 6 -> 5 -> 2 -> 3 -> 4 -> 1 */
    /*
    int costMatrix[N][N] =
    {
        {INF, 5, INF, 6, 5, 4},
        {5, INF, 2, 4, 3, INF},
        {INF, 2, INF, 1, INF, INF},
        {6, 4, 1, INF, 7, INF},
        {5, 3, INF, 7, INF, 3},
        {4, INF, INF, INF, 3, INF}
    };
    */

    /* Test 08
     *
     * cost = 23
     * 1 -> 3 -> 2 -> 4 -> 6 -> 5 -> 1 */
    /*
    int costMatrix[N][N] =
    {
        {INF, 7, 1, 5, 9, 8},
        {7, INF, 8, 6, 10, 4},
        {9, 3, INF, 3, 2, 10},
        {5, 9, 10, INF, 5, 2},
        {2, 6, 8, 9, INF, 6},
        {7, 6, 10, INF, 9, INF}
    };
    */

    /* Test 09 part 1
     *
     * cost = 22
     * 1 -> 8 -> 10 -> 7 -> 4 -> 2 -> 3 -> 5 -> 9 -> 6 -> 1 */
    /*
    int costMatrix[N][N] =
    {
        {INF, 6, 7, 3, 4, 1, 2, 3, 4, 9},
        {4, INF, 1, 8, 8, 8, 7, 8, 10, 4},
        {7, 2, INF, 4, 1, 5, 9, 7, 8, 7},
        {2, 5, 2, INF, 7, 10, 7, 2, 1, 6},
        {4, 2, 8, 9, INF, 10, 3, 10, 2, 9},
        {1, 8, 4, 3, 10, INF, 10, 8, 5, 9},
        {6, 7, 3, 3, 10, 2, INF, 6, 6, 8},
        {9, 10, 4, 5, 3, 6, 9, INF, 9, 2},
        {9, 9, 4, 6, 4, 1, 5, 6, INF, 5},
        {1, 7, 5, 7, 5, 7, 3, 7, 2, INF}
    };
    */

    /* Test 09 part 2
     *
     * cost = 22 
     * 1 -> 2 -> 3 -> 5 -> 7 -> 4 -> 8 -> 10 -> 9 -> 6 -> 1 */
    /*
    int costMatrix[N][N] =
    {
        {INF, 6, INF, INF, INF, INF, INF, INF, INF, INF},
        {4, INF, 1, 8, 8, 8, 7, 8, 10, 4},
        {7, 2, INF, 4, 1, 5, 9, 7, 8, 7},
        {2, 5, 2, INF, 7, 10, 7, 2, 1, 6},
        {4, 2, 8, 9, INF, 10, 3, 10, 2, 9},
        {1, 8, 4, 3, 10, INF, 10, 8, 5, 9},
        {6, 7, 3, 3, 10, 2, INF, 6, 6, 8},
        {9, 10, 4, 5, 3, 6, 9, INF, 9, 2},
        {9, 9, 4, 6, 4, 1, 5, 6, INF, 5},
        {1, 7, 5, 7, 5, 7, 3, 7, 2, INF}
    };
    */

    /* Test 10 part 1
     *
     * cost = 7293
     * 1 -> 8 -> 3 -> 4 -> 5 -> 13 -> 7 -> 9 -> 2 -> 12 -> 11 -> 6 -> 10 -> 1 */
    /*
    int costMatrix[N][N] =
    {
        { INF, 2451, 713, 1018, 1631, 1374, 2408, 213, 2571, 875, 1420, 2145, 1972 },
        { 2451, INF, 1745, 1524, 831, 1240, 959, 2596, 403, 1589, 1374, 357, 579 },
        { 713, 1745, INF, 355, 920, 803, 1737, 851, 1858, 262, 940, 1453, 1260 },
        { 1018, 1524, 355, INF, 700, 862, 1395, 1123, 1584, 466, 1056, 1280, 987 },
        { 1631, 831, 920, 700, INF, 663, 1021, 1769, 949, 796, 879, 586, 371 },
        { 1374, 1240, 803, 862, 663, INF, 1681, 1551, 1765, 547, 225, 887, 999 },
        { 2408, 959, 1737, 1395, 1021, 1681, INF, 2493, 678, 1724, 1891, 1114, 701 },
        { 213, 2596, 851, 1123, 1769, 1551, 2493, INF, 2699, 1038, 1605, 2300, 2099 },
        { 2571, 403, 1858, 1584, 949, 1765, 678, 2699, INF, 1744, 1645, 653, 600 },
        { 875, 1589, 262, 466, 796, 547, 1724, 1038, 1744, INF, 679, 1272, 1162 },
        { 1420, 1374, 940, 1056, 879, 225, 1891, 1605, 1645, 679, INF, 1017, 1200 },
        { 2145, 357, 1453, 1280, 586, 887, 1114, 2300, 653, 1272, 1017, INF, 504 },
        { 1972, 579, 1260, 987, 371, 999, 701, 2099, 600, 1162, 1200, 504, INF }
    };
    */

    /* Test 10 part 2
     *
     * cost = 7293
     * 1 -> 10 -> 6 -> 11 -> 12 -> 2 -> 9 -> 7 -> 13 -> 5 -> 4 -> 3 -> 8 -> 1 */
    /*
    int costMatrix[N][N] =
    {
        { INF, INF, INF, INF, INF, INF, INF, INF, INF, 875, INF, INF, INF },
        { 2451, INF, 1745, 1524, 831, 1240, 959, 2596, 403, 1589, 1374, 357, 579 },
        { 713, 1745, INF, 355, 920, 803, 1737, 851, 1858, 262, 940, 1453, 1260 },
        { 1018, 1524, 355, INF, 700, 862, 1395, 1123, 1584, 466, 1056, 1280, 987 },
        { 1631, 831, 920, 700, INF, 663, 1021, 1769, 949, 796, 879, 586, 371 },
        { 1374, 1240, 803, 862, 663, INF, 1681, 1551, 1765, 547, 225, 887, 999 },
        { 2408, 959, 1737, 1395, 1021, 1681, INF, 2493, 678, 1724, 1891, 1114, 701 },
        { 213, 2596, 851, 1123, 1769, 1551, 2493, INF, 2699, 1038, 1605, 2300, 2099 },
        { 2571, 403, 1858, 1584, 949, 1765, 678, 2699, INF, 1744, 1645, 653, 600 },
        { 875, 1589, 262, 466, 796, 547, 1724, 1038, 1744, INF, 679, 1272, 1162 },
        { 1420, 1374, 940, 1056, 879, 225, 1891, 1605, 1645, 679, INF, 1017, 1200 },
        { 2145, 357, 1453, 1280, 586, 887, 1114, 2300, 653, 1272, 1017, INF, 504 },
        { 1972, 579, 1260, 987, 371, 999, 701, 2099, 600, 1162, 1200, 504, INF }
    };
    */

    /* Test 11
     *
     * cost = 1370
     * 1 -> 3 -> 17 -> 19 -> 16 -> 20 -> 12 -> 2 -> 11 -> 7 -> 14 -> 4 -> 10 -> 13 -> 8 -> 15 -> 5 -> 18 -> 9 -> 6 -> 1 */
    /*
    int costMatrix[N][N] =
    {
        {INF,   243, 57,  248, 144, 66,  120, 281, 61,  294, 171, 238, 307, 211, 242, 186, 49,  84,  101, 254},
        {243, INF,   296, 94,  208, 178, 125, 261, 234, 183, 66,  64,  236, 101, 265, 174, 287, 250, 202, 161},
        {57,  296, INF,   300, 171, 119, 172, 320, 88,  343, 224, 288, 349, 264, 269, 213, 58,  111, 128, 281},
        {248, 94,  300, INF,   161, 182, 134, 196, 238, 98,  97,  158, 151, 39,  200, 243, 297, 234, 231, 250},
        {144, 208, 171, 161, INF,   86,  114, 149, 83,  172, 158, 246, 178, 118, 98,  261, 193, 72,  186, 291},
        {66,  178, 119, 182, 86,  INF,   54,  215, 56,  228, 106, 171, 241, 146, 184, 175, 115, 73,  101, 205},
        {120, 125, 172, 134, 114, 54,  INF,   208, 110, 183, 59,  147, 234, 97,  193, 162, 168, 127, 130, 193},
        {281, 261, 320, 196, 149, 215, 208, INF,   233, 120, 239, 325, 75,  159, 53,  370, 329, 222, 310, 401},
        {61,  234, 88,  238, 83,  56,  110, 233, INF,   255, 162, 232, 262, 201, 181, 222, 110, 23,  137, 267},
        {294, 183, 343, 98,  172, 228, 183, 120, 255, INF,   165, 247, 55,  80,  153, 327, 342, 244, 299, 335},
        {171, 66,  224, 97,  158, 106, 59,  239, 162, 165, INF,   88,  219, 79,  224, 162, 220, 178, 136, 170},
        {238, 64,  288, 158, 246, 171, 147, 325, 232, 247, 88,  INF,   300, 165, 312, 130, 243, 249, 159, 97 },
        {307, 236, 349, 151, 178, 241, 234, 75,  262, 55,  219, 300, INF,   134, 124, 381, 355, 251, 336, 388},
        {211, 101, 264, 39,  118, 146, 97,  159, 201, 80,  79,  165, 134, INF,   157, 241, 260, 190, 213, 249},
        {242, 265, 269, 200, 98,  184, 193, 53,  181, 153, 224, 312, 124, 157, INF,   355, 291, 170, 284, 385},
        {186, 174, 213, 243, 261, 175, 162, 370, 222, 327, 162, 130, 381, 241, 355, INF,   169, 245, 85,  68 },
        {49,  287, 58,  297, 193, 115, 168, 329, 110, 342, 220, 243, 355, 260, 291, 169, INF,   133, 84,  237},
        {84,  250, 111, 234, 72,  73,  127, 222, 23,  244, 178, 249, 251, 190, 170, 245, 133, INF,   161, 284},
        {101, 202, 128, 231, 186, 101, 130, 310, 137, 299, 136, 159, 336, 213, 284, 85,  84,  161, INF,   152},
        {254, 161, 281, 250, 291, 205, 193, 401, 267, 335, 170, 97,  388, 249, 385, 68,  237, 284, 152, INF  }
    };
    */

    cout << "\n\nTotal cost is\n" << solve(costMatrix) << "\n";
    cout << "iterations: " << iterations << "\n";

    return 0;
}

