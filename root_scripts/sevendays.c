void sevendays(TString columnName = "Susceptible",TString csvFile = "cu-current-R0-callibration",Double_t c_level = 0.95,Int_t k = 7) {
    Int_t           Step;
    Double_t        Susceptible;

    TFile *hfile = TFile::Open("../outcomes/" + csvFile + ".root","READ");
    TTree *tree = (TTree*)hfile->Get("T");

    cout<<tree->GetEntries()<<endl;

    tree->SetBranchAddress("Step",&Step);
    tree->SetBranchAddress(columnName,&Susceptible);

    Int_t maxStep = tree->GetMaximum("Step");//3839
    Int_t al = maxStep+1;//array length = 3840
    Int_t entries = tree->GetEntries();//115200
    Int_t ns = entries/al;//number of simulations = 30
    Double_t ci_a = 1 - c_level;

    Double_t x[al];
    Double_t y[al];
    Double_t ky[al];
    Double_t yel[al];
    Double_t yeh[al];
    Double_t lci95[al];
    Double_t hci95[al];
    Double_t y_sem[al];

    for (int i = 0; i < ns; ++i) {
        for (int j = 0; j < al; ++j) {
            Int_t entry = i*al+j;
            tree->GetEntry(entry);
            if (i == 0) {
                x[j] = j;
                y[j] = 0;
                ky[j] = 0;
                y_sem[j] = 0;
            }
            y[j] += Susceptible;
            y_sem[j] += Susceptible*Susceptible;
        }
    } 
    for (int j = 0; j < al; ++j) {
        y[j] = y[j]/ns;
        Double_t variance = fabs(y_sem[j]/ns - y[j]*y[j]);
        Double_t std = sqrt(variance/(ns-1));
        y_sem[j] = std/sqrt(ns);
        lci95[j] = TMath::StudentQuantile(ci_a/2, ns-1)*y_sem[j] + y[j]; 
        hci95[j] = TMath::StudentQuantile(1-ci_a/2, ns-1)*y_sem[j] + y[j];
        yel[j] = y[j] - lci95[j];
        yeh[j] = hci95[j] - y[j];
    }

    for (int j = 0; j < al; ++j) {
        if (j < 96*k) { 
            for (int i = 0; i <= j; ++i) {
                ky[j] += y[i];
            }
            ky[j] = ky[j]/(j+1);
        }
        else {
            for (int i = j-(96*k -1 ); i <= j; ++i) { 
                ky[j] += y[i];
            }
            ky[j] = ky[j]/(96*k); 
        }
    }

    auto gf = new TGraphAsymmErrors(al,x,y,nullptr,nullptr,yel,yeh);
    gf->Draw("A4");
    gf->GetXaxis()->SetTitle("Step");
    gf->GetYaxis()->SetTitle(columnName);
    gf->SetFillColorAlpha(kBlue-7,0.3);
    gf->SetFillStyle(1003);

    auto gf2 = new TGraph(al,x,ky);
    gf2->Draw("L");

    gStyle->SetOptTitle(0);
    gPad->Print(k + csvFile + ", " + columnName + "," + c_level + ".ps");
} 