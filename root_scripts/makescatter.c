using namespace ROOT;

void makescatter() {
   TFile *myFile = TFile::Open("data.root");
   TTree* T=(TTree*)myFile->Get("T");

   //construct dataframe
   RDataFrame d("T", "cu-current-R0-callibration.root");
   //draw scatter plot
   //{"h2", "ptD0 vs Dm_d", 30, 0.135, 0.165, 30, -3, 6},
   //auto mycanvas = new TCanvas();
   auto h = d.Histo2D({"myHisto", "My Title", 5, 0.5, 5.5, 256, -400, 400}, "Step", "Susceptible");
   h->Draw();
   
   // std::vector<Int_t> stepno_;
   // std::vector<Double_t> average_;
   // std::vector<Double_t> dayAverage_;
   // std::vector<Double_t> std_;
   // std::vector<Double_t> upperCI_;
   // std::vector<Double_t> lowerCI_;

   // //create average and draw it
   // auto maxStep = d.Max<Int_t>("Step");
   // for (Int_t i = 0; i < maxStep; i++) {
   //    stepno_.push_back(i);
   //    avergae_.push_back(d.Filter("Step == i").Mean<Double_t>("Susceptible"));
   // }
   // // https://stackoverflow.com/questions/29610318/what-is-the-return-type-of-a-lambda-expression-if-an-item-of-a-vector-is-returne
   // std::function<const Double_t&(Double_t)> ave = [&average_](Double_t i) -> const Double_t& { return average_[i];};
   // std::function<const Int_t&(Int_t)> ste = [&stepno_](Int_t i) -> const Int_t& { return stepno_[i];};
   // d.Define("average", ave);
   // d.Define("stepno", ste);
   // auto myGraph1 = d.Graph<Int_t, Double_t>("stepno", "average");
   // myGraph1->Draw();

   // //create 7 days average
   // for (Int_t i = 0; i < maxStep; i++) {
   //    Double_t values = 0;
   //    Int_t k = 7;
   //    if (i < k) {
   //       for (Int_t j = 0; j <= i; j++) {
   //          values += average_[j];
   //       }
   //          dayAverage_.push_back(values/i);
   //    }
   //    else if (i >= k) {
   //       for (Int_t j = i-k; j <= i; j++) {
   //          values += average_[j];
   //       }
   //       dayAverage_.push_back(values/k);
   //    }
   // }
   // std::function<const Double_t&(Double_t)> save = [&dayaAverage_](Double_t i) -> const Double_t& { return dayAverage_[i];};
   // d.Define("dayAverage", save);
   // auto myGraph2 = d.Graph<Int_t, Double_t>("stepno", "dayAverage");
   // myGraph2->Draw();

   // Double_t ci95 = 0.95; 
   // for (Int_t i = 0; i < maxStep; i++) {
   //    std_.push_back(d.Filter("Step == i").StdDev<double>("Susceptible"));
   //    //error_.push_back(), how to get z score?
   //    upperCI_.push_back(average_[i]+error_[i]);
   //    lowerCI_.push_back(average_[i]-error_[i]);
   // }

}
