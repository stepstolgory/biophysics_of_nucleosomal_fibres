

#include <iostream>
#include <fstream>
#include <cmath>
#include <set>

using namespace std;

#include "lammpsgeometry.h"
#include "nucleosome.h"

// key to atom species -- these are set in nucleosome.h

// key to atom types -- these are set in nucleosome.h

// key to bond and angle types
#define BONDTYPE 1
#define NBONDTYPES 1
#define BENDANGLETYPE 1
#define TWANGLETYPE 2
#define TWENDANGLETYPE 3
#define NANGLETYPES 3

constexpr double PI = 3.14159265358979323846;


vec rand_unit_vec() {
  // return a random unit vector
  vec x;
  double theta=double(rand())/double(RAND_MAX)*PI,
    phi=double(rand())/double(RAND_MAX)*2.0*PI;
  x[0]=sin(theta)*cos(phi);
  x[1]=sin(theta)*sin(phi);
  x[2]=cos(theta);
  return x;
}

int main(int argc, char *argv[]) {

  // get options from command line
  if (argc<5) {
    cout<<"Usage :"<<endl;
    cout<<"       ./generate_ic -f filename -s seed [-N numberNucleosomes] [-L1 initialLinkerLength] [-L internalLinkerLengths] [-LF finalLinkerLength] [-b boxLength] [-e ellipseFlag]"<<endl;
    cout<<"where       filename               is the output file name (must not exist already)"<<endl;
    cout<<"            seed                   an integer seed for random number generator"<<endl;
    cout<<"            numberNucleosomes      is the required number of nucleosomes (Default=1)"<<endl;
    cout<<"            initialLinkerLength    number of DNA beads for first linker (Default=4)"<<endl;
    cout<<"            internalLinkerLengths  number of DNA beads for internal linkers (Default=4)"<<endl;
    cout<<"            finalLinkerLength      number of DNA beads for final linker (Default=4)"<<endl;
    cout<<"            boxLength              size of simulation box in LAMMPS length units (Default=100.0)"<<endl;
    cout<<"            ellipseFlag            1 for ellipsoids, 0 for point atoms (Default=0)"<<endl;
    exit(EXIT_FAILURE);
  }

  
  string fname = "";
  int initialLinker = 4,                // length of DNA before first nuc (beads)
    LinkerLenght = 4,                  // length of intermediate linkers (beads)
    finalLinker = 4,                    // length of DNA after final nuc (beads)
    Nnucs = 1,                          // number or nucleosomes
    seed = 0;                       // seed for randoms
  bool ellipseFlag = false;
  double box = 100.0,
    relativeAngle = 0.0;

  
  // parse command line 
  int argi=1;
  while (argi < argc) {

    if ( string(argv[argi]) == "-f" ) { // input file
      if (!(argi+1 < argc)) {
        cerr<<"Error parsing command line (-f)"<<endl;
        exit(EXIT_FAILURE);
      }
      fname = string(argv[argi+1]);
      argi += 2;
      
    } else if ( string(argv[argi]) == "-N" ) {
      if (!(argi+1 < argc)) {
        cerr<<"Error parsing command line (-f)"<<endl;
        exit(EXIT_FAILURE);
      }
      Nnucs = atoi(argv[argi+1]);
      argi += 2;
      
    } else if ( string(argv[argi]) == "-L1" ) {
      if (!(argi+1 < argc)) {
        cerr<<"Error parsing command line (-L1)"<<endl;
        exit(EXIT_FAILURE);
      }
      initialLinker = atoi(argv[argi+1]);
      argi += 2;

    } else if ( string(argv[argi]) == "-L" ) {
      if (!(argi+1 < argc)) {
        cerr<<"Error parsing command line (-L)"<<endl;
        exit(EXIT_FAILURE);
      }
      LinkerLenght = atoi(argv[argi+1]);
      argi += 2;
		
    } else if ( string(argv[argi]) == "-LF" ) {
      if (!(argi+1 < argc)) {
        cerr<<"Error parsing command line (-LF)"<<endl;
        exit(EXIT_FAILURE);
      }
      finalLinker = atoi(argv[argi+1]);
      argi += 2;
	
    } else if ( string(argv[argi]) == "-b" ) {
      if (!(argi+1 < argc)) {
        cerr<<"Error parsing command line (-b)"<<endl;
        exit(EXIT_FAILURE);
      }
      box = atof(argv[argi+1]);
      argi += 2;
      
    } else if ( string(argv[argi]) == "-s" ) {
      if (!(argi+1 < argc)) {
        cerr<<"Error parsing command line (-s)"<<endl;
        exit(EXIT_FAILURE);
      }
      seed = atoi(argv[argi+1]);
      argi += 2;

    } else if ( string(argv[argi]) == "-e" ) {
      if (!(argi+1 < argc)) {
        cerr<<"Error parsing command line (-e)"<<endl;
        exit(EXIT_FAILURE);
      }
      ellipseFlag = atoi(argv[argi+1]);
      argi += 2;
	  
    } else {
      cerr<<"Error parsing command line (unrecognised option)"<<endl;
      exit(EXIT_FAILURE);
    }
      
  }

  // check parameters
  if ( fname == "" ) {
    cout<<"File name not provided."<<endl;
    exit(EXIT_FAILURE);
  }
  if ( seed = 0 ) {
    cout<<"Seed not provided."<<endl;
    exit(EXIT_FAILURE);
  }

  
  // write a message
  cout<<"Generating an initial configuration with "<<endl
      <<"        "<<Nnucs<<" nucleosomes"<<endl
      <<"        "<<initialLinker<<" beads in the initial linker"<<endl
      <<"        "<<LinkerLenght<<" beads in internal linkers"<<endl
      <<"        "<<finalLinker<<" beads in the final linker"<<endl
      <<"        "<<box<<" box size (square)"<<endl
      <<"and the atoms will";
  if (!ellipseFlag) { cout<<" not"; }
  cout<<" be ellipsoids."<<endl;
  cout<<"Each bead is 5bp, so the linker length is "<<LinkerLenght*5<<"bp."<<endl;
  if ( LinkerLenght % 2 ) {
    cout<<"Since the linker is 10n+5 bp, the relative orientaion of neighbouring nucleosomes will be pi"<<endl;
    relativeAngle = M_PI;
  } else {
    cout<<"Since the linker is 10n bp, the relative orientaion of neighbouring nucleosomes will be 0"<<endl;
    relativeAngle = 0.0;
  }


  double hbox=0.5*box;
  
  int atom_types=NATOMTYPES,
    bond_types=NBONDTYPES,
    angle_types=NANGLETYPES;

  ifstream inf;
  ofstream ouf;
  
  atom new_atom;
  vector<atom> atoms;
  vec nuc_position_offset;
  int nuc_counter = 0;

  vector<bond> bonds;
  vector<angle> angles;

  
  // set up randoms
  srand(seed);

  
  // open the file and check
  inf.open( fname );
  if ( inf.good() ) {
    cout<<"ERROR : output file "<<fname<<" already exists. Will not overwrite."<<endl;
    exit(EXIT_FAILURE);
  }
  inf.close();
  
  // place the initial DNA bead
  atoms.push_back( atom() ); // will be at 0,0,0 by default
  atoms.back().species = LINKER;
  atoms.back().type = DNATYPE;
  atoms.back().id = 1;
  atoms.back().mol = 0;
  atoms.back().ellipse_flag = 1;
  atoms.back().density=1.0;
    
  // add the remaining initial linker atoms
  for (int i=1;i<initialLinker;i++) {
    new_atom = atom( atoms.back().x+rand_unit_vec() );
    new_atom.species = LINKER;
    new_atom.type = DNATYPE;
    new_atom.id = atoms.back().id+1;
    new_atom.mol = 0;
    new_atom.ellipse_flag = 1;
    new_atom.density = 1.0;
  
    atoms.push_back( new_atom );
  }

  // add Nnuc-1 groups of nucleosome and linkers
  for (int i=0;i<Nnucs-1;i++) {

    // add nucleosome
    nucleosome::addNuc(atoms, ++nuc_counter,atoms.back().x,relativeAngle); // increment counter and pass;
                                                             // take atoms.back().x as position offset
    // add linker
    for (int i=0;i<LinkerLenght;i++) {
      new_atom = atom( atoms.back().x+rand_unit_vec() );
      new_atom.species = LINKER;
      new_atom.type = DNATYPE;
      new_atom.id = atoms.back().id+1;
      new_atom.mol = 0;
      new_atom.ellipse_flag = 1;
      new_atom.density = 1.0;
      
      atoms.push_back( new_atom );
    }

  }
  
  // add the final nucleosome
  nucleosome::addNuc(atoms, ++nuc_counter,atoms.back().x,relativeAngle); // increment counter and pass;
                                                           // take back as position offset
  // add the final stretch of DNA
  for (int i=0;i<finalLinker;i++) {
    new_atom = atom( atoms.back().x+rand_unit_vec() );
    new_atom.species = LINKER;
    new_atom.type = DNATYPE;
    new_atom.id=atoms.back().id+1;
    new_atom.mol = 0;
    new_atom.ellipse_flag = 1;
    new_atom.density = 1.0;
    
    atoms.push_back( new_atom );
  }

  
  // generated bond topology
  for (vector<atom>::const_iterator it=atoms.begin()+1; it!=atoms.end(); ++it) {
    vector<atom>::const_iterator last=prev(it);  
    // if both i and i-1 are LINKER or UNWRAPABLE -- add a bond
    // if i-1 is UNWRAPABLE and i is NUCLEOSOME -- add a bond
    // if i-1 is NUCLEOSOME and i is UNWRAPABLE -- add a bond
    // otherwise don't

    if ( (it->species == LINKER || it->species ==  UNWRAPABLE)
	 && (last->species == LINKER || last->species ==  UNWRAPABLE) ) {
      bonds.push_back( bond(BONDTYPE,last->id,it->id) );
    } else if ( (it->species == NUCLEOSOME)
	 && (last->species == LINKER || last->species ==  UNWRAPABLE) ) {
      bonds.push_back( bond(BONDTYPE,last->id,it->id) );
    } else if ( (it->species == LINKER || it->species ==  UNWRAPABLE)
	 && (last->species == NUCLEOSOME ) ) {
      bonds.push_back( bond(BONDTYPE,last->id,it->id) );
    }    
  }

  
  // generatate angle topology
  for (vector<atom>::const_iterator it=atoms.begin()+2; it!=atoms.end(); ++it) {
    vector<atom>::const_iterator last=prev(it);  
    vector<atom>::const_iterator lastlast=prev(last);
    // if i, i-1, and i-2 are LINKER or UNWRAPABLE -- add an angle
    // if i, i-1, are LINKER or UNWRAPABLE and i-2 is NUCLEOSOME -- add an angle
    // if i, is LINKER or UNWRAPABLE and i-1, i-2 are NUCLEOSOME -- add an angle
    
    // if i and i-1 are NUCLEOSOME and i-2 is LINKER or UNWRAPABLE -- add an angle   
    // if i, is NUCLEOSOME and i-1, i-2 are LINKER or UNWRAPABLE -- add an angle

    if ( (lastlast->species == LINKER || lastlast->species ==  UNWRAPABLE)
	 && (last->species == LINKER || last->species ==  UNWRAPABLE)
	 && (it->species == LINKER || it->species ==  UNWRAPABLE) ) {
      angles.push_back( angle(BENDANGLETYPE,lastlast->id,last->id,it->id) );
    } else if ( (lastlast->species == LINKER || lastlast->species ==  UNWRAPABLE)
	 && (last->species == LINKER || last->species ==  UNWRAPABLE)
	 && it->species == NUCLEOSOME ) {
      angles.push_back( angle(BENDANGLETYPE,lastlast->id,last->id,it->id) );
    } else  if ( (lastlast->species == LINKER || lastlast->species ==  UNWRAPABLE)
	 && last->species == NUCLEOSOME && it->species == NUCLEOSOME ) {
      angles.push_back( angle(BENDANGLETYPE,lastlast->id,last->id,it->id) );
    } else if ( lastlast->species == NUCLEOSOME && last->species == NUCLEOSOME
	 && (it->species == LINKER || it->species ==  UNWRAPABLE) ) {
      angles.push_back( angle(BENDANGLETYPE,lastlast->id,last->id,it->id) );
    } else if ( lastlast->species == NUCLEOSOME
	 && (last->species == LINKER || last->species ==  UNWRAPABLE)
	 && (it->species == LINKER || it->species ==  UNWRAPABLE) ) {
      angles.push_back( angle(BENDANGLETYPE,lastlast->id,last->id,it->id) );
    }
    
  }
    
  // generate twist angle topology
  // looks like bonds, but need to be careful at the end
  if (ellipseFlag) {
    for (vector<atom>::const_iterator it=atoms.begin()+1; it!=atoms.end()-1; ++it) {
      vector<atom>::const_iterator last=prev(it);  
      // if both i and i-1 are LINKER or UNWRAPABLE -- add a bond
      // if i-1 is UNWRAPABLE and i is NUCLEOSOME -- add a bond
      // if i-1 is NUCLEOSOME and i is UNWRAPABLE -- add a bond
      // otherwise don't

      if ( (it->species == LINKER || it->species ==  UNWRAPABLE)
	   && (last->species == LINKER || last->species ==  UNWRAPABLE) ) {
	angles.push_back( angle(TWANGLETYPE,last->id,it->id,it->id+1) );
      } else if ( (it->species == NUCLEOSOME)
		  && (last->species == LINKER || last->species ==  UNWRAPABLE) ) {
	angles.push_back( angle(TWANGLETYPE,last->id,it->id,it->id+1) );
      } else if ( (it->species == LINKER || it->species ==  UNWRAPABLE)
		  && (last->species == NUCLEOSOME ) ) {
	angles.push_back( angle(TWANGLETYPE,last->id,it->id,it->id+1) );
      }    
    }

    // THIS BIT WAS CAUSING PROBLEMS
    // second to last bead - third needs to be different, lets make it third to last bead
    //angles.push_back( angle(TWANGLETYPE,(atoms.end()-2)->id,(atoms.end()-1)->id,(atoms.end()-3)->id) );
    // last bead - it can have the same bead ids, but a different angle type
    //angles.push_back( angle(TWENDANGLETYPE,(atoms.end()-2)->id,(atoms.end()-1)->id,(atoms.end()-3)->id) );

    // Fixed version -- final angle is the twist angle between N-1 and N, which should be a different type
    angles.push_back( angle(TWENDANGLETYPE,(atoms.end()-2)->id,(atoms.end()-1)->id,(atoms.end()-3)->id) );
  }

  // set angle types accorsing to what was added to the angles list
  set<int> angle_types_list;
  for (int i=0;i<angles.size();i++) {
    angle_types_list.insert( angles[i].type );
  }
  angle_types = angle_types_list.size();

  
  // output
  ouf.open( fname );

  // the header
  ouf<< "LAMMPS Description"<<endl<<endl;
  ouf<<atoms.size()<< " atoms"<<endl;
  if (ellipseFlag) {
    ouf<<atoms.size()<<" ellipsoids"<<endl;
  }
  ouf<<bonds.size()<< " bonds"<<endl;
  ouf<<angles.size()<< " angles"<<endl<<endl;;
  ouf<<atom_types<<" atom types"<<endl;
  ouf<<bond_types<<" bond types"<<endl;
  ouf<<angle_types<<" angle types"<<endl<<endl;
  ouf<<-hbox<<" "<<hbox<<" xlo xhi"<<endl;
  ouf<<-hbox<<" "<<hbox<<" ylo yhi"<<endl;
  ouf<<-hbox<<" "<<hbox<<" zlo zhi"<<endl;
  ouf<<"Masses"<<endl<<endl;
  for (int i=0;i<atom_types;i++) {
    ouf<<i+1<<" 1.0"<<endl;
  }
  ouf<<endl;

  // atoms section
  ouf<<"Atoms"<<endl<<endl;
  if (ellipseFlag) {
    for (int i=0;i<atoms.size();i++) {
      ouf<<" "<<atoms[i].id<<" "<<atoms[i].type<<" "
	 <<atoms[i].x[0]<<" "<<atoms[i].x[1]<<" "<<atoms[i].x[2]
	 <<" "<<atoms[i].mol<<" "<<atoms[i].ellipse_flag<<" "<<atoms[i].density<<endl;
    }
  } else {

    for (int i=0;i<atoms.size();i++) {
      ouf<<" "<<atoms[i].id<<" "<<atoms[i].mol<<" "<<atoms[i].type
	 <<" "<<atoms[i].x[0]<<" "<<atoms[i].x[1]<<" "<<atoms[i].x[2]
	 <<" 0 0 0"<<endl;
    }
    ouf<<endl;
  }

  // ellipsoids section
  if (ellipseFlag) {
    ouf<<endl<<" Ellipsoids"<<endl<<endl;
    for (int i=0;i<atoms.size();i++) {
      if (atoms[i].ellipse_flag==1) {
	ouf<<" "<<atoms[i].id<<" 1 1 1 "
	   <<atoms[i].q[0]<<" "<<atoms[i].q[1]<<" "<<atoms[i].q[2]<<" "<<atoms[i].q[3]<<endl; 
      }
    }
  }
  
  // velocities section
  ouf<<endl<<"Velocities"<<endl<<endl;
  if (ellipseFlag) {
    for (int i=0;i<atoms.size();i++) {
      ouf<<" "<<atoms[i].id<<" 0 0 0 0 0 0"<<endl;
    }
  }  else {
    for (int i=0;i<atoms.size();i++) {
      ouf<<" "<<atoms[i].id<<" 0 0 0"<<endl;
    }
  }
      
  // bonds and anlges section
  ouf<<endl<<"Bonds"<<endl<<endl;
  for (int i=0;i<bonds.size();i++) {
    ouf<<" "<<i+1<<" "<<bonds[i].type<<" "<<bonds[i].first<<" "<<bonds[i].second<<endl;
  }
  ouf<<endl<<"Angles"<<endl<<endl;
  for (int i=0;i<angles.size();i++) {
    ouf<<" "<<i+1<<" "<<angles[i].type<<" "
       <<angles[i].first<<" "<<angles[i].second<<" "<<angles[i].third<<endl;
  }
  
  ouf.close();
  
}
