void draw(TString columnName="Susceptible") {
    Int_t           Step;
    Double_t        Susceptible;

    TFile *hfile = TFile::Open("../outcomes/cu-current-R0-callibration.root","READ");
    TTree *tree = (TTree*)hfile->Get("T");

    tree->SetBranchAddress("Step",&Step);
    tree->SetBranchAddress(columnName,&Susceptible);

    Double_t x[3840];
    Double_t y[3840];
    Double_t yel[3840];
    Double_t yeh[3840];
    Double_t lci95[3840];
    Double_t hci95[3840];
    Double_t y_sem[3840];

    for (int i = 0; i < 30; ++i) {
        for (int j = 0; j < 3840; ++j) {
            Int_t entry = i*3840+j;
            tree->GetEntry(entry);
            if (i == 0) {
                x[j] = j;
                y[j] = 0;
                y_sem[j] = 0;
            }
            y[j] += Susceptible;
            y_sem[j] += Susceptible*Susceptible;
        }
    } 
    for (int j = 0; j < 3840; ++j) {
        y[j] = y[j]/30.;
        Double_t variance = fabs(y_sem[j]/30. - y[j]*y[j]);
        Double_t std = sqrt(variance/(29.));
        y_sem[j] = std/sqrt(30.);
        lci95[j] = TMath::StudentQuantile(0.025,29)*y_sem[j] + y[j];
        hci95[j] = TMath::StudentQuantile(0.975,29)*y_sem[j] + y[j];
        yel[j] = y[j] - lci95[j];
        yeh[j] = hci95[j] - y[j];
    }

    auto gf = new TGraphAsymmErrors(3840,x,y,nullptr,nullptr,yel,yeh);
    gf->Draw("A4");
    gf->GetXaxis()->SetTitle("Step");
    gf->GetYaxis()->SetTitle(columnName);
    gf->SetFillColorAlpha(kBlue-7,0.3);
    gf->SetFillStyle(1003);

    auto gf2 = new TGraph(3840,x,y);
    gf2->Draw("L");

    gStyle->SetOptTitle(0);
    gPad->Print(columnName + ".png");
}