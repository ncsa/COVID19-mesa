void MakeTree(TString csvFile = "cu-current-R0-callibration") {   
   
   TFile *hfile = hfile = TFile::Open("../outcomes/" + csvFile + ".root","RECREATE");

   TTree *tree = new TTree("T", csvFile + "Tree");

   tree->ReadFile("../outcomes/" + csvFile + ".csv","index/I:Step/I:N/D:Susceptible/D:Exposed/D:Asymptomatic/D:SymptQuarantined/D:AsymptQuarantined/D:Severe/D:Recovered/D:Deceased/D:Isolated/D:CumulPrivValue/D:CumulPublValue/D:CumulTestCost/D:Rt/D:Employed/D:Unemployed/D:Tested/D:Traced/D:Iteration");

   tree->Print();
   tree->Write();

   delete hfile;
}
