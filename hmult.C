//macro to add histogram files
//NOTE: This macro is kept for back compatibility only.
//Use instead the executable $ROOTSYS/bin/hadd
//
//This macro will add histograms from a list of root files and write them
//to a target root file. The target file is newly created and must not be
//identical to one of the source files.
//
//Author: Sven A. Schmidt, sven.schmidt@cern.ch
//Date:   13.2.2001

//This code is based on the hadd.C example by Rene Brun and Dirk Geppert,
//which had a problem with directories more than one level deep.
//(see macro hadd_old.C for this previous implementation).
//
//The macro from Sven has been enhanced by
//   Anne-Sylvie Nicollerat <Anne-Sylvie.Nicollerat@cern.ch>
// to automatically add Trees (via a chain of trees).
//
//To use this macro, modify the file names in function hadd.
//
//NB: This macro is provided as a tutorial.
//    Use $ROOTSYS/bin/hadd to merge many histogram files



#include <iostream>
#include <string>
#include "TChain.h"
#include "TFile.h"
#include "TH1.h"
#include "TTree.h"
#include "TKey.h"
#include "Riostream.h"

#include <boost/program_options.hpp>
using namespace boost::program_options;

void MergeRootfile( TDirectory *target, TList *sourcelist, double fac );
void hmult( const TString& source, const TString& target, double fac );

int main( int argc, char** argv) {
	  std::cout << "Using Boost "     
          << BOOST_VERSION / 100000     << "."  // major version
          << BOOST_VERSION / 100 % 1000 << "."  // minor version
          << BOOST_VERSION % 100                // patch level
          << std::endl;

	auto isGood = false;
	variables_map vm;

	try
	{
		std::string inputfilename;
		std::string outputfilename;
		
		options_description desc{"Multiply all histograms in a file except for those with 'data_obs' in the name by a constant factor (hist->Scale(fac))"};
		desc.add_options()
			("help,h", "Print this message and quit")
			("input,i", value<std::string>(&inputfilename), "Input ROOT file")
			("output,o", value<std::string>(&outputfilename), "Output ROOT file")
			("fac", value<double>()->default_value(1.f), "Multiplication factor");

		store(parse_command_line(argc, argv, desc), vm);
		notify(vm);

		if (vm.count("help"))
			std::cout << desc << '\n';
		if (vm.count("input") && vm.count("output")) {
			std::cout << "All histograms in FILE: " << vm["input"].as<std::string>() << '\n';
			std::cout << "Will be multiplied by a FACTOR: " << vm["fac"].as<double>() << '\n';
			std::cout << "Output FILE: " << vm["output"].as<std::string>() << '\n';
			isGood=true;
		} else {
			std::cerr << "Required parameters are missing or something is wrong" << std::endl;
			std::cerr << "Terminating..." << std::endl;
		}
	}
	catch (const error &ex)
	{
		std::cerr << ex.what() << '\n';
	}

	if (isGood) hmult(vm["input"].as<std::string>(),vm["output"].as<std::string>(),vm["fac"].as<double>());
	return 0;
}

void showprogress( double progress ) {
	const int barWidth = 70;

	std::cout << "[";
	int pos = barWidth * progress;
	for (int i = 0; i < barWidth; ++i) {
		if (i < pos) std::cout << "=";
		else if (i == pos) std::cout << ">";
		else std::cout << " ";
	}
	std::cout << "] " << int(progress * 100.0) << " %\r";
	std::cout.flush();
}

void hmult( const TString& source, const TString& target, double fac ) {

   // in an interactive ROOT session, edit the file names
   // Target and FileList, then
   // root > .L hadd.C
   // root > hadd()

   auto Target = TFile::Open( target, "RECREATE" );

   auto FileList = new TList();
   FileList->Add( TFile::Open(source) );

   MergeRootfile( Target, FileList, fac );
   Target->Close();
   delete FileList;
   delete Target;

}

void MergeRootfile( TDirectory *target, TList *sourcelist, double fac ) {

   std::cout << "Target path: " << target->GetPath() << std::endl;
   TString path( (char*)strstr( target->GetPath(), ":" ) );
   path.Remove( 0, 2 );

   TFile *first_source = (TFile*)sourcelist->First();
   first_source->cd( path );
   TDirectory *current_sourcedir = gDirectory;
   //gain time, do not add the objects in the list in memory
   Bool_t status = TH1::AddDirectoryStatus();
   TH1::AddDirectory(kFALSE);

   // loop over all keys in this directory
   TChain *globChain = 0;
   TIter nextkey( current_sourcedir->GetListOfKeys() );
   TKey *key, *oldkey=0;

   // for progress tracking purpose
   auto nkeys = (double)current_sourcedir->GetListOfKeys()->GetEntries();
   auto histnum = 0.;

   while ( (key = (TKey*)nextkey())) {

      //keep only the highest cycle number for each key
      if (oldkey && !strcmp(oldkey->GetName(),key->GetName())) continue;

      // read object from first source file
      first_source->cd( path );
      TObject *obj = key->ReadObj();
      TH1 *h1 = nullptr;
      if ( obj->IsA()->InheritsFrom( TH1::Class() ) ) {
	 
         h1 = (TH1*)obj->Clone();
	 TString name(obj->GetTitle());

         // descendant of TH1 -> merge it

         std::cout << "Multiplying histogram " << obj->GetName() << std::endl;
         h1 = (TH1*)obj->Clone();
	 h1 -> Sumw2();
	 if (!name.Contains("Data")) {				// Skip lumiscaling of data histograms
		if (!( name.Contains("TTJetsPowheg4nJets") || 
		       name.Contains("TTJetsPowheg6nJets") || 
		       name.Contains("TTJetsPowheg8nJets") )) // Skip low cycle number TTJets histograms
			h1 -> Scale(fac);
		else {
			std::cout << "Skipping " << name.Data() << std::endl;
			h1 = nullptr;
			continue;
		}
	 } else std::cout << "Skipping " << name.Data() << std::endl;

      } else if ( obj->IsA()->InheritsFrom( TDirectory::Class() ) ) {
         // it's a subdirectory

         std::cout << "Found subdirectory " << obj->GetName() << std::endl;

         // create a new subdir of same name and title in the target file
         target->cd();
         TDirectory *newdir = target->mkdir( obj->GetName(), obj->GetTitle() );
	 h1 = nullptr;

         // newdir is now the starting point of another round of merging
         // newdir still knows its depth within the target file via
         // GetPath(), so we can still figure out where we are in the recursion
         MergeRootfile( newdir, sourcelist, fac );

      } else {

         // object is of no type that we know or can handle
         std::cout << "Unknown object type, name: "
         << obj->GetName() << " title: " << obj->GetTitle() << std::endl;
	 h1 = nullptr;
	 continue;
      }

      // now write the merged histogram (which is "in" obj) to the target file
      // note that this will just store obj in the current directory level,
      // which is not persistent until the complete directory itself is stored
      // by "target->Write()" below
      if ( h1 ) {
         target->cd();

	 h1->Write( key->GetName() );
      }

   } // while ( ( TKey *key = (TKey*)nextkey() ) )

   // save modifications to target file
   target->SaveSelf(kTRUE);
   TH1::AddDirectory(status);
}
