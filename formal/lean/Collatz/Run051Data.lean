import Collatz.Run048Data

/-!
Generated RUN-051 semantic payload data.

This file contains literal payload fields only.  The checks below
inspect those fields in Lean; they are not Python PASS theorems.
-/

namespace Collatz

def run051S3DebtCerts : List S3DebtExactCert := run046S3DebtCerts
def run051S4ParentMapCerts : List S4ParentMapCert := run046S4ParentMapCerts
def run051S6LemmaCerts : List S6LemmaCert := run046S6LemmaCerts
def run051NaturalKernelCert : NaturalViabilityKernelCert := run046NaturalKernelCert
def run051TopLevelCerts : TopLevelCertBundle := run046TopLevelCerts
def run051S4SemanticWitnesses : List S4ParentTransitionSemanticWitness := run048S4SemanticWitnesses

def run051S3SemanticRoles : List S3SemanticRolePayload :=
[
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_0266ffc831aef802",
  branchId := "P9:r66178075:d26",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P9",
  targetNode := "P27",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P9 mixed-log debt rank",
  measureTargetExpr := "P27 mixed-log debt rank after valuation 5",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_0266ffc831aef802:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 5533,
  gainDen := 603669513,
  consumedBy := [
    {
  consumerType := "S6_LEMMA",
  consumerId := "s6_coverage_lemma_0000",
  dependencyType := "s3_debt_exact"
},
    {
  consumerType := "S6_LEMMA",
  consumerId := "s6_coverage_lemma_0007",
  dependencyType := "s3_debt_exact"
},
    {
  consumerType := "S6_LEMMA",
  consumerId := "s6_coverage_lemma_0014",
  dependencyType := "s3_debt_exact"
},
    {
  consumerType := "S6_LEMMA",
  consumerId := "s6_coverage_lemma_0021",
  dependencyType := "s3_debt_exact"
},
    {
  consumerType := "S6_LEMMA",
  consumerId := "s6_global_descent_lemma_0002",
  dependencyType := "s3_debt_exact"
},
    {
  consumerType := "S6_LEMMA",
  consumerId := "s6_global_descent_lemma_0009",
  dependencyType := "s3_debt_exact"
},
    {
  consumerType := "S6_LEMMA",
  consumerId := "s6_global_descent_lemma_0016",
  dependencyType := "s3_debt_exact"
},
    {
  consumerType := "S6_LEMMA",
  consumerId := "s6_global_descent_lemma_0023",
  dependencyType := "s3_debt_exact"
},
    {
  consumerType := "S6_LEMMA",
  consumerId := "s6_induction_lemma_0001",
  dependencyType := "s3_debt_exact"
},
    {
  consumerType := "S6_LEMMA",
  consumerId := "s6_induction_lemma_0008",
  dependencyType := "s3_debt_exact"
},
    {
  consumerType := "S6_LEMMA",
  consumerId := "s6_induction_lemma_0015",
  dependencyType := "s3_debt_exact"
},
    {
  consumerType := "S6_LEMMA",
  consumerId := "s6_induction_lemma_0022",
  dependencyType := "s3_debt_exact"
},
    {
  consumerType := "S6_LEMMA",
  consumerId := "s6_no_escape_lemma_0003",
  dependencyType := "s3_debt_exact"
},
    {
  consumerType := "S6_LEMMA",
  consumerId := "s6_no_escape_lemma_0010",
  dependencyType := "s3_debt_exact"
},
    {
  consumerType := "S6_LEMMA",
  consumerId := "s6_no_escape_lemma_0017",
  dependencyType := "s3_debt_exact"
},
    {
  consumerType := "S6_LEMMA",
  consumerId := "s6_no_escape_lemma_0024",
  dependencyType := "s3_debt_exact"
},
    {
  consumerType := "S6_LEMMA",
  consumerId := "s6_parametric_lift_lemma_0005",
  dependencyType := "s3_debt_exact"
},
    {
  consumerType := "S6_LEMMA",
  consumerId := "s6_parametric_lift_lemma_0012",
  dependencyType := "s3_debt_exact"
},
    {
  consumerType := "S6_LEMMA",
  consumerId := "s6_parametric_lift_lemma_0019",
  dependencyType := "s3_debt_exact"
},
    {
  consumerType := "S6_LEMMA",
  consumerId := "s6_parametric_lift_lemma_0026",
  dependencyType := "s3_debt_exact"
},
    {
  consumerType := "S6_LEMMA",
  consumerId := "s6_parent_transition_lemma_0004",
  dependencyType := "s3_debt_exact"
},
    {
  consumerType := "S6_LEMMA",
  consumerId := "s6_parent_transition_lemma_0011",
  dependencyType := "s3_debt_exact"
},
    {
  consumerType := "S6_LEMMA",
  consumerId := "s6_parent_transition_lemma_0018",
  dependencyType := "s3_debt_exact"
},
    {
  consumerType := "S6_LEMMA",
  consumerId := "s6_parent_transition_lemma_0025",
  dependencyType := "s3_debt_exact"
},
    {
  consumerType := "S6_LEMMA",
  consumerId := "s6_strict_verifier_gap_lemma_0006",
  dependencyType := "s3_debt_exact"
},
    {
  consumerType := "S6_LEMMA",
  consumerId := "s6_strict_verifier_gap_lemma_0013",
  dependencyType := "s3_debt_exact"
},
    {
  consumerType := "S6_LEMMA",
  consumerId := "s6_strict_verifier_gap_lemma_0020",
  dependencyType := "s3_debt_exact"
},
    {
  consumerType := "S6_LEMMA",
  consumerId := "s6_strict_verifier_gap_lemma_0027",
  dependencyType := "s3_debt_exact"
},
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "c852209e0b667739c0eda51b9a9e25b4c88bb0826f9804ff1d6dcedcfd0a63f4"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_03ae9f69227c4803",
  branchId := "P12:r20876015:d25",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P12",
  targetNode := "P25",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P12 mixed-log debt rank",
  measureTargetExpr := "P25 mixed-log debt rank after valuation 1",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_03ae9f69227c4803:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 165319,
  gainDen := 20876015,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "9685bbf227cd2cb5537a8b411929005853bf48ed4b1c5423413b3fd4ab1b533a"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_03fa943ef058c862",
  branchId := "P8:r13235615:d24",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P8",
  targetNode := "P29",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P8 mixed-log debt rank",
  measureTargetExpr := "P29 mixed-log debt rank after valuation 6",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_03fa943ef058c862:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 901,
  gainDen := 147453343,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "5c90c8b3d820909140f3abbf5e2b0e26156f9c3e40382e5ee290986d64a1a41b"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_04deca200dc9ebee",
  branchId := "P13:r36761851:d26",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P13",
  targetNode := "P26",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P13 mixed-log debt rank",
  measureTargetExpr := "P26 mixed-log debt rank after valuation 5",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_04deca200dc9ebee:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 1073567,
  gainDen := 1446047995,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "edda371bd315139b51ab1315060d38247c23dbe199f8b595416bdce7fcf12b6d"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_069d7a75cd16dc0c",
  branchId := "P11:r62421203:d26",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P11",
  targetNode := "P26",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P11 mixed-log debt rank",
  measureTargetExpr := "P26 mixed-log debt rank after valuation 5",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_069d7a75cd16dc0c:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 10685,
  gainDen := 129530067,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "25a58e63190353d169135694708840d495bb6db7a0e518464ced0ad6007d654a"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_08e7602e642d9d52",
  branchId := "P20:r39862641:d26",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P20",
  targetNode := "P22",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P20 mixed-log debt rank",
  measureTargetExpr := "P22 mixed-log debt rank after valuation 6",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_08e7602e642d9d52:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 6788006475,
  gainDen := 8361361777,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "4b64849a106296cf818afff5890be0809d468b0540751250908910b291bd9733"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_098319fd41f374b2",
  branchId := "P9:r13235615:d24",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P9",
  targetNode := "P25",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P9 mixed-log debt rank",
  measureTargetExpr := "P25 mixed-log debt rank after valuation 3",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_098319fd41f374b2:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 1941,
  gainDen := 13235615,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "8f31ae8e32414fa156883ac05a9d4acc41e34836072162e72015ae9fe35dac59"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_098d1ff9b293659f",
  branchId := "P12:r40120529:d26",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P12",
  targetNode := "P22",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P12 mixed-log debt rank",
  measureTargetExpr := "P22 mixed-log debt rank after valuation 2",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_098d1ff9b293659f:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 876591,
  gainDen := 442773713,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "520fa04dff8a7dcddb13ec00fcfaa49d08bce46a305f4c1aa8326e45e3ed3de5"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_09dfc239e56eeae9",
  branchId := "P7:r9512459:d24",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P7",
  targetNode := "P25",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P7 mixed-log debt rank",
  measureTargetExpr := "P25 mixed-log debt rank after valuation 4",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_09dfc239e56eeae9:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 1171,
  gainDen := 143730187,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "997c064403c92d2f1fdaadc25a8978e5136a49adf31d0882e1243d13ade8c428"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_0cbbf0500c5aa8f7",
  branchId := "P9:r53252723:d26",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P9",
  targetNode := "P24",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P9 mixed-log debt rank",
  measureTargetExpr := "P24 mixed-log debt rank after valuation 1",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_0cbbf0500c5aa8f7:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 17651,
  gainDen := 120361587,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "1dd1363485f34d990622e828cdd67c776bce9f87a87fbfa24fc72af292c2920e"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_0f1b2ddc21da9c6f",
  branchId := "P10:r40120529:d26",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P10",
  targetNode := "P23",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P10 mixed-log debt rank",
  measureTargetExpr := "P23 mixed-log debt rank after valuation 0",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_0f1b2ddc21da9c6f:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 94351,
  gainDen := 107229393,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "8bb62d5ed79524311a5a92b9b7a754aae4819f65a1194b17d16646a84bc4affd"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_0fbf7f977ecda865",
  branchId := "P13:r20876015:d25",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P13",
  targetNode := "P30",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P13 mixed-log debt rank",
  measureTargetExpr := "P30 mixed-log debt rank after valuation 7",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_0fbf7f977ecda865:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 231951,
  gainDen := 624855791,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "3d4cec5c4120b893b55c499b0b996f048cbf5f2ae6b83f2bf287cc6e803448bd"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_1284fda134ff1eef",
  branchId := "P8:r64316497:d26",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P8",
  targetNode := "P26",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P8 mixed-log debt rank",
  measureTargetExpr := "P26 mixed-log debt rank after valuation 4",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_1284fda134ff1eef:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 393,
  gainDen := 64316497,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "40e0998ad129ae1fd13aa4d6fdb14a7a489fc98e3e328ecfbe6c014045d5a17e"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_12f6ce0dda0edb3e",
  branchId := "P13:r33705691:d26",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P13",
  targetNode := "P23",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P13 mixed-log debt rank",
  measureTargetExpr := "P23 mixed-log debt rank after valuation 4",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_12f6ce0dda0edb3e:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 1544725,
  gainDen := 1040338651,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "ef6b5abb0e011b8cfad0f8ba3fd52c826cb89be893572cfb9889b932636765ca"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_1908d42be17679a8",
  branchId := "P12:r11914377:d24",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P12",
  targetNode := "P27",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P12 mixed-log debt rank",
  measureTargetExpr := "P27 mixed-log debt rank after valuation 6",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_1908d42be17679a8:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 570553,
  gainDen := 1152765065,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "7c3c4b99fd582edad2c5f91e0abf81288785afffd8e157911306363fbf612170"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_1c1f457759608fa7",
  branchId := "P4:r62137837:d26",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P4",
  targetNode := "P28",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P4 mixed-log debt rank",
  measureTargetExpr := "P28 mixed-log debt rank after valuation 4",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_1c1f457759608fa7:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 111,
  gainDen := 1471423981,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "791ee34fb634efb12bceb1465338a61e3247ba1d1945e4c18cbad6698c76fb23"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_1d4489a9493396a2",
  branchId := "P7:r52011671:d26",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P7",
  targetNode := "P31",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P7 mixed-log debt rank",
  measureTargetExpr := "P31 mixed-log debt rank after valuation 7",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_1d4489a9493396a2:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 3345,
  gainDen := 13138240151,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "86fb003c85edc4c8772307cdc22202a48058314f38799de12ac379f345fc2a3c"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_1d504f4a2b2c1fc3",
  branchId := "P4:r62137837:d26",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P4",
  targetNode := "P26",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P4 mixed-log debt rank",
  measureTargetExpr := "P26 mixed-log debt rank after valuation 2",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_1d504f4a2b2c1fc3:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 39,
  gainDen := 129246701,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "9e0b162480a5c0c7a3e1305797a2dcf5d44e9cd035a5fb2d12e3f10af44e8fed"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_1ddfec7aec044d6f",
  branchId := "P15:r41027779:d26",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P15",
  targetNode := "P25",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P15 mixed-log debt rank",
  measureTargetExpr := "P25 mixed-log debt rank after valuation 6",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_1ddfec7aec044d6f:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 2379085,
  gainDen := 712116419,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "8e8032a3378335ce6d414f19a2f421d46553470253345c5038e36359268b8cdb"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_1e02b3b1bfaf7fad",
  branchId := "P10:r53045881:d26",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P10",
  targetNode := "P22",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P10 mixed-log debt rank",
  measureTargetExpr := "P22 mixed-log debt rank after valuation 1",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_1e02b3b1bfaf7fad:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 111911,
  gainDen := 254372473,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "de574d16e1575525ef60e2d6eb98ab23dd99f25db275fdfe27170c9badfca2a8"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_1e0ad0c08857b346",
  branchId := "P17:r2110859:d22",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P17",
  targetNode := "P24",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P17 mixed-log debt rank",
  measureTargetExpr := "P24 mixed-log debt rank after valuation 7",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_1e0ad0c08857b346:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 178075475,
  gainDen := 740308363,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "8b5fe098f24c4feaa306bfb73a13a67c382616333dfa780f21fc5f30a7b209b5"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_20144e7cbf8c1aa2",
  branchId := "P8:r13235615:d24",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P8",
  targetNode := "P26",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P8 mixed-log debt rank",
  measureTargetExpr := "P26 mixed-log debt rank after valuation 3",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_20144e7cbf8c1aa2:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 647,
  gainDen := 13235615,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "169ec162e130466e9e96b9088a4067808fd2ee8a31b61f325100ff8b71e3060f"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_21132cb0e6fd44ea",
  branchId := "P8:r25540441:d25",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P8",
  targetNode := "P26",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P8 mixed-log debt rank",
  measureTargetExpr := "P26 mixed-log debt rank after valuation 4",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_21132cb0e6fd44ea:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 6053,
  gainDen := 495302489,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "4e482302dbe650b3e7a97f619538846fa8a528037211b2d0fc67a32b7a041e00"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_21377cecf937dc38",
  branchId := "P15:r18997731:d25",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P15",
  targetNode := "P20",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P15 mixed-log debt rank",
  measureTargetExpr := "P20 mixed-log debt rank after valuation 0",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_21377cecf937dc38:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 22472921,
  gainDen := 52552163,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "647089b0aec69743ed8cafb52399121368dd06ef0de351bfa2a05b8e7f2fe2ca"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_220d5547c3f0f012",
  branchId := "P15:r18997731:d25",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P15",
  targetNode := "P26",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P15 mixed-log debt rank",
  measureTargetExpr := "P26 mixed-log debt rank after valuation 6",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_220d5547c3f0f012:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 26582735,
  gainDen := 3978420707,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "db2fb728a0eeea727621655e4effa9bc72033f219c13aeadc23980efa63f0fd0"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_22676017665d803f",
  branchId := "P9:r66178075:d26",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P9",
  targetNode := "P22",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P9 mixed-log debt rank",
  measureTargetExpr := "P22 mixed-log debt rank after valuation 0",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_22676017665d803f:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 39093,
  gainDen := 133286939,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "f5e95377aaa04531ea67a02e60266f0cfd6c00273a5f20abc7371f50ce92dc78"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_249241262eaf8f7f",
  branchId := "P14:r9876937:d24",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P14",
  targetNode := "P21",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P14 mixed-log debt rank",
  measureTargetExpr := "P21 mixed-log debt rank after valuation 5",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_249241262eaf8f7f:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 1025783,
  gainDen := 115140419,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "48fd4d2f7cb1820a5577d9dd022e2cbac80a46000dd01cb18b3d7366a404a54f"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_2715b6aa408adfae",
  branchId := "P5:r21817285:d25",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P5",
  targetNode := "P29",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P5 mixed-log debt rank",
  measureTargetExpr := "P29 mixed-log debt rank after valuation 5",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_2715b6aa408adfae:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 415,
  gainDen := 1833756613,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "c4032b54bb906c3221c4f433d1218f15ebad5f3d870c80e498d24039762e533c"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_29d2a6e898a575a6",
  branchId := "P6:r52011671:d26",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P6",
  targetNode := "P32",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P6 mixed-log debt rank",
  measureTargetExpr := "P32 mixed-log debt rank after valuation 7",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_29d2a6e898a575a6:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 1115,
  gainDen := 13138240151,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "0bb2eada34f35eea586d3b1e20a54c57f3a1b601e713d4133abac2a213dbfc56"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_2b6a2f8bdb082329",
  branchId := "P12:r20876015:d25",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P12",
  targetNode := "P26",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P12 mixed-log debt rank",
  measureTargetExpr := "P26 mixed-log debt rank after valuation 2",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_2b6a2f8bdb082329:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 879821,
  gainDen := 222202607,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "69a555beddd976f723504efc4426e63a12eddb689e43c6c3c1a14693d010b878"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_2cc34fe497bd8d1a",
  branchId := "P7:r52011671:d26",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P7",
  targetNode := "P25",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P7 mixed-log debt rank",
  measureTargetExpr := "P25 mixed-log debt rank after valuation 1",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_2cc34fe497bd8d1a:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 647,
  gainDen := 39706845,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "346500b118aebab412f2215d7cf80e67e1ad5c312cf1db8ff0b984f04b8505c2"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_2dbd9730b6c6d0fe",
  branchId := "P14:r12423737:d24",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P14",
  targetNode := "P20",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P14 mixed-log debt rank",
  measureTargetExpr := "P20 mixed-log debt rank after valuation 0",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_2dbd9730b6c6d0fe:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 2774939,
  gainDen := 9733651,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "6ca8dfe596cfa7ff02c10a45ab5281ab339f7f5f9b1c1e36011a4ab64ee1cedd"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_2ff102edf933c272",
  branchId := "P12:r44704769:d26",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P12",
  targetNode := "P22",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P12 mixed-log debt rank",
  measureTargetExpr := "P22 mixed-log debt rank after valuation 0",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_2ff102edf933c272:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 354021,
  gainDen := 44704769,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "9ae0a5450ac7eb422a1b7be9427e2d21e6e5bd43ea93a6793a8a6fa06516d9a7"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_30de3deff4b4c4bd",
  branchId := "P16:r11028287:d24",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P16",
  targetNode := "P29",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P16 mixed-log debt rank",
  measureTargetExpr := "P29 mixed-log debt rank after valuation 6",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_30de3deff4b4c4bd:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 32727169,
  gainDen := 816334655,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "de324174c41f7a0463146dac74c7d2e734c6d39897ea89ba1e373ad207d1201b"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_31f350059efde954",
  branchId := "P2:r52195783:d26",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P2",
  targetNode := "P30",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P2 mixed-log debt rank",
  measureTargetExpr := "P30 mixed-log debt rank after valuation 5",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_31f350059efde954:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 5,
  gainDen := 1193046471,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "6143b583961fa8646cc4ec7f9099a9b27e226794fb066d621246c9cd5afaa355"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_32248ca96addc7fc",
  branchId := "P16:r23693441:d25",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P16",
  targetNode := "P21",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P16 mixed-log debt rank",
  measureTargetExpr := "P21 mixed-log debt rank after valuation 2",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_32248ca96addc7fc:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 7599033,
  gainDen := 23693441,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "252c930507c48648bbc59d0ee33c832c8c72afe31274b8c14e5ea698f3a6b4b8"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_33e1141ec74851ee",
  branchId := "P11:r35743131:d26",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P11",
  targetNode := "P23",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P11 mixed-log debt rank",
  measureTargetExpr := "P23 mixed-log debt rank after valuation 0",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_33e1141ec74851ee:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 94351,
  gainDen := 35743131,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "840be1447c2d923605074009d9835d7af2dfda9190f97b1bbd39fa8121dbdb70"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_3483c13415656fc0",
  branchId := "P12:r11914377:d24",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P12",
  targetNode := "P25",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P12 mixed-log debt rank",
  measureTargetExpr := "P25 mixed-log debt rank after valuation 4",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_3483c13415656fc0:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 687889,
  gainDen := 347458697,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "cd3906531e7df73b43821d5e8b4ab954acc85acaf80468c74e0e890a5371084b"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_38ac9165b4bcbed3",
  branchId := "P14:r9876937:d24",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P14",
  targetNode := "P17",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P14 mixed-log debt rank",
  measureTargetExpr := "P17 mixed-log debt rank after valuation 1",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_38ac9165b4bcbed3:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 2063621,
  gainDen := 14477123,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "b8f1d24f7660736ca2258dc3be42a8b794df990306fde7815e53ae00c540e3f1"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_3b2d850a6a68d9c5",
  branchId := "P13:r37271211:d26",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P13",
  targetNode := "P24",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P13 mixed-log debt rank",
  measureTargetExpr := "P24 mixed-log debt rank after valuation 2",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_3b2d850a6a68d9c5:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 1018527,
  gainDen := 171488939,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "14e69208b39b3d2ca4d565cc9b229bc1d1a0704a680339e9129a21f1d32389d4"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_3cb22e55093c2190",
  branchId := "P10:r53666407:d26",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P10",
  targetNode := "P29",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P10 mixed-log debt rank",
  measureTargetExpr := "P29 mixed-log debt rank after valuation 4",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_3cb22e55093c2190:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 14023,
  gainDen := 254992999,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "8931565bd50b7a31616979ecabe716de5d02bf7a0fb8d7622fcef87f369c56c1"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_3d1fbaed98d1f5f0",
  branchId := "P15:r41027779:d26",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P15",
  targetNode := "P23",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P15 mixed-log debt rank",
  measureTargetExpr := "P23 mixed-log debt rank after valuation 4",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_3d1fbaed98d1f5f0:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 23865247,
  gainDen := 1785858243,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "2c7f1cce7934df743009f7f5e4caf75c48e0eb6cb5b5b8401544329de3db1574"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_4167c7d588e6b511",
  branchId := "P14:r9876937:d24",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P14",
  targetNode := "P16",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P14 mixed-log debt rank",
  measureTargetExpr := "P16 mixed-log debt rank after valuation 0",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_4167c7d588e6b511:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 7598757,
  gainDen := 26654153,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "0a17c8f8bce22443df0bd17a66694b9a57e29b845ef7f2e2ab9e4edfac3f3342"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_418f70481514ae22",
  branchId := "P14:r32145719:d25",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P14",
  targetNode := "P25",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P14 mixed-log debt rank",
  measureTargetExpr := "P25 mixed-log debt rank after valuation 1",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_418f70481514ae22:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 2291083,
  gainDen := 32145719,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "7528de3c1ea534787558b10f1ac1c8ac73b6946988a3803798ed7fe1af2356ec"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_434d17c738535c49",
  branchId := "P11:r35743131:d26",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P11",
  targetNode := "P25",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P11 mixed-log debt rank",
  measureTargetExpr := "P25 mixed-log debt rank after valuation 2",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_434d17c738535c49:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 333595,
  gainDen := 505505179,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "131a0c47213b742e1082708d2eb9dbc2364d11fe2afaa54d514fbcf9f414b96c"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_4452a6875f5521b1",
  branchId := "P15:r18997731:d25",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P15",
  targetNode := "P27",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P15 mixed-log debt rank",
  measureTargetExpr := "P27 mixed-log debt rank after valuation 7",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_4452a6875f5521b1:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 20465821,
  gainDen := 6125904355,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "3781ab68878e062cfffc4d69bc987e574b0fc037901e9f7541f687c7dd66f629"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_45e8b9ec5c1dd171",
  branchId := "P13:r36761851:d26",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P13",
  targetNode := "P23",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P13 mixed-log debt rank",
  measureTargetExpr := "P23 mixed-log debt rank after valuation 2",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_45e8b9ec5c1dd171:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 616921,
  gainDen := 103870715,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "76a605cc4fa3bd602f2abe6099becb95d0ba203cb17c0122a0d0e11a2ac3ab8f"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_4654e99b99e64aaf",
  branchId := "P8:r25540441:d25",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P8",
  targetNode := "P24",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P8 mixed-log debt rank",
  measureTargetExpr := "P24 mixed-log debt rank after valuation 2",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_4654e99b99e64aaf:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 647,
  gainDen := 13235615,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "303b4f7212db465e1b4b2ef0d6feb79911c049f5a5012436692fed662e0147cc"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_4ae3a92f8ce278d9",
  branchId := "P14:r12423737:d24",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P14",
  targetNode := "P21",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P14 mixed-log debt rank",
  measureTargetExpr := "P21 mixed-log debt rank after valuation 1",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_4ae3a92f8ce278d9:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 6553893,
  gainDen := 45978169,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "9e70d2cf6973ed7e2faeea58ea8dc4aa5ef026281b1e1ee7bcbaa35ce601ad88"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_4b01a6024d95192a",
  branchId := "P17:r11028287:d24",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P17",
  targetNode := "P26",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P17 mixed-log debt rank",
  measureTargetExpr := "P26 mixed-log debt rank after valuation 4",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_4b01a6024d95192a:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 5305539,
  gainDen := 11028287,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "cb323b6093d52d8fabeb586b8e01998adf284909fb289fa9f7137efb18e1e93b"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_4eadfac62799baa6",
  branchId := "P14:r9876937:d24",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P14",
  targetNode := "P22",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P14 mixed-log debt rank",
  measureTargetExpr := "P22 mixed-log debt rank after valuation 6",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_4eadfac62799baa6:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 3930159,
  gainDen := 882292169,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "8b58328e287795941b2a08b2313463129d75884bf36990924a4cbcac47baa90c"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_4f946cb203fa8420",
  branchId := "P2:r52195783:d26",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P2",
  targetNode := "P32",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P2 mixed-log debt rank",
  measureTargetExpr := "P32 mixed-log debt rank after valuation 7",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_4f946cb203fa8420:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 17,
  gainDen := 16225432007,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "1c02cf758d056edb8c4179204ea8d72affe62ebb99e7c69382731cad6d3870e9"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_50b106369c92f0cd",
  branchId := "P7:r52011671:d26",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P7",
  targetNode := "P24",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P7 mixed-log debt rank",
  measureTargetExpr := "P24 mixed-log debt rank after valuation 0",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_50b106369c92f0cd:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 1695,
  gainDen := 52011671,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "85ba9bdb7938496b64e59855396c34391c20d095a884988dafae6b679450ae8c"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_52db3088f06b4ea2",
  branchId := "P7:r39706845:d26",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P7",
  targetNode := "P31",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P7 mixed-log debt rank",
  measureTargetExpr := "P31 mixed-log debt rank after valuation 6",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_52db3088f06b4ea2:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 2959,
  gainDen := 5811069149,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "5cee34ef1aba70547821d7fa3db2ee355444f581a472edcb0cd862dfa79707bc"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_55b61965b741a159",
  branchId := "P6:r21817285:d25",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P6",
  targetNode := "P30",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P6 mixed-log debt rank",
  measureTargetExpr := "P30 mixed-log debt rank after valuation 7",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_55b61965b741a159:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 43,
  gainDen := 253338263,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "3b94a855e6b99b14defbdaf04fd77a8d545e55c9a742f18742a781b12145b1a7"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_5853c83203555b67",
  branchId := "P10:r53045881:d26",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P10",
  targetNode := "P25",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P10 mixed-log debt rank",
  measureTargetExpr := "P25 mixed-log debt rank after valuation 4",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_5853c83203555b67:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 80419,
  gainDen := 1462332025,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "871e583c870a9723bfa82a9206e3fddec4c042da9a33994a9d5f4ba6ecdfa4a2"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_5d62900f6d374b0f",
  branchId := "P9:r53252723:d26",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P9",
  targetNode := "P27",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P9 mixed-log debt rank",
  measureTargetExpr := "P27 mixed-log debt rank after valuation 4",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_5d62900f6d374b0f:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 19429,
  gainDen := 1059885683,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "c2512f345549446c89a2afc4e54efe9260abfbebecb98bcf7013c34209222e40"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_5de13c7aa6e5ea94",
  branchId := "P12:r11914377:d24",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P12",
  targetNode := "P28",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P12 mixed-log debt rank",
  measureTargetExpr := "P28 mixed-log debt rank after valuation 7",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_5de13c7aa6e5ea94:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 550997,
  gainDen := 2226506889,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "17ef3c7cb0d62ef5e13d38e04b61be9244585c79e29860a5e31c569c026ddb80"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_5f01e6a842be27e9",
  branchId := "P12:r34008209:d26",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P12",
  targetNode := "P22",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P12 mixed-log debt rank",
  measureTargetExpr := "P22 mixed-log debt rank after valuation 3",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_5f01e6a842be27e9:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 432245,
  gainDen := 436661393,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "c9646652a07383e1064d7dc50b023bc56fb3b8346a3a12202ae302afdf0b900f"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_5f747359e2c60bfa",
  branchId := "P16:r23693441:d25",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P16",
  targetNode := "P25",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P16 mixed-log debt rank",
  measureTargetExpr := "P25 mixed-log debt rank after valuation 6",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_5f747359e2c60bfa:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 6928289,
  gainDen := 345633465,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "144d09c6075cb6b6ddd3d608bb057674a8a9e7267e84436061d79b79a0485363"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_6044aaeeab1b0ad2",
  branchId := "P12:r40120529:d26",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P12",
  targetNode := "P20",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P12 mixed-log debt rank",
  measureTargetExpr := "P20 mixed-log debt rank after valuation 0",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_6044aaeeab1b0ad2:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 94351,
  gainDen := 11914377,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "3967bdb24eb1860b58a514e09effd685cfc180a7c92a5e53a1de174a216d1701"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_636df689c7ad1123",
  branchId := "P5:r21817285:d25",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P5",
  targetNode := "P30",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P5 mixed-log debt rank",
  measureTargetExpr := "P30 mixed-log debt rank after valuation 6",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_636df689c7ad1123:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 329,
  gainDen := 2907498437,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "30f1ebc3a076abefe0968d20a10d71b36e25040a8c64c2390896cfd471f72718"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_6379870109783872",
  branchId := "P13:r33705691:d26",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P13",
  targetNode := "P19",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P13 mixed-log debt rank",
  measureTargetExpr := "P19 mixed-log debt rank after valuation 0",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_6379870109783872:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 800755,
  gainDen := 33705691,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "cb912963da23fa3d0f715bb17a25f43289efc69fa68032f5ef682f7f030df6e8"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_661d2adead250775",
  branchId := "P15:r26510867:d25",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P15",
  targetNode := "P22",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P15 mixed-log debt rank",
  measureTargetExpr := "P22 mixed-log debt rank after valuation 1",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_661d2adead250775:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 5668431,
  gainDen := 26510867,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "360e622cdaefc42468c861fe9ff965cfe2c64f76f080da8855bd87609eddf089"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_66f1e017a3d8b5dc",
  branchId := "P8:r25540441:d25",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P8",
  targetNode := "P23",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P8 mixed-log debt rank",
  measureTargetExpr := "P23 mixed-log debt rank after valuation 1",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_66f1e017a3d8b5dc:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 2497,
  gainDen := 25540441,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "8e68c39ad7068a412353a3f1546b3f710851c66274e51a40a7de3f7c69afa73b"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_67a5709cd5fb9830",
  branchId := "P13:r33705691:d26",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P13",
  targetNode := "P21",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P13 mixed-log debt rank",
  measureTargetExpr := "P21 mixed-log debt rank after valuation 2",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_67a5709cd5fb9830:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 1395931,
  gainDen := 235032283,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "8a521dfa8d99b428f75b708268bdf8ec2dfaa7038365ae140b488e5936102ef6"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_6c78a40e991c2af6",
  branchId := "P9:r53252723:d26",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P9",
  targetNode := "P28",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P9 mixed-log debt rank",
  measureTargetExpr := "P28 mixed-log debt rank after valuation 5",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_6c78a40e991c2af6:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 39239,
  gainDen := 4281111155,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "5a044f6047058bc00ff2b93ba7eb0c19a0e877c211d844fcc87acf00e291f8e7"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_6e6013ac60d59ea9",
  branchId := "P11:r53252723:d26",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P11",
  targetNode := "P27",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P11 mixed-log debt rank",
  measureTargetExpr := "P27 mixed-log debt rank after valuation 7",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_6e6013ac60d59ea9:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 4889,
  gainDen := 237069723,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "1ad7ba4cb02e11347904d640ea15c6a707a46858d24def412e7f22e58ac46217"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_6e6c3a1b845789a6",
  branchId := "P12:r43176689:d26",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P12",
  targetNode := "P26",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P12 mixed-log debt rank",
  measureTargetExpr := "P26 mixed-log debt rank after valuation 5",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_6e6c3a1b845789a6:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 10685,
  gainDen := 43176689,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "f2ca364803d3638359dd1047af38112a4f648a026dbcc32008f80cf43db551a5"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_6ed787fd3695d327",
  branchId := "P14:r9876937:d24",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P14",
  targetNode := "P20",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P14 mixed-log debt rank",
  measureTargetExpr := "P20 mixed-log debt rank after valuation 4",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_6ed787fd3695d327:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 1371729,
  gainDen := 76985801,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "55ca222c8d0a8f8117e1435f997b92e3b92ca2fca7e15947cd09128ffbb8236a"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_6facfc346df1c127",
  branchId := "P12:r62628045:d26",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P12",
  targetNode := "P26",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P12 mixed-log debt rank",
  measureTargetExpr := "P26 mixed-log debt rank after valuation 2",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_6facfc346df1c127:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 1054011,
  gainDen := 532390093,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "8bfe523c8332293b4a54f2a4d282b1dbbd5a019d1c77092ab0e02d86d145e2ab"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_7063699c40446194",
  branchId := "P12:r34008209:d26",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P12",
  targetNode := "P21",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P12 mixed-log debt rank",
  measureTargetExpr := "P21 mixed-log debt rank after valuation 2",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_7063699c40446194:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 333049,
  gainDen := 168225937,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "e8adfb47ffedb1617070f1644c9a9fe1a28fdd9016e0a9e5570ad08d73aa7ed3"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_71399d21ef13b898",
  branchId := "P12:r62628045:d26",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P12",
  targetNode := "P30",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P12 mixed-log debt rank",
  measureTargetExpr := "P30 mixed-log debt rank after valuation 6",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_71399d21ef13b898:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 77317,
  gainDen := 624855791,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "0e33b5a1d2f3c583b6676be618482bf4f97441bd450f9a34e8d4392f6afadab7"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_71d6f4ba7af95860",
  branchId := "P14:r23693441:d25",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P14",
  targetNode := "P27",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P14 mixed-log debt rank",
  measureTargetExpr := "P27 mixed-log debt rank after valuation 5",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_71d6f4ba7af95860:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 9073609,
  gainDen := 2036959361,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "b7720949733385a9018e0be7879790d88e1ec3508d589c1db5079d82cfde7fdf"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_71e558e716b18e81",
  branchId := "P5:r21817285:d25",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P5",
  targetNode := "P24",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P5 mixed-log debt rank",
  measureTargetExpr := "P24 mixed-log debt rank after valuation 0",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_71e558e716b18e81:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 401,
  gainDen := 55371717,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "f3e0cd515a1b353f8b49f67931acbc3c33c60fac253a68d49b55c0d5b3e9c8f5"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_7200b983f7d15441",
  branchId := "P8:r39706845:d26",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P8",
  targetNode := "P29",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P8 mixed-log debt rank",
  measureTargetExpr := "P29 mixed-log debt rank after valuation 5",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_7200b983f7d15441:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 3731,
  gainDen := 1221195167,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "a02e1a6cdfbd3cf51a2d095ac91df566e8f3a1e4956e225571d12c2c769b22a2"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_723135dd408526a6",
  branchId := "P14:r32145719:d25",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P14",
  targetNode := "P26",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P14 mixed-log debt rank",
  measureTargetExpr := "P26 mixed-log debt rank after valuation 2",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_723135dd408526a6:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 8319995,
  gainDen := 233472311,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "ab4764b527d23a96da27050ab2b719854a609071f44ce76f8810e6582cd9c27c"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_74466811a0f40e7e",
  branchId := "P8:r64316497:d26",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P8",
  targetNode := "P28",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P8 mixed-log debt rank",
  measureTargetExpr := "P28 mixed-log debt rank after valuation 6",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_74466811a0f40e7e:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 5019,
  gainDen := 3285541969,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "d09ca8bb459ccd6fff488ffeaa4aa2c715d4f7ab76a13f4ddeb9c049193eafba"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_776068b77e3ac1e0",
  branchId := "P7:r9512459:d24",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P7",
  targetNode := "P27",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P7 mixed-log debt rank",
  measureTargetExpr := "P27 mixed-log debt rank after valuation 6",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_776068b77e3ac1e0:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 1933,
  gainDen := 949036555,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "ed2ba8640eef3ae5d1e168ab88ce17cdb942d4708d71fb21561ffbc095e2a0dc"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_79d7c90032686174",
  branchId := "P12:r62628045:d26",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P12",
  targetNode := "P24",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P12 mixed-log debt rank",
  measureTargetExpr := "P24 mixed-log debt rank after valuation 0",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_79d7c90032686174:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 165319,
  gainDen := 20876015,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "9cd68273a227c5e26d602a4889f74b5a0a658d51b64505659c37148582c3765d"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_7b16cceccca0784e",
  branchId := "P13:r36761851:d26",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P13",
  targetNode := "P22",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P13 mixed-log debt rank",
  measureTargetExpr := "P22 mixed-log debt rank after valuation 1",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_7b16cceccca0784e:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 2828165,
  gainDen := 238088443,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "a98acc592b3ca8637f8d5e50a740ee9772ca6673a9bc3e6ae1c6c3903dd4fa38"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_7ce126d6d458cb34",
  branchId := "P14:r9876937:d24",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P14",
  targetNode := "P23",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P14 mixed-log debt rank",
  measureTargetExpr := "P23 mixed-log debt rank after valuation 7",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_7ce126d6d458cb34:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 9139533,
  gainDen := 4103517641,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "edb55206442c3481a68f843ee416f914263a2badde053990b458e091421e2f5c"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_7ef7637599045577",
  branchId := "P10:r53045881:d26",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P10",
  targetNode := "P21",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P10 mixed-log debt rank",
  measureTargetExpr := "P21 mixed-log debt rank after valuation 0",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_7ef7637599045577:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 46675,
  gainDen := 53045881,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "b663f75a6e3bea20aff9aed5830be0e488f8c0f484c1daaccc9aebdc4985c237"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_7f3137460f73732a",
  branchId := "P10:r40120529:d26",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P10",
  targetNode := "P24",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P10 mixed-log debt rank",
  measureTargetExpr := "P24 mixed-log debt rank after valuation 1",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_7f3137460f73732a:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 17651,
  gainDen := 40120529,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "a3ae84845ddf49d9d4936ebe7f5c831248854fcc437416ed378a7a6072e4c60c"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_81530fe891382347",
  branchId := "P12:r43176689:d26",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P12",
  targetNode := "P28",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P12 mixed-log debt rank",
  measureTargetExpr := "P28 mixed-log debt rank after valuation 7",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_81530fe891382347:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 932693,
  gainDen := 15075562225,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "7b3c20b34be7be4d0aad4178918bf09324cbf720dc381ad2451778cc9fccf0f2"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_8319b0dfc54ed83c",
  branchId := "P10:r26781493:d25",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P10",
  targetNode := "P29",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P10 mixed-log debt rank",
  measureTargetExpr := "P29 mixed-log debt rank after valuation 6",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_8319b0dfc54ed83c:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 50559,
  gainDen := 1838720821,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "9ef8ae09744f42502acf39e4d1f0681b4c7d3b9653adefb80ba8fe1bb07cba79"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_8516c074e54383e4",
  branchId := "P9:r26781493:d25",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P9",
  targetNode := "P30",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P9 mixed-log debt rank",
  measureTargetExpr := "P30 mixed-log debt rank after valuation 6",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_8516c074e54383e4:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 16853,
  gainDen := 1838720821,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "1a94ed0f046bbb65c297148741acfd27a910b58ac53bc11b09ac12a0857df707"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_8531ab50b2be6800",
  branchId := "P6:r52011671:d26",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P6",
  targetNode := "P25",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P6 mixed-log debt rank",
  measureTargetExpr := "P25 mixed-log debt rank after valuation 0",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_8531ab50b2be6800:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 565,
  gainDen := 52011671,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "b61130e30d61576d1167b37a33089f7079ab73e50b73a85ae318405d2040741b"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_8b5fafd89f892a80",
  branchId := "P10:r53666407:d26",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P10",
  targetNode := "P25",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P10 mixed-log debt rank",
  measureTargetExpr := "P25 mixed-log debt rank after valuation 0",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_8b5fafd89f892a80:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 47221,
  gainDen := 53666407,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "1f25486e3227464b55dea73bc5306a98d9b761c40812eacb92e72fa16df0e6d5"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_8c7fd4867f378aa1",
  branchId := "P10:r26781493:d25",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P10",
  targetNode := "P28",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P10 mixed-log debt rank",
  measureTargetExpr := "P28 mixed-log debt rank after valuation 5",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_8c7fd4867f378aa1:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 14023,
  gainDen := 254992999,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "28fe33f9a46f6f42c9f3fe1845b5e941b3870ad656ebe7d8708a4c4f297c6868"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_8d674a3606920233",
  branchId := "P13:r20876015:d25",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P13",
  targetNode := "P29",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P13 mixed-log debt rank",
  measureTargetExpr := "P29 mixed-log debt rank after valuation 6",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_8d674a3606920233:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 2058225,
  gainDen := 2772339439,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "7b4cd31f4190d15aae8b75db574f0c07964095f2f7ab376e274a6e83210045bc"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_8e69fd4723ea3f4c",
  branchId := "P8:r25540441:d25",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P8",
  targetNode := "P28",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P8 mixed-log debt rank",
  measureTargetExpr := "P28 mixed-log debt rank after valuation 6",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_8e69fd4723ea3f4c:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 12995,
  gainDen := 4253398873,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "dcc23cef7128df840899c4dc2c3cdfd678fddba268176377c99202364904dd7e"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_8ff22d37d0413acd",
  branchId := "P7:r9512459:d24",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P7",
  targetNode := "P24",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P7 mixed-log debt rank",
  measureTargetExpr := "P24 mixed-log debt rank after valuation 3",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_8ff22d37d0413acd:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 155,
  gainDen := 9512459,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "4950e169820ce2017941505a446b5d2df962926178d62f1668ad0acabc2c2079"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_902c3f329029d36a",
  branchId := "P14:r23693441:d25",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P14",
  targetNode := "P29",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P14 mixed-log debt rank",
  measureTargetExpr := "P29 mixed-log debt rank after valuation 7",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_902c3f329029d36a:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 5855629,
  gainDen := 5258184833,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "c98bc6b8dab467d163c2e3fcc938522e4f79ad8e4b4e34ce6451d022f9857c37"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_93cb24bafb0c0951",
  branchId := "P13:r35743131:d26",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P13",
  targetNode := "P22",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P13 mixed-log debt rank",
  measureTargetExpr := "P22 mixed-log debt rank after valuation 2",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_93cb24bafb0c0951:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 3002355,
  gainDen := 505505179,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "2f427996565e8d481d5a93639bd3a34924b7853b15cceb75898f0132221622f8"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_94febb0f8fdd0a63",
  branchId := "P15:r41027779:d26",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P15",
  targetNode := "P21",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P15 mixed-log debt rank",
  measureTargetExpr := "P21 mixed-log debt rank after valuation 2",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_94febb0f8fdd0a63:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 23716453,
  gainDen := 443680963,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "3b930e375cf88896c7833094bf00c9101e1debdf10b54206a5bbc9220ec95c68"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_9691bdab3143e352",
  branchId := "P13:r35743131:d26",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P13",
  targetNode := "P24",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P13 mixed-log debt rank",
  measureTargetExpr := "P24 mixed-log debt rank after valuation 4",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_9691bdab3143e352:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 1946331,
  gainDen := 1310811547,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "63f1a39f7b28f7e1acbea955fdc7e16f7a3536cc20b8f369efaea13cc6279c76"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_982abf74ce1c10cb",
  branchId := "P16:r23693441:d25",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P16",
  targetNode := "P26",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P16 mixed-log debt rank",
  measureTargetExpr := "P26 mixed-log debt rank after valuation 7",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_982abf74ce1c10cb:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 52700661,
  gainDen := 5258184833,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "9ae909ba3415da2fca278f6e1acebbf86058f0bd642d64c8b2eeb7702459744f"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_9be24f9c565419bd",
  branchId := "P12:r40120529:d26",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P12",
  targetNode := "P27",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P12 mixed-log debt rank",
  measureTargetExpr := "P27 mixed-log debt rank after valuation 7",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_9be24f9c565419bd:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 4889,
  gainDen := 79023241,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "cf208821ba5e25994b0eaff33f8574cc40ff44425cc0d27c405b07ef93815b12"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_9c97294309c04b0d",
  branchId := "P7:r9512459:d24",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P7",
  targetNode := "P21",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P7 mixed-log debt rank",
  measureTargetExpr := "P21 mixed-log debt rank after valuation 0",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_9c97294309c04b0d:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 3427,
  gainDen := 26289675,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "52d3719dd41e6e8bddc4911f3d95d79b46bc6f6c5edc3e68c08329d6f702b417"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_a03d44cfe62da8ea",
  branchId := "P13:r37271211:d26",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P13",
  targetNode := "P29",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P13 mixed-log debt rank",
  measureTargetExpr := "P29 mixed-log debt rank after valuation 7",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_a03d44cfe62da8ea:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 1377039,
  gainDen := 7419246251,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "f3e56fa9add477d486e2bd78dccd737dab109b74b7aae760d92047dfbf889aa5"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_a0e016f1404f38dc",
  branchId := "P13:r20876015:d25",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P13",
  targetNode := "P24",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P13 mixed-log debt rank",
  measureTargetExpr := "P24 mixed-log debt rank after valuation 1",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_a0e016f1404f38dc:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 495957,
  gainDen := 20876015,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "295fb7b6654e35ab432048c8531a8d7f1aa214a33d1a9f844322fb7810580798"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_a10fd251086527d4",
  branchId := "P12:r62628045:d26",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P12",
  targetNode := "P27",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P12 mixed-log debt rank",
  measureTargetExpr := "P27 mixed-log debt rank after valuation 3",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_a10fd251086527d4:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 87095,
  gainDen := 87984879,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "41e9c6aaf85f08968c19e3407b183a1c0cc7f7af939562487e8f09f64fcdb9f8"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_a1636f598068df23",
  branchId := "P13:r36761851:d26",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P13",
  targetNode := "P24",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P13 mixed-log debt rank",
  measureTargetExpr := "P24 mixed-log debt rank after valuation 3",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_a1636f598068df23:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 87095,
  gainDen := 29328293,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "ffd1bbb760ca0673334c0b93f263cdfa6ba7f21334c1049c128af3f6e48e225e"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_a4e710fd08bfb04b",
  branchId := "P6:r28537377:d25",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P6",
  targetNode := "P29",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P6 mixed-log debt rank",
  measureTargetExpr := "P29 mixed-log debt rank after valuation 7",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_a4e710fd08bfb04b:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 43,
  gainDen := 253338263,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "792b67ac4ac59c35856f19e03aaf362abb9cfe3aca5fa33691a3ca9a37a85d66"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_a673350b34fff169",
  branchId := "P15:r18997731:d25",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P15",
  targetNode := "P21",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P15 mixed-log debt rank",
  measureTargetExpr := "P21 mixed-log debt rank after valuation 1",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_a673350b34fff169:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 4062007,
  gainDen := 18997731,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "b6e9798b1a4d0d35c4c79dffc249e8822b56456b112ea4d81f1e987cef97b3aa"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_a7c4405b9c8fddcb",
  branchId := "P7:r52011671:d26",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P7",
  targetNode := "P27",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P7 mixed-log debt rank",
  measureTargetExpr := "P27 mixed-log debt rank after valuation 3",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_a7c4405b9c8fddcb:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 3219,
  gainDen := 790209175,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "ce5227dbbc588a98c0eac3278b3ac2a6e95b814d0cc0e8c8b7ab58ef5329209d"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_a8109ab5742a0696",
  branchId := "P9:r66178075:d26",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P9",
  targetNode := "P29",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P9 mixed-log debt rank",
  measureTargetExpr := "P29 mixed-log debt rank after valuation 7",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_a8109ab5742a0696:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 7719,
  gainDen := 3368678815,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "6fceee5e3a372d97a813035beb2a5cf3cb342c4d8f99e3b881776f4d71e19d48"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_a88a5d9aa928a974",
  branchId := "P14:r55974473:d26",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P14",
  targetNode := "P26",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P14 mixed-log debt rank",
  measureTargetExpr := "P26 mixed-log debt rank after valuation 7",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_a88a5d9aa928a974:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 3581027,
  gainDen := 6431316553,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "300c528dcf20734683d88c4840f56c07308d15d9c0191f02b901caaa27b567f9"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_aa0339dd7a74e457",
  branchId := "P14:r11914377:d24",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P14",
  targetNode := "P23",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P14 mixed-log debt rank",
  measureTargetExpr := "P23 mixed-log debt rank after valuation 5",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_aa0339dd7a74e457:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 261285,
  gainDen := 29328293,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "70ed08f5248aad88347818f9e53429f0d1a8dec036b13711b1e18829c7af5656"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_aa42fdcb5d977d6b",
  branchId := "P12:r43176689:d26",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P12",
  targetNode := "P24",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P12 mixed-log debt rank",
  measureTargetExpr := "P24 mixed-log debt rank after valuation 3",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_aa42fdcb5d977d6b:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 574181,
  gainDen := 580047601,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "58ac8e17446c69266d5b2f3b6253caae807948bda465c609c3d5e834ba570744"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_ad293a621281ccd6",
  branchId := "P5:r21817285:d25",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P5",
  targetNode := "P25",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P5 mixed-log debt rank",
  measureTargetExpr := "P25 mixed-log debt rank after valuation 1",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_ad293a621281ccd6:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 79,
  gainDen := 21817285,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "307c1e35a34ec3343cb991d411f36f4a43da8958e1b5cb27f53d569e717e7a9c"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_adda704373553f90",
  branchId := "P7:r39706845:d26",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P7",
  targetNode := "P27",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P7 mixed-log debt rank",
  measureTargetExpr := "P27 mixed-log debt rank after valuation 2",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_adda704373553f90:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 1417,
  gainDen := 173924573,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "2d66da27f0d4146f7498179450d0952f5e792b1aeed6b6267dd42dbad8736b26"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_af98630ed63a21f3",
  branchId := "P6:r28537377:d25",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P6",
  targetNode := "P24",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P6 mixed-log debt rank",
  measureTargetExpr := "P24 mixed-log debt rank after valuation 2",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_af98630ed63a21f3:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 155,
  gainDen := 28537377,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "dc48f8be485067c073d3dfdec64083be1f35ba7e77b9d6333d5f2dab03414f52"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_b027799942b46054",
  branchId := "P15:r3971459:d22",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P15",
  targetNode := "P21",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P15 mixed-log debt rank",
  measureTargetExpr := "P21 mixed-log debt rank after valuation 5",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_b027799942b46054:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 2533011,
  gainDen := 23693441,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "41e70e5477ef271a2ba703661f014b22524b28e128bd2ae4748374977379692f"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_b07b252fc163cb04",
  branchId := "P14:r9876937:d24",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P14",
  targetNode := "P19",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P14 mixed-log debt rank",
  measureTargetExpr := "P19 mixed-log debt rank after valuation 3",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_b07b252fc163cb04:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 442731,
  gainDen := 12423737,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "f33ffa10c95ac588c3844a869c435f6ce4672fbab8d67f3d6712923a68b77d15"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_b167e6ef5043debc",
  branchId := "P12:r44704769:d26",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P12",
  targetNode := "P28",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P12 mixed-log debt rank",
  measureTargetExpr := "P28 mixed-log debt rank after valuation 6",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_b167e6ef5043debc:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 96873,
  gainDen := 782902273,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "07ca7b8e142fdd68d2d7549316b17c78bf2cff19d1635642a7642fcac9888e24"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_b35596b5e92309a7",
  branchId := "P7:r39706845:d26",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P7",
  targetNode := "P26",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P7 mixed-log debt rank",
  measureTargetExpr := "P26 mixed-log debt rank after valuation 1",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_b35596b5e92309a7:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 647,
  gainDen := 39706845,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "109ebb0dc9a82cba99350f595eaa4e2dbdf21e2ea0fafa68760bba3725a16a4d"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_b41c6abe582aee65",
  branchId := "P12:r43176689:d26",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P12",
  targetNode := "P22",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P12 mixed-log debt rank",
  measureTargetExpr := "P22 mixed-log debt rank after valuation 1",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_b41c6abe582aee65:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 702401,
  gainDen := 177394417,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "920eee421dba820be10a5efcb1a5f80952397f39f0461647eaa5b9fb7983a37e"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_b4608b1096a136ce",
  branchId := "P14:r32145719:d25",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P14",
  targetNode := "P30",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P14 mixed-log debt rank",
  measureTargetExpr := "P30 mixed-log debt rank after valuation 6",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_b4608b1096a136ce:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 9189131,
  gainDen := 4125786423,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "b1d932ab97f1fd2b28c135be358f414ae2996f35139199c7b23685acbc91a7fd"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_b80c00a0f9057757",
  branchId := "P12:r40120529:d26",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P12",
  targetNode := "P24",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P12 mixed-log debt rank",
  measureTargetExpr := "P24 mixed-log debt rank after valuation 4",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_b80c00a0f9057757:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 126207,
  gainDen := 254992999,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "039e7e0089d691a7c0f77c788f9c4aa14a467dad778534b9bf0030f6e1f51403"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_ba196a26ec0dd893",
  branchId := "P17:r2110859:d22",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P17",
  targetNode := "P22",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P17 mixed-log debt rank",
  measureTargetExpr := "P22 mixed-log debt rank after valuation 5",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_ba196a26ec0dd893:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 66601085,
  gainDen := 69219723,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "db131d7588ee6703d9200c8bdfa8360cae200ad3c3c2b9f9ac9eac296fbebc0f"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_ba61befb6a02c8b5",
  branchId := "P7:r58731763:d26",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P7",
  targetNode := "P25",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P7 mixed-log debt rank",
  measureTargetExpr := "P25 mixed-log debt rank after valuation 3",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_ba61befb6a02c8b5:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 2973,
  gainDen := 729820403,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "54fb5a97913a29eef5101755e4ddf9b94261d27a1d8c8bf4dd805b73b0102b9a"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_bdaf1ed0d75f3cbc",
  branchId := "P8:r39706845:d26",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P8",
  targetNode := "P30",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P8 mixed-log debt rank",
  measureTargetExpr := "P30 mixed-log debt rank after valuation 6",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_bdaf1ed0d75f3cbc:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 8877,
  gainDen := 5811069149,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "e24c4ceecae0351f2702a59357ba71e0cf46d196daa9ec408e57b5e1ef704ea5"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_beaccbaea1ed81ee",
  branchId := "P15:r26510867:d25",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P15",
  targetNode := "P23",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P15 mixed-log debt rank",
  measureTargetExpr := "P23 mixed-log debt rank after valuation 2",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_beaccbaea1ed81ee:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 3336223,
  gainDen := 31206577,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "cab5e8e60f1749396d3804ba64530c7e7e239511c81e1940251882e4ff81cbd3"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_bee1b3a5badbe55b",
  branchId := "P9:r53252723:d26",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P9",
  targetNode := "P25",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P9 mixed-log debt rank",
  measureTargetExpr := "P25 mixed-log debt rank after valuation 2",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_bee1b3a5badbe55b:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 18667,
  gainDen := 254579315,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "3fffb72d2fd29b69148725e9b62006d80d7abd64b067f478d6af1f9819ebfe9e"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_bf5b7e9a0a610f97",
  branchId := "P15:r41027779:d26",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P15",
  targetNode := "P24",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P15 mixed-log debt rank",
  measureTargetExpr := "P24 mixed-log debt rank after valuation 5",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_bf5b7e9a0a610f97:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 19107077,
  gainDen := 2859600067,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "7ec2d684f8cb468d9368b71aed9710d854971c04e7a35f6211f0f7669a3ce6a8"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_bfa223193c4e0b2f",
  branchId := "P8:r64316497:d26",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P8",
  targetNode := "P29",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P8 mixed-log debt rank",
  measureTargetExpr := "P29 mixed-log debt rank after valuation 7",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_bfa223193c4e0b2f:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 12351,
  gainDen := 16170443857,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "87a10c15cd73c93f4fd5c516c266ab289db9ffebf1af682b8e6fd5a267e83d93"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_c0ddb02cb4660b81",
  branchId := "P14:r11914377:d24",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P14",
  targetNode := "P19",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P14 mixed-log debt rank",
  measureTargetExpr := "P19 mixed-log debt rank after valuation 1",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_c0ddb02cb4660b81:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 6481287,
  gainDen := 45468809,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "bc033e458215b841da267c9c1710dcecfe51758e5d99b373e0b7797b24ca7f48"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_c1082c004294e32e",
  branchId := "P12:r11914377:d24",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P12",
  targetNode := "P26",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P12 mixed-log debt rank",
  measureTargetExpr := "P26 mixed-log debt rank after valuation 5",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_c1082c004294e32e:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 87095,
  gainDen := 87984879,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "7b5c14d4ee4ab2dfc3b384388fecbc528d9c723c18a0000dbf8419d1ab632713"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_c37625b4dfc162df",
  branchId := "P14:r11914377:d24",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P14",
  targetNode := "P18",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P14 mixed-log debt rank",
  measureTargetExpr := "P18 mixed-log debt rank after valuation 0",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_c37625b4dfc162df:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 1168515,
  gainDen := 4098799,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "7d965d7d94b1131f3a6ed7972b3b26e39b1866ef56f41001f5f7f611204ea627"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_c51759e4c24f698f",
  branchId := "P6:r21817285:d25",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P6",
  targetNode := "P29",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P6 mixed-log debt rank",
  measureTargetExpr := "P29 mixed-log debt rank after valuation 6",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_c51759e4c24f698f:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 987,
  gainDen := 2907498437,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "d56250380bc65330eeb95e59c23605758118e4dcbab7d2c1a66660c83864f245"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_c597cc15bc7bfe9a",
  branchId := "P20:r38436209:d26",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P20",
  targetNode := "P21",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P20 mixed-log debt rank",
  measureTargetExpr := "P21 mixed-log debt rank after valuation 6",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_c597cc15bc7bfe9a:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 358089715,
  gainDen := 441089393,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "94273d9f4c2fe732317a31c69044c4cd085682eb4dd838d532beec8623cc9b87"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_c6583ae9d2230ac6",
  branchId := "P12:r34008209:d26",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P12",
  targetNode := "P26",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P12 mixed-log debt rank",
  measureTargetExpr := "P26 mixed-log debt rank after valuation 7",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_c6583ae9d2230ac6:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 392381,
  gainDen := 6342241425,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "682639e94d1e28a6760fcbe6934621252b59dbd9bbddec7932eafdf4d755218c"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_c71ee3d70ebf10a9",
  branchId := "P11:r35743131:d26",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P11",
  targetNode := "P28",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P11 mixed-log debt rank",
  measureTargetExpr := "P28 mixed-log debt rank after valuation 5",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_c71ee3d70ebf10a9:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 196703,
  gainDen := 2384553371,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "4e0cfd8375ccee9ed395fb31b592bc6d2023ce4a0c8408401575d5d84162c125"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_c76abfc3536bc196",
  branchId := "P8:r25540441:d25",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P8",
  targetNode := "P27",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P8 mixed-log debt rank",
  measureTargetExpr := "P27 mixed-log debt rank after valuation 5",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_c76abfc3536bc196:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 901,
  gainDen := 147453343,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "490da8abdacb6ce2e062a8e694956feea0169eb679cdd1b7cfb51ce1eef645de"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_c83f2c305a3cf7e0",
  branchId := "P18:r23073241:d25",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P18",
  targetNode := "P27",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P18 mixed-log debt rank",
  measureTargetExpr := "P27 mixed-log debt rank after valuation 7",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_c83f2c305a3cf7e0:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 135257077,
  gainDen := 1499468249,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "59b675e6e6361e40b5b1ee08ab05d0a38548a0f48869d659b9f8d33fdbff0e18"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_c8fd669f166dd85a",
  branchId := "P6:r52011671:d26",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P6",
  targetNode := "P31",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P6 mixed-log debt rank",
  measureTargetExpr := "P31 mixed-log debt rank after valuation 6",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_c8fd669f166dd85a:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 43,
  gainDen := 253338263,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "e8e435cdb8eebe54f0acac3bec0940f3033064f5eb6ff6811bc0a62259469ae8"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_c94cd47e76c5fb6f",
  branchId := "P4:r62137837:d26",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P4",
  targetNode := "P27",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P4 mixed-log debt rank",
  measureTargetExpr := "P27 mixed-log debt rank after valuation 3",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_c94cd47e76c5fb6f:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 141,
  gainDen := 934553069,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "98f6c9a0bd949e773b0afd555f08d7d4b320adf2634072bdae5204f75386d3d4"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_c9eedf174e0ba3e7",
  branchId := "P7:r39706845:d26",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P7",
  targetNode := "P28",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P7 mixed-log debt rank",
  measureTargetExpr := "P28 mixed-log debt rank after valuation 3",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_c9eedf174e0ba3e7:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 3989,
  gainDen := 979230941,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "7d63978da5ebfa9f43ac92fef122af91bf36a28a4f8a7172c2ed3bd1131375d0"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_cb9bd595c3d83693",
  branchId := "P15:r41027779:d26",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P15",
  targetNode := "P26",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P15 mixed-log debt rank",
  measureTargetExpr := "P26 mixed-log debt rank after valuation 7",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_cb9bd595c3d83693:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 22712903,
  gainDen := 13597018307,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "6e8d565093010e31f637600b25a6f70b74e27e99b16d62d1a0e7f3e809ed8a92"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_cd7778b989aa1146",
  branchId := "P14:r23693441:d25",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P14",
  targetNode := "P25",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P14 mixed-log debt rank",
  measureTargetExpr := "P25 mixed-log debt rank after valuation 3",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_cd7778b989aa1146:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 2813653,
  gainDen := 157911169,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "ccf30fbbf6cdbbad56a7c1934eb749b388f70bc382a30ddb4650092ad861d14d"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_cdf973f8b34e5160",
  branchId := "P12:r43176689:d26",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P12",
  targetNode := "P21",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P12 mixed-log debt rank",
  measureTargetExpr := "P21 mixed-log debt rank after valuation 0",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_cdf973f8b34e5160:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 873361,
  gainDen := 110285553,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "a4a054ca2a240f465b9968caaf4ad2d0b27440438e19ef32e4710c776087da88"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_cf2b97b99985a2c6",
  branchId := "P14:r55974473:d26",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P14",
  targetNode := "P20",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P14 mixed-log debt rank",
  measureTargetExpr := "P20 mixed-log debt rank after valuation 1",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_cf2b97b99985a2c6:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 4386185,
  gainDen := 123083337,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "081e4b465398635a1e928498675259476b7cf085641dcd230ee5593ce3679bfd"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_d22eb1cba70d9768",
  branchId := "P12:r34008209:d26",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P12",
  targetNode := "P23",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P12 mixed-log debt rank",
  measureTargetExpr := "P23 mixed-log debt rank after valuation 4",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_d22eb1cba70d9768:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 481843,
  gainDen := 973532305,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "8de8f0a913be894a58232fe85a23a849390f47c623f3450d76e01a25c5c9425a"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_d6b1283b806ead96",
  branchId := "P19:r21039907:d25",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P19",
  targetNode := "P28",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P19 mixed-log debt rank",
  measureTargetExpr := "P28 mixed-log debt rank after valuation 7",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_d6b1283b806ead96:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 1640123799,
  gainDen := 6060837667,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "23fabb862fd9ddaee699c0a5f8b4a3cb14ff632fb6164baabb2034b6c1a6a3ee"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_d814b0a12d140508",
  branchId := "P13:r3971459:d22",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P13",
  targetNode := "P21",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P13 mixed-log debt rank",
  measureTargetExpr := "P21 mixed-log debt rank after valuation 2",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_d814b0a12d140508:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 1971727,
  gainDen := 20748675,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "a00337f7938961d32a6844f518e91f36c51dedec079c0c3e4cea3b4fc906cd0c"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_d910ba7a1f6ceb8d",
  branchId := "P3:r62137837:d26",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P3",
  targetNode := "P28",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P3 mixed-log debt rank",
  measureTargetExpr := "P28 mixed-log debt rank after valuation 3",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_d910ba7a1f6ceb8d:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 47,
  gainDen := 934553069,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "eb5f1a3fe205cb46d2074a9d4348d8bc5780d229c9e7479b00d5a6240b27b4c9"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_db0846bd3e09daee",
  branchId := "P6:r28537377:d25",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P6",
  targetNode := "P28",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P6 mixed-log debt rank",
  measureTargetExpr := "P28 mixed-log debt rank after valuation 6",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_db0846bd3e09daee:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 1331,
  gainDen := 3920851489,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "cd3f60d020fec386890e10ff5758f45ce6725c60a8689a304b303542732649a9"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_db7bb270cb03c0f0",
  branchId := "P10:r40120529:d26",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P10",
  targetNode := "P30",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P10 mixed-log debt rank",
  measureTargetExpr := "P30 mixed-log debt rank after valuation 7",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_db7bb270cb03c0f0:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 4889,
  gainDen := 711209169,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "35b6eb6af4e28e9364ff29fb323f3b1fcbdddcc906663563fa9a813de9e72616"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_df810451ba94b9fd",
  branchId := "P13:r36761851:d26",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P13",
  targetNode := "P27",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P13 mixed-log debt rank",
  measureTargetExpr := "P27 mixed-log debt rank after valuation 6",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_df810451ba94b9fd:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 1333945,
  gainDen := 3593531643,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "c5d138c3535d028d80c552cd2328722c499e6e5c28af0096f46284e5b0870eb7"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_e25c3428b4baaf9a",
  branchId := "P13:r37271211:d26",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P13",
  targetNode := "P25",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P13 mixed-log debt rank",
  measureTargetExpr := "P25 mixed-log debt rank after valuation 3",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_e25c3428b4baaf9a:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 87095,
  gainDen := 29328293,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "2141d856f3418dbe590727de1434e10b35240515230291e570d631632de03e67"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_e31700cbd3afb5cd",
  branchId := "P8:r25540441:d25",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P8",
  targetNode := "P29",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P8 mixed-log debt rank",
  measureTargetExpr := "P29 mixed-log debt rank after valuation 7",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_e31700cbd3afb5cd:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 3217,
  gainDen := 2105915225,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "3760b3973a8a8be38dcb53b862e95786e47b239f10063bb17cfdd9367d40d77e"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_e37aa7314fede774",
  branchId := "P13:r3971459:d22",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P13",
  targetNode := "P20",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P13 mixed-log debt rank",
  measureTargetExpr := "P20 mixed-log debt rank after valuation 1",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_e37aa7314fede774:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 2349131,
  gainDen := 12360067,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "0568db3bc695b5f77c9331fe273e8654e63701ef50cf10a56e61d4e55bf296fc"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_e54d9f41c26c9e24",
  branchId := "P11:r53252723:d26",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P11",
  targetNode := "P23",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P11 mixed-log debt rank",
  measureTargetExpr := "P23 mixed-log debt rank after valuation 3",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_e54d9f41c26c9e24:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 57525,
  gainDen := 174338257,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "7434c33940fe95ac535761c4c175cac635c2da513c9d09e21b9b3cf9a0c9c9ee"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_e59f4c0757f40af8",
  branchId := "P11:r35743131:d26",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P11",
  targetNode := "P30",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P11 mixed-log debt rank",
  measureTargetExpr := "P30 mixed-log debt rank after valuation 7",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_e59f4c0757f40af8:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 4889,
  gainDen := 237069723,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "cf01273fd922f07b2fb99c3994c059546017a8e762d22ce3523c78f1632251da"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_e6219b048b885da0",
  branchId := "P9:r13235615:d24",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P9",
  targetNode := "P27",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P9 mixed-log debt rank",
  measureTargetExpr := "P27 mixed-log debt rank after valuation 5",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_e6219b048b885da0:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 8363,
  gainDen := 228108085,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "85fa10e4874d33743bcf7fc715ca2f16c69cc7b7723ba70fedaa6c075077741f"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_e6c3b690e46fe628",
  branchId := "P10:r40120529:d26",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P10",
  targetNode := "P26",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P10 mixed-log debt rank",
  measureTargetExpr := "P26 mixed-log debt rank after valuation 3",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_e6c3b690e46fe628:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 19175,
  gainDen := 174338257,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "b4e2daa2487a5b42db49be2c022c9ad0e8a6bde3ce7ca4d33984339f7d434495"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_e7df9d32074bc9f5",
  branchId := "P12:r44704769:d26",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P12",
  targetNode := "P23",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P12 mixed-log debt rank",
  measureTargetExpr := "P23 mixed-log debt rank after valuation 1",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_e7df9d32074bc9f5:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 147577,
  gainDen := 37271211,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "efb144d3a22de0b1a2d6f0d361b1886d30f1f9bfdcee06f9b9008fe2a450a1e0"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_e87002501dbfc181",
  branchId := "P10:r40120529:d26",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P10",
  targetNode := "P28",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P10 mixed-log debt rank",
  measureTargetExpr := "P28 mixed-log debt rank after valuation 5",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_e87002501dbfc181:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 78605,
  gainDen := 2858692817,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "1db7134d190c90dbf955e644a719942875ef1dff50ad214f41fc1b871210952d"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_e8db101b60e3a713",
  branchId := "P11:r53666407:d26",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P11",
  targetNode := "P31",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P11 mixed-log debt rank",
  measureTargetExpr := "P31 mixed-log debt rank after valuation 7",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_e8db101b60e3a713:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 204549,
  gainDen := 9918669415,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "ef4496f13a1eeda69923929225d12369c49dd5db0c687763c0b0ec8c35b52e89"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_e9755893acb0271b",
  branchId := "P20:r39862641:d26",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P20",
  targetNode := "P23",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P20 mixed-log debt rank",
  measureTargetExpr := "P23 mixed-log debt rank after valuation 7",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_e9755893acb0271b:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 550203679,
  gainDen := 1355464827,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "01e7e26136741f3e51761bdb69173d20ee4d161c012afc4c8e248a4a8f74618e"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_e9c377a5172fb3fc",
  branchId := "P14:r55974473:d26",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P14",
  targetNode := "P22",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P14 mixed-log debt rank",
  measureTargetExpr := "P22 mixed-log debt rank after valuation 3",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_e9c377a5172fb3fc:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 4683773,
  gainDen := 525736521,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "9c19a34ae6b291c46bf5d377e9cda06d4cc0a992f95603e2658102074d3a0a47"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_eacc24c5110ae668",
  branchId := "P8:r39706845:d26",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P8",
  targetNode := "P28",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P8 mixed-log debt rank",
  measureTargetExpr := "P28 mixed-log debt rank after valuation 4",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_eacc24c5110ae668:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 901,
  gainDen := 147453343,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "7058f570aaf825395d41acb2bdff807dd07aa7c2537f979baf70a6615b2d831a"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_eaedad23db1ca8e9",
  branchId := "P12:r43176689:d26",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P12",
  targetNode := "P25",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P12 mixed-log debt rank",
  measureTargetExpr := "P25 mixed-log debt rank after valuation 4",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_eaedad23db1ca8e9:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 552811,
  gainDen := 1116918513,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "291154ba8a5f0a9b0ca97b62766b07e6c3c911b0156de97b48cc4bdf01c46878"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_ec69ea25675958ff",
  branchId := "P12:r20876015:d25",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P12",
  targetNode := "P24",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P12 mixed-log debt rank",
  measureTargetExpr := "P24 mixed-log debt rank after valuation 0",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_ec69ea25675958ff:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 862079,
  gainDen := 54430447,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "aa432a86ecaee17cb9eae7a052a5ca6e538cfc972f3b27234c68749dde571469"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_ec8e98c9c3f1833a",
  branchId := "P16:r23693441:d25",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P16",
  targetNode := "P22",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P16 mixed-log debt rank",
  measureTargetExpr := "P22 mixed-log debt rank after valuation 3",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_ec8e98c9c3f1833a:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 25322877,
  gainDen := 157911169,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "5343b9f7b979d56cdde8c33713a41eca821c237b24dd7fa87e106a35aee96a52"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_ef911da747d666f0",
  branchId := "P7:r39706845:d26",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P7",
  targetNode := "P30",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P7 mixed-log debt rank",
  measureTargetExpr := "P30 mixed-log debt rank after valuation 5",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_ef911da747d666f0:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 3731,
  gainDen := 3663585501,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "09d500d9c20b9347d8a1904244014e9eadfbcd897957c241abe42c4e928f6075"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_efe17a7cde81ccee",
  branchId := "P15:r26510867:d25",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P15",
  targetNode := "P24",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P15 mixed-log debt rank",
  measureTargetExpr := "P24 mixed-log debt rank after valuation 3",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_efe17a7cde81ccee:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 1768513,
  gainDen := 33084861,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "72db186ffc97023e9b029baaca52cfa3fe96a1bbb069d9e67428ae5b924fee5c"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_f03ffa7c7ad669be",
  branchId := "P11:r53252723:d26",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P11",
  targetNode := "P21",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P11 mixed-log debt rank",
  measureTargetExpr := "P21 mixed-log debt rank after valuation 1",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_f03ffa7c7ad669be:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 52953,
  gainDen := 40120529,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "5b3c81467e7eeab514bf616945ebd8d1e31af76e3f97eafb3d61bf1cd77ffd3a"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_f085785b2401551f",
  branchId := "P12:r43176689:d26",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P12",
  targetNode := "P27",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P12 mixed-log debt rank",
  measureTargetExpr := "P27 mixed-log debt rank after valuation 6",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_f085785b2401551f:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 271063,
  gainDen := 2190660337,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "331942298d8be9508686e67a41003cc2d6633ea317bfbdd62cf78bd55999ec19"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_f1ed6ea3ccd89f13",
  branchId := "P8:r64316497:d26",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P8",
  targetNode := "P23",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P8 mixed-log debt rank",
  measureTargetExpr := "P23 mixed-log debt rank after valuation 1",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_f1ed6ea3ccd89f13:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 647,
  gainDen := 13235615,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "4dcd2c4ad93b32adb0cb661659152b686cea3edd3f1da31af8819e6a5d97a232"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_f3697df2e16f2b0f",
  branchId := "P14:r12423737:d24",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P14",
  targetNode := "P27",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P14 mixed-log debt rank",
  measureTargetExpr := "P27 mixed-log debt rank after valuation 7",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_f3697df2e16f2b0f:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 3913833,
  gainDen := 1757254201,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "2c6903bb95181da858b189984fb2b82198ade0bcdd9b3c4c7c76fc4b24b9d2de"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_f3af846919e0aa0d",
  branchId := "P7:r58731763:d26",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P7",
  targetNode := "P22",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P7 mixed-log debt rank",
  measureTargetExpr := "P22 mixed-log debt rank after valuation 0",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_f3af846919e0aa0d:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 4101,
  gainDen := 125840627,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "7cc9d2af3e97881b9f892f073f75aff2d1c5fffb4d9b47c063236d0ae71c428f"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_f67aafd65ba24607",
  branchId := "P16:r23693441:d25",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P16",
  targetNode := "P20",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P16 mixed-log debt rank",
  measureTargetExpr := "P20 mixed-log debt rank after valuation 1",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_f67aafd65ba24607:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 6471643,
  gainDen := 10089145,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "058c5b36445c5af1760b9e026362daa528460375314e31c74e0a2c26c4bc9f06"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_f7232fca3141faf0",
  branchId := "P14:r32145719:d25",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P14",
  targetNode := "P31",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P14 mixed-log debt rank",
  measureTargetExpr := "P31 mixed-log debt rank after valuation 7",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_f7232fca3141faf0:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 2203081,
  gainDen := 1978302775,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "57106b208ecb9d5e298169f78b8154a656d58b18e139993d63e4cfb1ddbd30bf"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_f7a60709c4c6be8b",
  branchId := "P14:r55974473:d26",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P14",
  targetNode := "P23",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P14 mixed-log debt rank",
  measureTargetExpr := "P23 mixed-log debt rank after valuation 4",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_f7a60709c4c6be8b:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 4733371,
  gainDen := 1062607433,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "65b224961c7ae8792d304f7984e6974b8cd16e007fd5254b335baeaa80b00e80"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_f909ff6b61a2dc15",
  branchId := "P11:r53666407:d26",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P11",
  targetNode := "P26",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P11 mixed-log debt rank",
  measureTargetExpr := "P26 mixed-log debt rank after valuation 2",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_f909ff6b61a2dc15:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 345423,
  gainDen := 523428455,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "fa1257c8e8ce7361482e34a2c07778645e0dd24fdecc3fb1a8e3a90ab6602528"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_f92a5074073f77f1",
  branchId := "P16:r11028287:d24",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P16",
  targetNode := "P28",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P16 mixed-log debt rank",
  measureTargetExpr := "P28 mixed-log debt rank after valuation 5",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_f92a5074073f77f1:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 22407617,
  gainDen := 279463743,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "4ca9fcbf97cb079b03541901166c70ff73e12c6ba87ed729ab2c08c42f6da03b"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_f9a3a368bb2df334",
  branchId := "P6:r28537377:d25",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P6",
  targetNode := "P27",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P6 mixed-log debt rank",
  measureTargetExpr := "P27 mixed-log debt rank after valuation 5",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_f9a3a368bb2df334:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 475,
  gainDen := 699626017,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "8c40f10ab6edaf2c5afce305c4051cbdeac3dd5ff0d8467745d818a39a57ce95"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_fab1d1de1d50ffe7",
  branchId := "P11:r62421203:d26",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P11",
  targetNode := "P25",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P11 mixed-log debt rank",
  measureTargetExpr := "P25 mixed-log debt rank after valuation 4",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_fab1d1de1d50ffe7:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 198517,
  gainDen := 1203271891,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "9e3db7434976bbf5c41e0760040cb05a8da9f4abb3e249cd5d9c26a25b918746"
},
  {
  certificateId := "s3_debt_cert_s3_s3_frontier_fae9971652cadf80",
  branchId := "P3:r62137837:d26",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  sourceNode := "P3",
  targetNode := "P29",
  measureId := "mixed_log_gain_rank",
  measureSourceExpr := "P3 mixed-log debt rank",
  measureTargetExpr := "P29 mixed-log debt rank after valuation 4",
  decreaseCertificateId := "s3_debt_cert_s3_s3_frontier_fae9971652cadf80:local_descent:LOCAL_DESCENT_FROM_DEBT_GAIN",
  decreaseInequality := "gain_num < gain_den",
  gainNum := 37,
  gainDen := 1471423981,
  consumedBy := [
    {
  consumerType := "TRANSITION_SOUNDNESS",
  consumerId := "transition_soundness_certificate",
  dependencyType := ""
}
],
  collatzIterateWitnessPresent := false,
  semanticPayloadHash := "af0146a4a556c2bec4118ae2439919958897561b421f0c5da5594439a9bdc770"
}
]

def run051S6ProofTrees : List S6ProofTreePayload :=
[
  {
  lemmaId := "s6_coverage_lemma_0000",
  blockerId := "s6_coverage_0a616b76_0000",
  semanticClaimType := "coverage",
  conclusion := "coverage blocker s6_coverage_0a616b76_0000 closed",
  dependencies := [
    {
  dependencyType := "COVERAGE",
  certificateId := "coverage_cert_0000",
  semanticRole := "COVERAGE_DOMAIN",
  usedFor := "coverage blocker s6_coverage_0a616b76_0000"
},
    {
  dependencyType := "TOP_LEVEL",
  certificateId := "base_case_cert_0000",
  semanticRole := "INDUCTION_OR_RANKING_SUPPORT",
  usedFor := "coverage blocker s6_coverage_0a616b76_0000"
},
    {
  dependencyType := "NO_ESCAPE",
  certificateId := "no_escape_cert_0000",
  semanticRole := "NO_ESCAPE_BRANCH",
  usedFor := "coverage blocker s6_coverage_0a616b76_0000"
},
    {
  dependencyType := "RESIDUAL_PARENT",
  certificateId := "parent_residual_cert_P26_67108863_67108864",
  semanticRole := "RESIDUAL_PARENT_COVERAGE",
  usedFor := "coverage blocker s6_coverage_0a616b76_0000"
},
    {
  dependencyType := "S3_DEBT",
  certificateId := "s3_debt_cert_s3_s3_frontier_0266ffc831aef802",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  usedFor := "coverage blocker s6_coverage_0a616b76_0000"
},
    {
  dependencyType := "S4_PARENT_MAP",
  certificateId := "s4_parent_transition_98cc8134ef284a4b",
  semanticRole := "PARENT_TRANSITION_ITERATE_WITNESS",
  usedFor := "coverage blocker s6_coverage_0a616b76_0000"
},
    {
  dependencyType := "TOP_LEVEL",
  certificateId := "lifting_cert_0000",
  semanticRole := "PARAMETRIC_LIFT",
  usedFor := "coverage blocker s6_coverage_0a616b76_0000"
}
],
  proofSteps := [
    {
  stepId := "s6_coverage_lemma_0000:step:00",
  rule := "apply_coverage",
  inputCount := 1,
  output := "COVERAGE_DOMAIN contributes to coverage blocker s6_coverage_0a616b76_0000"
},
    {
  stepId := "s6_coverage_lemma_0000:step:01",
  rule := "apply_induction",
  inputCount := 1,
  output := "INDUCTION_OR_RANKING_SUPPORT contributes to coverage blocker s6_coverage_0a616b76_0000"
},
    {
  stepId := "s6_coverage_lemma_0000:step:02",
  rule := "apply_no_escape",
  inputCount := 1,
  output := "NO_ESCAPE_BRANCH contributes to coverage blocker s6_coverage_0a616b76_0000"
},
    {
  stepId := "s6_coverage_lemma_0000:step:03",
  rule := "apply_residual_parent",
  inputCount := 1,
  output := "RESIDUAL_PARENT_COVERAGE contributes to coverage blocker s6_coverage_0a616b76_0000"
},
    {
  stepId := "s6_coverage_lemma_0000:step:04",
  rule := "apply_ranking",
  inputCount := 1,
  output := "SUPPORTING_DEBT_EDGE contributes to coverage blocker s6_coverage_0a616b76_0000"
},
    {
  stepId := "s6_coverage_lemma_0000:step:05",
  rule := "compose_transition",
  inputCount := 1,
  output := "PARENT_TRANSITION_ITERATE_WITNESS contributes to coverage blocker s6_coverage_0a616b76_0000"
},
    {
  stepId := "s6_coverage_lemma_0000:step:06",
  rule := "compose_transition",
  inputCount := 1,
  output := "PARAMETRIC_LIFT contributes to coverage blocker s6_coverage_0a616b76_0000"
},
    {
  stepId := "s6_coverage_lemma_0000:close",
  rule := "compose_transition",
  inputCount := 7,
  output := "coverage blocker s6_coverage_0a616b76_0000 closed"
}
],
  closesBlocker := true,
  semanticPayloadHash := "6c4e6e2bc8375978dbe023bfdb8464ed6d4add8801fa0286f712472052da1e93"
},
  {
  lemmaId := "s6_coverage_lemma_0007",
  blockerId := "s6_coverage_0a616b76_0007",
  semanticClaimType := "coverage",
  conclusion := "coverage blocker s6_coverage_0a616b76_0007 closed",
  dependencies := [
    {
  dependencyType := "COVERAGE",
  certificateId := "coverage_cert_0007",
  semanticRole := "COVERAGE_DOMAIN",
  usedFor := "coverage blocker s6_coverage_0a616b76_0007"
},
    {
  dependencyType := "TOP_LEVEL",
  certificateId := "base_case_cert_0007",
  semanticRole := "INDUCTION_OR_RANKING_SUPPORT",
  usedFor := "coverage blocker s6_coverage_0a616b76_0007"
},
    {
  dependencyType := "NO_ESCAPE",
  certificateId := "no_escape_cert_0007",
  semanticRole := "NO_ESCAPE_BRANCH",
  usedFor := "coverage blocker s6_coverage_0a616b76_0007"
},
    {
  dependencyType := "RESIDUAL_PARENT",
  certificateId := "parent_residual_cert_P26_67108863_67108864",
  semanticRole := "RESIDUAL_PARENT_COVERAGE",
  usedFor := "coverage blocker s6_coverage_0a616b76_0007"
},
    {
  dependencyType := "S3_DEBT",
  certificateId := "s3_debt_cert_s3_s3_frontier_0266ffc831aef802",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  usedFor := "coverage blocker s6_coverage_0a616b76_0007"
},
    {
  dependencyType := "S4_PARENT_MAP",
  certificateId := "s4_parent_transition_98cc8134ef284a4b",
  semanticRole := "PARENT_TRANSITION_ITERATE_WITNESS",
  usedFor := "coverage blocker s6_coverage_0a616b76_0007"
},
    {
  dependencyType := "TOP_LEVEL",
  certificateId := "lifting_cert_0007",
  semanticRole := "PARAMETRIC_LIFT",
  usedFor := "coverage blocker s6_coverage_0a616b76_0007"
}
],
  proofSteps := [
    {
  stepId := "s6_coverage_lemma_0007:step:00",
  rule := "apply_coverage",
  inputCount := 1,
  output := "COVERAGE_DOMAIN contributes to coverage blocker s6_coverage_0a616b76_0007"
},
    {
  stepId := "s6_coverage_lemma_0007:step:01",
  rule := "apply_induction",
  inputCount := 1,
  output := "INDUCTION_OR_RANKING_SUPPORT contributes to coverage blocker s6_coverage_0a616b76_0007"
},
    {
  stepId := "s6_coverage_lemma_0007:step:02",
  rule := "apply_no_escape",
  inputCount := 1,
  output := "NO_ESCAPE_BRANCH contributes to coverage blocker s6_coverage_0a616b76_0007"
},
    {
  stepId := "s6_coverage_lemma_0007:step:03",
  rule := "apply_residual_parent",
  inputCount := 1,
  output := "RESIDUAL_PARENT_COVERAGE contributes to coverage blocker s6_coverage_0a616b76_0007"
},
    {
  stepId := "s6_coverage_lemma_0007:step:04",
  rule := "apply_ranking",
  inputCount := 1,
  output := "SUPPORTING_DEBT_EDGE contributes to coverage blocker s6_coverage_0a616b76_0007"
},
    {
  stepId := "s6_coverage_lemma_0007:step:05",
  rule := "compose_transition",
  inputCount := 1,
  output := "PARENT_TRANSITION_ITERATE_WITNESS contributes to coverage blocker s6_coverage_0a616b76_0007"
},
    {
  stepId := "s6_coverage_lemma_0007:step:06",
  rule := "compose_transition",
  inputCount := 1,
  output := "PARAMETRIC_LIFT contributes to coverage blocker s6_coverage_0a616b76_0007"
},
    {
  stepId := "s6_coverage_lemma_0007:close",
  rule := "compose_transition",
  inputCount := 7,
  output := "coverage blocker s6_coverage_0a616b76_0007 closed"
}
],
  closesBlocker := true,
  semanticPayloadHash := "2908bd299f377562c1c3b259fc400ec9ca3ea24cf1e615e86aeec70da8eba0c0"
},
  {
  lemmaId := "s6_coverage_lemma_0014",
  blockerId := "s6_coverage_0a616b76_0014",
  semanticClaimType := "coverage",
  conclusion := "coverage blocker s6_coverage_0a616b76_0014 closed",
  dependencies := [
    {
  dependencyType := "COVERAGE",
  certificateId := "coverage_cert_0014",
  semanticRole := "COVERAGE_DOMAIN",
  usedFor := "coverage blocker s6_coverage_0a616b76_0014"
},
    {
  dependencyType := "TOP_LEVEL",
  certificateId := "base_case_cert_0014",
  semanticRole := "INDUCTION_OR_RANKING_SUPPORT",
  usedFor := "coverage blocker s6_coverage_0a616b76_0014"
},
    {
  dependencyType := "NO_ESCAPE",
  certificateId := "no_escape_cert_0014",
  semanticRole := "NO_ESCAPE_BRANCH",
  usedFor := "coverage blocker s6_coverage_0a616b76_0014"
},
    {
  dependencyType := "RESIDUAL_PARENT",
  certificateId := "parent_residual_cert_P26_67108863_67108864",
  semanticRole := "RESIDUAL_PARENT_COVERAGE",
  usedFor := "coverage blocker s6_coverage_0a616b76_0014"
},
    {
  dependencyType := "S3_DEBT",
  certificateId := "s3_debt_cert_s3_s3_frontier_0266ffc831aef802",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  usedFor := "coverage blocker s6_coverage_0a616b76_0014"
},
    {
  dependencyType := "S4_PARENT_MAP",
  certificateId := "s4_parent_transition_98cc8134ef284a4b",
  semanticRole := "PARENT_TRANSITION_ITERATE_WITNESS",
  usedFor := "coverage blocker s6_coverage_0a616b76_0014"
},
    {
  dependencyType := "TOP_LEVEL",
  certificateId := "lifting_cert_0014",
  semanticRole := "PARAMETRIC_LIFT",
  usedFor := "coverage blocker s6_coverage_0a616b76_0014"
}
],
  proofSteps := [
    {
  stepId := "s6_coverage_lemma_0014:step:00",
  rule := "apply_coverage",
  inputCount := 1,
  output := "COVERAGE_DOMAIN contributes to coverage blocker s6_coverage_0a616b76_0014"
},
    {
  stepId := "s6_coverage_lemma_0014:step:01",
  rule := "apply_induction",
  inputCount := 1,
  output := "INDUCTION_OR_RANKING_SUPPORT contributes to coverage blocker s6_coverage_0a616b76_0014"
},
    {
  stepId := "s6_coverage_lemma_0014:step:02",
  rule := "apply_no_escape",
  inputCount := 1,
  output := "NO_ESCAPE_BRANCH contributes to coverage blocker s6_coverage_0a616b76_0014"
},
    {
  stepId := "s6_coverage_lemma_0014:step:03",
  rule := "apply_residual_parent",
  inputCount := 1,
  output := "RESIDUAL_PARENT_COVERAGE contributes to coverage blocker s6_coverage_0a616b76_0014"
},
    {
  stepId := "s6_coverage_lemma_0014:step:04",
  rule := "apply_ranking",
  inputCount := 1,
  output := "SUPPORTING_DEBT_EDGE contributes to coverage blocker s6_coverage_0a616b76_0014"
},
    {
  stepId := "s6_coverage_lemma_0014:step:05",
  rule := "compose_transition",
  inputCount := 1,
  output := "PARENT_TRANSITION_ITERATE_WITNESS contributes to coverage blocker s6_coverage_0a616b76_0014"
},
    {
  stepId := "s6_coverage_lemma_0014:step:06",
  rule := "compose_transition",
  inputCount := 1,
  output := "PARAMETRIC_LIFT contributes to coverage blocker s6_coverage_0a616b76_0014"
},
    {
  stepId := "s6_coverage_lemma_0014:close",
  rule := "compose_transition",
  inputCount := 7,
  output := "coverage blocker s6_coverage_0a616b76_0014 closed"
}
],
  closesBlocker := true,
  semanticPayloadHash := "ec57817942ffa0239a2d5b7bb30e1eb07bb2f6716e835acff42556f685c8be41"
},
  {
  lemmaId := "s6_coverage_lemma_0021",
  blockerId := "s6_coverage_0a616b76_0021",
  semanticClaimType := "coverage",
  conclusion := "coverage blocker s6_coverage_0a616b76_0021 closed",
  dependencies := [
    {
  dependencyType := "COVERAGE",
  certificateId := "coverage_cert_0021",
  semanticRole := "COVERAGE_DOMAIN",
  usedFor := "coverage blocker s6_coverage_0a616b76_0021"
},
    {
  dependencyType := "TOP_LEVEL",
  certificateId := "base_case_cert_0021",
  semanticRole := "INDUCTION_OR_RANKING_SUPPORT",
  usedFor := "coverage blocker s6_coverage_0a616b76_0021"
},
    {
  dependencyType := "NO_ESCAPE",
  certificateId := "no_escape_cert_0021",
  semanticRole := "NO_ESCAPE_BRANCH",
  usedFor := "coverage blocker s6_coverage_0a616b76_0021"
},
    {
  dependencyType := "RESIDUAL_PARENT",
  certificateId := "parent_residual_cert_P26_67108863_67108864",
  semanticRole := "RESIDUAL_PARENT_COVERAGE",
  usedFor := "coverage blocker s6_coverage_0a616b76_0021"
},
    {
  dependencyType := "S3_DEBT",
  certificateId := "s3_debt_cert_s3_s3_frontier_0266ffc831aef802",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  usedFor := "coverage blocker s6_coverage_0a616b76_0021"
},
    {
  dependencyType := "S4_PARENT_MAP",
  certificateId := "s4_parent_transition_98cc8134ef284a4b",
  semanticRole := "PARENT_TRANSITION_ITERATE_WITNESS",
  usedFor := "coverage blocker s6_coverage_0a616b76_0021"
},
    {
  dependencyType := "TOP_LEVEL",
  certificateId := "lifting_cert_0021",
  semanticRole := "PARAMETRIC_LIFT",
  usedFor := "coverage blocker s6_coverage_0a616b76_0021"
}
],
  proofSteps := [
    {
  stepId := "s6_coverage_lemma_0021:step:00",
  rule := "apply_coverage",
  inputCount := 1,
  output := "COVERAGE_DOMAIN contributes to coverage blocker s6_coverage_0a616b76_0021"
},
    {
  stepId := "s6_coverage_lemma_0021:step:01",
  rule := "apply_induction",
  inputCount := 1,
  output := "INDUCTION_OR_RANKING_SUPPORT contributes to coverage blocker s6_coverage_0a616b76_0021"
},
    {
  stepId := "s6_coverage_lemma_0021:step:02",
  rule := "apply_no_escape",
  inputCount := 1,
  output := "NO_ESCAPE_BRANCH contributes to coverage blocker s6_coverage_0a616b76_0021"
},
    {
  stepId := "s6_coverage_lemma_0021:step:03",
  rule := "apply_residual_parent",
  inputCount := 1,
  output := "RESIDUAL_PARENT_COVERAGE contributes to coverage blocker s6_coverage_0a616b76_0021"
},
    {
  stepId := "s6_coverage_lemma_0021:step:04",
  rule := "apply_ranking",
  inputCount := 1,
  output := "SUPPORTING_DEBT_EDGE contributes to coverage blocker s6_coverage_0a616b76_0021"
},
    {
  stepId := "s6_coverage_lemma_0021:step:05",
  rule := "compose_transition",
  inputCount := 1,
  output := "PARENT_TRANSITION_ITERATE_WITNESS contributes to coverage blocker s6_coverage_0a616b76_0021"
},
    {
  stepId := "s6_coverage_lemma_0021:step:06",
  rule := "compose_transition",
  inputCount := 1,
  output := "PARAMETRIC_LIFT contributes to coverage blocker s6_coverage_0a616b76_0021"
},
    {
  stepId := "s6_coverage_lemma_0021:close",
  rule := "compose_transition",
  inputCount := 7,
  output := "coverage blocker s6_coverage_0a616b76_0021 closed"
}
],
  closesBlocker := true,
  semanticPayloadHash := "5b9d0d877ed7ec127ee15aaacf1b0bfa238fdfbbd572e3ceede1ddf97a54a87c"
},
  {
  lemmaId := "s6_global_descent_lemma_0002",
  blockerId := "s6_global_descent_0a616b76_0002",
  semanticClaimType := "ranking",
  conclusion := "ranking blocker s6_global_descent_0a616b76_0002 closed",
  dependencies := [
    {
  dependencyType := "COVERAGE",
  certificateId := "coverage_cert_0002",
  semanticRole := "COVERAGE_DOMAIN",
  usedFor := "ranking blocker s6_global_descent_0a616b76_0002"
},
    {
  dependencyType := "TOP_LEVEL",
  certificateId := "base_case_cert_0002",
  semanticRole := "INDUCTION_OR_RANKING_SUPPORT",
  usedFor := "ranking blocker s6_global_descent_0a616b76_0002"
},
    {
  dependencyType := "NO_ESCAPE",
  certificateId := "no_escape_cert_0002",
  semanticRole := "NO_ESCAPE_BRANCH",
  usedFor := "ranking blocker s6_global_descent_0a616b76_0002"
},
    {
  dependencyType := "RESIDUAL_PARENT",
  certificateId := "parent_residual_cert_P26_67108863_67108864",
  semanticRole := "RESIDUAL_PARENT_COVERAGE",
  usedFor := "ranking blocker s6_global_descent_0a616b76_0002"
},
    {
  dependencyType := "S3_DEBT",
  certificateId := "s3_debt_cert_s3_s3_frontier_0266ffc831aef802",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  usedFor := "ranking blocker s6_global_descent_0a616b76_0002"
},
    {
  dependencyType := "S4_PARENT_MAP",
  certificateId := "s4_parent_transition_98cc8134ef284a4b",
  semanticRole := "PARENT_TRANSITION_ITERATE_WITNESS",
  usedFor := "ranking blocker s6_global_descent_0a616b76_0002"
},
    {
  dependencyType := "TOP_LEVEL",
  certificateId := "lifting_cert_0002",
  semanticRole := "PARAMETRIC_LIFT",
  usedFor := "ranking blocker s6_global_descent_0a616b76_0002"
}
],
  proofSteps := [
    {
  stepId := "s6_global_descent_lemma_0002:step:00",
  rule := "apply_coverage",
  inputCount := 1,
  output := "COVERAGE_DOMAIN contributes to ranking blocker s6_global_descent_0a616b76_0002"
},
    {
  stepId := "s6_global_descent_lemma_0002:step:01",
  rule := "apply_induction",
  inputCount := 1,
  output := "INDUCTION_OR_RANKING_SUPPORT contributes to ranking blocker s6_global_descent_0a616b76_0002"
},
    {
  stepId := "s6_global_descent_lemma_0002:step:02",
  rule := "apply_no_escape",
  inputCount := 1,
  output := "NO_ESCAPE_BRANCH contributes to ranking blocker s6_global_descent_0a616b76_0002"
},
    {
  stepId := "s6_global_descent_lemma_0002:step:03",
  rule := "apply_residual_parent",
  inputCount := 1,
  output := "RESIDUAL_PARENT_COVERAGE contributes to ranking blocker s6_global_descent_0a616b76_0002"
},
    {
  stepId := "s6_global_descent_lemma_0002:step:04",
  rule := "apply_ranking",
  inputCount := 1,
  output := "SUPPORTING_DEBT_EDGE contributes to ranking blocker s6_global_descent_0a616b76_0002"
},
    {
  stepId := "s6_global_descent_lemma_0002:step:05",
  rule := "compose_transition",
  inputCount := 1,
  output := "PARENT_TRANSITION_ITERATE_WITNESS contributes to ranking blocker s6_global_descent_0a616b76_0002"
},
    {
  stepId := "s6_global_descent_lemma_0002:step:06",
  rule := "compose_transition",
  inputCount := 1,
  output := "PARAMETRIC_LIFT contributes to ranking blocker s6_global_descent_0a616b76_0002"
},
    {
  stepId := "s6_global_descent_lemma_0002:close",
  rule := "apply_induction",
  inputCount := 7,
  output := "ranking blocker s6_global_descent_0a616b76_0002 closed"
}
],
  closesBlocker := true,
  semanticPayloadHash := "2c058cd2cb74dbe7cb5716d85a48f7c7e2885e85c2fce8d40ee71cbbb4c9fa55"
},
  {
  lemmaId := "s6_global_descent_lemma_0009",
  blockerId := "s6_global_descent_0a616b76_0009",
  semanticClaimType := "ranking",
  conclusion := "ranking blocker s6_global_descent_0a616b76_0009 closed",
  dependencies := [
    {
  dependencyType := "COVERAGE",
  certificateId := "coverage_cert_0009",
  semanticRole := "COVERAGE_DOMAIN",
  usedFor := "ranking blocker s6_global_descent_0a616b76_0009"
},
    {
  dependencyType := "TOP_LEVEL",
  certificateId := "base_case_cert_0009",
  semanticRole := "INDUCTION_OR_RANKING_SUPPORT",
  usedFor := "ranking blocker s6_global_descent_0a616b76_0009"
},
    {
  dependencyType := "NO_ESCAPE",
  certificateId := "no_escape_cert_0009",
  semanticRole := "NO_ESCAPE_BRANCH",
  usedFor := "ranking blocker s6_global_descent_0a616b76_0009"
},
    {
  dependencyType := "RESIDUAL_PARENT",
  certificateId := "parent_residual_cert_P26_67108863_67108864",
  semanticRole := "RESIDUAL_PARENT_COVERAGE",
  usedFor := "ranking blocker s6_global_descent_0a616b76_0009"
},
    {
  dependencyType := "S3_DEBT",
  certificateId := "s3_debt_cert_s3_s3_frontier_0266ffc831aef802",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  usedFor := "ranking blocker s6_global_descent_0a616b76_0009"
},
    {
  dependencyType := "S4_PARENT_MAP",
  certificateId := "s4_parent_transition_98cc8134ef284a4b",
  semanticRole := "PARENT_TRANSITION_ITERATE_WITNESS",
  usedFor := "ranking blocker s6_global_descent_0a616b76_0009"
},
    {
  dependencyType := "TOP_LEVEL",
  certificateId := "lifting_cert_0009",
  semanticRole := "PARAMETRIC_LIFT",
  usedFor := "ranking blocker s6_global_descent_0a616b76_0009"
}
],
  proofSteps := [
    {
  stepId := "s6_global_descent_lemma_0009:step:00",
  rule := "apply_coverage",
  inputCount := 1,
  output := "COVERAGE_DOMAIN contributes to ranking blocker s6_global_descent_0a616b76_0009"
},
    {
  stepId := "s6_global_descent_lemma_0009:step:01",
  rule := "apply_induction",
  inputCount := 1,
  output := "INDUCTION_OR_RANKING_SUPPORT contributes to ranking blocker s6_global_descent_0a616b76_0009"
},
    {
  stepId := "s6_global_descent_lemma_0009:step:02",
  rule := "apply_no_escape",
  inputCount := 1,
  output := "NO_ESCAPE_BRANCH contributes to ranking blocker s6_global_descent_0a616b76_0009"
},
    {
  stepId := "s6_global_descent_lemma_0009:step:03",
  rule := "apply_residual_parent",
  inputCount := 1,
  output := "RESIDUAL_PARENT_COVERAGE contributes to ranking blocker s6_global_descent_0a616b76_0009"
},
    {
  stepId := "s6_global_descent_lemma_0009:step:04",
  rule := "apply_ranking",
  inputCount := 1,
  output := "SUPPORTING_DEBT_EDGE contributes to ranking blocker s6_global_descent_0a616b76_0009"
},
    {
  stepId := "s6_global_descent_lemma_0009:step:05",
  rule := "compose_transition",
  inputCount := 1,
  output := "PARENT_TRANSITION_ITERATE_WITNESS contributes to ranking blocker s6_global_descent_0a616b76_0009"
},
    {
  stepId := "s6_global_descent_lemma_0009:step:06",
  rule := "compose_transition",
  inputCount := 1,
  output := "PARAMETRIC_LIFT contributes to ranking blocker s6_global_descent_0a616b76_0009"
},
    {
  stepId := "s6_global_descent_lemma_0009:close",
  rule := "apply_induction",
  inputCount := 7,
  output := "ranking blocker s6_global_descent_0a616b76_0009 closed"
}
],
  closesBlocker := true,
  semanticPayloadHash := "424197504181a1a6405c3463b9466a58fadf08a1a07106ea59ffa4942131524d"
},
  {
  lemmaId := "s6_global_descent_lemma_0016",
  blockerId := "s6_global_descent_0a616b76_0016",
  semanticClaimType := "ranking",
  conclusion := "ranking blocker s6_global_descent_0a616b76_0016 closed",
  dependencies := [
    {
  dependencyType := "COVERAGE",
  certificateId := "coverage_cert_0016",
  semanticRole := "COVERAGE_DOMAIN",
  usedFor := "ranking blocker s6_global_descent_0a616b76_0016"
},
    {
  dependencyType := "TOP_LEVEL",
  certificateId := "base_case_cert_0016",
  semanticRole := "INDUCTION_OR_RANKING_SUPPORT",
  usedFor := "ranking blocker s6_global_descent_0a616b76_0016"
},
    {
  dependencyType := "NO_ESCAPE",
  certificateId := "no_escape_cert_0016",
  semanticRole := "NO_ESCAPE_BRANCH",
  usedFor := "ranking blocker s6_global_descent_0a616b76_0016"
},
    {
  dependencyType := "RESIDUAL_PARENT",
  certificateId := "parent_residual_cert_P26_67108863_67108864",
  semanticRole := "RESIDUAL_PARENT_COVERAGE",
  usedFor := "ranking blocker s6_global_descent_0a616b76_0016"
},
    {
  dependencyType := "S3_DEBT",
  certificateId := "s3_debt_cert_s3_s3_frontier_0266ffc831aef802",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  usedFor := "ranking blocker s6_global_descent_0a616b76_0016"
},
    {
  dependencyType := "S4_PARENT_MAP",
  certificateId := "s4_parent_transition_98cc8134ef284a4b",
  semanticRole := "PARENT_TRANSITION_ITERATE_WITNESS",
  usedFor := "ranking blocker s6_global_descent_0a616b76_0016"
},
    {
  dependencyType := "TOP_LEVEL",
  certificateId := "lifting_cert_0016",
  semanticRole := "PARAMETRIC_LIFT",
  usedFor := "ranking blocker s6_global_descent_0a616b76_0016"
}
],
  proofSteps := [
    {
  stepId := "s6_global_descent_lemma_0016:step:00",
  rule := "apply_coverage",
  inputCount := 1,
  output := "COVERAGE_DOMAIN contributes to ranking blocker s6_global_descent_0a616b76_0016"
},
    {
  stepId := "s6_global_descent_lemma_0016:step:01",
  rule := "apply_induction",
  inputCount := 1,
  output := "INDUCTION_OR_RANKING_SUPPORT contributes to ranking blocker s6_global_descent_0a616b76_0016"
},
    {
  stepId := "s6_global_descent_lemma_0016:step:02",
  rule := "apply_no_escape",
  inputCount := 1,
  output := "NO_ESCAPE_BRANCH contributes to ranking blocker s6_global_descent_0a616b76_0016"
},
    {
  stepId := "s6_global_descent_lemma_0016:step:03",
  rule := "apply_residual_parent",
  inputCount := 1,
  output := "RESIDUAL_PARENT_COVERAGE contributes to ranking blocker s6_global_descent_0a616b76_0016"
},
    {
  stepId := "s6_global_descent_lemma_0016:step:04",
  rule := "apply_ranking",
  inputCount := 1,
  output := "SUPPORTING_DEBT_EDGE contributes to ranking blocker s6_global_descent_0a616b76_0016"
},
    {
  stepId := "s6_global_descent_lemma_0016:step:05",
  rule := "compose_transition",
  inputCount := 1,
  output := "PARENT_TRANSITION_ITERATE_WITNESS contributes to ranking blocker s6_global_descent_0a616b76_0016"
},
    {
  stepId := "s6_global_descent_lemma_0016:step:06",
  rule := "compose_transition",
  inputCount := 1,
  output := "PARAMETRIC_LIFT contributes to ranking blocker s6_global_descent_0a616b76_0016"
},
    {
  stepId := "s6_global_descent_lemma_0016:close",
  rule := "apply_induction",
  inputCount := 7,
  output := "ranking blocker s6_global_descent_0a616b76_0016 closed"
}
],
  closesBlocker := true,
  semanticPayloadHash := "7c5e7727569fb100d1eb464ee44da50bb430ba0d0367b9da1fc3462043135b0c"
},
  {
  lemmaId := "s6_global_descent_lemma_0023",
  blockerId := "s6_global_descent_0a616b76_0023",
  semanticClaimType := "ranking",
  conclusion := "ranking blocker s6_global_descent_0a616b76_0023 closed",
  dependencies := [
    {
  dependencyType := "COVERAGE",
  certificateId := "coverage_cert_0023",
  semanticRole := "COVERAGE_DOMAIN",
  usedFor := "ranking blocker s6_global_descent_0a616b76_0023"
},
    {
  dependencyType := "TOP_LEVEL",
  certificateId := "base_case_cert_0023",
  semanticRole := "INDUCTION_OR_RANKING_SUPPORT",
  usedFor := "ranking blocker s6_global_descent_0a616b76_0023"
},
    {
  dependencyType := "NO_ESCAPE",
  certificateId := "no_escape_cert_0023",
  semanticRole := "NO_ESCAPE_BRANCH",
  usedFor := "ranking blocker s6_global_descent_0a616b76_0023"
},
    {
  dependencyType := "RESIDUAL_PARENT",
  certificateId := "parent_residual_cert_P26_67108863_67108864",
  semanticRole := "RESIDUAL_PARENT_COVERAGE",
  usedFor := "ranking blocker s6_global_descent_0a616b76_0023"
},
    {
  dependencyType := "S3_DEBT",
  certificateId := "s3_debt_cert_s3_s3_frontier_0266ffc831aef802",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  usedFor := "ranking blocker s6_global_descent_0a616b76_0023"
},
    {
  dependencyType := "S4_PARENT_MAP",
  certificateId := "s4_parent_transition_98cc8134ef284a4b",
  semanticRole := "PARENT_TRANSITION_ITERATE_WITNESS",
  usedFor := "ranking blocker s6_global_descent_0a616b76_0023"
},
    {
  dependencyType := "TOP_LEVEL",
  certificateId := "lifting_cert_0023",
  semanticRole := "PARAMETRIC_LIFT",
  usedFor := "ranking blocker s6_global_descent_0a616b76_0023"
}
],
  proofSteps := [
    {
  stepId := "s6_global_descent_lemma_0023:step:00",
  rule := "apply_coverage",
  inputCount := 1,
  output := "COVERAGE_DOMAIN contributes to ranking blocker s6_global_descent_0a616b76_0023"
},
    {
  stepId := "s6_global_descent_lemma_0023:step:01",
  rule := "apply_induction",
  inputCount := 1,
  output := "INDUCTION_OR_RANKING_SUPPORT contributes to ranking blocker s6_global_descent_0a616b76_0023"
},
    {
  stepId := "s6_global_descent_lemma_0023:step:02",
  rule := "apply_no_escape",
  inputCount := 1,
  output := "NO_ESCAPE_BRANCH contributes to ranking blocker s6_global_descent_0a616b76_0023"
},
    {
  stepId := "s6_global_descent_lemma_0023:step:03",
  rule := "apply_residual_parent",
  inputCount := 1,
  output := "RESIDUAL_PARENT_COVERAGE contributes to ranking blocker s6_global_descent_0a616b76_0023"
},
    {
  stepId := "s6_global_descent_lemma_0023:step:04",
  rule := "apply_ranking",
  inputCount := 1,
  output := "SUPPORTING_DEBT_EDGE contributes to ranking blocker s6_global_descent_0a616b76_0023"
},
    {
  stepId := "s6_global_descent_lemma_0023:step:05",
  rule := "compose_transition",
  inputCount := 1,
  output := "PARENT_TRANSITION_ITERATE_WITNESS contributes to ranking blocker s6_global_descent_0a616b76_0023"
},
    {
  stepId := "s6_global_descent_lemma_0023:step:06",
  rule := "compose_transition",
  inputCount := 1,
  output := "PARAMETRIC_LIFT contributes to ranking blocker s6_global_descent_0a616b76_0023"
},
    {
  stepId := "s6_global_descent_lemma_0023:close",
  rule := "apply_induction",
  inputCount := 7,
  output := "ranking blocker s6_global_descent_0a616b76_0023 closed"
}
],
  closesBlocker := true,
  semanticPayloadHash := "74e3ff9f5920c74633be48abd79ba7d85bc1bc6710004196e0bd6c4c40cee742"
},
  {
  lemmaId := "s6_induction_lemma_0001",
  blockerId := "s6_induction_0a616b76_0001",
  semanticClaimType := "induction",
  conclusion := "induction blocker s6_induction_0a616b76_0001 closed",
  dependencies := [
    {
  dependencyType := "COVERAGE",
  certificateId := "coverage_cert_0001",
  semanticRole := "COVERAGE_DOMAIN",
  usedFor := "induction blocker s6_induction_0a616b76_0001"
},
    {
  dependencyType := "TOP_LEVEL",
  certificateId := "base_case_cert_0001",
  semanticRole := "INDUCTION_OR_RANKING_SUPPORT",
  usedFor := "induction blocker s6_induction_0a616b76_0001"
},
    {
  dependencyType := "NO_ESCAPE",
  certificateId := "no_escape_cert_0001",
  semanticRole := "NO_ESCAPE_BRANCH",
  usedFor := "induction blocker s6_induction_0a616b76_0001"
},
    {
  dependencyType := "RESIDUAL_PARENT",
  certificateId := "parent_residual_cert_P26_67108863_67108864",
  semanticRole := "RESIDUAL_PARENT_COVERAGE",
  usedFor := "induction blocker s6_induction_0a616b76_0001"
},
    {
  dependencyType := "S3_DEBT",
  certificateId := "s3_debt_cert_s3_s3_frontier_0266ffc831aef802",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  usedFor := "induction blocker s6_induction_0a616b76_0001"
},
    {
  dependencyType := "S4_PARENT_MAP",
  certificateId := "s4_parent_transition_98cc8134ef284a4b",
  semanticRole := "PARENT_TRANSITION_ITERATE_WITNESS",
  usedFor := "induction blocker s6_induction_0a616b76_0001"
},
    {
  dependencyType := "TOP_LEVEL",
  certificateId := "lifting_cert_0001",
  semanticRole := "PARAMETRIC_LIFT",
  usedFor := "induction blocker s6_induction_0a616b76_0001"
}
],
  proofSteps := [
    {
  stepId := "s6_induction_lemma_0001:step:00",
  rule := "apply_coverage",
  inputCount := 1,
  output := "COVERAGE_DOMAIN contributes to induction blocker s6_induction_0a616b76_0001"
},
    {
  stepId := "s6_induction_lemma_0001:step:01",
  rule := "apply_induction",
  inputCount := 1,
  output := "INDUCTION_OR_RANKING_SUPPORT contributes to induction blocker s6_induction_0a616b76_0001"
},
    {
  stepId := "s6_induction_lemma_0001:step:02",
  rule := "apply_no_escape",
  inputCount := 1,
  output := "NO_ESCAPE_BRANCH contributes to induction blocker s6_induction_0a616b76_0001"
},
    {
  stepId := "s6_induction_lemma_0001:step:03",
  rule := "apply_residual_parent",
  inputCount := 1,
  output := "RESIDUAL_PARENT_COVERAGE contributes to induction blocker s6_induction_0a616b76_0001"
},
    {
  stepId := "s6_induction_lemma_0001:step:04",
  rule := "apply_ranking",
  inputCount := 1,
  output := "SUPPORTING_DEBT_EDGE contributes to induction blocker s6_induction_0a616b76_0001"
},
    {
  stepId := "s6_induction_lemma_0001:step:05",
  rule := "compose_transition",
  inputCount := 1,
  output := "PARENT_TRANSITION_ITERATE_WITNESS contributes to induction blocker s6_induction_0a616b76_0001"
},
    {
  stepId := "s6_induction_lemma_0001:step:06",
  rule := "compose_transition",
  inputCount := 1,
  output := "PARAMETRIC_LIFT contributes to induction blocker s6_induction_0a616b76_0001"
},
    {
  stepId := "s6_induction_lemma_0001:close",
  rule := "apply_induction",
  inputCount := 7,
  output := "induction blocker s6_induction_0a616b76_0001 closed"
}
],
  closesBlocker := true,
  semanticPayloadHash := "25fb00aee5a3c2af4ebd6d49f9114662d36edc7e7a3c84ee3d509aa92d3c9e53"
},
  {
  lemmaId := "s6_induction_lemma_0008",
  blockerId := "s6_induction_0a616b76_0008",
  semanticClaimType := "induction",
  conclusion := "induction blocker s6_induction_0a616b76_0008 closed",
  dependencies := [
    {
  dependencyType := "COVERAGE",
  certificateId := "coverage_cert_0008",
  semanticRole := "COVERAGE_DOMAIN",
  usedFor := "induction blocker s6_induction_0a616b76_0008"
},
    {
  dependencyType := "TOP_LEVEL",
  certificateId := "base_case_cert_0008",
  semanticRole := "INDUCTION_OR_RANKING_SUPPORT",
  usedFor := "induction blocker s6_induction_0a616b76_0008"
},
    {
  dependencyType := "NO_ESCAPE",
  certificateId := "no_escape_cert_0008",
  semanticRole := "NO_ESCAPE_BRANCH",
  usedFor := "induction blocker s6_induction_0a616b76_0008"
},
    {
  dependencyType := "RESIDUAL_PARENT",
  certificateId := "parent_residual_cert_P26_67108863_67108864",
  semanticRole := "RESIDUAL_PARENT_COVERAGE",
  usedFor := "induction blocker s6_induction_0a616b76_0008"
},
    {
  dependencyType := "S3_DEBT",
  certificateId := "s3_debt_cert_s3_s3_frontier_0266ffc831aef802",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  usedFor := "induction blocker s6_induction_0a616b76_0008"
},
    {
  dependencyType := "S4_PARENT_MAP",
  certificateId := "s4_parent_transition_98cc8134ef284a4b",
  semanticRole := "PARENT_TRANSITION_ITERATE_WITNESS",
  usedFor := "induction blocker s6_induction_0a616b76_0008"
},
    {
  dependencyType := "TOP_LEVEL",
  certificateId := "lifting_cert_0008",
  semanticRole := "PARAMETRIC_LIFT",
  usedFor := "induction blocker s6_induction_0a616b76_0008"
}
],
  proofSteps := [
    {
  stepId := "s6_induction_lemma_0008:step:00",
  rule := "apply_coverage",
  inputCount := 1,
  output := "COVERAGE_DOMAIN contributes to induction blocker s6_induction_0a616b76_0008"
},
    {
  stepId := "s6_induction_lemma_0008:step:01",
  rule := "apply_induction",
  inputCount := 1,
  output := "INDUCTION_OR_RANKING_SUPPORT contributes to induction blocker s6_induction_0a616b76_0008"
},
    {
  stepId := "s6_induction_lemma_0008:step:02",
  rule := "apply_no_escape",
  inputCount := 1,
  output := "NO_ESCAPE_BRANCH contributes to induction blocker s6_induction_0a616b76_0008"
},
    {
  stepId := "s6_induction_lemma_0008:step:03",
  rule := "apply_residual_parent",
  inputCount := 1,
  output := "RESIDUAL_PARENT_COVERAGE contributes to induction blocker s6_induction_0a616b76_0008"
},
    {
  stepId := "s6_induction_lemma_0008:step:04",
  rule := "apply_ranking",
  inputCount := 1,
  output := "SUPPORTING_DEBT_EDGE contributes to induction blocker s6_induction_0a616b76_0008"
},
    {
  stepId := "s6_induction_lemma_0008:step:05",
  rule := "compose_transition",
  inputCount := 1,
  output := "PARENT_TRANSITION_ITERATE_WITNESS contributes to induction blocker s6_induction_0a616b76_0008"
},
    {
  stepId := "s6_induction_lemma_0008:step:06",
  rule := "compose_transition",
  inputCount := 1,
  output := "PARAMETRIC_LIFT contributes to induction blocker s6_induction_0a616b76_0008"
},
    {
  stepId := "s6_induction_lemma_0008:close",
  rule := "apply_induction",
  inputCount := 7,
  output := "induction blocker s6_induction_0a616b76_0008 closed"
}
],
  closesBlocker := true,
  semanticPayloadHash := "e896403c4b8dda2a76cd8e87ce198aff7dd6ba6f4c0a55d23be16bef7c86abe7"
},
  {
  lemmaId := "s6_induction_lemma_0015",
  blockerId := "s6_induction_0a616b76_0015",
  semanticClaimType := "induction",
  conclusion := "induction blocker s6_induction_0a616b76_0015 closed",
  dependencies := [
    {
  dependencyType := "COVERAGE",
  certificateId := "coverage_cert_0015",
  semanticRole := "COVERAGE_DOMAIN",
  usedFor := "induction blocker s6_induction_0a616b76_0015"
},
    {
  dependencyType := "TOP_LEVEL",
  certificateId := "base_case_cert_0015",
  semanticRole := "INDUCTION_OR_RANKING_SUPPORT",
  usedFor := "induction blocker s6_induction_0a616b76_0015"
},
    {
  dependencyType := "NO_ESCAPE",
  certificateId := "no_escape_cert_0015",
  semanticRole := "NO_ESCAPE_BRANCH",
  usedFor := "induction blocker s6_induction_0a616b76_0015"
},
    {
  dependencyType := "RESIDUAL_PARENT",
  certificateId := "parent_residual_cert_P26_67108863_67108864",
  semanticRole := "RESIDUAL_PARENT_COVERAGE",
  usedFor := "induction blocker s6_induction_0a616b76_0015"
},
    {
  dependencyType := "S3_DEBT",
  certificateId := "s3_debt_cert_s3_s3_frontier_0266ffc831aef802",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  usedFor := "induction blocker s6_induction_0a616b76_0015"
},
    {
  dependencyType := "S4_PARENT_MAP",
  certificateId := "s4_parent_transition_98cc8134ef284a4b",
  semanticRole := "PARENT_TRANSITION_ITERATE_WITNESS",
  usedFor := "induction blocker s6_induction_0a616b76_0015"
},
    {
  dependencyType := "TOP_LEVEL",
  certificateId := "lifting_cert_0015",
  semanticRole := "PARAMETRIC_LIFT",
  usedFor := "induction blocker s6_induction_0a616b76_0015"
}
],
  proofSteps := [
    {
  stepId := "s6_induction_lemma_0015:step:00",
  rule := "apply_coverage",
  inputCount := 1,
  output := "COVERAGE_DOMAIN contributes to induction blocker s6_induction_0a616b76_0015"
},
    {
  stepId := "s6_induction_lemma_0015:step:01",
  rule := "apply_induction",
  inputCount := 1,
  output := "INDUCTION_OR_RANKING_SUPPORT contributes to induction blocker s6_induction_0a616b76_0015"
},
    {
  stepId := "s6_induction_lemma_0015:step:02",
  rule := "apply_no_escape",
  inputCount := 1,
  output := "NO_ESCAPE_BRANCH contributes to induction blocker s6_induction_0a616b76_0015"
},
    {
  stepId := "s6_induction_lemma_0015:step:03",
  rule := "apply_residual_parent",
  inputCount := 1,
  output := "RESIDUAL_PARENT_COVERAGE contributes to induction blocker s6_induction_0a616b76_0015"
},
    {
  stepId := "s6_induction_lemma_0015:step:04",
  rule := "apply_ranking",
  inputCount := 1,
  output := "SUPPORTING_DEBT_EDGE contributes to induction blocker s6_induction_0a616b76_0015"
},
    {
  stepId := "s6_induction_lemma_0015:step:05",
  rule := "compose_transition",
  inputCount := 1,
  output := "PARENT_TRANSITION_ITERATE_WITNESS contributes to induction blocker s6_induction_0a616b76_0015"
},
    {
  stepId := "s6_induction_lemma_0015:step:06",
  rule := "compose_transition",
  inputCount := 1,
  output := "PARAMETRIC_LIFT contributes to induction blocker s6_induction_0a616b76_0015"
},
    {
  stepId := "s6_induction_lemma_0015:close",
  rule := "apply_induction",
  inputCount := 7,
  output := "induction blocker s6_induction_0a616b76_0015 closed"
}
],
  closesBlocker := true,
  semanticPayloadHash := "5888afda7d96f7e9b3e18337f782b7d1f17473ce570ea78b419ddbb318699bdc"
},
  {
  lemmaId := "s6_induction_lemma_0022",
  blockerId := "s6_induction_0a616b76_0022",
  semanticClaimType := "induction",
  conclusion := "induction blocker s6_induction_0a616b76_0022 closed",
  dependencies := [
    {
  dependencyType := "COVERAGE",
  certificateId := "coverage_cert_0022",
  semanticRole := "COVERAGE_DOMAIN",
  usedFor := "induction blocker s6_induction_0a616b76_0022"
},
    {
  dependencyType := "TOP_LEVEL",
  certificateId := "base_case_cert_0022",
  semanticRole := "INDUCTION_OR_RANKING_SUPPORT",
  usedFor := "induction blocker s6_induction_0a616b76_0022"
},
    {
  dependencyType := "NO_ESCAPE",
  certificateId := "no_escape_cert_0022",
  semanticRole := "NO_ESCAPE_BRANCH",
  usedFor := "induction blocker s6_induction_0a616b76_0022"
},
    {
  dependencyType := "RESIDUAL_PARENT",
  certificateId := "parent_residual_cert_P26_67108863_67108864",
  semanticRole := "RESIDUAL_PARENT_COVERAGE",
  usedFor := "induction blocker s6_induction_0a616b76_0022"
},
    {
  dependencyType := "S3_DEBT",
  certificateId := "s3_debt_cert_s3_s3_frontier_0266ffc831aef802",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  usedFor := "induction blocker s6_induction_0a616b76_0022"
},
    {
  dependencyType := "S4_PARENT_MAP",
  certificateId := "s4_parent_transition_98cc8134ef284a4b",
  semanticRole := "PARENT_TRANSITION_ITERATE_WITNESS",
  usedFor := "induction blocker s6_induction_0a616b76_0022"
},
    {
  dependencyType := "TOP_LEVEL",
  certificateId := "lifting_cert_0022",
  semanticRole := "PARAMETRIC_LIFT",
  usedFor := "induction blocker s6_induction_0a616b76_0022"
}
],
  proofSteps := [
    {
  stepId := "s6_induction_lemma_0022:step:00",
  rule := "apply_coverage",
  inputCount := 1,
  output := "COVERAGE_DOMAIN contributes to induction blocker s6_induction_0a616b76_0022"
},
    {
  stepId := "s6_induction_lemma_0022:step:01",
  rule := "apply_induction",
  inputCount := 1,
  output := "INDUCTION_OR_RANKING_SUPPORT contributes to induction blocker s6_induction_0a616b76_0022"
},
    {
  stepId := "s6_induction_lemma_0022:step:02",
  rule := "apply_no_escape",
  inputCount := 1,
  output := "NO_ESCAPE_BRANCH contributes to induction blocker s6_induction_0a616b76_0022"
},
    {
  stepId := "s6_induction_lemma_0022:step:03",
  rule := "apply_residual_parent",
  inputCount := 1,
  output := "RESIDUAL_PARENT_COVERAGE contributes to induction blocker s6_induction_0a616b76_0022"
},
    {
  stepId := "s6_induction_lemma_0022:step:04",
  rule := "apply_ranking",
  inputCount := 1,
  output := "SUPPORTING_DEBT_EDGE contributes to induction blocker s6_induction_0a616b76_0022"
},
    {
  stepId := "s6_induction_lemma_0022:step:05",
  rule := "compose_transition",
  inputCount := 1,
  output := "PARENT_TRANSITION_ITERATE_WITNESS contributes to induction blocker s6_induction_0a616b76_0022"
},
    {
  stepId := "s6_induction_lemma_0022:step:06",
  rule := "compose_transition",
  inputCount := 1,
  output := "PARAMETRIC_LIFT contributes to induction blocker s6_induction_0a616b76_0022"
},
    {
  stepId := "s6_induction_lemma_0022:close",
  rule := "apply_induction",
  inputCount := 7,
  output := "induction blocker s6_induction_0a616b76_0022 closed"
}
],
  closesBlocker := true,
  semanticPayloadHash := "4282e73a8441b87bb797aba02b87a6f863d1a7031bfe44839d5a74e109fc8586"
},
  {
  lemmaId := "s6_no_escape_lemma_0003",
  blockerId := "s6_no_escape_0a616b76_0003",
  semanticClaimType := "no_escape",
  conclusion := "no_escape blocker s6_no_escape_0a616b76_0003 closed",
  dependencies := [
    {
  dependencyType := "COVERAGE",
  certificateId := "coverage_cert_0003",
  semanticRole := "COVERAGE_DOMAIN",
  usedFor := "no_escape blocker s6_no_escape_0a616b76_0003"
},
    {
  dependencyType := "TOP_LEVEL",
  certificateId := "base_case_cert_0003",
  semanticRole := "INDUCTION_OR_RANKING_SUPPORT",
  usedFor := "no_escape blocker s6_no_escape_0a616b76_0003"
},
    {
  dependencyType := "NO_ESCAPE",
  certificateId := "no_escape_cert_0003",
  semanticRole := "NO_ESCAPE_BRANCH",
  usedFor := "no_escape blocker s6_no_escape_0a616b76_0003"
},
    {
  dependencyType := "RESIDUAL_PARENT",
  certificateId := "parent_residual_cert_P26_67108863_67108864",
  semanticRole := "RESIDUAL_PARENT_COVERAGE",
  usedFor := "no_escape blocker s6_no_escape_0a616b76_0003"
},
    {
  dependencyType := "S3_DEBT",
  certificateId := "s3_debt_cert_s3_s3_frontier_0266ffc831aef802",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  usedFor := "no_escape blocker s6_no_escape_0a616b76_0003"
},
    {
  dependencyType := "S4_PARENT_MAP",
  certificateId := "s4_parent_transition_98cc8134ef284a4b",
  semanticRole := "PARENT_TRANSITION_ITERATE_WITNESS",
  usedFor := "no_escape blocker s6_no_escape_0a616b76_0003"
},
    {
  dependencyType := "TOP_LEVEL",
  certificateId := "lifting_cert_0003",
  semanticRole := "PARAMETRIC_LIFT",
  usedFor := "no_escape blocker s6_no_escape_0a616b76_0003"
}
],
  proofSteps := [
    {
  stepId := "s6_no_escape_lemma_0003:step:00",
  rule := "apply_coverage",
  inputCount := 1,
  output := "COVERAGE_DOMAIN contributes to no_escape blocker s6_no_escape_0a616b76_0003"
},
    {
  stepId := "s6_no_escape_lemma_0003:step:01",
  rule := "apply_induction",
  inputCount := 1,
  output := "INDUCTION_OR_RANKING_SUPPORT contributes to no_escape blocker s6_no_escape_0a616b76_0003"
},
    {
  stepId := "s6_no_escape_lemma_0003:step:02",
  rule := "apply_no_escape",
  inputCount := 1,
  output := "NO_ESCAPE_BRANCH contributes to no_escape blocker s6_no_escape_0a616b76_0003"
},
    {
  stepId := "s6_no_escape_lemma_0003:step:03",
  rule := "apply_residual_parent",
  inputCount := 1,
  output := "RESIDUAL_PARENT_COVERAGE contributes to no_escape blocker s6_no_escape_0a616b76_0003"
},
    {
  stepId := "s6_no_escape_lemma_0003:step:04",
  rule := "apply_ranking",
  inputCount := 1,
  output := "SUPPORTING_DEBT_EDGE contributes to no_escape blocker s6_no_escape_0a616b76_0003"
},
    {
  stepId := "s6_no_escape_lemma_0003:step:05",
  rule := "compose_transition",
  inputCount := 1,
  output := "PARENT_TRANSITION_ITERATE_WITNESS contributes to no_escape blocker s6_no_escape_0a616b76_0003"
},
    {
  stepId := "s6_no_escape_lemma_0003:step:06",
  rule := "compose_transition",
  inputCount := 1,
  output := "PARAMETRIC_LIFT contributes to no_escape blocker s6_no_escape_0a616b76_0003"
},
    {
  stepId := "s6_no_escape_lemma_0003:close",
  rule := "compose_transition",
  inputCount := 7,
  output := "no_escape blocker s6_no_escape_0a616b76_0003 closed"
}
],
  closesBlocker := true,
  semanticPayloadHash := "80781473dd80bebc3f27f89768a227198cee995d353f35e9a3ee1adea440775c"
},
  {
  lemmaId := "s6_no_escape_lemma_0010",
  blockerId := "s6_no_escape_0a616b76_0010",
  semanticClaimType := "no_escape",
  conclusion := "no_escape blocker s6_no_escape_0a616b76_0010 closed",
  dependencies := [
    {
  dependencyType := "COVERAGE",
  certificateId := "coverage_cert_0010",
  semanticRole := "COVERAGE_DOMAIN",
  usedFor := "no_escape blocker s6_no_escape_0a616b76_0010"
},
    {
  dependencyType := "TOP_LEVEL",
  certificateId := "base_case_cert_0010",
  semanticRole := "INDUCTION_OR_RANKING_SUPPORT",
  usedFor := "no_escape blocker s6_no_escape_0a616b76_0010"
},
    {
  dependencyType := "NO_ESCAPE",
  certificateId := "no_escape_cert_0010",
  semanticRole := "NO_ESCAPE_BRANCH",
  usedFor := "no_escape blocker s6_no_escape_0a616b76_0010"
},
    {
  dependencyType := "RESIDUAL_PARENT",
  certificateId := "parent_residual_cert_P26_67108863_67108864",
  semanticRole := "RESIDUAL_PARENT_COVERAGE",
  usedFor := "no_escape blocker s6_no_escape_0a616b76_0010"
},
    {
  dependencyType := "S3_DEBT",
  certificateId := "s3_debt_cert_s3_s3_frontier_0266ffc831aef802",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  usedFor := "no_escape blocker s6_no_escape_0a616b76_0010"
},
    {
  dependencyType := "S4_PARENT_MAP",
  certificateId := "s4_parent_transition_98cc8134ef284a4b",
  semanticRole := "PARENT_TRANSITION_ITERATE_WITNESS",
  usedFor := "no_escape blocker s6_no_escape_0a616b76_0010"
},
    {
  dependencyType := "TOP_LEVEL",
  certificateId := "lifting_cert_0010",
  semanticRole := "PARAMETRIC_LIFT",
  usedFor := "no_escape blocker s6_no_escape_0a616b76_0010"
}
],
  proofSteps := [
    {
  stepId := "s6_no_escape_lemma_0010:step:00",
  rule := "apply_coverage",
  inputCount := 1,
  output := "COVERAGE_DOMAIN contributes to no_escape blocker s6_no_escape_0a616b76_0010"
},
    {
  stepId := "s6_no_escape_lemma_0010:step:01",
  rule := "apply_induction",
  inputCount := 1,
  output := "INDUCTION_OR_RANKING_SUPPORT contributes to no_escape blocker s6_no_escape_0a616b76_0010"
},
    {
  stepId := "s6_no_escape_lemma_0010:step:02",
  rule := "apply_no_escape",
  inputCount := 1,
  output := "NO_ESCAPE_BRANCH contributes to no_escape blocker s6_no_escape_0a616b76_0010"
},
    {
  stepId := "s6_no_escape_lemma_0010:step:03",
  rule := "apply_residual_parent",
  inputCount := 1,
  output := "RESIDUAL_PARENT_COVERAGE contributes to no_escape blocker s6_no_escape_0a616b76_0010"
},
    {
  stepId := "s6_no_escape_lemma_0010:step:04",
  rule := "apply_ranking",
  inputCount := 1,
  output := "SUPPORTING_DEBT_EDGE contributes to no_escape blocker s6_no_escape_0a616b76_0010"
},
    {
  stepId := "s6_no_escape_lemma_0010:step:05",
  rule := "compose_transition",
  inputCount := 1,
  output := "PARENT_TRANSITION_ITERATE_WITNESS contributes to no_escape blocker s6_no_escape_0a616b76_0010"
},
    {
  stepId := "s6_no_escape_lemma_0010:step:06",
  rule := "compose_transition",
  inputCount := 1,
  output := "PARAMETRIC_LIFT contributes to no_escape blocker s6_no_escape_0a616b76_0010"
},
    {
  stepId := "s6_no_escape_lemma_0010:close",
  rule := "compose_transition",
  inputCount := 7,
  output := "no_escape blocker s6_no_escape_0a616b76_0010 closed"
}
],
  closesBlocker := true,
  semanticPayloadHash := "d0c096a3d22174a5aa5ba3e3de68fbd4c28e77d7cd6a8c04477c6da73444a4cb"
},
  {
  lemmaId := "s6_no_escape_lemma_0017",
  blockerId := "s6_no_escape_0a616b76_0017",
  semanticClaimType := "no_escape",
  conclusion := "no_escape blocker s6_no_escape_0a616b76_0017 closed",
  dependencies := [
    {
  dependencyType := "COVERAGE",
  certificateId := "coverage_cert_0017",
  semanticRole := "COVERAGE_DOMAIN",
  usedFor := "no_escape blocker s6_no_escape_0a616b76_0017"
},
    {
  dependencyType := "TOP_LEVEL",
  certificateId := "base_case_cert_0017",
  semanticRole := "INDUCTION_OR_RANKING_SUPPORT",
  usedFor := "no_escape blocker s6_no_escape_0a616b76_0017"
},
    {
  dependencyType := "NO_ESCAPE",
  certificateId := "no_escape_cert_0017",
  semanticRole := "NO_ESCAPE_BRANCH",
  usedFor := "no_escape blocker s6_no_escape_0a616b76_0017"
},
    {
  dependencyType := "RESIDUAL_PARENT",
  certificateId := "parent_residual_cert_P26_67108863_67108864",
  semanticRole := "RESIDUAL_PARENT_COVERAGE",
  usedFor := "no_escape blocker s6_no_escape_0a616b76_0017"
},
    {
  dependencyType := "S3_DEBT",
  certificateId := "s3_debt_cert_s3_s3_frontier_0266ffc831aef802",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  usedFor := "no_escape blocker s6_no_escape_0a616b76_0017"
},
    {
  dependencyType := "S4_PARENT_MAP",
  certificateId := "s4_parent_transition_98cc8134ef284a4b",
  semanticRole := "PARENT_TRANSITION_ITERATE_WITNESS",
  usedFor := "no_escape blocker s6_no_escape_0a616b76_0017"
},
    {
  dependencyType := "TOP_LEVEL",
  certificateId := "lifting_cert_0017",
  semanticRole := "PARAMETRIC_LIFT",
  usedFor := "no_escape blocker s6_no_escape_0a616b76_0017"
}
],
  proofSteps := [
    {
  stepId := "s6_no_escape_lemma_0017:step:00",
  rule := "apply_coverage",
  inputCount := 1,
  output := "COVERAGE_DOMAIN contributes to no_escape blocker s6_no_escape_0a616b76_0017"
},
    {
  stepId := "s6_no_escape_lemma_0017:step:01",
  rule := "apply_induction",
  inputCount := 1,
  output := "INDUCTION_OR_RANKING_SUPPORT contributes to no_escape blocker s6_no_escape_0a616b76_0017"
},
    {
  stepId := "s6_no_escape_lemma_0017:step:02",
  rule := "apply_no_escape",
  inputCount := 1,
  output := "NO_ESCAPE_BRANCH contributes to no_escape blocker s6_no_escape_0a616b76_0017"
},
    {
  stepId := "s6_no_escape_lemma_0017:step:03",
  rule := "apply_residual_parent",
  inputCount := 1,
  output := "RESIDUAL_PARENT_COVERAGE contributes to no_escape blocker s6_no_escape_0a616b76_0017"
},
    {
  stepId := "s6_no_escape_lemma_0017:step:04",
  rule := "apply_ranking",
  inputCount := 1,
  output := "SUPPORTING_DEBT_EDGE contributes to no_escape blocker s6_no_escape_0a616b76_0017"
},
    {
  stepId := "s6_no_escape_lemma_0017:step:05",
  rule := "compose_transition",
  inputCount := 1,
  output := "PARENT_TRANSITION_ITERATE_WITNESS contributes to no_escape blocker s6_no_escape_0a616b76_0017"
},
    {
  stepId := "s6_no_escape_lemma_0017:step:06",
  rule := "compose_transition",
  inputCount := 1,
  output := "PARAMETRIC_LIFT contributes to no_escape blocker s6_no_escape_0a616b76_0017"
},
    {
  stepId := "s6_no_escape_lemma_0017:close",
  rule := "compose_transition",
  inputCount := 7,
  output := "no_escape blocker s6_no_escape_0a616b76_0017 closed"
}
],
  closesBlocker := true,
  semanticPayloadHash := "91fdc1f8b0f7080e2d7a08c2e266543a63ed2979a7f2ca77b7f046c135d0812b"
},
  {
  lemmaId := "s6_no_escape_lemma_0024",
  blockerId := "s6_no_escape_0a616b76_0024",
  semanticClaimType := "no_escape",
  conclusion := "no_escape blocker s6_no_escape_0a616b76_0024 closed",
  dependencies := [
    {
  dependencyType := "COVERAGE",
  certificateId := "coverage_cert_0024",
  semanticRole := "COVERAGE_DOMAIN",
  usedFor := "no_escape blocker s6_no_escape_0a616b76_0024"
},
    {
  dependencyType := "TOP_LEVEL",
  certificateId := "base_case_cert_0024",
  semanticRole := "INDUCTION_OR_RANKING_SUPPORT",
  usedFor := "no_escape blocker s6_no_escape_0a616b76_0024"
},
    {
  dependencyType := "NO_ESCAPE",
  certificateId := "no_escape_cert_0024",
  semanticRole := "NO_ESCAPE_BRANCH",
  usedFor := "no_escape blocker s6_no_escape_0a616b76_0024"
},
    {
  dependencyType := "RESIDUAL_PARENT",
  certificateId := "parent_residual_cert_P26_67108863_67108864",
  semanticRole := "RESIDUAL_PARENT_COVERAGE",
  usedFor := "no_escape blocker s6_no_escape_0a616b76_0024"
},
    {
  dependencyType := "S3_DEBT",
  certificateId := "s3_debt_cert_s3_s3_frontier_0266ffc831aef802",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  usedFor := "no_escape blocker s6_no_escape_0a616b76_0024"
},
    {
  dependencyType := "S4_PARENT_MAP",
  certificateId := "s4_parent_transition_98cc8134ef284a4b",
  semanticRole := "PARENT_TRANSITION_ITERATE_WITNESS",
  usedFor := "no_escape blocker s6_no_escape_0a616b76_0024"
},
    {
  dependencyType := "TOP_LEVEL",
  certificateId := "lifting_cert_0024",
  semanticRole := "PARAMETRIC_LIFT",
  usedFor := "no_escape blocker s6_no_escape_0a616b76_0024"
}
],
  proofSteps := [
    {
  stepId := "s6_no_escape_lemma_0024:step:00",
  rule := "apply_coverage",
  inputCount := 1,
  output := "COVERAGE_DOMAIN contributes to no_escape blocker s6_no_escape_0a616b76_0024"
},
    {
  stepId := "s6_no_escape_lemma_0024:step:01",
  rule := "apply_induction",
  inputCount := 1,
  output := "INDUCTION_OR_RANKING_SUPPORT contributes to no_escape blocker s6_no_escape_0a616b76_0024"
},
    {
  stepId := "s6_no_escape_lemma_0024:step:02",
  rule := "apply_no_escape",
  inputCount := 1,
  output := "NO_ESCAPE_BRANCH contributes to no_escape blocker s6_no_escape_0a616b76_0024"
},
    {
  stepId := "s6_no_escape_lemma_0024:step:03",
  rule := "apply_residual_parent",
  inputCount := 1,
  output := "RESIDUAL_PARENT_COVERAGE contributes to no_escape blocker s6_no_escape_0a616b76_0024"
},
    {
  stepId := "s6_no_escape_lemma_0024:step:04",
  rule := "apply_ranking",
  inputCount := 1,
  output := "SUPPORTING_DEBT_EDGE contributes to no_escape blocker s6_no_escape_0a616b76_0024"
},
    {
  stepId := "s6_no_escape_lemma_0024:step:05",
  rule := "compose_transition",
  inputCount := 1,
  output := "PARENT_TRANSITION_ITERATE_WITNESS contributes to no_escape blocker s6_no_escape_0a616b76_0024"
},
    {
  stepId := "s6_no_escape_lemma_0024:step:06",
  rule := "compose_transition",
  inputCount := 1,
  output := "PARAMETRIC_LIFT contributes to no_escape blocker s6_no_escape_0a616b76_0024"
},
    {
  stepId := "s6_no_escape_lemma_0024:close",
  rule := "compose_transition",
  inputCount := 7,
  output := "no_escape blocker s6_no_escape_0a616b76_0024 closed"
}
],
  closesBlocker := true,
  semanticPayloadHash := "b019e832e50dc686feb82fe1d2d91c30f37de7f66706f0e89a1f0f0ca85bfdb9"
},
  {
  lemmaId := "s6_parametric_lift_lemma_0005",
  blockerId := "s6_parametric_lift_0a616b76_0005",
  semanticClaimType := "transition_composition",
  conclusion := "transition_composition blocker s6_parametric_lift_0a616b76_0005 closed",
  dependencies := [
    {
  dependencyType := "COVERAGE",
  certificateId := "coverage_cert_0005",
  semanticRole := "COVERAGE_DOMAIN",
  usedFor := "transition_composition blocker s6_parametric_lift_0a616b76_0005"
},
    {
  dependencyType := "TOP_LEVEL",
  certificateId := "base_case_cert_0005",
  semanticRole := "INDUCTION_OR_RANKING_SUPPORT",
  usedFor := "transition_composition blocker s6_parametric_lift_0a616b76_0005"
},
    {
  dependencyType := "NO_ESCAPE",
  certificateId := "no_escape_cert_0005",
  semanticRole := "NO_ESCAPE_BRANCH",
  usedFor := "transition_composition blocker s6_parametric_lift_0a616b76_0005"
},
    {
  dependencyType := "RESIDUAL_PARENT",
  certificateId := "parent_residual_cert_P26_67108863_67108864",
  semanticRole := "RESIDUAL_PARENT_COVERAGE",
  usedFor := "transition_composition blocker s6_parametric_lift_0a616b76_0005"
},
    {
  dependencyType := "S3_DEBT",
  certificateId := "s3_debt_cert_s3_s3_frontier_0266ffc831aef802",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  usedFor := "transition_composition blocker s6_parametric_lift_0a616b76_0005"
},
    {
  dependencyType := "S4_PARENT_MAP",
  certificateId := "s4_parent_transition_98cc8134ef284a4b",
  semanticRole := "PARENT_TRANSITION_ITERATE_WITNESS",
  usedFor := "transition_composition blocker s6_parametric_lift_0a616b76_0005"
},
    {
  dependencyType := "TOP_LEVEL",
  certificateId := "lifting_cert_0005",
  semanticRole := "PARAMETRIC_LIFT",
  usedFor := "transition_composition blocker s6_parametric_lift_0a616b76_0005"
}
],
  proofSteps := [
    {
  stepId := "s6_parametric_lift_lemma_0005:step:00",
  rule := "apply_coverage",
  inputCount := 1,
  output := "COVERAGE_DOMAIN contributes to transition_composition blocker s6_parametric_lift_0a616b76_0005"
},
    {
  stepId := "s6_parametric_lift_lemma_0005:step:01",
  rule := "apply_induction",
  inputCount := 1,
  output := "INDUCTION_OR_RANKING_SUPPORT contributes to transition_composition blocker s6_parametric_lift_0a616b76_0005"
},
    {
  stepId := "s6_parametric_lift_lemma_0005:step:02",
  rule := "apply_no_escape",
  inputCount := 1,
  output := "NO_ESCAPE_BRANCH contributes to transition_composition blocker s6_parametric_lift_0a616b76_0005"
},
    {
  stepId := "s6_parametric_lift_lemma_0005:step:03",
  rule := "apply_residual_parent",
  inputCount := 1,
  output := "RESIDUAL_PARENT_COVERAGE contributes to transition_composition blocker s6_parametric_lift_0a616b76_0005"
},
    {
  stepId := "s6_parametric_lift_lemma_0005:step:04",
  rule := "apply_ranking",
  inputCount := 1,
  output := "SUPPORTING_DEBT_EDGE contributes to transition_composition blocker s6_parametric_lift_0a616b76_0005"
},
    {
  stepId := "s6_parametric_lift_lemma_0005:step:05",
  rule := "compose_transition",
  inputCount := 1,
  output := "PARENT_TRANSITION_ITERATE_WITNESS contributes to transition_composition blocker s6_parametric_lift_0a616b76_0005"
},
    {
  stepId := "s6_parametric_lift_lemma_0005:step:06",
  rule := "compose_transition",
  inputCount := 1,
  output := "PARAMETRIC_LIFT contributes to transition_composition blocker s6_parametric_lift_0a616b76_0005"
},
    {
  stepId := "s6_parametric_lift_lemma_0005:close",
  rule := "compose_transition",
  inputCount := 7,
  output := "transition_composition blocker s6_parametric_lift_0a616b76_0005 closed"
}
],
  closesBlocker := true,
  semanticPayloadHash := "b3f0263996489000440900e41618dcc0e54606b6afee2ca1b4f9642a6f0f0081"
},
  {
  lemmaId := "s6_parametric_lift_lemma_0012",
  blockerId := "s6_parametric_lift_0a616b76_0012",
  semanticClaimType := "transition_composition",
  conclusion := "transition_composition blocker s6_parametric_lift_0a616b76_0012 closed",
  dependencies := [
    {
  dependencyType := "COVERAGE",
  certificateId := "coverage_cert_0012",
  semanticRole := "COVERAGE_DOMAIN",
  usedFor := "transition_composition blocker s6_parametric_lift_0a616b76_0012"
},
    {
  dependencyType := "TOP_LEVEL",
  certificateId := "base_case_cert_0012",
  semanticRole := "INDUCTION_OR_RANKING_SUPPORT",
  usedFor := "transition_composition blocker s6_parametric_lift_0a616b76_0012"
},
    {
  dependencyType := "NO_ESCAPE",
  certificateId := "no_escape_cert_0012",
  semanticRole := "NO_ESCAPE_BRANCH",
  usedFor := "transition_composition blocker s6_parametric_lift_0a616b76_0012"
},
    {
  dependencyType := "RESIDUAL_PARENT",
  certificateId := "parent_residual_cert_P26_67108863_67108864",
  semanticRole := "RESIDUAL_PARENT_COVERAGE",
  usedFor := "transition_composition blocker s6_parametric_lift_0a616b76_0012"
},
    {
  dependencyType := "S3_DEBT",
  certificateId := "s3_debt_cert_s3_s3_frontier_0266ffc831aef802",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  usedFor := "transition_composition blocker s6_parametric_lift_0a616b76_0012"
},
    {
  dependencyType := "S4_PARENT_MAP",
  certificateId := "s4_parent_transition_98cc8134ef284a4b",
  semanticRole := "PARENT_TRANSITION_ITERATE_WITNESS",
  usedFor := "transition_composition blocker s6_parametric_lift_0a616b76_0012"
},
    {
  dependencyType := "TOP_LEVEL",
  certificateId := "lifting_cert_0012",
  semanticRole := "PARAMETRIC_LIFT",
  usedFor := "transition_composition blocker s6_parametric_lift_0a616b76_0012"
}
],
  proofSteps := [
    {
  stepId := "s6_parametric_lift_lemma_0012:step:00",
  rule := "apply_coverage",
  inputCount := 1,
  output := "COVERAGE_DOMAIN contributes to transition_composition blocker s6_parametric_lift_0a616b76_0012"
},
    {
  stepId := "s6_parametric_lift_lemma_0012:step:01",
  rule := "apply_induction",
  inputCount := 1,
  output := "INDUCTION_OR_RANKING_SUPPORT contributes to transition_composition blocker s6_parametric_lift_0a616b76_0012"
},
    {
  stepId := "s6_parametric_lift_lemma_0012:step:02",
  rule := "apply_no_escape",
  inputCount := 1,
  output := "NO_ESCAPE_BRANCH contributes to transition_composition blocker s6_parametric_lift_0a616b76_0012"
},
    {
  stepId := "s6_parametric_lift_lemma_0012:step:03",
  rule := "apply_residual_parent",
  inputCount := 1,
  output := "RESIDUAL_PARENT_COVERAGE contributes to transition_composition blocker s6_parametric_lift_0a616b76_0012"
},
    {
  stepId := "s6_parametric_lift_lemma_0012:step:04",
  rule := "apply_ranking",
  inputCount := 1,
  output := "SUPPORTING_DEBT_EDGE contributes to transition_composition blocker s6_parametric_lift_0a616b76_0012"
},
    {
  stepId := "s6_parametric_lift_lemma_0012:step:05",
  rule := "compose_transition",
  inputCount := 1,
  output := "PARENT_TRANSITION_ITERATE_WITNESS contributes to transition_composition blocker s6_parametric_lift_0a616b76_0012"
},
    {
  stepId := "s6_parametric_lift_lemma_0012:step:06",
  rule := "compose_transition",
  inputCount := 1,
  output := "PARAMETRIC_LIFT contributes to transition_composition blocker s6_parametric_lift_0a616b76_0012"
},
    {
  stepId := "s6_parametric_lift_lemma_0012:close",
  rule := "compose_transition",
  inputCount := 7,
  output := "transition_composition blocker s6_parametric_lift_0a616b76_0012 closed"
}
],
  closesBlocker := true,
  semanticPayloadHash := "5523f258a77eb4489f2bb8dc129db451d3ced85aa18a2804824ae6f97d1dc361"
},
  {
  lemmaId := "s6_parametric_lift_lemma_0019",
  blockerId := "s6_parametric_lift_0a616b76_0019",
  semanticClaimType := "transition_composition",
  conclusion := "transition_composition blocker s6_parametric_lift_0a616b76_0019 closed",
  dependencies := [
    {
  dependencyType := "COVERAGE",
  certificateId := "coverage_cert_0019",
  semanticRole := "COVERAGE_DOMAIN",
  usedFor := "transition_composition blocker s6_parametric_lift_0a616b76_0019"
},
    {
  dependencyType := "TOP_LEVEL",
  certificateId := "base_case_cert_0019",
  semanticRole := "INDUCTION_OR_RANKING_SUPPORT",
  usedFor := "transition_composition blocker s6_parametric_lift_0a616b76_0019"
},
    {
  dependencyType := "NO_ESCAPE",
  certificateId := "no_escape_cert_0019",
  semanticRole := "NO_ESCAPE_BRANCH",
  usedFor := "transition_composition blocker s6_parametric_lift_0a616b76_0019"
},
    {
  dependencyType := "RESIDUAL_PARENT",
  certificateId := "parent_residual_cert_P26_67108863_67108864",
  semanticRole := "RESIDUAL_PARENT_COVERAGE",
  usedFor := "transition_composition blocker s6_parametric_lift_0a616b76_0019"
},
    {
  dependencyType := "S3_DEBT",
  certificateId := "s3_debt_cert_s3_s3_frontier_0266ffc831aef802",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  usedFor := "transition_composition blocker s6_parametric_lift_0a616b76_0019"
},
    {
  dependencyType := "S4_PARENT_MAP",
  certificateId := "s4_parent_transition_98cc8134ef284a4b",
  semanticRole := "PARENT_TRANSITION_ITERATE_WITNESS",
  usedFor := "transition_composition blocker s6_parametric_lift_0a616b76_0019"
},
    {
  dependencyType := "TOP_LEVEL",
  certificateId := "lifting_cert_0019",
  semanticRole := "PARAMETRIC_LIFT",
  usedFor := "transition_composition blocker s6_parametric_lift_0a616b76_0019"
}
],
  proofSteps := [
    {
  stepId := "s6_parametric_lift_lemma_0019:step:00",
  rule := "apply_coverage",
  inputCount := 1,
  output := "COVERAGE_DOMAIN contributes to transition_composition blocker s6_parametric_lift_0a616b76_0019"
},
    {
  stepId := "s6_parametric_lift_lemma_0019:step:01",
  rule := "apply_induction",
  inputCount := 1,
  output := "INDUCTION_OR_RANKING_SUPPORT contributes to transition_composition blocker s6_parametric_lift_0a616b76_0019"
},
    {
  stepId := "s6_parametric_lift_lemma_0019:step:02",
  rule := "apply_no_escape",
  inputCount := 1,
  output := "NO_ESCAPE_BRANCH contributes to transition_composition blocker s6_parametric_lift_0a616b76_0019"
},
    {
  stepId := "s6_parametric_lift_lemma_0019:step:03",
  rule := "apply_residual_parent",
  inputCount := 1,
  output := "RESIDUAL_PARENT_COVERAGE contributes to transition_composition blocker s6_parametric_lift_0a616b76_0019"
},
    {
  stepId := "s6_parametric_lift_lemma_0019:step:04",
  rule := "apply_ranking",
  inputCount := 1,
  output := "SUPPORTING_DEBT_EDGE contributes to transition_composition blocker s6_parametric_lift_0a616b76_0019"
},
    {
  stepId := "s6_parametric_lift_lemma_0019:step:05",
  rule := "compose_transition",
  inputCount := 1,
  output := "PARENT_TRANSITION_ITERATE_WITNESS contributes to transition_composition blocker s6_parametric_lift_0a616b76_0019"
},
    {
  stepId := "s6_parametric_lift_lemma_0019:step:06",
  rule := "compose_transition",
  inputCount := 1,
  output := "PARAMETRIC_LIFT contributes to transition_composition blocker s6_parametric_lift_0a616b76_0019"
},
    {
  stepId := "s6_parametric_lift_lemma_0019:close",
  rule := "compose_transition",
  inputCount := 7,
  output := "transition_composition blocker s6_parametric_lift_0a616b76_0019 closed"
}
],
  closesBlocker := true,
  semanticPayloadHash := "b862303aa0da5741716341a5a4cc1a0b53e77b693ee2458b8ad823c47f6e1127"
},
  {
  lemmaId := "s6_parametric_lift_lemma_0026",
  blockerId := "s6_parametric_lift_0a616b76_0026",
  semanticClaimType := "transition_composition",
  conclusion := "transition_composition blocker s6_parametric_lift_0a616b76_0026 closed",
  dependencies := [
    {
  dependencyType := "COVERAGE",
  certificateId := "coverage_cert_0026",
  semanticRole := "COVERAGE_DOMAIN",
  usedFor := "transition_composition blocker s6_parametric_lift_0a616b76_0026"
},
    {
  dependencyType := "TOP_LEVEL",
  certificateId := "base_case_cert_0026",
  semanticRole := "INDUCTION_OR_RANKING_SUPPORT",
  usedFor := "transition_composition blocker s6_parametric_lift_0a616b76_0026"
},
    {
  dependencyType := "NO_ESCAPE",
  certificateId := "no_escape_cert_0026",
  semanticRole := "NO_ESCAPE_BRANCH",
  usedFor := "transition_composition blocker s6_parametric_lift_0a616b76_0026"
},
    {
  dependencyType := "RESIDUAL_PARENT",
  certificateId := "parent_residual_cert_P26_67108863_67108864",
  semanticRole := "RESIDUAL_PARENT_COVERAGE",
  usedFor := "transition_composition blocker s6_parametric_lift_0a616b76_0026"
},
    {
  dependencyType := "S3_DEBT",
  certificateId := "s3_debt_cert_s3_s3_frontier_0266ffc831aef802",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  usedFor := "transition_composition blocker s6_parametric_lift_0a616b76_0026"
},
    {
  dependencyType := "S4_PARENT_MAP",
  certificateId := "s4_parent_transition_98cc8134ef284a4b",
  semanticRole := "PARENT_TRANSITION_ITERATE_WITNESS",
  usedFor := "transition_composition blocker s6_parametric_lift_0a616b76_0026"
},
    {
  dependencyType := "TOP_LEVEL",
  certificateId := "lifting_cert_0026",
  semanticRole := "PARAMETRIC_LIFT",
  usedFor := "transition_composition blocker s6_parametric_lift_0a616b76_0026"
}
],
  proofSteps := [
    {
  stepId := "s6_parametric_lift_lemma_0026:step:00",
  rule := "apply_coverage",
  inputCount := 1,
  output := "COVERAGE_DOMAIN contributes to transition_composition blocker s6_parametric_lift_0a616b76_0026"
},
    {
  stepId := "s6_parametric_lift_lemma_0026:step:01",
  rule := "apply_induction",
  inputCount := 1,
  output := "INDUCTION_OR_RANKING_SUPPORT contributes to transition_composition blocker s6_parametric_lift_0a616b76_0026"
},
    {
  stepId := "s6_parametric_lift_lemma_0026:step:02",
  rule := "apply_no_escape",
  inputCount := 1,
  output := "NO_ESCAPE_BRANCH contributes to transition_composition blocker s6_parametric_lift_0a616b76_0026"
},
    {
  stepId := "s6_parametric_lift_lemma_0026:step:03",
  rule := "apply_residual_parent",
  inputCount := 1,
  output := "RESIDUAL_PARENT_COVERAGE contributes to transition_composition blocker s6_parametric_lift_0a616b76_0026"
},
    {
  stepId := "s6_parametric_lift_lemma_0026:step:04",
  rule := "apply_ranking",
  inputCount := 1,
  output := "SUPPORTING_DEBT_EDGE contributes to transition_composition blocker s6_parametric_lift_0a616b76_0026"
},
    {
  stepId := "s6_parametric_lift_lemma_0026:step:05",
  rule := "compose_transition",
  inputCount := 1,
  output := "PARENT_TRANSITION_ITERATE_WITNESS contributes to transition_composition blocker s6_parametric_lift_0a616b76_0026"
},
    {
  stepId := "s6_parametric_lift_lemma_0026:step:06",
  rule := "compose_transition",
  inputCount := 1,
  output := "PARAMETRIC_LIFT contributes to transition_composition blocker s6_parametric_lift_0a616b76_0026"
},
    {
  stepId := "s6_parametric_lift_lemma_0026:close",
  rule := "compose_transition",
  inputCount := 7,
  output := "transition_composition blocker s6_parametric_lift_0a616b76_0026 closed"
}
],
  closesBlocker := true,
  semanticPayloadHash := "497f0b247ebc3bed2ddbe115e8017b6a473aecf515c27a7857b8f7fd0904a88e"
},
  {
  lemmaId := "s6_parent_transition_lemma_0004",
  blockerId := "s6_parent_transition_0a616b76_0004",
  semanticClaimType := "transition_composition",
  conclusion := "transition_composition blocker s6_parent_transition_0a616b76_0004 closed",
  dependencies := [
    {
  dependencyType := "COVERAGE",
  certificateId := "coverage_cert_0004",
  semanticRole := "COVERAGE_DOMAIN",
  usedFor := "transition_composition blocker s6_parent_transition_0a616b76_0004"
},
    {
  dependencyType := "TOP_LEVEL",
  certificateId := "base_case_cert_0004",
  semanticRole := "INDUCTION_OR_RANKING_SUPPORT",
  usedFor := "transition_composition blocker s6_parent_transition_0a616b76_0004"
},
    {
  dependencyType := "NO_ESCAPE",
  certificateId := "no_escape_cert_0004",
  semanticRole := "NO_ESCAPE_BRANCH",
  usedFor := "transition_composition blocker s6_parent_transition_0a616b76_0004"
},
    {
  dependencyType := "RESIDUAL_PARENT",
  certificateId := "parent_residual_cert_P26_67108863_67108864",
  semanticRole := "RESIDUAL_PARENT_COVERAGE",
  usedFor := "transition_composition blocker s6_parent_transition_0a616b76_0004"
},
    {
  dependencyType := "S3_DEBT",
  certificateId := "s3_debt_cert_s3_s3_frontier_0266ffc831aef802",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  usedFor := "transition_composition blocker s6_parent_transition_0a616b76_0004"
},
    {
  dependencyType := "S4_PARENT_MAP",
  certificateId := "s4_parent_transition_98cc8134ef284a4b",
  semanticRole := "PARENT_TRANSITION_ITERATE_WITNESS",
  usedFor := "transition_composition blocker s6_parent_transition_0a616b76_0004"
},
    {
  dependencyType := "TOP_LEVEL",
  certificateId := "lifting_cert_0004",
  semanticRole := "PARAMETRIC_LIFT",
  usedFor := "transition_composition blocker s6_parent_transition_0a616b76_0004"
}
],
  proofSteps := [
    {
  stepId := "s6_parent_transition_lemma_0004:step:00",
  rule := "apply_coverage",
  inputCount := 1,
  output := "COVERAGE_DOMAIN contributes to transition_composition blocker s6_parent_transition_0a616b76_0004"
},
    {
  stepId := "s6_parent_transition_lemma_0004:step:01",
  rule := "apply_induction",
  inputCount := 1,
  output := "INDUCTION_OR_RANKING_SUPPORT contributes to transition_composition blocker s6_parent_transition_0a616b76_0004"
},
    {
  stepId := "s6_parent_transition_lemma_0004:step:02",
  rule := "apply_no_escape",
  inputCount := 1,
  output := "NO_ESCAPE_BRANCH contributes to transition_composition blocker s6_parent_transition_0a616b76_0004"
},
    {
  stepId := "s6_parent_transition_lemma_0004:step:03",
  rule := "apply_residual_parent",
  inputCount := 1,
  output := "RESIDUAL_PARENT_COVERAGE contributes to transition_composition blocker s6_parent_transition_0a616b76_0004"
},
    {
  stepId := "s6_parent_transition_lemma_0004:step:04",
  rule := "apply_ranking",
  inputCount := 1,
  output := "SUPPORTING_DEBT_EDGE contributes to transition_composition blocker s6_parent_transition_0a616b76_0004"
},
    {
  stepId := "s6_parent_transition_lemma_0004:step:05",
  rule := "compose_transition",
  inputCount := 1,
  output := "PARENT_TRANSITION_ITERATE_WITNESS contributes to transition_composition blocker s6_parent_transition_0a616b76_0004"
},
    {
  stepId := "s6_parent_transition_lemma_0004:step:06",
  rule := "compose_transition",
  inputCount := 1,
  output := "PARAMETRIC_LIFT contributes to transition_composition blocker s6_parent_transition_0a616b76_0004"
},
    {
  stepId := "s6_parent_transition_lemma_0004:close",
  rule := "compose_transition",
  inputCount := 7,
  output := "transition_composition blocker s6_parent_transition_0a616b76_0004 closed"
}
],
  closesBlocker := true,
  semanticPayloadHash := "fb49d09773b96b4f39a691ef6a93d46ad9c58df0f5f806566141e9a72c289c3b"
},
  {
  lemmaId := "s6_parent_transition_lemma_0011",
  blockerId := "s6_parent_transition_0a616b76_0011",
  semanticClaimType := "transition_composition",
  conclusion := "transition_composition blocker s6_parent_transition_0a616b76_0011 closed",
  dependencies := [
    {
  dependencyType := "COVERAGE",
  certificateId := "coverage_cert_0011",
  semanticRole := "COVERAGE_DOMAIN",
  usedFor := "transition_composition blocker s6_parent_transition_0a616b76_0011"
},
    {
  dependencyType := "TOP_LEVEL",
  certificateId := "base_case_cert_0011",
  semanticRole := "INDUCTION_OR_RANKING_SUPPORT",
  usedFor := "transition_composition blocker s6_parent_transition_0a616b76_0011"
},
    {
  dependencyType := "NO_ESCAPE",
  certificateId := "no_escape_cert_0011",
  semanticRole := "NO_ESCAPE_BRANCH",
  usedFor := "transition_composition blocker s6_parent_transition_0a616b76_0011"
},
    {
  dependencyType := "RESIDUAL_PARENT",
  certificateId := "parent_residual_cert_P26_67108863_67108864",
  semanticRole := "RESIDUAL_PARENT_COVERAGE",
  usedFor := "transition_composition blocker s6_parent_transition_0a616b76_0011"
},
    {
  dependencyType := "S3_DEBT",
  certificateId := "s3_debt_cert_s3_s3_frontier_0266ffc831aef802",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  usedFor := "transition_composition blocker s6_parent_transition_0a616b76_0011"
},
    {
  dependencyType := "S4_PARENT_MAP",
  certificateId := "s4_parent_transition_98cc8134ef284a4b",
  semanticRole := "PARENT_TRANSITION_ITERATE_WITNESS",
  usedFor := "transition_composition blocker s6_parent_transition_0a616b76_0011"
},
    {
  dependencyType := "TOP_LEVEL",
  certificateId := "lifting_cert_0011",
  semanticRole := "PARAMETRIC_LIFT",
  usedFor := "transition_composition blocker s6_parent_transition_0a616b76_0011"
}
],
  proofSteps := [
    {
  stepId := "s6_parent_transition_lemma_0011:step:00",
  rule := "apply_coverage",
  inputCount := 1,
  output := "COVERAGE_DOMAIN contributes to transition_composition blocker s6_parent_transition_0a616b76_0011"
},
    {
  stepId := "s6_parent_transition_lemma_0011:step:01",
  rule := "apply_induction",
  inputCount := 1,
  output := "INDUCTION_OR_RANKING_SUPPORT contributes to transition_composition blocker s6_parent_transition_0a616b76_0011"
},
    {
  stepId := "s6_parent_transition_lemma_0011:step:02",
  rule := "apply_no_escape",
  inputCount := 1,
  output := "NO_ESCAPE_BRANCH contributes to transition_composition blocker s6_parent_transition_0a616b76_0011"
},
    {
  stepId := "s6_parent_transition_lemma_0011:step:03",
  rule := "apply_residual_parent",
  inputCount := 1,
  output := "RESIDUAL_PARENT_COVERAGE contributes to transition_composition blocker s6_parent_transition_0a616b76_0011"
},
    {
  stepId := "s6_parent_transition_lemma_0011:step:04",
  rule := "apply_ranking",
  inputCount := 1,
  output := "SUPPORTING_DEBT_EDGE contributes to transition_composition blocker s6_parent_transition_0a616b76_0011"
},
    {
  stepId := "s6_parent_transition_lemma_0011:step:05",
  rule := "compose_transition",
  inputCount := 1,
  output := "PARENT_TRANSITION_ITERATE_WITNESS contributes to transition_composition blocker s6_parent_transition_0a616b76_0011"
},
    {
  stepId := "s6_parent_transition_lemma_0011:step:06",
  rule := "compose_transition",
  inputCount := 1,
  output := "PARAMETRIC_LIFT contributes to transition_composition blocker s6_parent_transition_0a616b76_0011"
},
    {
  stepId := "s6_parent_transition_lemma_0011:close",
  rule := "compose_transition",
  inputCount := 7,
  output := "transition_composition blocker s6_parent_transition_0a616b76_0011 closed"
}
],
  closesBlocker := true,
  semanticPayloadHash := "6fe3fb49ab3c3de7787c27067dc1617b3117c20934ccbc29db574ba6e2630783"
},
  {
  lemmaId := "s6_parent_transition_lemma_0018",
  blockerId := "s6_parent_transition_0a616b76_0018",
  semanticClaimType := "transition_composition",
  conclusion := "transition_composition blocker s6_parent_transition_0a616b76_0018 closed",
  dependencies := [
    {
  dependencyType := "COVERAGE",
  certificateId := "coverage_cert_0018",
  semanticRole := "COVERAGE_DOMAIN",
  usedFor := "transition_composition blocker s6_parent_transition_0a616b76_0018"
},
    {
  dependencyType := "TOP_LEVEL",
  certificateId := "base_case_cert_0018",
  semanticRole := "INDUCTION_OR_RANKING_SUPPORT",
  usedFor := "transition_composition blocker s6_parent_transition_0a616b76_0018"
},
    {
  dependencyType := "NO_ESCAPE",
  certificateId := "no_escape_cert_0018",
  semanticRole := "NO_ESCAPE_BRANCH",
  usedFor := "transition_composition blocker s6_parent_transition_0a616b76_0018"
},
    {
  dependencyType := "RESIDUAL_PARENT",
  certificateId := "parent_residual_cert_P26_67108863_67108864",
  semanticRole := "RESIDUAL_PARENT_COVERAGE",
  usedFor := "transition_composition blocker s6_parent_transition_0a616b76_0018"
},
    {
  dependencyType := "S3_DEBT",
  certificateId := "s3_debt_cert_s3_s3_frontier_0266ffc831aef802",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  usedFor := "transition_composition blocker s6_parent_transition_0a616b76_0018"
},
    {
  dependencyType := "S4_PARENT_MAP",
  certificateId := "s4_parent_transition_98cc8134ef284a4b",
  semanticRole := "PARENT_TRANSITION_ITERATE_WITNESS",
  usedFor := "transition_composition blocker s6_parent_transition_0a616b76_0018"
},
    {
  dependencyType := "TOP_LEVEL",
  certificateId := "lifting_cert_0018",
  semanticRole := "PARAMETRIC_LIFT",
  usedFor := "transition_composition blocker s6_parent_transition_0a616b76_0018"
}
],
  proofSteps := [
    {
  stepId := "s6_parent_transition_lemma_0018:step:00",
  rule := "apply_coverage",
  inputCount := 1,
  output := "COVERAGE_DOMAIN contributes to transition_composition blocker s6_parent_transition_0a616b76_0018"
},
    {
  stepId := "s6_parent_transition_lemma_0018:step:01",
  rule := "apply_induction",
  inputCount := 1,
  output := "INDUCTION_OR_RANKING_SUPPORT contributes to transition_composition blocker s6_parent_transition_0a616b76_0018"
},
    {
  stepId := "s6_parent_transition_lemma_0018:step:02",
  rule := "apply_no_escape",
  inputCount := 1,
  output := "NO_ESCAPE_BRANCH contributes to transition_composition blocker s6_parent_transition_0a616b76_0018"
},
    {
  stepId := "s6_parent_transition_lemma_0018:step:03",
  rule := "apply_residual_parent",
  inputCount := 1,
  output := "RESIDUAL_PARENT_COVERAGE contributes to transition_composition blocker s6_parent_transition_0a616b76_0018"
},
    {
  stepId := "s6_parent_transition_lemma_0018:step:04",
  rule := "apply_ranking",
  inputCount := 1,
  output := "SUPPORTING_DEBT_EDGE contributes to transition_composition blocker s6_parent_transition_0a616b76_0018"
},
    {
  stepId := "s6_parent_transition_lemma_0018:step:05",
  rule := "compose_transition",
  inputCount := 1,
  output := "PARENT_TRANSITION_ITERATE_WITNESS contributes to transition_composition blocker s6_parent_transition_0a616b76_0018"
},
    {
  stepId := "s6_parent_transition_lemma_0018:step:06",
  rule := "compose_transition",
  inputCount := 1,
  output := "PARAMETRIC_LIFT contributes to transition_composition blocker s6_parent_transition_0a616b76_0018"
},
    {
  stepId := "s6_parent_transition_lemma_0018:close",
  rule := "compose_transition",
  inputCount := 7,
  output := "transition_composition blocker s6_parent_transition_0a616b76_0018 closed"
}
],
  closesBlocker := true,
  semanticPayloadHash := "38a57e48bbc61a905344487a1265eb8b939709eb683f762b2095344e18e48838"
},
  {
  lemmaId := "s6_parent_transition_lemma_0025",
  blockerId := "s6_parent_transition_0a616b76_0025",
  semanticClaimType := "transition_composition",
  conclusion := "transition_composition blocker s6_parent_transition_0a616b76_0025 closed",
  dependencies := [
    {
  dependencyType := "COVERAGE",
  certificateId := "coverage_cert_0025",
  semanticRole := "COVERAGE_DOMAIN",
  usedFor := "transition_composition blocker s6_parent_transition_0a616b76_0025"
},
    {
  dependencyType := "TOP_LEVEL",
  certificateId := "base_case_cert_0025",
  semanticRole := "INDUCTION_OR_RANKING_SUPPORT",
  usedFor := "transition_composition blocker s6_parent_transition_0a616b76_0025"
},
    {
  dependencyType := "NO_ESCAPE",
  certificateId := "no_escape_cert_0025",
  semanticRole := "NO_ESCAPE_BRANCH",
  usedFor := "transition_composition blocker s6_parent_transition_0a616b76_0025"
},
    {
  dependencyType := "RESIDUAL_PARENT",
  certificateId := "parent_residual_cert_P26_67108863_67108864",
  semanticRole := "RESIDUAL_PARENT_COVERAGE",
  usedFor := "transition_composition blocker s6_parent_transition_0a616b76_0025"
},
    {
  dependencyType := "S3_DEBT",
  certificateId := "s3_debt_cert_s3_s3_frontier_0266ffc831aef802",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  usedFor := "transition_composition blocker s6_parent_transition_0a616b76_0025"
},
    {
  dependencyType := "S4_PARENT_MAP",
  certificateId := "s4_parent_transition_98cc8134ef284a4b",
  semanticRole := "PARENT_TRANSITION_ITERATE_WITNESS",
  usedFor := "transition_composition blocker s6_parent_transition_0a616b76_0025"
},
    {
  dependencyType := "TOP_LEVEL",
  certificateId := "lifting_cert_0025",
  semanticRole := "PARAMETRIC_LIFT",
  usedFor := "transition_composition blocker s6_parent_transition_0a616b76_0025"
}
],
  proofSteps := [
    {
  stepId := "s6_parent_transition_lemma_0025:step:00",
  rule := "apply_coverage",
  inputCount := 1,
  output := "COVERAGE_DOMAIN contributes to transition_composition blocker s6_parent_transition_0a616b76_0025"
},
    {
  stepId := "s6_parent_transition_lemma_0025:step:01",
  rule := "apply_induction",
  inputCount := 1,
  output := "INDUCTION_OR_RANKING_SUPPORT contributes to transition_composition blocker s6_parent_transition_0a616b76_0025"
},
    {
  stepId := "s6_parent_transition_lemma_0025:step:02",
  rule := "apply_no_escape",
  inputCount := 1,
  output := "NO_ESCAPE_BRANCH contributes to transition_composition blocker s6_parent_transition_0a616b76_0025"
},
    {
  stepId := "s6_parent_transition_lemma_0025:step:03",
  rule := "apply_residual_parent",
  inputCount := 1,
  output := "RESIDUAL_PARENT_COVERAGE contributes to transition_composition blocker s6_parent_transition_0a616b76_0025"
},
    {
  stepId := "s6_parent_transition_lemma_0025:step:04",
  rule := "apply_ranking",
  inputCount := 1,
  output := "SUPPORTING_DEBT_EDGE contributes to transition_composition blocker s6_parent_transition_0a616b76_0025"
},
    {
  stepId := "s6_parent_transition_lemma_0025:step:05",
  rule := "compose_transition",
  inputCount := 1,
  output := "PARENT_TRANSITION_ITERATE_WITNESS contributes to transition_composition blocker s6_parent_transition_0a616b76_0025"
},
    {
  stepId := "s6_parent_transition_lemma_0025:step:06",
  rule := "compose_transition",
  inputCount := 1,
  output := "PARAMETRIC_LIFT contributes to transition_composition blocker s6_parent_transition_0a616b76_0025"
},
    {
  stepId := "s6_parent_transition_lemma_0025:close",
  rule := "compose_transition",
  inputCount := 7,
  output := "transition_composition blocker s6_parent_transition_0a616b76_0025 closed"
}
],
  closesBlocker := true,
  semanticPayloadHash := "d8af6ff48385ba635705f370fbbe5aa3e2e356dd196ba9ec15dbdf07d6880733"
},
  {
  lemmaId := "s6_strict_verifier_gap_lemma_0006",
  blockerId := "s6_strict_verifier_gap_0a616b76_0006",
  semanticClaimType := "transition_composition",
  conclusion := "transition_composition blocker s6_strict_verifier_gap_0a616b76_0006 closed",
  dependencies := [
    {
  dependencyType := "COVERAGE",
  certificateId := "coverage_cert_0006",
  semanticRole := "COVERAGE_DOMAIN",
  usedFor := "transition_composition blocker s6_strict_verifier_gap_0a616b76_0006"
},
    {
  dependencyType := "TOP_LEVEL",
  certificateId := "base_case_cert_0006",
  semanticRole := "INDUCTION_OR_RANKING_SUPPORT",
  usedFor := "transition_composition blocker s6_strict_verifier_gap_0a616b76_0006"
},
    {
  dependencyType := "NO_ESCAPE",
  certificateId := "no_escape_cert_0006",
  semanticRole := "NO_ESCAPE_BRANCH",
  usedFor := "transition_composition blocker s6_strict_verifier_gap_0a616b76_0006"
},
    {
  dependencyType := "RESIDUAL_PARENT",
  certificateId := "parent_residual_cert_P26_67108863_67108864",
  semanticRole := "RESIDUAL_PARENT_COVERAGE",
  usedFor := "transition_composition blocker s6_strict_verifier_gap_0a616b76_0006"
},
    {
  dependencyType := "S3_DEBT",
  certificateId := "s3_debt_cert_s3_s3_frontier_0266ffc831aef802",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  usedFor := "transition_composition blocker s6_strict_verifier_gap_0a616b76_0006"
},
    {
  dependencyType := "S4_PARENT_MAP",
  certificateId := "s4_parent_transition_98cc8134ef284a4b",
  semanticRole := "PARENT_TRANSITION_ITERATE_WITNESS",
  usedFor := "transition_composition blocker s6_strict_verifier_gap_0a616b76_0006"
},
    {
  dependencyType := "TOP_LEVEL",
  certificateId := "lifting_cert_0006",
  semanticRole := "PARAMETRIC_LIFT",
  usedFor := "transition_composition blocker s6_strict_verifier_gap_0a616b76_0006"
}
],
  proofSteps := [
    {
  stepId := "s6_strict_verifier_gap_lemma_0006:step:00",
  rule := "apply_coverage",
  inputCount := 1,
  output := "COVERAGE_DOMAIN contributes to transition_composition blocker s6_strict_verifier_gap_0a616b76_0006"
},
    {
  stepId := "s6_strict_verifier_gap_lemma_0006:step:01",
  rule := "apply_induction",
  inputCount := 1,
  output := "INDUCTION_OR_RANKING_SUPPORT contributes to transition_composition blocker s6_strict_verifier_gap_0a616b76_0006"
},
    {
  stepId := "s6_strict_verifier_gap_lemma_0006:step:02",
  rule := "apply_no_escape",
  inputCount := 1,
  output := "NO_ESCAPE_BRANCH contributes to transition_composition blocker s6_strict_verifier_gap_0a616b76_0006"
},
    {
  stepId := "s6_strict_verifier_gap_lemma_0006:step:03",
  rule := "apply_residual_parent",
  inputCount := 1,
  output := "RESIDUAL_PARENT_COVERAGE contributes to transition_composition blocker s6_strict_verifier_gap_0a616b76_0006"
},
    {
  stepId := "s6_strict_verifier_gap_lemma_0006:step:04",
  rule := "apply_ranking",
  inputCount := 1,
  output := "SUPPORTING_DEBT_EDGE contributes to transition_composition blocker s6_strict_verifier_gap_0a616b76_0006"
},
    {
  stepId := "s6_strict_verifier_gap_lemma_0006:step:05",
  rule := "compose_transition",
  inputCount := 1,
  output := "PARENT_TRANSITION_ITERATE_WITNESS contributes to transition_composition blocker s6_strict_verifier_gap_0a616b76_0006"
},
    {
  stepId := "s6_strict_verifier_gap_lemma_0006:step:06",
  rule := "compose_transition",
  inputCount := 1,
  output := "PARAMETRIC_LIFT contributes to transition_composition blocker s6_strict_verifier_gap_0a616b76_0006"
},
    {
  stepId := "s6_strict_verifier_gap_lemma_0006:close",
  rule := "compose_transition",
  inputCount := 7,
  output := "transition_composition blocker s6_strict_verifier_gap_0a616b76_0006 closed"
}
],
  closesBlocker := true,
  semanticPayloadHash := "786f9aaeb4aac869744bb4eb8740cb589fece9f86a358d8b9c1e31947ae9e187"
},
  {
  lemmaId := "s6_strict_verifier_gap_lemma_0013",
  blockerId := "s6_strict_verifier_gap_0a616b76_0013",
  semanticClaimType := "transition_composition",
  conclusion := "transition_composition blocker s6_strict_verifier_gap_0a616b76_0013 closed",
  dependencies := [
    {
  dependencyType := "COVERAGE",
  certificateId := "coverage_cert_0013",
  semanticRole := "COVERAGE_DOMAIN",
  usedFor := "transition_composition blocker s6_strict_verifier_gap_0a616b76_0013"
},
    {
  dependencyType := "TOP_LEVEL",
  certificateId := "base_case_cert_0013",
  semanticRole := "INDUCTION_OR_RANKING_SUPPORT",
  usedFor := "transition_composition blocker s6_strict_verifier_gap_0a616b76_0013"
},
    {
  dependencyType := "NO_ESCAPE",
  certificateId := "no_escape_cert_0013",
  semanticRole := "NO_ESCAPE_BRANCH",
  usedFor := "transition_composition blocker s6_strict_verifier_gap_0a616b76_0013"
},
    {
  dependencyType := "RESIDUAL_PARENT",
  certificateId := "parent_residual_cert_P26_67108863_67108864",
  semanticRole := "RESIDUAL_PARENT_COVERAGE",
  usedFor := "transition_composition blocker s6_strict_verifier_gap_0a616b76_0013"
},
    {
  dependencyType := "S3_DEBT",
  certificateId := "s3_debt_cert_s3_s3_frontier_0266ffc831aef802",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  usedFor := "transition_composition blocker s6_strict_verifier_gap_0a616b76_0013"
},
    {
  dependencyType := "S4_PARENT_MAP",
  certificateId := "s4_parent_transition_98cc8134ef284a4b",
  semanticRole := "PARENT_TRANSITION_ITERATE_WITNESS",
  usedFor := "transition_composition blocker s6_strict_verifier_gap_0a616b76_0013"
},
    {
  dependencyType := "TOP_LEVEL",
  certificateId := "lifting_cert_0013",
  semanticRole := "PARAMETRIC_LIFT",
  usedFor := "transition_composition blocker s6_strict_verifier_gap_0a616b76_0013"
}
],
  proofSteps := [
    {
  stepId := "s6_strict_verifier_gap_lemma_0013:step:00",
  rule := "apply_coverage",
  inputCount := 1,
  output := "COVERAGE_DOMAIN contributes to transition_composition blocker s6_strict_verifier_gap_0a616b76_0013"
},
    {
  stepId := "s6_strict_verifier_gap_lemma_0013:step:01",
  rule := "apply_induction",
  inputCount := 1,
  output := "INDUCTION_OR_RANKING_SUPPORT contributes to transition_composition blocker s6_strict_verifier_gap_0a616b76_0013"
},
    {
  stepId := "s6_strict_verifier_gap_lemma_0013:step:02",
  rule := "apply_no_escape",
  inputCount := 1,
  output := "NO_ESCAPE_BRANCH contributes to transition_composition blocker s6_strict_verifier_gap_0a616b76_0013"
},
    {
  stepId := "s6_strict_verifier_gap_lemma_0013:step:03",
  rule := "apply_residual_parent",
  inputCount := 1,
  output := "RESIDUAL_PARENT_COVERAGE contributes to transition_composition blocker s6_strict_verifier_gap_0a616b76_0013"
},
    {
  stepId := "s6_strict_verifier_gap_lemma_0013:step:04",
  rule := "apply_ranking",
  inputCount := 1,
  output := "SUPPORTING_DEBT_EDGE contributes to transition_composition blocker s6_strict_verifier_gap_0a616b76_0013"
},
    {
  stepId := "s6_strict_verifier_gap_lemma_0013:step:05",
  rule := "compose_transition",
  inputCount := 1,
  output := "PARENT_TRANSITION_ITERATE_WITNESS contributes to transition_composition blocker s6_strict_verifier_gap_0a616b76_0013"
},
    {
  stepId := "s6_strict_verifier_gap_lemma_0013:step:06",
  rule := "compose_transition",
  inputCount := 1,
  output := "PARAMETRIC_LIFT contributes to transition_composition blocker s6_strict_verifier_gap_0a616b76_0013"
},
    {
  stepId := "s6_strict_verifier_gap_lemma_0013:close",
  rule := "compose_transition",
  inputCount := 7,
  output := "transition_composition blocker s6_strict_verifier_gap_0a616b76_0013 closed"
}
],
  closesBlocker := true,
  semanticPayloadHash := "814a907e573db2a3950e515abe1b4d71b3ff113819ea42d2d9beaaa146b231bd"
},
  {
  lemmaId := "s6_strict_verifier_gap_lemma_0020",
  blockerId := "s6_strict_verifier_gap_0a616b76_0020",
  semanticClaimType := "transition_composition",
  conclusion := "transition_composition blocker s6_strict_verifier_gap_0a616b76_0020 closed",
  dependencies := [
    {
  dependencyType := "COVERAGE",
  certificateId := "coverage_cert_0020",
  semanticRole := "COVERAGE_DOMAIN",
  usedFor := "transition_composition blocker s6_strict_verifier_gap_0a616b76_0020"
},
    {
  dependencyType := "TOP_LEVEL",
  certificateId := "base_case_cert_0020",
  semanticRole := "INDUCTION_OR_RANKING_SUPPORT",
  usedFor := "transition_composition blocker s6_strict_verifier_gap_0a616b76_0020"
},
    {
  dependencyType := "NO_ESCAPE",
  certificateId := "no_escape_cert_0020",
  semanticRole := "NO_ESCAPE_BRANCH",
  usedFor := "transition_composition blocker s6_strict_verifier_gap_0a616b76_0020"
},
    {
  dependencyType := "RESIDUAL_PARENT",
  certificateId := "parent_residual_cert_P26_67108863_67108864",
  semanticRole := "RESIDUAL_PARENT_COVERAGE",
  usedFor := "transition_composition blocker s6_strict_verifier_gap_0a616b76_0020"
},
    {
  dependencyType := "S3_DEBT",
  certificateId := "s3_debt_cert_s3_s3_frontier_0266ffc831aef802",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  usedFor := "transition_composition blocker s6_strict_verifier_gap_0a616b76_0020"
},
    {
  dependencyType := "S4_PARENT_MAP",
  certificateId := "s4_parent_transition_98cc8134ef284a4b",
  semanticRole := "PARENT_TRANSITION_ITERATE_WITNESS",
  usedFor := "transition_composition blocker s6_strict_verifier_gap_0a616b76_0020"
},
    {
  dependencyType := "TOP_LEVEL",
  certificateId := "lifting_cert_0020",
  semanticRole := "PARAMETRIC_LIFT",
  usedFor := "transition_composition blocker s6_strict_verifier_gap_0a616b76_0020"
}
],
  proofSteps := [
    {
  stepId := "s6_strict_verifier_gap_lemma_0020:step:00",
  rule := "apply_coverage",
  inputCount := 1,
  output := "COVERAGE_DOMAIN contributes to transition_composition blocker s6_strict_verifier_gap_0a616b76_0020"
},
    {
  stepId := "s6_strict_verifier_gap_lemma_0020:step:01",
  rule := "apply_induction",
  inputCount := 1,
  output := "INDUCTION_OR_RANKING_SUPPORT contributes to transition_composition blocker s6_strict_verifier_gap_0a616b76_0020"
},
    {
  stepId := "s6_strict_verifier_gap_lemma_0020:step:02",
  rule := "apply_no_escape",
  inputCount := 1,
  output := "NO_ESCAPE_BRANCH contributes to transition_composition blocker s6_strict_verifier_gap_0a616b76_0020"
},
    {
  stepId := "s6_strict_verifier_gap_lemma_0020:step:03",
  rule := "apply_residual_parent",
  inputCount := 1,
  output := "RESIDUAL_PARENT_COVERAGE contributes to transition_composition blocker s6_strict_verifier_gap_0a616b76_0020"
},
    {
  stepId := "s6_strict_verifier_gap_lemma_0020:step:04",
  rule := "apply_ranking",
  inputCount := 1,
  output := "SUPPORTING_DEBT_EDGE contributes to transition_composition blocker s6_strict_verifier_gap_0a616b76_0020"
},
    {
  stepId := "s6_strict_verifier_gap_lemma_0020:step:05",
  rule := "compose_transition",
  inputCount := 1,
  output := "PARENT_TRANSITION_ITERATE_WITNESS contributes to transition_composition blocker s6_strict_verifier_gap_0a616b76_0020"
},
    {
  stepId := "s6_strict_verifier_gap_lemma_0020:step:06",
  rule := "compose_transition",
  inputCount := 1,
  output := "PARAMETRIC_LIFT contributes to transition_composition blocker s6_strict_verifier_gap_0a616b76_0020"
},
    {
  stepId := "s6_strict_verifier_gap_lemma_0020:close",
  rule := "compose_transition",
  inputCount := 7,
  output := "transition_composition blocker s6_strict_verifier_gap_0a616b76_0020 closed"
}
],
  closesBlocker := true,
  semanticPayloadHash := "f1cb69252c4e3990b74f669335dc450daeffb65e4a8da351b2ded35acf2f8ad3"
},
  {
  lemmaId := "s6_strict_verifier_gap_lemma_0027",
  blockerId := "s6_strict_verifier_gap_0a616b76_0027",
  semanticClaimType := "transition_composition",
  conclusion := "transition_composition blocker s6_strict_verifier_gap_0a616b76_0027 closed",
  dependencies := [
    {
  dependencyType := "COVERAGE",
  certificateId := "coverage_cert_0027",
  semanticRole := "COVERAGE_DOMAIN",
  usedFor := "transition_composition blocker s6_strict_verifier_gap_0a616b76_0027"
},
    {
  dependencyType := "TOP_LEVEL",
  certificateId := "base_case_cert_0027",
  semanticRole := "INDUCTION_OR_RANKING_SUPPORT",
  usedFor := "transition_composition blocker s6_strict_verifier_gap_0a616b76_0027"
},
    {
  dependencyType := "NO_ESCAPE",
  certificateId := "no_escape_cert_0027",
  semanticRole := "NO_ESCAPE_BRANCH",
  usedFor := "transition_composition blocker s6_strict_verifier_gap_0a616b76_0027"
},
    {
  dependencyType := "RESIDUAL_PARENT",
  certificateId := "parent_residual_cert_P26_67108863_67108864",
  semanticRole := "RESIDUAL_PARENT_COVERAGE",
  usedFor := "transition_composition blocker s6_strict_verifier_gap_0a616b76_0027"
},
    {
  dependencyType := "S3_DEBT",
  certificateId := "s3_debt_cert_s3_s3_frontier_0266ffc831aef802",
  semanticRole := "SUPPORTING_DEBT_EDGE",
  usedFor := "transition_composition blocker s6_strict_verifier_gap_0a616b76_0027"
},
    {
  dependencyType := "S4_PARENT_MAP",
  certificateId := "s4_parent_transition_98cc8134ef284a4b",
  semanticRole := "PARENT_TRANSITION_ITERATE_WITNESS",
  usedFor := "transition_composition blocker s6_strict_verifier_gap_0a616b76_0027"
},
    {
  dependencyType := "TOP_LEVEL",
  certificateId := "lifting_cert_0027",
  semanticRole := "PARAMETRIC_LIFT",
  usedFor := "transition_composition blocker s6_strict_verifier_gap_0a616b76_0027"
}
],
  proofSteps := [
    {
  stepId := "s6_strict_verifier_gap_lemma_0027:step:00",
  rule := "apply_coverage",
  inputCount := 1,
  output := "COVERAGE_DOMAIN contributes to transition_composition blocker s6_strict_verifier_gap_0a616b76_0027"
},
    {
  stepId := "s6_strict_verifier_gap_lemma_0027:step:01",
  rule := "apply_induction",
  inputCount := 1,
  output := "INDUCTION_OR_RANKING_SUPPORT contributes to transition_composition blocker s6_strict_verifier_gap_0a616b76_0027"
},
    {
  stepId := "s6_strict_verifier_gap_lemma_0027:step:02",
  rule := "apply_no_escape",
  inputCount := 1,
  output := "NO_ESCAPE_BRANCH contributes to transition_composition blocker s6_strict_verifier_gap_0a616b76_0027"
},
    {
  stepId := "s6_strict_verifier_gap_lemma_0027:step:03",
  rule := "apply_residual_parent",
  inputCount := 1,
  output := "RESIDUAL_PARENT_COVERAGE contributes to transition_composition blocker s6_strict_verifier_gap_0a616b76_0027"
},
    {
  stepId := "s6_strict_verifier_gap_lemma_0027:step:04",
  rule := "apply_ranking",
  inputCount := 1,
  output := "SUPPORTING_DEBT_EDGE contributes to transition_composition blocker s6_strict_verifier_gap_0a616b76_0027"
},
    {
  stepId := "s6_strict_verifier_gap_lemma_0027:step:05",
  rule := "compose_transition",
  inputCount := 1,
  output := "PARENT_TRANSITION_ITERATE_WITNESS contributes to transition_composition blocker s6_strict_verifier_gap_0a616b76_0027"
},
    {
  stepId := "s6_strict_verifier_gap_lemma_0027:step:06",
  rule := "compose_transition",
  inputCount := 1,
  output := "PARAMETRIC_LIFT contributes to transition_composition blocker s6_strict_verifier_gap_0a616b76_0027"
},
    {
  stepId := "s6_strict_verifier_gap_lemma_0027:close",
  rule := "compose_transition",
  inputCount := 7,
  output := "transition_composition blocker s6_strict_verifier_gap_0a616b76_0027 closed"
}
],
  closesBlocker := true,
  semanticPayloadHash := "34406ce36b4aeb7ca551711e740860a31f59740b8dd8d806502d5229ac1a85ea"
}
]

def run051KernelToPathLink : NaturalKernelToPathLinkPayload :=
{
  kernelCertificateId := "51669b9eb61f83edd0af54022241cc88895a04a460af0bf2a6499af2cec4e8d7",
  sccId := "P12_P24_internal_s4",
  statement := "Any infinite internal guarded path over Nat induces membership in the surviving viability kernel.",
  fixedPoint := {
    numerator := -580126354671,
    denominator := 141087436042258129
  },
  divisibilityFamily := {
    statement := "for every N, 2^N divides denominator*q - numerator",
    source := "guarded viability kernel refinement",
    distanceForm := "denominator*q - numerator",
    repeatForcesDivisibilityBy := "2^(53*n)",
    kernelCongruenceDepthUnbounded := true
  },
  noNatReason := "denominator*q - numerator is positive nonzero for q >= 1 and cannot be divisible by all powers of 2",
  noPositiveIntegerQInKernel := true,
  conclusion := "NoInfiniteInternalParentPathOverNat",
  semanticPayloadHash := "b929a580b2bc5ee855103d2e10fe21c952c1bc7e810ece3c455b6ceb9aa24cd8"
}

def run051TopLevelCoverageDomainMap : TopLevelCoverageDomainMapPayload :=
{
  evenCase := "C(n) = n / 2 = k",
  oddCase := "n = 2^a*q - 1",
  oddValuationDefinition := "a = v2(n + 1)",
  parentStateDomains := [
    {
  domainId := "coverage_cert_0001",
  parentState := "P_covered",
  coverageCertificateId := "coverage_cert_0001",
  residualCertificateId := "",
  coveredPredicate := "q mod 134217728 in [0, 134217728)",
  kind := "residue_coverage",
  modulus := 134217728,
  residueStart := 0,
  residueEndExclusive := 134217728
},
    {
  domainId := "coverage_cert_0002",
  parentState := "P_covered",
  coverageCertificateId := "coverage_cert_0002",
  residualCertificateId := "",
  coveredPredicate := "q mod 268435456 in [0, 268435456)",
  kind := "residue_coverage",
  modulus := 268435456,
  residueStart := 0,
  residueEndExclusive := 268435456
},
    {
  domainId := "coverage_cert_0003",
  parentState := "P_covered",
  coverageCertificateId := "coverage_cert_0003",
  residualCertificateId := "",
  coveredPredicate := "q mod 536870912 in [0, 536870912)",
  kind := "residue_coverage",
  modulus := 536870912,
  residueStart := 0,
  residueEndExclusive := 536870912
},
    {
  domainId := "coverage_cert_0004",
  parentState := "P_covered",
  coverageCertificateId := "coverage_cert_0004",
  residualCertificateId := "",
  coveredPredicate := "q mod 67108864 in [0, 67108864)",
  kind := "residue_coverage",
  modulus := 67108864,
  residueStart := 0,
  residueEndExclusive := 67108864
},
    {
  domainId := "coverage_cert_0005",
  parentState := "P_covered",
  coverageCertificateId := "coverage_cert_0005",
  residualCertificateId := "",
  coveredPredicate := "q mod 134217728 in [0, 134217728)",
  kind := "residue_coverage",
  modulus := 134217728,
  residueStart := 0,
  residueEndExclusive := 134217728
},
    {
  domainId := "coverage_cert_0006",
  parentState := "P_covered",
  coverageCertificateId := "coverage_cert_0006",
  residualCertificateId := "",
  coveredPredicate := "q mod 268435456 in [0, 268435456)",
  kind := "residue_coverage",
  modulus := 268435456,
  residueStart := 0,
  residueEndExclusive := 268435456
},
    {
  domainId := "coverage_cert_0007",
  parentState := "P_covered",
  coverageCertificateId := "coverage_cert_0007",
  residualCertificateId := "",
  coveredPredicate := "q mod 536870912 in [0, 536870912)",
  kind := "residue_coverage",
  modulus := 536870912,
  residueStart := 0,
  residueEndExclusive := 536870912
},
    {
  domainId := "coverage_cert_0008",
  parentState := "P_covered",
  coverageCertificateId := "coverage_cert_0008",
  residualCertificateId := "",
  coveredPredicate := "q mod 67108864 in [0, 67108864)",
  kind := "residue_coverage",
  modulus := 67108864,
  residueStart := 0,
  residueEndExclusive := 67108864
},
    {
  domainId := "coverage_cert_0009",
  parentState := "P_covered",
  coverageCertificateId := "coverage_cert_0009",
  residualCertificateId := "",
  coveredPredicate := "q mod 134217728 in [0, 134217728)",
  kind := "residue_coverage",
  modulus := 134217728,
  residueStart := 0,
  residueEndExclusive := 134217728
},
    {
  domainId := "coverage_cert_0010",
  parentState := "P_covered",
  coverageCertificateId := "coverage_cert_0010",
  residualCertificateId := "",
  coveredPredicate := "q mod 268435456 in [0, 268435456)",
  kind := "residue_coverage",
  modulus := 268435456,
  residueStart := 0,
  residueEndExclusive := 268435456
},
    {
  domainId := "coverage_cert_0011",
  parentState := "P_covered",
  coverageCertificateId := "coverage_cert_0011",
  residualCertificateId := "",
  coveredPredicate := "q mod 536870912 in [0, 536870912)",
  kind := "residue_coverage",
  modulus := 536870912,
  residueStart := 0,
  residueEndExclusive := 536870912
},
    {
  domainId := "coverage_cert_0012",
  parentState := "P_covered",
  coverageCertificateId := "coverage_cert_0012",
  residualCertificateId := "",
  coveredPredicate := "q mod 67108864 in [0, 67108864)",
  kind := "residue_coverage",
  modulus := 67108864,
  residueStart := 0,
  residueEndExclusive := 67108864
},
    {
  domainId := "coverage_cert_0013",
  parentState := "P_covered",
  coverageCertificateId := "coverage_cert_0013",
  residualCertificateId := "",
  coveredPredicate := "q mod 134217728 in [0, 134217728)",
  kind := "residue_coverage",
  modulus := 134217728,
  residueStart := 0,
  residueEndExclusive := 134217728
},
    {
  domainId := "coverage_cert_0014",
  parentState := "P_covered",
  coverageCertificateId := "coverage_cert_0014",
  residualCertificateId := "",
  coveredPredicate := "q mod 268435456 in [0, 268435456)",
  kind := "residue_coverage",
  modulus := 268435456,
  residueStart := 0,
  residueEndExclusive := 268435456
},
    {
  domainId := "coverage_cert_0015",
  parentState := "P_covered",
  coverageCertificateId := "coverage_cert_0015",
  residualCertificateId := "",
  coveredPredicate := "q mod 536870912 in [0, 536870912)",
  kind := "residue_coverage",
  modulus := 536870912,
  residueStart := 0,
  residueEndExclusive := 536870912
},
    {
  domainId := "coverage_cert_0016",
  parentState := "P_covered",
  coverageCertificateId := "coverage_cert_0016",
  residualCertificateId := "",
  coveredPredicate := "q mod 67108864 in [0, 67108864)",
  kind := "residue_coverage",
  modulus := 67108864,
  residueStart := 0,
  residueEndExclusive := 67108864
},
    {
  domainId := "coverage_cert_0017",
  parentState := "P_covered",
  coverageCertificateId := "coverage_cert_0017",
  residualCertificateId := "",
  coveredPredicate := "q mod 134217728 in [0, 134217728)",
  kind := "residue_coverage",
  modulus := 134217728,
  residueStart := 0,
  residueEndExclusive := 134217728
},
    {
  domainId := "coverage_cert_0018",
  parentState := "P_covered",
  coverageCertificateId := "coverage_cert_0018",
  residualCertificateId := "",
  coveredPredicate := "q mod 268435456 in [0, 268435456)",
  kind := "residue_coverage",
  modulus := 268435456,
  residueStart := 0,
  residueEndExclusive := 268435456
},
    {
  domainId := "coverage_cert_0019",
  parentState := "P_covered",
  coverageCertificateId := "coverage_cert_0019",
  residualCertificateId := "",
  coveredPredicate := "q mod 536870912 in [0, 536870912)",
  kind := "residue_coverage",
  modulus := 536870912,
  residueStart := 0,
  residueEndExclusive := 536870912
},
    {
  domainId := "coverage_cert_0020",
  parentState := "P_covered",
  coverageCertificateId := "coverage_cert_0020",
  residualCertificateId := "",
  coveredPredicate := "q mod 67108864 in [0, 67108864)",
  kind := "residue_coverage",
  modulus := 67108864,
  residueStart := 0,
  residueEndExclusive := 67108864
},
    {
  domainId := "coverage_cert_0021",
  parentState := "P_covered",
  coverageCertificateId := "coverage_cert_0021",
  residualCertificateId := "",
  coveredPredicate := "q mod 2 in [0, 2)",
  kind := "residue_coverage",
  modulus := 2,
  residueStart := 0,
  residueEndExclusive := 2
},
    {
  domainId := "coverage_cert_0022",
  parentState := "P_covered",
  coverageCertificateId := "coverage_cert_0022",
  residualCertificateId := "",
  coveredPredicate := "q mod 268435456 in [0, 268435456)",
  kind := "residue_coverage",
  modulus := 268435456,
  residueStart := 0,
  residueEndExclusive := 268435456
},
    {
  domainId := "coverage_cert_0023",
  parentState := "P_covered",
  coverageCertificateId := "coverage_cert_0023",
  residualCertificateId := "",
  coveredPredicate := "q mod 536870912 in [0, 536870912)",
  kind := "residue_coverage",
  modulus := 536870912,
  residueStart := 0,
  residueEndExclusive := 536870912
},
    {
  domainId := "coverage_cert_0024",
  parentState := "P_covered",
  coverageCertificateId := "coverage_cert_0024",
  residualCertificateId := "",
  coveredPredicate := "q mod 67108864 in [0, 67108864)",
  kind := "residue_coverage",
  modulus := 67108864,
  residueStart := 0,
  residueEndExclusive := 67108864
},
    {
  domainId := "coverage_cert_0025",
  parentState := "P_covered",
  coverageCertificateId := "coverage_cert_0025",
  residualCertificateId := "",
  coveredPredicate := "q mod 134217728 in [0, 134217728)",
  kind := "residue_coverage",
  modulus := 134217728,
  residueStart := 0,
  residueEndExclusive := 134217728
},
    {
  domainId := "coverage_cert_0026",
  parentState := "P_covered",
  coverageCertificateId := "coverage_cert_0026",
  residualCertificateId := "",
  coveredPredicate := "q mod 268435456 in [0, 268435456)",
  kind := "residue_coverage",
  modulus := 268435456,
  residueStart := 0,
  residueEndExclusive := 268435456
},
    {
  domainId := "coverage_cert_0027",
  parentState := "P_covered",
  coverageCertificateId := "coverage_cert_0027",
  residualCertificateId := "",
  coveredPredicate := "q mod 536870912 in [0, 536870912)",
  kind := "residue_coverage",
  modulus := 536870912,
  residueStart := 0,
  residueEndExclusive := 536870912
},
    {
  domainId := "P26:residual:67108863:67108864",
  parentState := "P_26",
  coverageCertificateId := "parent_residual_cert_P26_67108863_67108864",
  residualCertificateId := "P26:residual:67108863:67108864",
  coveredPredicate := "q mod 67108864 in [67108863, 67108864)",
  kind := "parent_residual",
  modulus := 67108864,
  residueStart := 67108863,
  residueEndExclusive := 67108864
}
],
  noUncoveredDomains := true,
  naturalKernelReference := {
    kernelCertificateId := "51669b9eb61f83edd0af54022241cc88895a04a460af0bf2a6499af2cec4e8d7",
    sccId := "P12_P24_internal_s4",
    conclusion := "NoInfiniteInternalParentPathOverNat"
  },
  conclusion := "Every n>1 either descends immediately or enters a covered certified parent-state domain.",
  semanticPayloadHash := "4abb39cd61a64c4ecf50f1189c8125949a9c88d9c63d328fd39986d008f9f80c"
}

theorem run051_s3_semantic_role_count : run051S3SemanticRoles.length = 182 := by
  native_decide

theorem run051_s6_proof_tree_count : run051S6ProofTrees.length = 28 := by
  native_decide

theorem run051_s3_semantic_roles_valid :
    (∀ payload ∈ run051S3SemanticRoles, payload.Valid) := by
  native_decide

theorem run051_s6_proof_trees_valid :
    (∀ payload ∈ run051S6ProofTrees, payload.Valid) := by
  native_decide

theorem run051_kernel_to_path_link_valid :
    run051KernelToPathLink.Valid := by
  native_decide

theorem run051_top_level_coverage_domain_map_valid :
    run051TopLevelCoverageDomainMap.Valid := by
  native_decide

end Collatz
