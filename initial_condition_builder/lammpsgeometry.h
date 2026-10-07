/***

Header for basic classes for LAMMPS geometry

 ***/

#ifndef LAMMPSGEO_H
#define LAMMPSGEO_H

#include <cmath>

using namespace std;

//--------------------------------------------------------------------------------------------------------------

class vec {
  
private:
  double x[3]; // The 3 components of the vector
  
public:
  vec(double x0=0.0, double x1=0.0, double x2=0.0) {
    // constructor, gives zero by default, or the given value
        x[0] = x0;
        x[1] = x1;
        x[2] = x2;
    }
  
  double& operator[](const int &i) {
    if (i < 0 || i >= 3) {
      throw std::out_of_range("Index out of range");
    }
    return x[i];
  }
  const double& operator[](int i) const {
    if (i < 0 || i >= 3) {
      throw std::out_of_range("Index out of range");
    }
    return x[i];
  }

  const vec operator+(const vec &v2) {
    vec p;
    for (int i=0;i<3;i++) {
      p[i]=x[i]+v2[i];
    }
    return p;
  }
  
  // Compute the Euclidean norm of the vector
  double len() const {
    return sqrt(x[0]*x[0] + x[1]*x[1] + x[2]*x[2]);
  }

  // Convert to unit vector
  void make_unit() {
    double L=len();
    for (int i=0;i<3;i++) {
      x[i]/=L;
    }
  }
  
  // Static function to compute dot product of two vectors
  static double dot_product(const vec& v1, const vec& v2) {
    return v1.x[0]*v2.x[0] + v1.x[1]*v2.x[1] + v1.x[2]*v2.x[2];
  }
  
  // Static function to compute cross  product of two vectors
  static vec cross_product(const vec& v1, const vec& v2) {
    return vec(
		    v1.x[1] * v2.x[2] - v1.x[2] * v2.x[1],
		    v1.x[2] * v2.x[0] - v1.x[0] * v2.x[2],
		    v1.x[0] * v2.x[1] - v1.x[1] * v2.x[0]
        );
  }

  // Static function to take vector v and rotate it about vector k, assumes v is perpendicular to k
  static vec rotatePerpUnitVecs(const vec& v, const vec& k, double ang) {
    // assumes v and k are unit vectors and perpendicular to each other
    // ang is in radians
    vec kCrossV = cross_product(k, v);
    
    // Rodrigues' rotation formula for perpendicular vectors (simplified)
    vec vRot = vec(v.x[0] * cos(ang) + kCrossV.x[0] * sin(ang),
			v.x[1] * cos(ang) + kCrossV.x[1] * sin(ang),
			v.x[2] * cos(ang) + kCrossV.x[2] * sin(ang));
    return vRot;
  }
  

};


//--------------------------------------------------------------------------------------------------------------


class quaternion {

private:
  double q[4]; // The 3 components of the vector
  
public:

  quaternion(double q0=1.0, double q1=0.0, double q2=0.0, double q3=0.0) {
    // constructor, gives 1,0,0,0 by default
    q[0] = q0; q[1] = q1; q[2] = q2;  q[3] = q3; 
  }
    
  double& operator[](const int &i) {
    if (i < 0 || i >= 4) {
      throw std::out_of_range("Index out of range");
    }
    return q[i];
  }

  static quaternion make_quat(const vec &,const vec &,const vec &);

  static double sign(const double &x) {return (x >= 0.0) ? +1.0 : -1.0;}
  
};



quaternion quaternion::make_quat(const vec &xax,const vec &yax,const vec &zax) {
  // make a quaternion from a set of 3 unit vectors
    
  double q0,q1,q2,q3,
    r11,r12,r13,
    r21,r22,r23,
    r31,r32,r33,
    r;

  r11=xax[0]; r21=xax[1]; r31=xax[2];
  r12=yax[0]; r22=yax[1]; r32=yax[2];
  r13=zax[0]; r23=zax[1]; r33=zax[2];

  q0=( r11 + r22 + r33 + 1.0f) / 4.0;
  q1=( r11 - r22 - r33 + 1.0f) / 4.0;
  q2=(-r11 + r22 - r33 + 1.0f) / 4.0;
  q3=(-r11 - r22 + r33 + 1.0f) / 4.0;

  if(q0 < 0.0) q0 = 0.0;
  if(q1 < 0.0) q1 = 0.0;
  if(q2 < 0.0) q2 = 0.0;
  if(q3 < 0.0) q3 = 0.0;

  q0 = sqrt(q0);
  q1 = sqrt(q1);
  q2 = sqrt(q2);
  q3 = sqrt(q3);

  if(q0 >= q1 && q0 >= q2 && q0 >= q3) {
    q0 *= +1.0f;
    q1 *= sign(r32 - r23);
    q2 *= sign(r13 - r31);
    q3 *= sign(r21 - r12);
  } else if(q1 >= q0 && q1 >= q2 && q1 >= q3) {
    q0 *= sign(r32 - r23);
    q1 *= 1.0;
    q2 *= sign(r21 + r12);
    q3 *= sign(r13 + r31);
  } else if(q2 >= q0 && q2 >= q1 && q2 >= q3) {
    q0 *= sign(r13 - r31);
    q1 *= sign(r21 + r12);
    q2 *= 1.0;
    q3 *= sign(r32 + r23);
  } else if(q3 >= q0 && q3 >= q1 && q3 >= q2) {
    q0 *= sign(r21 - r12);
    q1 *= sign(r31 + r13);
    q2 *= sign(r32 + r23);
    q3 *= 1.0;
  } else {
    cout<<"quaternion error"<<endl;;
  }
  r = sqrt(q0*q0 + q1*q1 + q2*q2 + q3*q3);
  q0 /= r;
  q1 /= r;
  q2 /= r;
  q3 /= r;

  return  quaternion(q0,q1,q2,q3);
  
}



//--------------------------------------------------------------------------------------------------------------


class atom {

public:

int species,  // LINKER or NUCLEOSOME
  id,
  type, 
  mol,
  ellipse_flag;
  vec x;  // position
  quaternion q;        // orientation
  double density;


  atom() {};
  atom(const double &xx, const double &yy, const double &zz) {
    x[0]=xx; x[1]=yy; x[2]=zz;
  }
  atom(const vec xx) {
    x[0]=xx[0]; x[1]=xx[1]; x[2]=xx[2];
  }
  
};

//--------------------------------------------------------------------------------------------------------------

class bond {

public:
  int id,
    type,
    first,
    second;

  bond(const int &ttype, const int &ffirst, const int &ssecond) :
    type(ttype), first(ffirst), second(ssecond) {};

};

//--------------------------------------------------------------------------------------------------------------


class angle {

public:
    int id,
    type,
    first,
      second,
      third;

  angle(const int &ttype, const int &ffirst, const int &ssecond, const int &tthird) :
    type(ttype), first(ffirst), second(ssecond), third(tthird) {}; 

};

//--------------------------------------------------------------------------------------------------------------


#endif
