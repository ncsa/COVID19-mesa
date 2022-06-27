#include <iostream>

using namespace std;

void test() {
   // Simplified version of cernbuild.C.
   // This macro to read data from an ascii file and
   // create a root file with a TTree

   
   Int_t           A;
   Int_t           Step;
   Int_t           N;
   Double_t        Susceptible;
   Double_t        Exposed;
   Double_t        Asymptomatic;
   Double_t        SymptQuarantined;
   Double_t        AsymptQuarantined;
   Double_t        Severe;
   Double_t        Recovered;
   Double_t        Deceased;
   Double_t        Isolated;
   Double_t        CumulPrivValue;
   Double_t        CumulPublValue;
   Double_t        CumulTestCost;
   Double_t        Rt;
   Double_t        Employed;
   Double_t        Unemployed;
   Int_t           Tested;
   Int_t           Traced;
   Int_t           Iteration;

   cout << "file opened" << endl;

   gSystem->ChangeDirectory("C:\\Users\\14037\\COVID19-mesa\\outcomes");
   // open File with raw Data
   FILE *fp = fopen("cu-current-R0-callibration.csv","r");

   
   // create File
   TFile *hfile = hfile = TFile::Open("cu-current-R0-callibration.root","RECREATE");

   // create Tree
   TTree *tree = new TTree("T","R0-callibration Tree");

   // create Branches
   tree->Branch("A",&A,"A/I");
   tree->Branch("Step",&Step,"Step/I");
   tree->Branch("N",&N,"N/I");
   tree->Branch("Susceptible",&Susceptible,"Susceptible/D");
   tree->Branch("Exposed",&Exposed,"Exposed/D");
   tree->Branch("Asymptomatic",&Asymptomatic,"Asymptomatic/D");
   tree->Branch("SymptQuarantined",&SymptQuarantined,"SymptQuarantined/D");
   tree->Branch("AsymptQuarantined",&AsymptQuarantined,"AsymptQuarantined/D");
   tree->Branch("Severe",&Severe,"Severe/D");
   tree->Branch("Recovered",&Recovered,"Recovered/D");
   tree->Branch("Deceased",&Deceased,"Deceased/D");
   tree->Branch("Isolated",&Isolated,"Isolated/D");
   tree->Branch("CumulPrivValue",&CumulPrivValue,"CumulPrivValue/D");
   tree->Branch("CumulPublValue",&CumulPublValue,"CumulPublValue/D");
   tree->Branch("CumulTestCost",&CumulTestCost,"CumulTestCost/D");
   tree->Branch("Rt",&Rt,"Rt/D");
   tree->Branch("Employed",&Employed,"Employed/D");
   tree->Branch("Unemployed",&Unemployed,"Unemployed/D");
   tree->Branch("Tested",&Tested,"Tested/I");
   tree->Branch("Traced",&Traced,"Traced/I");
   tree->Branch("Iteration",&Iteration,"Iteration/I");

   //fill the tree
   tree->ReadFile("cu-current-R0-callibration.csv");



   TCanvas *c1 = new TCanvas("c1","graph",700,500);

   //create graph

   tree->Draw("Susceptible:Step>>graph");

   
   graph->GetXaxis()->SetTitle("Step");
   graph->GetYaxis()->SetTitle("Susceptible");

   graph->GetYaxis()->SetRangeUser(0., 1.);
   tree->Print();
   tree->Write();

   // std::vector<Int_t> stepno; //store the number of steps
   // std::vector<vector<Double_t>> values;//store vectors of value at each step
   // std::vector<Double_t> average; // store the mean value at each step
   // std::vector<Double_t> dayAverage; // 7 days average
   // std::vector<Int_t> sampleSize;//store the number of observations at each step

   // std::vector<Double_t> error;//store error at each step
   // std::vector<Double_t> std;
   // std::vector<Double_t> upperCI;
   // std::vector<Double_t> lowerCI;



   // for (Int_t i = 0; i < 3839; i++) {
   //    Int_t j = 0;
   //    Double_t value = 0;
   //    vector<Double_t> vec;
   //    for (int k = 0; k<tree->GetEntries(); k++) {
   //       // tree->GetEntry(k);
   //       TLeaf *sus = tree->GetLeaf("Susceptible");
   //       sus->GetBranch()->GetEntry(k);
   //       Double_t valuesus = sus->GetValue();
   //       TLeaf *st = tree->GetLeaf("Step");
   //       st->GetBranch()->GetEntry(k);
   //       Double_t valuestep = st->GetValue();
   //       if (valuestep == i); {
   //          j++;
   //          value += valuesus;
   //          vec.push_back(valuesus);
   //       }
   //    }
   //    values.push_back(vec);
   //    sampleSize.push_back(j);
   //    average.push_back(value/j);
   //    stepno.push_back(i);
   // }

   hfile->Write();

   fclose(fp);
   delete hfile;
}

//String_t *feature, bool ave_7day, bool with_CI