void MakeTree(TString csvFile = "cu-current-R0-callibration") {   
   gSystem->ChangeDirectory("C:\\Users\\14037\\COVID19-mesa\\outcomes");

   TFile *hfile = hfile = TFile::Open(csvFile + ".root","RECREATE");

   TTree *tree = new TTree("T", csvFile + "Tree");

   tree->ReadFile("../outcomes/" + csvFile + ".csv","index/I:Step/I:N/D:Susceptible/D:Exposed/D:Asymptomatic/D:SymptQuarantined/D:AsymptQuarantined/D:Severe/D:Recovered/D:Deceased/D:Isolated/D:CumulPrivValue/D:CumulPublValue/D:CumulTestCost/D:Rt/D:Employed/D:Unemployed/D:Tested/D:Traced/D:Iteration");

   tree->Print();
   tree->Write();

   delete hfile;
}
