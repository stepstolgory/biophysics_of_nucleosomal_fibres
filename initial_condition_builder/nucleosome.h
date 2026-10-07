/***

Header for nucleosome model specific classes and functions. Includes the coordinates.

To obtain coordinates from the structure data files:

We want the first bead to be at 1.0,1.0,1.0, and to convert from angstroms to 
LAMMPS lengths, sigm=2.5nm

Fx=$( awk '{if (NR==1) print $2;}' ../nucleosome_structure2.0/core_beads.dat )
Fy=$( awk '{if (NR==1) print $3;}' ../nucleosome_structure2.0/core_beads.dat )
Fz=$( awk '{if (NR==1) print $4;}' ../nucleosome_structure2.0/core_beads.dat )

## **** NEW 4.0 VERSION
## Add an extra centre bead for each nucleosome. It is a new type (23)
awk -v Fx=$Fx -v Fy=$Fy -v Fz=$Fz '{x=($2-Fx)/25.0+1.0;y=($2-Fy)/25.0+1.0;z=($2-Fz)/25.0+1.0;print x,y,z}' ../nucleosome_structure3.0/centre_core.dat


## **** NEW VERSION --- have added an extra two unwrappable DNA beads on each side
##                      which removes two wrapped beads on each side, and add 2 patches on each side
# The nucleosome beads
# OLD: first 12 beads are DNA sized cores; then there are 15 wrapped DNA beads; then 6 big cores; then 14 patches
# NEW: first 12 beads are DNA sized cores; then there are 11 wrapped DNA beads; then 6 big cores; then 18 patches

Order must be:
  nuc DNA entry
  nuc patches entry
  nuc cores
  nuc patches exit
  nuc DNA exit

# OLD: first we want beads 13-19 as the 'in' DNA beads 
# NEW: first we want beads 13-17 as the 'in' DNA beads 
awk -v F=$Fx '{if (NR>12&&NR<=17) a=a ", " ($2-F)/25.0+1.0}END{print a}' ../nucleosome_structure2.0/core_beads.dat
awk -v F=$Fy '{if (NR>12&&NR<=17) a=a ", " ($3-F)/25.0+1.0}END{print a}' ../nucleosome_structure2.0/core_beads.dat
awk -v F=$Fz '{if (NR>12&&NR<=17) a=a ", " ($4-F)/25.0+1.0}END{print a}' ../nucleosome_structure2.0/core_beads.dat

# OLD: then we want beads 1-12, 20, 28-33 as the core
# NEW: then we want beads 1-12, 18, 24-29 as the core
awk -v F=$Fx '{if (NR<=12||NR==18||(NR>=24&&NR<=29)) a=a ", " ($2-F)/25.0+1.0}END{print a}' ../nucleosome_structure2.0/core_beads.dat
awk -v F=$Fy '{if (NR<=12||NR==18||(NR>=24&&NR<=29)) a=a ", " ($3-F)/25.0+1.0}END{print a}' ../nucleosome_structure2.0/core_beads.dat
awk -v F=$Fz '{if (NR<=12||NR==18||(NR>=24&&NR<=29)) a=a ", " ($4-F)/25.0+1.0}END{print a}' ../nucleosome_structure2.0/core_beads.dat
# OLD: for the types, we want the DNA sized central core to be type 2 (1-12), bead 20 to be type 1, and the large central core to be type 3
# NEW: for the types, we want the DNA sized central core to be type 3 (1-12), bead 18 to be type 2, and the large central core to be type 4
awk '{if (NR!=18) {$1++}; if (NR<=12||NR==18||(NR>=24&&NR<=29)) a=a ", " $1+1}END{print a}' ../nucleosome_structure2.0/core_beads.dat

# OLD: then we want beads 21-27 as the 'out' DNA beads
# NEW: then we want beads 19-23 as the 'out' DNA beads
awk -v F=$Fx '{if (NR>=19&&NR<=23) a=a ", " ($2-F)/25.0+1.0}END{print a}' ../nucleosome_structure2.0/core_beads.dat
awk -v F=$Fy '{if (NR>=19&&NR<=23) a=a ", " ($3-F)/25.0+1.0}END{print a}' ../nucleosome_structure2.0/core_beads.dat
awk -v F=$Fz '{if (NR>=19&&NR<=23) a=a ", " ($4-F)/25.0+1.0}END{print a}' ../nucleosome_structure2.0/core_beads.dat

# then the unwrappable DNA and the patches
# OLD: first 7 are in, second 7 are out
# NEW: first 9 are in, second 9 are out
awk -v F=$Fx '{a=a ", " ($2-F)/25.0+1.0}END{print a}' ../nucleosome_structure2.0/DNA_beads_unwrapable.dat
awk -v F=$Fy '{a=a ", " ($3-F)/25.0+1.0}END{print a}' ../nucleosome_structure2.0/DNA_beads_unwrapable.dat
awk -v F=$Fz '{a=a ", " ($4-F)/25.0+1.0}END{print a}' ../nucleosome_structure2.0/DNA_beads_unwrapable.dat
# OLD: for types, 34-40 are in, 41-47 are out; we want them to go from 4-10
# NEW: for types, 30-38 are in, 39-47 are out; we want them to go from 5-13 then 14 to 22
awk '{if (NR>=30) a=a ", " $1+2}END{print a}' ../nucleosome_structure2.0/core_beads.dat

 ***/

#ifndef NUCLEOSOME_H
#define NUCLEOSOME_H


#include <vector>

#include "lammpsgeometry.h"

using namespace std;


// key to atom species
#define LINKER 1
#define UNWRAPABLE 2
#define NUCLEOSOME 3

// key to atom types
#define DNATYPE 1
#define DNATYPE2 2
#define SMALLCORE 3
#define BIGCORE 4
#define FIRSTPATCHTYPE 5
#define NPATCHTYPES 18       // types 5 to 22
#define CENTREBEADTYPE 23  
#define NATOMTYPES 23


class nucleosome {

public:

  const double correctionAngle=-0.0351079193833743; 
  
  const vector<double> inCRx = { 0.71616, 0.72096, 0.8654, 0.92472, 1.0894 },
    inCRy = { -0.538712, -0.02272, 0.61424, 1.2614, 1.73736 },
    inCRz = { 2.71228, 3.16956, 3.23812, 3.09628, 2.65372 };

  const vector<double> centCRx = { 1, 1.04632, 1.10644, 1.14536, 1.1566, 1.1434, 1.53468, 1.5172, 1.52112, 1.55752, 1.61088, 1.65056, 1.30908, 0.9248, 1.72436, 0.91928, 1.71884, 0.94364, 1.7432 },
    centCRy = { 1, 0.75484, 0.39732, 0.12404, -0.0848, -0.249, -0.30436, -0.23272, -0.10832, 0.10012, 0.43404, 0.70224, 2.07012, 0.95056, 0.95724, 0.38016, 0.38684, 0.56108, 0.56776 },
    centCRz = { 1, 0.89214, 0.87902, 0.953, 1.11384, 1.29932, 1.56908, 1.80348, 2.03264, 2.23228, 2.37508, 2.38172, 1.96244, 1.69736, 1.72324, 1.98872, 2.0146, 1.18916, 1.21504 };
  
  const vector<int> CRtypes = { 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 2, 4, 4, 4, 4, 4, 4 };
  
  const vector<double> outCRx = { 1.53392, 1.70396, 1.77576, 1.93372, 1.95176 },
    outCRy = { 2.06224, 1.83336, 1.30544, 0.70184, 0.052 },
    outCRz = { 1.20032, 0.591348, 0.192864, -0.024944, 0.171452 };
 


  //const int Ncent=CRtypes.size();
  
  const vector<double> inDNAx = { 0.647812, 0.659048, 0.69392, 0.79644, 0.85976, 0.86472, 0.83348, 0.77576, 0.72196 },
    inDNAy = { 2.305, 1.744, 1.2294, 0.5636, -0.10992, -0.68768, -1.11204, -1.14153, -0.982768 },
    inDNAz = { 0.817616, 0.425344, -0.001128, -0.057068, 0.023644, 0.371324, 0.88654, 1.56056, 2.21576 };

  const vector<double> outDNAx = { 1.97328, 1.93308, 1.87132, 1.8294, 1.81768, 1.86624, 1.95468, 1.97612, 1.9128 },
    outDNAy = { -0.568752, -0.980688, -1.25454, -1.08906, -0.71048, -0.14096, 0.49464, 1.13668, 1.8114 },
    outDNAz = { 0.4346, 0.949524, 1.56864, 2.2148, 2.77388, 3.15236, 3.38544, 3.22152, 3.13284 };

  const vector<double> inPATCHtypes = { 5, 6, 7, 8, 9, 10, 11, 12, 13 },
    outPATCHtypes = { 22, 21, 20, 19, 18, 17, 16, 15, 14 };

  //const int NunwrH=inDNAtypes.size();      // there are this many unwrapable DNAs on each side

  const vector<double> centreBeadXYZ = {1.33124, 0.30504, 1.6176};

  
  static void addNuc(vector<atom> &, const int &, const vec &, const double &);


  /***
      nucleosome() {
      // some checks for debugging
      cout<<CRtypes.size()<<" "<<centCRx.size()<<" "<<centCRy.size()<<" "<<centCRz.size()<<endl;
      cout<<inCRx.size()<<" "<<inCRy.size()<<" "<<inCRz.size()<<endl;
      cout<<outCRx.size()<<" "<<outCRy.size()<<" "<<outCRz.size()<<endl;
      cout<<inDNAtypes.size()<<" "<<inDNAx.size()<<" "<<outDNAx.size()<<endl;
      }
  ***/
  
} nuc;


void nucleosome::addNuc(vector<atom> &atoms, const int &nuc_counter, const vec &nuc_position_offset, const double &rotAngle) {

  atom new_atom;

  
  for (int i=0;i<nuc.inPATCHtypes.size();i++) { // the unwrappable DNA
    new_atom = atom( nuc_position_offset[0]+nuc.inDNAx[i],
		     nuc_position_offset[1]+nuc.inDNAy[i],
		     nuc_position_offset[2]+nuc.inDNAz[i] );;
    
    new_atom.species = UNWRAPABLE;
    new_atom.type = DNATYPE;
    new_atom.id = atoms.back().id+1;
    new_atom.mol = 0;
    new_atom.ellipse_flag = 1;
    new_atom.density = 1.0;
    
    atoms.push_back( new_atom );
  }
  for (int i=0;i<nuc.inCRx.size();i++) { // the core inDNA
    new_atom = atom( nuc_position_offset[0]+nuc.inCRx[i],
		     nuc_position_offset[1]+nuc.inCRy[i],
		     nuc_position_offset[2]+nuc.inCRz[i] );
    
    new_atom.species = NUCLEOSOME;
    new_atom.type = DNATYPE2;//nuc.CRtypes[i];
    new_atom.id = atoms.back().id+1;
    new_atom.mol = nuc_counter;
    new_atom.ellipse_flag = 1;
    new_atom.density = 1.0;
 
    if (i==0) { // for ellipsoids, the orienation of this one matters
      vec F,V,U;
      U[0]=nuc.inCRx[1]-nuc.inCRx[0]; // vector pointing to next bead
      U[1]=nuc.inCRy[1]-nuc.inCRy[0];
      U[2]=nuc.inCRz[1]-nuc.inCRz[0];
      U.make_unit();
      V[0]=1.0; V[1]=0.0; V[2]=0.0; // vector in X direction - all we want here is that F is perp to U
      F = vec::cross_product(V,U);
      F.make_unit();
      V = vec::cross_product(U,F);
      F = vec::cross_product(V,U);

      new_atom.q = quaternion::make_quat(F,V,U);
    }
    
    atoms.push_back( new_atom );
  }
  for (int i=0;i<nuc.inPATCHtypes.size();i++) { // the patches
    new_atom = atom( nuc_position_offset[0]+nuc.inDNAx[i],
		     nuc_position_offset[1]+nuc.inDNAy[i],
		     nuc_position_offset[2]+nuc.inDNAz[i] );;
    
    new_atom.species = NUCLEOSOME;
    new_atom.type = nuc.inPATCHtypes[i];
    new_atom.id = atoms.back().id+1;
    new_atom.mol = nuc_counter;
    new_atom.ellipse_flag=1;
    new_atom.density = 1.0;
    
    atoms.push_back( new_atom );
  }
  for (int i=0;i<nuc.centCRx.size();i++) { // the core central
    new_atom = atom( nuc_position_offset[0]+nuc.centCRx[i],
		     nuc_position_offset[1]+nuc.centCRy[i],
		     nuc_position_offset[2]+nuc.centCRz[i] );
    
    new_atom.species = NUCLEOSOME;
    new_atom.type = nuc.CRtypes[i];
    new_atom.id = atoms.back().id+1;
    new_atom.mol = nuc_counter;
    new_atom.ellipse_flag = 1;
    new_atom.density = 1.0;
    
    atoms.push_back( new_atom );
  }
  // now add the centre bead
  new_atom = atom( nuc_position_offset[0]+nuc.centreBeadXYZ[0],
		   nuc_position_offset[1]+nuc.centreBeadXYZ[1],
		   nuc_position_offset[2]+nuc.centreBeadXYZ[2] );
  new_atom.species = NUCLEOSOME;
  new_atom.type = CENTREBEADTYPE;
  new_atom.id = atoms.back().id+1;
  new_atom.mol = nuc_counter;
  new_atom.ellipse_flag = 1;
  new_atom.density = 1.0;
  { // set the orientation
    vec F,V,U;
    // U vecotr should be aligned perpendicular to the cyliner, along the x-axis
    U[0]=1.0; U[1]=0.0; U[2]=0.0;  // vector in X direction - this must be perpendicular to the cylinder
    F[0]=0.0; F[1]=0.0; F[2]=-1.0; // vector in -Z direction
    V[0]=0.0; V[1]=1.0; V[2]=0.0;  // vector in Y direction
    // ^ first one I is correct ^ .... 
    //U[0]=0.0; U[1]=1.0; U[2]=0.0;  // vector in Y direction - this must be perpendicular to the cylinder
    //F[0]=1.0; F[1]=0.0; F[2]=0.0;  // vector in X direction - but does not matter
    //V[0]=0.0; V[1]=0.0; V[2]=-1.0; // vector in -Z direction - but does not matter
    //U[0]=0.0; U[1]=0.0; U[2]=1.0; 
    //F[0]=1.0; F[1]=0.0; F[2]=0.0; 
    //V[0]=0.0; V[1]=1.0; V[2]=0.0; 
    new_atom.q = quaternion::make_quat(F,V,U);
  }
  atoms.push_back( new_atom );
  for (int i=0;i<nuc.outPATCHtypes.size();i++) { // the patches
    new_atom = atom( nuc_position_offset[0]+nuc.outDNAx[i],
		     nuc_position_offset[1]+nuc.outDNAy[i],
		     nuc_position_offset[2]+nuc.outDNAz[i] );;
    
    new_atom.species = NUCLEOSOME;
    new_atom.type = nuc.outPATCHtypes[i];
    new_atom.id = atoms.back().id+1;
    new_atom.mol = nuc_counter;
    new_atom.ellipse_flag = 1;
    new_atom.density = 1.0;
    
    atoms.push_back( new_atom );
  }
  for (int i=0;i<nuc.outCRx.size();i++) { // the core outDNA
    new_atom = atom( nuc_position_offset[0]+nuc.outCRx[i],
		     nuc_position_offset[1]+nuc.outCRy[i],
		     nuc_position_offset[2]+nuc.outCRz[i] );
    
    new_atom.species=NUCLEOSOME;
    new_atom.type = DNATYPE2; //nuc.CRtypes[i];
    new_atom.id = atoms.back().id+1;
    new_atom.mol = nuc_counter;
    new_atom.ellipse_flag = 1;
    new_atom.density = 1.0;
    
    if (i==nuc.outCRx.size()-1) { // for ellipsoids, the orienation of this one matters
      // it must point toward the first of the unwrapable DNAs
      vec F,V,U;
      U[0]=nuc.outDNAx[0]-nuc.outCRx[i]; // vector pointing to next bead
      U[1]=nuc.outDNAy[0]-nuc.outCRy[i];
      U[2]=nuc.outDNAz[0]-nuc.outCRz[i];
      U.make_unit();
      V[0]=1.0; V[1]=0.0; V[2]=0.0; // vector in X direction - all we want here is that F is perp to U
      F = vec::cross_product(V,U);
      F.make_unit();
      V = vec::cross_product(U,F);
      F = vec::cross_product(V,U);
      
      // add here a rotation about the U vector, to get the desired angle between nucleosome planes
      F = vec::rotatePerpUnitVecs(F,U,nuc.correctionAngle+rotAngle);
      V = vec::rotatePerpUnitVecs(V,U,nuc.correctionAngle+rotAngle);
      
      new_atom.q = quaternion::make_quat(F,V,U);
    }
    
    atoms.push_back( new_atom );
  }
  for (int i=0;i<nuc.outPATCHtypes.size();i++) { // the unwrappable DNA
    new_atom = atom( nuc_position_offset[0]+nuc.outDNAx[i],
		     nuc_position_offset[1]+nuc.outDNAy[i],
		     nuc_position_offset[2]+nuc.outDNAz[i] );;
    
    new_atom.species = UNWRAPABLE;
    new_atom.type = DNATYPE;
    new_atom.id = atoms.back().id+1;
    new_atom.mol = 0;
    new_atom.ellipse_flag = 1;
    new_atom.density = 1.0;
    
    atoms.push_back( new_atom );
  }

  
}


#endif
