// No partial branching: visit all 15^7 complete row tuples, then filter.
// Different radial-path representation (Boolean closure), no Python bitset DFS.
#include <algorithm>
#include <array>
#include <cstdint>
#include <iostream>
#include <stdexcept>
#include <vector>
int main() {
    constexpr int n=7;
    std::array<std::vector<std::array<int,2>>,n> choices;
    for(int i=0;i<n;++i)for(int a=0;a<n;++a)for(int b=a+1;b<n;++b)
        if(a!=i&&b!=i)choices[i].push_back({a,b});
    constexpr uint64_t total=170859375;
    std::array<uint64_t,6> counts{};
    std::vector<std::array<int,n>> survivors;
    for(uint64_t code=0;code<total;++code){
        ++counts[0];uint64_t x=code;
        bool arrow[n][n]{};
        std::array<int,n> masks{};
        for(int i=0;i<n;++i){auto row=choices[i][x%15];x/=15;
            for(int j:row){arrow[i][j]=true;masks[i]|=1<<j;}}
        bool bad=false;
        for(int i=0;i<n&&!bad;++i)for(int j=i+1;j<n;++j)
            if(arrow[i][j]&&arrow[j][i]){bad=true;break;}
        if(bad)continue;
        ++counts[1];
        bool reach[n][n]{};
        for(int a=0;a<n;++a)for(int b=a+1;b<n;++b)reach[a][b]=arrow[a][b]||arrow[b][a];
        for(int k=0;k<n;++k)for(int a=0;a<k;++a)for(int b=k+1;b<n;++b)
            reach[a][b]=reach[a][b]||(reach[a][k]&&reach[k][b]);
        for(int low=0;low<n&&!bad;++low)for(int high=low+2;high<n&&!bad;++high)
            if(arrow[high][low])for(int k=low+1;k<high;++k)
                if((arrow[low][k]||arrow[k][low])&&reach[k][high]){bad=true;break;}
        if(bad)continue;
        ++counts[2];
        for(int a=0;a<n&&!bad;++a)for(int b=a+1;b<n&&!bad;++b){
            int lo=-1,hi=-1;
            for(int c=0;c<n;++c)if(arrow[a][c]&&arrow[b][c]){if(lo<0)lo=c;else hi=c;}
            if(hi>=0&&!(lo<b&&b<hi))bad=true;
        }
        if(bad)continue;
        ++counts[3];
        for(int a=0;a<n&&!bad;++a)for(int b=0;b<n&&!bad;++b)if(arrow[a][b])
            for(int c=0;c<n&&!bad;++c)if(arrow[a][c]&&arrow[b][c])
                for(int d=0;d<n;++d)if(d!=a&&arrow[b][d]&&arrow[c][d]){bad=true;break;}
        if(bad)continue;
        ++counts[4];
        for(int a=0;a<n&&!bad;++a)for(int b=a+1;b<n&&!bad;++b)if(arrow[a][b])
            for(int c=b+1;c<n;++c)if(arrow[a][c]&&arrow[b][c]){bad=true;break;}
        if(bad)continue;
        ++counts[5];survivors.push_back(masks);
    }
    std::sort(survivors.begin(),survivors.end());
    std::cout<<"{\"complete_tuples\":"<<counts[0]<<",\"reciprocal_free\":"<<counts[1]
             <<",\"after_radial_path\":"<<counts[2]<<",\"after_common_supplier\":"<<counts[3]
             <<",\"after_diamond\":"<<counts[4]<<",\"after_transitive_radius_order\":"<<counts[5]
             <<",\"graphs\":[";
    for(size_t i=0;i<survivors.size();++i){if(i)std::cout<<',';std::cout<<'[';
        for(int j=0;j<n;++j){if(j)std::cout<<',';std::cout<<survivors[i][j];}std::cout<<']';}
    std::cout<<"],\"exhausted\":true}\n";
}
