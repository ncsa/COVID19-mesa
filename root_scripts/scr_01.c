void src_01() {
    auto d = ROOT::RDF::MakeCsvDataFrame("data.csv");
    auto maxStep = d.Max<Long_t>("Step");

    std::vector<const Long_t> stepno_;
    std::vector<const Double_t> average_;

    for (Long_t i = 0; i < maxStep.GetValue(); i++) {
        stepno_.push_back(i);
        auto a = d.Filter("Step == i").Mean<Double_t>("Susceptible").GetValue();
        average_.push_back(a);
    }

    std::function<const Double_t&(Double_t)> ave = [&average_](Double_t i) -> const Double_t& { return average_[i];};
    std::function<const Long_t&(Long_t)> ste = [&stepno_](Long_t i) -> const Long_t& { return stepno_[i];};
    d.Define("average", ave);
    d.Define("stepno", ste);
    auto myGraph1 = d.Graph<Long_t, Double_t>("stepno", "average");
    myGraph1->Draw();
}