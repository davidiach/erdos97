// Exhaustive integer-only audit of a finite metric, not a Euclidean solver.
#include <gmpxx.h>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>
using Z=mpz_class;
int main(int argc,char**argv){
 try{
  if(argc!=2)throw std::runtime_error("usage: check_metric matrix.txt");
  std::ifstream f(argv[1]);int n;Z scale,radius;
  if(!(f>>n>>scale>>radius)||n<4||n>1000||scale<=0||radius<=0)throw std::runtime_error("invalid header");
  std::vector<std::vector<Z>> d(n,std::vector<Z>(n));
  for(auto &row:d)for(auto &x:row)if(!(f>>x))throw std::runtime_error("truncated matrix");
  std::string extra;if(f>>extra)throw std::runtime_error("trailing data");
  unsigned long long equalities=0,triangles=0,quads=0,kalmanson=0,ptolemy=0;
  int min_degree=n;Z min_distance=radius, min_tri=radius;
  for(int i=0;i<n;i++){
   if(d[i][i]!=0)throw std::runtime_error("nonzero diagonal");
   int degree=0;
   for(int j=0;j<n;j++)if(i!=j){
    if(d[i][j]<=0||d[i][j]!=d[j][i])throw std::runtime_error("not a positive symmetric distance array");
    if(d[i][j]<min_distance)min_distance=d[i][j];
    if(d[i][j]==radius)degree++;
   }
   if(degree<4)throw std::runtime_error("a vertex is not rich at the common radius");
   if(degree<min_degree)min_degree=degree;
   equalities+=degree;
  }
  for(int i=0;i<n;i++)for(int j=i+1;j<n;j++)for(int k=j+1;k<n;k++){
   Z x=d[i][j]+d[i][k]-d[j][k];
   Z y=d[i][j]+d[j][k]-d[i][k];
   Z z=d[i][k]+d[j][k]-d[i][j];
   if(x<=0||y<=0||z<=0)throw std::runtime_error("strict triangle failure");
   if(x<min_tri)min_tri=x;
   if(y<min_tri)min_tri=y;
   if(z<min_tri)min_tri=z;
   triangles+=3;
  }
  Z x,y,z;
  for(int i=0;i<n;i++)for(int j=i+1;j<n;j++)for(int k=j+1;k<n;k++)for(int l=k+1;l<n;l++){
   if(d[i][k]+d[j][l]<=d[i][j]+d[k][l]||d[i][k]+d[j][l]<=d[i][l]+d[j][k])throw std::runtime_error("strict Kalmanson failure");
   kalmanson+=2;
   x=d[i][j]*d[k][l];y=d[i][k]*d[j][l];z=d[i][l]*d[j][k];
   if(x+y<=z||x+z<=y||y+z<=x)throw std::runtime_error("strict Ptolemy failure");
   ptolemy+=3;quads++;
  }
  // 2*Gram avoids rational arithmetic. Three planar displacement vectors
  // necessarily have zero determinant, regardless of the coordinate order.
  std::vector<std::vector<Z>> G(3,std::vector<Z>(3));
  for(int i=0;i<3;i++)for(int j=0;j<3;j++)G[i][j]=d[0][i+1]*d[0][i+1]+d[0][j+1]*d[0][j+1]-d[i+1][j+1]*d[i+1][j+1];
  Z det=G[0][0]*(G[1][1]*G[2][2]-G[1][2]*G[2][1])-G[0][1]*(G[1][0]*G[2][2]-G[1][2]*G[2][0])+G[0][2]*(G[1][0]*G[2][1]-G[1][1]*G[2][0]);
  if(det==0)throw std::runtime_error("specified nonplanarity certificate vanished");
  Z divisor=8;for(int k=0;k<6;k++)divisor*=scale;
  if(det%divisor!=0)throw std::runtime_error("unexpected nonintegral Gram determinant");
  Z normalized=det/divisor;
  std::cout<<"{\n  \"status\": \"all exact checks passed\",\n  \"n\": "<<n<<",\n  \"common_radius_incidences\": "<<equalities<<",\n  \"minimum_common_radius_degree\": "<<min_degree<<",\n  \"strict_triangle_inequalities\": "<<triangles<<",\n  \"quadruples\": "<<quads<<",\n  \"strict_kalmanson_inequalities\": "<<kalmanson<<",\n  \"strict_ptolemy_inequalities\": "<<ptolemy<<",\n  \"normalized_gram_determinant\": \""<<normalized<<"\",\n  \"planar_euclidean\": false\n}\n";
 }catch(const std::exception&e){std::cerr<<e.what()<<"\n";return 1;}
 return 0;
}
