
void src_01() {
    //auto fileNameUrl = "C:/Users/14037/COVID19-mesa/outcomes/cu-current-R0-callibration.csv";
    //auto fileNameUrl = "https://uillinoisedu-my.sharepoint.com/:x:/g/personal/xinyih8_illinois_edu/EZCPkWd3IidMhJMzGFtBedIBBHBHzcMSeL2GgoKTm5sysA?e=55QVWz/cu-current-R0-callibration.csv";
    //auto fileName = "cu-current-R0-callibration.csv";
    auto fileNameUrl = "http://root.cern.ch/files/tutorials/df014_CsvDataSource_MuRun2010B.csv";
    auto fileName = "df014_CsvDataSource_MuRun2010B_cpp.csv";
    if(gSystem->AccessPathName(fileName))
       TFile::Cp(fileNameUrl, fileName);
    auto d = ROOT::RDF::MakeCsvDataFrame(fileName);

    //auto h = d.Histo2D({"h2", "ptD0 vs Dm_d", 30, 0.135, 0.165, 30, -3, 6}, "Step", "Susceptible");
    auto h = d.Histo2D({"h2", "ptD0 vs Dm_d", 30, 0.135, 0.165, 30, -3, 6}, "Q2", "M");
    h->Draw();

    // auto maxStep = d.Max("Step");

    // std::vector<Int_t> stepno_;
    // std::vector<Double_t> average_;

    // for (Int_t i = 0; i <= maxStep; i++) {
    //     stepno_.push_back(i);
    //     auto a = d.Filter("Step == i").Mean("Susceptible");
    //     average_.push_back(a);
    // }


    // std::function<Double_t&(Double_t)> ave = [&average_](Double_t i) -> Double_t& { return average_[i];};
    // std::function<Int_t&(Int_t)> ste = [&stepno_](Int_t i) -> Int_t& { return stepno_[i];};
    // auto d2 = d.Define("average", ave);
    //            .Define("stepno", ste);
    // auto myGraph1 = d2.Histo2D("stepno", "average");

    // auto c = new TCanvas();
    // c->SetLogx();
    // c->SetLogy();
    // myGraph1->DrawClone();
}