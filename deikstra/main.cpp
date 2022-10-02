#include <bits/stdc++.h>
using namespace std;

const double INF = 1e9;

pair<double, vector<int>> Dijkstra (vector<vector<pair<int, double>>> &matrix, int start, int finish)
{
    int n = matrix.size();
    vector<pair<double, vector<int> > > lengths (n, make_pair(INF, vector<int>()));
    lengths[start] = make_pair(start, vector<int>(1, start));
    //init query
    set < tuple<double, int, vector<int>> > mas;
    mas.insert (make_tuple(lengths[start].first, start, vector<int>(1,start)));
    while (!mas.empty()) {
        //take first
        int v = get<1>(*mas.begin());
        double len = get<0>(*mas.begin());
        vector<int> road = get<2>(*mas.begin());
        //erase first
        mas.erase (mas.begin());
        //next if long path
        if (len > lengths[v].first) continue;
        //enum all nodes, that have road
        for(int i = 0; i < matrix[v].size(); ++i) {
            //node number
            int n_v = matrix[v][i].first;
            //road len
            double n_len = len + matrix[v][i].second;
            //add if road len less
            if (lengths[n_v].first > n_len) {
                mas.erase (make_tuple(lengths[n_v].first, n_v, lengths[n_v].second));
                road.push_back(n_v);
                lengths[n_v] = make_pair(n_len, road);
                mas.insert (make_tuple (n_len, n_v, road));
                road.pop_back();
            }
        }
    }
    return lengths[finish];
};




int main() {
    ifstream  roads("../roads.txt", ios_base::in),
    city("../cities.txt", ios_base::in);
    ofstream out("../dj.txt", ios_base::out);
    if (!city.is_open()){
        return -1;
    }
    map<string, int> names;
    string s;
    int i = -1;
    while(!city.eof()){
        city >> s;
        names[s] = ++i;
        city >> s >> s;
    }
    cout << names.size();
    city.close();
    vector< vector< pair<int, double> > > graph (names.size(), vector<pair<int, double>>());
    if (!roads.is_open()) return -1;

    while(!roads.eof()){
        string city1, city2;
        roads >> city1;
        if (names.count(city1) == 0){
            string p;
            roads >> p;
            city1 += " " + p;
        }
        if (names.count(city1) == 0 ){
            cout << city1 << "\n";
            return 0;
        }
        double x, y;
        roads >> x >> y >> city2;
        if (names.count(city2) == 0){
            string p;
            roads >> p;
            city2 += " " + p;
        }
        if (names.count(city2) == 0){
            cout << city2 << "\n";
            return 0;
        }
        double len;
        roads >> len;
        int c1 = names[city1], c2 = names[city2];
        graph[min(c1, c2)].push_back(make_pair(max(c1, c2), len));
    }
    roads.close();

    cout << "start\n";
    //построить кратчайший путь от одного города до другого
    for (int i = 0; i < names.size(); ++i){
        for (int j = i + 1; j < names.size(); ++j){
            auto x = Dijkstra(graph, i, j);
            if (x.first == INF) continue;
            cout << i << " " << j << " \n";
            for (auto x : x.second){
                out << x << ' ';
            }
            out << x.first << "\n";
        }
    }
    cout << "finish\n";
    out.close();
    return 0;
}
