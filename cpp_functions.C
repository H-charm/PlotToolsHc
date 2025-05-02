  double deltaR(double eta1, double eta2, double phi1, double phi2) {
    if (abs(eta1) > 9 || abs(eta2) > 9)
      return 99;
    if (abs(phi1) > 6.3 || abs(phi2) > 6.3)
      return 99;
    double deta = eta1 - eta2;
    double dphi = TVector2::Phi_mpi_pi(phi1 - phi2);
    return std::sqrt(deta * deta + dphi * dphi);
  }