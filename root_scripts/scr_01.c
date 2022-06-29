void src_01() {
    auto d = ROOT::RDF::MakeCsvDataFrame("data.csv");
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
    myGraph1->Draw();
}