
void src_01() {
    auto fileNameUrl = "https://uillinoisedu-my.sharepoint.com/personal/xinyih8_illinois_edu/_layouts/15/download.aspx?e=Dwvgn5&share=Ec6S-peuh7BDtyuo0GBIk_kBAboIat589t7kYfoCHeuDRw/cu-current-R0-callibration.csv";
    auto fileName = "cu-current-R0-callibration.csv";
    if(gSystem->AccessPathName(fileName))
       TFile::Cp(fileNameUrl, fileName);
    auto d = ROOT::RDF::MakeCsvDataFrame(fileName);


   std::vector<Int_t> stepno_;
   std::vector<Double_t> average_;
   std::vector<Double_t> dayAverage_;
   std::vector<Double_t> std_;
   std::vector<Double_t> upperCI_;
   std::vector<Double_t> lowerCI_;

   //create average and draw it
   auto maxStep = d.Max<Int_t>("Step");
   for (Int_t i = 0; i < maxStep; i++) {
      stepno_.push_back(i);
      average_.push_back(d.Filter("Step == i").Mean<Double_t>("Susceptible"));
   }

   std::function<const Double_t&(Double_t)> ave = [&average_](Double_t i) -> const Double_t& { return average_[i];};
   std::function<const Int_t&(Int_t)> ste = [&stepno_](Int_t i) -> const Int_t& { return stepno_[i];};
   d.Define("average", ave);
   d.Define("stepno", ste);
   auto myGraph1 = d.Graph<Int_t, Double_t>("stepno", "average");
   0 1   2   3       4        5     6  7  8  9
   0 01 012 0123    0123456 1234567 
   //create 7 days average
   for (Int_t i = 0; i < maxStep; i++) {
      Double_t values = 0;
      Int_t k = 7;
      if (i < k) {
         for (Int_t j = 0; j <= i; j++) {
            values += average_[j];
         }
            dayAverage_.push_back(values/i);
      }
      else if (i >= k) {
         for (Int_t j = i-k; j <= i; j++) {
            values += average_[j];
         }
         dayAverage_.push_back(values/k);
      }
   }
   std::function<const Double_t&(Double_t)> save = [&dayaAverage_](Double_t i) -> const Double_t& { return dayAverage_[i];};
   d.Define("dayAverage", save);
   auto myGraph2 = d.Graph<Int_t, Double_t>("stepno", "dayAverage");
   myGraph2->Draw();

   Double_t ci95 = 0.95; 
   for (Int_t i = 0; i < maxStep; i++) {
      std_.push_back(d.Filter("Step == i").StdDev<double>("Susceptible"));
      //error_.push_back(), how to get z score?
      upperCI_.push_back(average_[i]+error_[i]);
      lowerCI_.push_back(average_[i]-error_[i]);
   }


    auto c = new TCanvas();
    c->SetLogx();
    c->SetLogy();
    myGraph1->DrawClone();
    myGraph2->DrawClone();
}