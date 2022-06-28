#include <iostream>

using namespace std;

test2(){

   TFile *myFile = TFile::Open("cu-current-R0-callibration.root");
   TTree* T=(TTree*)myFile->Get("T");
   // T->Show(10);

   std::vector<Int_t> stepno; //store the number of steps
   std::vector<vector<Double_t>> values;//store vectors of value at each step
   std::vector<Double_t> average; // store the mean value at each step
   std::vector<Double_t> dayAverage; // 7 days average
   std::vector<Int_t> sampleSize;//store the number of observations at each step

   std::vector<Double_t> error;//store error at each step
   std::vector<Double_t> std;
   std::vector<Double_t> upperCI;
   std::vector<Double_t> lowerCI;

   Int_t stepMax = 3839;
   
   // cout << tree->GetEntries() << endl;

   for (Int_t i = 0; i < stepMax; i++) {
      Int_t j = 0;
      Double_t value = 0;
      vector<Double_t> vec;
      for (int k = 0; k < T->GetEntries(); k++) {
         // tree->GetEntry(k);
         TLeaf *sus = T->GetLeaf("Susceptible");
         sus->GetBranch()->GetEntry(k);
         Double_t valuesus = sus->GetValue();
         TLeaf *st = T->GetLeaf("Step");
         st->GetBranch()->GetEntry(k);
         Double_t valuestep = st->GetValue();
         if (valuestep == i) {
            j++;
            value += valuesus;
            vec.push_back(valuesus);
         }
      }
      values.push_back(vec);
      sampleSize.push_back(j);
      average.push_back(value/j);
      stepno.push_back(i);
   }
   for (Int_t i = 0; i < stepMax; i++) {
      Double_t values = 0;
      Int_t k = 7;
      if (i < k) {
         for (Int_t j = 0; j <= i; j++) {
            values += average[j];
         }
            dayAverage.push_back(values/i);
      }
      else if (i >= k) {
         for (Int_t j = i-k; j <= i; j++) {
            values += average[j];
         }
         dayAverage.push_back(values/k);
      }
   }
   T->Branch("average", &average);
   T->Branch("dayAverage", &dayAverage);
   T->Branch("stepno", &stepno); 

   T->Write("", TObject::kOverwrite);

   Double_t ci95 = 0.95; 
   for (Int_t i = 0; i < stepMax; i++) {
      gRandom->RndmArray(values[i].size(),values[i].data());
      std.push_back(TMath::StdDev(values[i].begin(), values[i].end()));
      error.push_back(qt((ci + 1)/2, df = sampleSize[i] - 1) * std[i] / Math::sqrt(sampleSize[i]));
      upperCI.push_back(average[i]+error[i]);
      lowerCI.push_back(average[i]-error[i]);
   }

   // for(int i = 0; i < average.size();i++) {
   //    std::cout << average[i] << std::endl;
   // }
   
   auto c3 = new TCanvas("c3","c3",600, 400);
 
   auto mg = new TMultiGraph("mg","mg");

   auto gr1 = new TGraph( stepMax, stepno, average );
   gr1->SetName("gr1");
   gr1->SetTitle("graph 1");
   gr1->SetMarkerStyle(21);
   gr1->SetDrawOption("AP");
   gr1->SetLineColor(2);
   gr1->SetLineWidth(4);
   gr1->SetFillStyle(0);
 
   auto gr2 = new TGraph( stepMax, stepno, upperCI );
   gr2->SetName("gr2");
   gr2->SetTitle("graph 2");
   gr2->SetMarkerStyle(22);
   gr2->SetMarkerColor(2);
   gr2->SetDrawOption("P");
   gr2->SetLineColor(3);
   gr2->SetLineWidth(4);
   gr2->SetFillStyle(0);
 
   auto gr3 = new TGraph( stepMax, stepno, lowerCI );
   gr3->SetName("gr3");
   gr3->SetTitle("graph 3");
   gr3->SetMarkerStyle(23);
   gr3->SetLineColor(4);
   gr3->SetLineWidth(4);
   gr3->SetFillStyle(0);
 
   mg->Add( gr1 );
   mg->Add( gr2 );
 
   gr3->Draw("ALP");
   mg->Draw("LP");
   c3->BuildLegend();

   T->Write("", TObject::kOverwrite);
}
