
void src_01() {

    auto d = ROOT::RDF::MakeCsvDataFrame("cu-current-R0-callibration.csv");

    auto h = d.Histo2D({"h2", "ptD0 vs Dm_d", 30, 0.135, 0.165, 30, -3, 6}, "Step", "Susceptible");
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
    // d.Define("average", ave);
    // d.Define("stepno", ste);
    // auto myGraph1 = d.Graph<Int_t, Double_t>("stepno", "average");
    // myGraph1->Draw();
}