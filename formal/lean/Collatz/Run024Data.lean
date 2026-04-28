import Collatz.Checkers

/-!
Generated literal data from RUN-024/RUN-023 frozen artifacts.
This file contains data and computable checks; it does not trust Python replay status.
-/

namespace Collatz

def run024S3DebtExactCerts : List S3DebtExactCert :=
[
  {
  nodeId := "s3:s3_frontier:0266ffc831aef802",
  branchId := "P9:r66178075:d26",
  sourceParent := 9,
  targetParent := 27,
  valuation := 5,
  gainNum := 5533,
  gainDen := 603669513,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P9:r66178075:d26",
    sourceParent := 9,
    targetParent := 27,
    valuation := 5,
    branchResidue := 66178075,
    branchDepth := 26,
    sourceModulus := 67108864,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P9:r66178075:d26",
    sourceParent := 9,
    targetParent := 27,
    valuation := 5,
    gainNum := 5533,
    gainDen := 603669513,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P9:r66178075:d26",
    gainNum := 5533,
    gainDen := 603669513,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "a2a14f22d58c22c65cb4cb0a12928dad90776c3213e0c1a4de212df0df7b0635"
},
  {
  nodeId := "s3:s3_frontier:03ae9f69227c4803",
  branchId := "P12:r20876015:d25",
  sourceParent := 12,
  targetParent := 25,
  valuation := 1,
  gainNum := 165319,
  gainDen := 20876015,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P12:r20876015:d25",
    sourceParent := 12,
    targetParent := 25,
    valuation := 1,
    branchResidue := 20876015,
    branchDepth := 25,
    sourceModulus := 33554432,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P12:r20876015:d25",
    sourceParent := 12,
    targetParent := 25,
    valuation := 1,
    gainNum := 165319,
    gainDen := 20876015,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P12:r20876015:d25",
    gainNum := 165319,
    gainDen := 20876015,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "9f8f7a6d2892fb0b35387f5846602580ee5672c02ea651553741b440fccd61a2"
},
  {
  nodeId := "s3:s3_frontier:03fa943ef058c862",
  branchId := "P8:r13235615:d24",
  sourceParent := 8,
  targetParent := 29,
  valuation := 6,
  gainNum := 901,
  gainDen := 147453343,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P8:r13235615:d24",
    sourceParent := 8,
    targetParent := 29,
    valuation := 6,
    branchResidue := 13235615,
    branchDepth := 24,
    sourceModulus := 16777216,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P8:r13235615:d24",
    sourceParent := 8,
    targetParent := 29,
    valuation := 6,
    gainNum := 901,
    gainDen := 147453343,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P8:r13235615:d24",
    gainNum := 901,
    gainDen := 147453343,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "3e6e4945afcc04538adc977c0688aeca078a682c6f655d8d18a5c6e438c74f03"
},
  {
  nodeId := "s3:s3_frontier:04deca200dc9ebee",
  branchId := "P13:r36761851:d26",
  sourceParent := 13,
  targetParent := 26,
  valuation := 5,
  gainNum := 1073567,
  gainDen := 1446047995,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P13:r36761851:d26",
    sourceParent := 13,
    targetParent := 26,
    valuation := 5,
    branchResidue := 36761851,
    branchDepth := 26,
    sourceModulus := 67108864,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P13:r36761851:d26",
    sourceParent := 13,
    targetParent := 26,
    valuation := 5,
    gainNum := 1073567,
    gainDen := 1446047995,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P13:r36761851:d26",
    gainNum := 1073567,
    gainDen := 1446047995,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "14ef171f640824a677f4fb4930380fd70d824d72c867b88f132d959736905c84"
},
  {
  nodeId := "s3:s3_frontier:069d7a75cd16dc0c",
  branchId := "P11:r62421203:d26",
  sourceParent := 11,
  targetParent := 26,
  valuation := 5,
  gainNum := 10685,
  gainDen := 129530067,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P11:r62421203:d26",
    sourceParent := 11,
    targetParent := 26,
    valuation := 5,
    branchResidue := 62421203,
    branchDepth := 26,
    sourceModulus := 67108864,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P11:r62421203:d26",
    sourceParent := 11,
    targetParent := 26,
    valuation := 5,
    gainNum := 10685,
    gainDen := 129530067,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P11:r62421203:d26",
    gainNum := 10685,
    gainDen := 129530067,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "f865ced42c828a5c17ab63772309b36ab06c7e5f25c5bff81076342ade8cb0eb"
},
  {
  nodeId := "s3:s3_frontier:08e7602e642d9d52",
  branchId := "P20:r39862641:d26",
  sourceParent := 20,
  targetParent := 22,
  valuation := 6,
  gainNum := 6788006475,
  gainDen := 8361361777,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P20:r39862641:d26",
    sourceParent := 20,
    targetParent := 22,
    valuation := 6,
    branchResidue := 39862641,
    branchDepth := 26,
    sourceModulus := 67108864,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P20:r39862641:d26",
    sourceParent := 20,
    targetParent := 22,
    valuation := 6,
    gainNum := 6788006475,
    gainDen := 8361361777,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P20:r39862641:d26",
    gainNum := 6788006475,
    gainDen := 8361361777,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "be2c198cc942d86314c9ce57aa767cbf54e063e54e5438c37073353cbd88fbea"
},
  {
  nodeId := "s3:s3_frontier:098319fd41f374b2",
  branchId := "P9:r13235615:d24",
  sourceParent := 9,
  targetParent := 25,
  valuation := 3,
  gainNum := 1941,
  gainDen := 13235615,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P9:r13235615:d24",
    sourceParent := 9,
    targetParent := 25,
    valuation := 3,
    branchResidue := 13235615,
    branchDepth := 24,
    sourceModulus := 16777216,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P9:r13235615:d24",
    sourceParent := 9,
    targetParent := 25,
    valuation := 3,
    gainNum := 1941,
    gainDen := 13235615,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P9:r13235615:d24",
    gainNum := 1941,
    gainDen := 13235615,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "04ec713d5ef3d8ff39f51bf0b1fc82f44ea07b8841a7deef13d4174f9bd184b6"
},
  {
  nodeId := "s3:s3_frontier:098d1ff9b293659f",
  branchId := "P12:r40120529:d26",
  sourceParent := 12,
  targetParent := 22,
  valuation := 2,
  gainNum := 876591,
  gainDen := 442773713,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P12:r40120529:d26",
    sourceParent := 12,
    targetParent := 22,
    valuation := 2,
    branchResidue := 40120529,
    branchDepth := 26,
    sourceModulus := 67108864,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P12:r40120529:d26",
    sourceParent := 12,
    targetParent := 22,
    valuation := 2,
    gainNum := 876591,
    gainDen := 442773713,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P12:r40120529:d26",
    gainNum := 876591,
    gainDen := 442773713,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "3c4013ae8486b20aebfbbdee027c76b02cbbbb4156ee0986a45085873e6177ee"
},
  {
  nodeId := "s3:s3_frontier:09dfc239e56eeae9",
  branchId := "P7:r9512459:d24",
  sourceParent := 7,
  targetParent := 25,
  valuation := 4,
  gainNum := 1171,
  gainDen := 143730187,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P7:r9512459:d24",
    sourceParent := 7,
    targetParent := 25,
    valuation := 4,
    branchResidue := 9512459,
    branchDepth := 24,
    sourceModulus := 16777216,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P7:r9512459:d24",
    sourceParent := 7,
    targetParent := 25,
    valuation := 4,
    gainNum := 1171,
    gainDen := 143730187,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P7:r9512459:d24",
    gainNum := 1171,
    gainDen := 143730187,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "289fbdf3166cadd9c48c6e3aa8eca6005fb37ee968276ea0d1e95c41010c0dd9"
},
  {
  nodeId := "s3:s3_frontier:0cbbf0500c5aa8f7",
  branchId := "P9:r53252723:d26",
  sourceParent := 9,
  targetParent := 24,
  valuation := 1,
  gainNum := 17651,
  gainDen := 120361587,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P9:r53252723:d26",
    sourceParent := 9,
    targetParent := 24,
    valuation := 1,
    branchResidue := 53252723,
    branchDepth := 26,
    sourceModulus := 67108864,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P9:r53252723:d26",
    sourceParent := 9,
    targetParent := 24,
    valuation := 1,
    gainNum := 17651,
    gainDen := 120361587,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P9:r53252723:d26",
    gainNum := 17651,
    gainDen := 120361587,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "e3600dfc90ef73a6d88fb817ce1af828fd3061e0f6a018c8edc707fa0c261da8"
},
  {
  nodeId := "s3:s3_frontier:0f1b2ddc21da9c6f",
  branchId := "P10:r40120529:d26",
  sourceParent := 10,
  targetParent := 23,
  valuation := 0,
  gainNum := 94351,
  gainDen := 107229393,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P10:r40120529:d26",
    sourceParent := 10,
    targetParent := 23,
    valuation := 0,
    branchResidue := 40120529,
    branchDepth := 26,
    sourceModulus := 67108864,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P10:r40120529:d26",
    sourceParent := 10,
    targetParent := 23,
    valuation := 0,
    gainNum := 94351,
    gainDen := 107229393,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P10:r40120529:d26",
    gainNum := 94351,
    gainDen := 107229393,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "0e011799a0ab76ca859bce10c39a86f7cb5545bf023b0218994916cd81dbd00b"
},
  {
  nodeId := "s3:s3_frontier:0fbf7f977ecda865",
  branchId := "P13:r20876015:d25",
  sourceParent := 13,
  targetParent := 30,
  valuation := 7,
  gainNum := 231951,
  gainDen := 624855791,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P13:r20876015:d25",
    sourceParent := 13,
    targetParent := 30,
    valuation := 7,
    branchResidue := 20876015,
    branchDepth := 25,
    sourceModulus := 33554432,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P13:r20876015:d25",
    sourceParent := 13,
    targetParent := 30,
    valuation := 7,
    gainNum := 231951,
    gainDen := 624855791,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P13:r20876015:d25",
    gainNum := 231951,
    gainDen := 624855791,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "7b75cd166d17a897d5962b6bd426dade7b61b14eaafe8e99fd9c5146a49247db"
},
  {
  nodeId := "s3:s3_frontier:1284fda134ff1eef",
  branchId := "P8:r64316497:d26",
  sourceParent := 8,
  targetParent := 26,
  valuation := 4,
  gainNum := 393,
  gainDen := 64316497,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P8:r64316497:d26",
    sourceParent := 8,
    targetParent := 26,
    valuation := 4,
    branchResidue := 64316497,
    branchDepth := 26,
    sourceModulus := 67108864,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P8:r64316497:d26",
    sourceParent := 8,
    targetParent := 26,
    valuation := 4,
    gainNum := 393,
    gainDen := 64316497,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P8:r64316497:d26",
    gainNum := 393,
    gainDen := 64316497,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "e3fda0c977df2bf285f4323d2f644d3ef1119151a279a190adf5f19c11edbf76"
},
  {
  nodeId := "s3:s3_frontier:12f6ce0dda0edb3e",
  branchId := "P13:r33705691:d26",
  sourceParent := 13,
  targetParent := 23,
  valuation := 4,
  gainNum := 1544725,
  gainDen := 1040338651,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P13:r33705691:d26",
    sourceParent := 13,
    targetParent := 23,
    valuation := 4,
    branchResidue := 33705691,
    branchDepth := 26,
    sourceModulus := 67108864,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P13:r33705691:d26",
    sourceParent := 13,
    targetParent := 23,
    valuation := 4,
    gainNum := 1544725,
    gainDen := 1040338651,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P13:r33705691:d26",
    gainNum := 1544725,
    gainDen := 1040338651,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "c78ec0a9f2bf9a1dd4236c2c8fd242db538cbb11f8af46b8bac5b60bec90309c"
},
  {
  nodeId := "s3:s3_frontier:1908d42be17679a8",
  branchId := "P12:r11914377:d24",
  sourceParent := 12,
  targetParent := 27,
  valuation := 6,
  gainNum := 570553,
  gainDen := 1152765065,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P12:r11914377:d24",
    sourceParent := 12,
    targetParent := 27,
    valuation := 6,
    branchResidue := 11914377,
    branchDepth := 24,
    sourceModulus := 16777216,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P12:r11914377:d24",
    sourceParent := 12,
    targetParent := 27,
    valuation := 6,
    gainNum := 570553,
    gainDen := 1152765065,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P12:r11914377:d24",
    gainNum := 570553,
    gainDen := 1152765065,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "7bd4e42bb7a609b254b782e6d5c0ecab36213ec8e7b033568430cad91e91efeb"
},
  {
  nodeId := "s3:s3_frontier:1c1f457759608fa7",
  branchId := "P4:r62137837:d26",
  sourceParent := 4,
  targetParent := 28,
  valuation := 4,
  gainNum := 111,
  gainDen := 1471423981,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P4:r62137837:d26",
    sourceParent := 4,
    targetParent := 28,
    valuation := 4,
    branchResidue := 62137837,
    branchDepth := 26,
    sourceModulus := 67108864,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P4:r62137837:d26",
    sourceParent := 4,
    targetParent := 28,
    valuation := 4,
    gainNum := 111,
    gainDen := 1471423981,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P4:r62137837:d26",
    gainNum := 111,
    gainDen := 1471423981,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "8e863f8f574b9763f4233ad45d2c4a185c5014bfa1dbe1986a889e59162c9d8f"
},
  {
  nodeId := "s3:s3_frontier:1d4489a9493396a2",
  branchId := "P7:r52011671:d26",
  sourceParent := 7,
  targetParent := 31,
  valuation := 7,
  gainNum := 3345,
  gainDen := 13138240151,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P7:r52011671:d26",
    sourceParent := 7,
    targetParent := 31,
    valuation := 7,
    branchResidue := 52011671,
    branchDepth := 26,
    sourceModulus := 67108864,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P7:r52011671:d26",
    sourceParent := 7,
    targetParent := 31,
    valuation := 7,
    gainNum := 3345,
    gainDen := 13138240151,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P7:r52011671:d26",
    gainNum := 3345,
    gainDen := 13138240151,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "d94cc87b2ecd643eb3c602a9af74b3b300f2f63877f5def839b2e73fce1975e9"
},
  {
  nodeId := "s3:s3_frontier:1d504f4a2b2c1fc3",
  branchId := "P4:r62137837:d26",
  sourceParent := 4,
  targetParent := 26,
  valuation := 2,
  gainNum := 39,
  gainDen := 129246701,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P4:r62137837:d26",
    sourceParent := 4,
    targetParent := 26,
    valuation := 2,
    branchResidue := 62137837,
    branchDepth := 26,
    sourceModulus := 67108864,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P4:r62137837:d26",
    sourceParent := 4,
    targetParent := 26,
    valuation := 2,
    gainNum := 39,
    gainDen := 129246701,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P4:r62137837:d26",
    gainNum := 39,
    gainDen := 129246701,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "63cb4f8d8ab5c02551b635cf85648a0a3de337e0d0af814ba24f71f98c6f57d7"
},
  {
  nodeId := "s3:s3_frontier:1ddfec7aec044d6f",
  branchId := "P15:r41027779:d26",
  sourceParent := 15,
  targetParent := 25,
  valuation := 6,
  gainNum := 2379085,
  gainDen := 712116419,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P15:r41027779:d26",
    sourceParent := 15,
    targetParent := 25,
    valuation := 6,
    branchResidue := 41027779,
    branchDepth := 26,
    sourceModulus := 67108864,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P15:r41027779:d26",
    sourceParent := 15,
    targetParent := 25,
    valuation := 6,
    gainNum := 2379085,
    gainDen := 712116419,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P15:r41027779:d26",
    gainNum := 2379085,
    gainDen := 712116419,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "c359027e681e4264d2ecf73fdd6d20c124897c8e857cd3b26e061f0bf9b3bea8"
},
  {
  nodeId := "s3:s3_frontier:1e02b3b1bfaf7fad",
  branchId := "P10:r53045881:d26",
  sourceParent := 10,
  targetParent := 22,
  valuation := 1,
  gainNum := 111911,
  gainDen := 254372473,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P10:r53045881:d26",
    sourceParent := 10,
    targetParent := 22,
    valuation := 1,
    branchResidue := 53045881,
    branchDepth := 26,
    sourceModulus := 67108864,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P10:r53045881:d26",
    sourceParent := 10,
    targetParent := 22,
    valuation := 1,
    gainNum := 111911,
    gainDen := 254372473,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P10:r53045881:d26",
    gainNum := 111911,
    gainDen := 254372473,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "f5a4162047b93f215efcc9f805a6a3012ab075bc9f95e6f2c0618459ea8890f0"
},
  {
  nodeId := "s3:s3_frontier:1e0ad0c08857b346",
  branchId := "P17:r2110859:d22",
  sourceParent := 17,
  targetParent := 24,
  valuation := 7,
  gainNum := 178075475,
  gainDen := 740308363,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P17:r2110859:d22",
    sourceParent := 17,
    targetParent := 24,
    valuation := 7,
    branchResidue := 2110859,
    branchDepth := 22,
    sourceModulus := 4194304,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P17:r2110859:d22",
    sourceParent := 17,
    targetParent := 24,
    valuation := 7,
    gainNum := 178075475,
    gainDen := 740308363,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P17:r2110859:d22",
    gainNum := 178075475,
    gainDen := 740308363,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "614c920b42aa6bdf17e1abeac16fbfaf93a7fc9cf86fc6c456d6e372822b4ffb"
},
  {
  nodeId := "s3:s3_frontier:20144e7cbf8c1aa2",
  branchId := "P8:r13235615:d24",
  sourceParent := 8,
  targetParent := 26,
  valuation := 3,
  gainNum := 647,
  gainDen := 13235615,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P8:r13235615:d24",
    sourceParent := 8,
    targetParent := 26,
    valuation := 3,
    branchResidue := 13235615,
    branchDepth := 24,
    sourceModulus := 16777216,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P8:r13235615:d24",
    sourceParent := 8,
    targetParent := 26,
    valuation := 3,
    gainNum := 647,
    gainDen := 13235615,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P8:r13235615:d24",
    gainNum := 647,
    gainDen := 13235615,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "c469fac542410755fddbe8e800a050a1521c3c504e772c1ff225c4691e10a246"
},
  {
  nodeId := "s3:s3_frontier:21132cb0e6fd44ea",
  branchId := "P8:r25540441:d25",
  sourceParent := 8,
  targetParent := 26,
  valuation := 4,
  gainNum := 6053,
  gainDen := 495302489,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P8:r25540441:d25",
    sourceParent := 8,
    targetParent := 26,
    valuation := 4,
    branchResidue := 25540441,
    branchDepth := 25,
    sourceModulus := 33554432,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P8:r25540441:d25",
    sourceParent := 8,
    targetParent := 26,
    valuation := 4,
    gainNum := 6053,
    gainDen := 495302489,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P8:r25540441:d25",
    gainNum := 6053,
    gainDen := 495302489,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "3f6cb4ebec0ce0f609b70055ebc033f2f2bda8634ef1ebba99c1fa4d1042d226"
},
  {
  nodeId := "s3:s3_frontier:21377cecf937dc38",
  branchId := "P15:r18997731:d25",
  sourceParent := 15,
  targetParent := 20,
  valuation := 0,
  gainNum := 22472921,
  gainDen := 52552163,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P15:r18997731:d25",
    sourceParent := 15,
    targetParent := 20,
    valuation := 0,
    branchResidue := 18997731,
    branchDepth := 25,
    sourceModulus := 33554432,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P15:r18997731:d25",
    sourceParent := 15,
    targetParent := 20,
    valuation := 0,
    gainNum := 22472921,
    gainDen := 52552163,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P15:r18997731:d25",
    gainNum := 22472921,
    gainDen := 52552163,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "4cb7031e21a5a8eadec17ced81da5a8524d2ba2dbe8636fd23f65ed82ff0938f"
},
  {
  nodeId := "s3:s3_frontier:220d5547c3f0f012",
  branchId := "P15:r18997731:d25",
  sourceParent := 15,
  targetParent := 26,
  valuation := 6,
  gainNum := 26582735,
  gainDen := 3978420707,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P15:r18997731:d25",
    sourceParent := 15,
    targetParent := 26,
    valuation := 6,
    branchResidue := 18997731,
    branchDepth := 25,
    sourceModulus := 33554432,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P15:r18997731:d25",
    sourceParent := 15,
    targetParent := 26,
    valuation := 6,
    gainNum := 26582735,
    gainDen := 3978420707,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P15:r18997731:d25",
    gainNum := 26582735,
    gainDen := 3978420707,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "2d5561f23b86ae723884f61f177c20821c041453fca2212d3979bfb8ed55b0f6"
},
  {
  nodeId := "s3:s3_frontier:22676017665d803f",
  branchId := "P9:r66178075:d26",
  sourceParent := 9,
  targetParent := 22,
  valuation := 0,
  gainNum := 39093,
  gainDen := 133286939,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P9:r66178075:d26",
    sourceParent := 9,
    targetParent := 22,
    valuation := 0,
    branchResidue := 66178075,
    branchDepth := 26,
    sourceModulus := 67108864,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P9:r66178075:d26",
    sourceParent := 9,
    targetParent := 22,
    valuation := 0,
    gainNum := 39093,
    gainDen := 133286939,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P9:r66178075:d26",
    gainNum := 39093,
    gainDen := 133286939,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "5215970de2045488c7c5eb3ce59ba7316d679cf4788546562cca91c9b5c5cac3"
},
  {
  nodeId := "s3:s3_frontier:249241262eaf8f7f",
  branchId := "P14:r9876937:d24",
  sourceParent := 14,
  targetParent := 21,
  valuation := 5,
  gainNum := 1025783,
  gainDen := 115140419,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P14:r9876937:d24",
    sourceParent := 14,
    targetParent := 21,
    valuation := 5,
    branchResidue := 9876937,
    branchDepth := 24,
    sourceModulus := 16777216,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P14:r9876937:d24",
    sourceParent := 14,
    targetParent := 21,
    valuation := 5,
    gainNum := 1025783,
    gainDen := 115140419,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P14:r9876937:d24",
    gainNum := 1025783,
    gainDen := 115140419,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "f9902349b69c6f4faf49c7e19f4701c7491edd9a31cd5f0f9e4e91c5ffff1ee6"
},
  {
  nodeId := "s3:s3_frontier:2715b6aa408adfae",
  branchId := "P5:r21817285:d25",
  sourceParent := 5,
  targetParent := 29,
  valuation := 5,
  gainNum := 415,
  gainDen := 1833756613,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P5:r21817285:d25",
    sourceParent := 5,
    targetParent := 29,
    valuation := 5,
    branchResidue := 21817285,
    branchDepth := 25,
    sourceModulus := 33554432,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P5:r21817285:d25",
    sourceParent := 5,
    targetParent := 29,
    valuation := 5,
    gainNum := 415,
    gainDen := 1833756613,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P5:r21817285:d25",
    gainNum := 415,
    gainDen := 1833756613,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "435e710aa9f078bfcb72a5d86f451dfefedb19b3ae14e589f02ca4c48c937f2b"
},
  {
  nodeId := "s3:s3_frontier:29d2a6e898a575a6",
  branchId := "P6:r52011671:d26",
  sourceParent := 6,
  targetParent := 32,
  valuation := 7,
  gainNum := 1115,
  gainDen := 13138240151,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P6:r52011671:d26",
    sourceParent := 6,
    targetParent := 32,
    valuation := 7,
    branchResidue := 52011671,
    branchDepth := 26,
    sourceModulus := 67108864,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P6:r52011671:d26",
    sourceParent := 6,
    targetParent := 32,
    valuation := 7,
    gainNum := 1115,
    gainDen := 13138240151,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P6:r52011671:d26",
    gainNum := 1115,
    gainDen := 13138240151,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "b133dcb5c45605dce0dc475dd0705fab49dc427d871189e30ae8f621514b7780"
},
  {
  nodeId := "s3:s3_frontier:2b6a2f8bdb082329",
  branchId := "P12:r20876015:d25",
  sourceParent := 12,
  targetParent := 26,
  valuation := 2,
  gainNum := 879821,
  gainDen := 222202607,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P12:r20876015:d25",
    sourceParent := 12,
    targetParent := 26,
    valuation := 2,
    branchResidue := 20876015,
    branchDepth := 25,
    sourceModulus := 33554432,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P12:r20876015:d25",
    sourceParent := 12,
    targetParent := 26,
    valuation := 2,
    gainNum := 879821,
    gainDen := 222202607,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P12:r20876015:d25",
    gainNum := 879821,
    gainDen := 222202607,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "d9d907ccda058276bbdea1cee756ee4f09478e30cad90c4d65fbf4a4308943f3"
},
  {
  nodeId := "s3:s3_frontier:2cc34fe497bd8d1a",
  branchId := "P7:r52011671:d26",
  sourceParent := 7,
  targetParent := 25,
  valuation := 1,
  gainNum := 647,
  gainDen := 39706845,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P7:r52011671:d26",
    sourceParent := 7,
    targetParent := 25,
    valuation := 1,
    branchResidue := 52011671,
    branchDepth := 26,
    sourceModulus := 67108864,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P7:r52011671:d26",
    sourceParent := 7,
    targetParent := 25,
    valuation := 1,
    gainNum := 647,
    gainDen := 39706845,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P7:r52011671:d26",
    gainNum := 647,
    gainDen := 39706845,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "b1967c4f40c6f3be8526dbaa7096622fbe0a38b6c9ade4e776edb5b6bcbd670c"
},
  {
  nodeId := "s3:s3_frontier:2dbd9730b6c6d0fe",
  branchId := "P14:r12423737:d24",
  sourceParent := 14,
  targetParent := 20,
  valuation := 0,
  gainNum := 2774939,
  gainDen := 9733651,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P14:r12423737:d24",
    sourceParent := 14,
    targetParent := 20,
    valuation := 0,
    branchResidue := 12423737,
    branchDepth := 24,
    sourceModulus := 16777216,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P14:r12423737:d24",
    sourceParent := 14,
    targetParent := 20,
    valuation := 0,
    gainNum := 2774939,
    gainDen := 9733651,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P14:r12423737:d24",
    gainNum := 2774939,
    gainDen := 9733651,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "317ac59bb4c04923a3f704513db3253c60252f61e349ec82f2599fad15503147"
},
  {
  nodeId := "s3:s3_frontier:2ff102edf933c272",
  branchId := "P12:r44704769:d26",
  sourceParent := 12,
  targetParent := 22,
  valuation := 0,
  gainNum := 354021,
  gainDen := 44704769,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P12:r44704769:d26",
    sourceParent := 12,
    targetParent := 22,
    valuation := 0,
    branchResidue := 44704769,
    branchDepth := 26,
    sourceModulus := 67108864,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P12:r44704769:d26",
    sourceParent := 12,
    targetParent := 22,
    valuation := 0,
    gainNum := 354021,
    gainDen := 44704769,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P12:r44704769:d26",
    gainNum := 354021,
    gainDen := 44704769,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "f4a724c915cc2004598f9ae55b3092d8a7a197af6f4cbbca4afed16d3ee50e78"
},
  {
  nodeId := "s3:s3_frontier:30de3deff4b4c4bd",
  branchId := "P16:r11028287:d24",
  sourceParent := 16,
  targetParent := 29,
  valuation := 6,
  gainNum := 32727169,
  gainDen := 816334655,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P16:r11028287:d24",
    sourceParent := 16,
    targetParent := 29,
    valuation := 6,
    branchResidue := 11028287,
    branchDepth := 24,
    sourceModulus := 16777216,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P16:r11028287:d24",
    sourceParent := 16,
    targetParent := 29,
    valuation := 6,
    gainNum := 32727169,
    gainDen := 816334655,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P16:r11028287:d24",
    gainNum := 32727169,
    gainDen := 816334655,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "f1b7cde479e3d4ae300360c2578fb36d3487848d50878d133e8d1d3dbcd70bee"
},
  {
  nodeId := "s3:s3_frontier:31f350059efde954",
  branchId := "P2:r52195783:d26",
  sourceParent := 2,
  targetParent := 30,
  valuation := 5,
  gainNum := 5,
  gainDen := 1193046471,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P2:r52195783:d26",
    sourceParent := 2,
    targetParent := 30,
    valuation := 5,
    branchResidue := 52195783,
    branchDepth := 26,
    sourceModulus := 67108864,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P2:r52195783:d26",
    sourceParent := 2,
    targetParent := 30,
    valuation := 5,
    gainNum := 5,
    gainDen := 1193046471,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P2:r52195783:d26",
    gainNum := 5,
    gainDen := 1193046471,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "c3b5e2674a56b416bfbcea8c02e9b634117e674e8fe7335faefefe6a49784a73"
},
  {
  nodeId := "s3:s3_frontier:32248ca96addc7fc",
  branchId := "P16:r23693441:d25",
  sourceParent := 16,
  targetParent := 21,
  valuation := 2,
  gainNum := 7599033,
  gainDen := 23693441,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P16:r23693441:d25",
    sourceParent := 16,
    targetParent := 21,
    valuation := 2,
    branchResidue := 23693441,
    branchDepth := 25,
    sourceModulus := 33554432,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P16:r23693441:d25",
    sourceParent := 16,
    targetParent := 21,
    valuation := 2,
    gainNum := 7599033,
    gainDen := 23693441,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P16:r23693441:d25",
    gainNum := 7599033,
    gainDen := 23693441,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "787d4309ab69a07cab62d69c0809a32d85f625242d199f134a583e1f0c887751"
},
  {
  nodeId := "s3:s3_frontier:33e1141ec74851ee",
  branchId := "P11:r35743131:d26",
  sourceParent := 11,
  targetParent := 23,
  valuation := 0,
  gainNum := 94351,
  gainDen := 35743131,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P11:r35743131:d26",
    sourceParent := 11,
    targetParent := 23,
    valuation := 0,
    branchResidue := 35743131,
    branchDepth := 26,
    sourceModulus := 67108864,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P11:r35743131:d26",
    sourceParent := 11,
    targetParent := 23,
    valuation := 0,
    gainNum := 94351,
    gainDen := 35743131,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P11:r35743131:d26",
    gainNum := 94351,
    gainDen := 35743131,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "ab9392d9a81d02c2018015b6b9c268a01e1025f1482f9442ec97138c96ecff67"
},
  {
  nodeId := "s3:s3_frontier:3483c13415656fc0",
  branchId := "P12:r11914377:d24",
  sourceParent := 12,
  targetParent := 25,
  valuation := 4,
  gainNum := 687889,
  gainDen := 347458697,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P12:r11914377:d24",
    sourceParent := 12,
    targetParent := 25,
    valuation := 4,
    branchResidue := 11914377,
    branchDepth := 24,
    sourceModulus := 16777216,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P12:r11914377:d24",
    sourceParent := 12,
    targetParent := 25,
    valuation := 4,
    gainNum := 687889,
    gainDen := 347458697,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P12:r11914377:d24",
    gainNum := 687889,
    gainDen := 347458697,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "792696fe0b36983410cdafdadf0f3727f2a7a588009cc1d3f5e23207eaacf1c6"
},
  {
  nodeId := "s3:s3_frontier:38ac9165b4bcbed3",
  branchId := "P14:r9876937:d24",
  sourceParent := 14,
  targetParent := 17,
  valuation := 1,
  gainNum := 2063621,
  gainDen := 14477123,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P14:r9876937:d24",
    sourceParent := 14,
    targetParent := 17,
    valuation := 1,
    branchResidue := 9876937,
    branchDepth := 24,
    sourceModulus := 16777216,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P14:r9876937:d24",
    sourceParent := 14,
    targetParent := 17,
    valuation := 1,
    gainNum := 2063621,
    gainDen := 14477123,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P14:r9876937:d24",
    gainNum := 2063621,
    gainDen := 14477123,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "caa4808207a06ae262c4fe32210c4efdf0dbe49248f00f518c7852b4c62561da"
},
  {
  nodeId := "s3:s3_frontier:3b2d850a6a68d9c5",
  branchId := "P13:r37271211:d26",
  sourceParent := 13,
  targetParent := 24,
  valuation := 2,
  gainNum := 1018527,
  gainDen := 171488939,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P13:r37271211:d26",
    sourceParent := 13,
    targetParent := 24,
    valuation := 2,
    branchResidue := 37271211,
    branchDepth := 26,
    sourceModulus := 67108864,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P13:r37271211:d26",
    sourceParent := 13,
    targetParent := 24,
    valuation := 2,
    gainNum := 1018527,
    gainDen := 171488939,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P13:r37271211:d26",
    gainNum := 1018527,
    gainDen := 171488939,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "813ee1e802dc053319bfd8a847998b0e8f8f39b4e37fe4166b7f92f4a6a4e8a1"
},
  {
  nodeId := "s3:s3_frontier:3cb22e55093c2190",
  branchId := "P10:r53666407:d26",
  sourceParent := 10,
  targetParent := 29,
  valuation := 4,
  gainNum := 14023,
  gainDen := 254992999,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P10:r53666407:d26",
    sourceParent := 10,
    targetParent := 29,
    valuation := 4,
    branchResidue := 53666407,
    branchDepth := 26,
    sourceModulus := 67108864,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P10:r53666407:d26",
    sourceParent := 10,
    targetParent := 29,
    valuation := 4,
    gainNum := 14023,
    gainDen := 254992999,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P10:r53666407:d26",
    gainNum := 14023,
    gainDen := 254992999,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "600f939b1e4d425cb2a44e12821e85e8352560832fc7e0a9970305b50d49bc6c"
},
  {
  nodeId := "s3:s3_frontier:3d1fbaed98d1f5f0",
  branchId := "P15:r41027779:d26",
  sourceParent := 15,
  targetParent := 23,
  valuation := 4,
  gainNum := 23865247,
  gainDen := 1785858243,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P15:r41027779:d26",
    sourceParent := 15,
    targetParent := 23,
    valuation := 4,
    branchResidue := 41027779,
    branchDepth := 26,
    sourceModulus := 67108864,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P15:r41027779:d26",
    sourceParent := 15,
    targetParent := 23,
    valuation := 4,
    gainNum := 23865247,
    gainDen := 1785858243,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P15:r41027779:d26",
    gainNum := 23865247,
    gainDen := 1785858243,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "f779bc94f99de984371c5d1d191dd5122c2dad1dbbefb1872aa26af434111bb6"
},
  {
  nodeId := "s3:s3_frontier:4167c7d588e6b511",
  branchId := "P14:r9876937:d24",
  sourceParent := 14,
  targetParent := 16,
  valuation := 0,
  gainNum := 7598757,
  gainDen := 26654153,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P14:r9876937:d24",
    sourceParent := 14,
    targetParent := 16,
    valuation := 0,
    branchResidue := 9876937,
    branchDepth := 24,
    sourceModulus := 16777216,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P14:r9876937:d24",
    sourceParent := 14,
    targetParent := 16,
    valuation := 0,
    gainNum := 7598757,
    gainDen := 26654153,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P14:r9876937:d24",
    gainNum := 7598757,
    gainDen := 26654153,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "8d1f3cd9c203a6047efbaacd2326827ee690bd8c6c11c7363e39c7bc9cb35e03"
},
  {
  nodeId := "s3:s3_frontier:418f70481514ae22",
  branchId := "P14:r32145719:d25",
  sourceParent := 14,
  targetParent := 25,
  valuation := 1,
  gainNum := 2291083,
  gainDen := 32145719,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P14:r32145719:d25",
    sourceParent := 14,
    targetParent := 25,
    valuation := 1,
    branchResidue := 32145719,
    branchDepth := 25,
    sourceModulus := 33554432,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P14:r32145719:d25",
    sourceParent := 14,
    targetParent := 25,
    valuation := 1,
    gainNum := 2291083,
    gainDen := 32145719,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P14:r32145719:d25",
    gainNum := 2291083,
    gainDen := 32145719,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "e7d56d3a077d0647bb06497ed1662a10dbfbcf37ccd426b03856b8a48d024005"
},
  {
  nodeId := "s3:s3_frontier:434d17c738535c49",
  branchId := "P11:r35743131:d26",
  sourceParent := 11,
  targetParent := 25,
  valuation := 2,
  gainNum := 333595,
  gainDen := 505505179,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P11:r35743131:d26",
    sourceParent := 11,
    targetParent := 25,
    valuation := 2,
    branchResidue := 35743131,
    branchDepth := 26,
    sourceModulus := 67108864,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P11:r35743131:d26",
    sourceParent := 11,
    targetParent := 25,
    valuation := 2,
    gainNum := 333595,
    gainDen := 505505179,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P11:r35743131:d26",
    gainNum := 333595,
    gainDen := 505505179,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "4964803ad64577f2f1914efeddec0b54e539b74bc926461f4376be304eb8dd8b"
},
  {
  nodeId := "s3:s3_frontier:4452a6875f5521b1",
  branchId := "P15:r18997731:d25",
  sourceParent := 15,
  targetParent := 27,
  valuation := 7,
  gainNum := 20465821,
  gainDen := 6125904355,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P15:r18997731:d25",
    sourceParent := 15,
    targetParent := 27,
    valuation := 7,
    branchResidue := 18997731,
    branchDepth := 25,
    sourceModulus := 33554432,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P15:r18997731:d25",
    sourceParent := 15,
    targetParent := 27,
    valuation := 7,
    gainNum := 20465821,
    gainDen := 6125904355,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P15:r18997731:d25",
    gainNum := 20465821,
    gainDen := 6125904355,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "2a918f53a433223da75eb12c3cf240a68577398a1d9a83f3147b5dd6caa2a3f1"
},
  {
  nodeId := "s3:s3_frontier:45e8b9ec5c1dd171",
  branchId := "P13:r36761851:d26",
  sourceParent := 13,
  targetParent := 23,
  valuation := 2,
  gainNum := 616921,
  gainDen := 103870715,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P13:r36761851:d26",
    sourceParent := 13,
    targetParent := 23,
    valuation := 2,
    branchResidue := 36761851,
    branchDepth := 26,
    sourceModulus := 67108864,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P13:r36761851:d26",
    sourceParent := 13,
    targetParent := 23,
    valuation := 2,
    gainNum := 616921,
    gainDen := 103870715,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P13:r36761851:d26",
    gainNum := 616921,
    gainDen := 103870715,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "379f17efef6ae3e72586ea021799ad6e22d7201652b43e92397027181c29f690"
},
  {
  nodeId := "s3:s3_frontier:4654e99b99e64aaf",
  branchId := "P8:r25540441:d25",
  sourceParent := 8,
  targetParent := 24,
  valuation := 2,
  gainNum := 647,
  gainDen := 13235615,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P8:r25540441:d25",
    sourceParent := 8,
    targetParent := 24,
    valuation := 2,
    branchResidue := 25540441,
    branchDepth := 25,
    sourceModulus := 33554432,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P8:r25540441:d25",
    sourceParent := 8,
    targetParent := 24,
    valuation := 2,
    gainNum := 647,
    gainDen := 13235615,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P8:r25540441:d25",
    gainNum := 647,
    gainDen := 13235615,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "7a8bb628ddafdea04c1fd3e7fa4b23e15dc5e595611e92f36af2642d284af657"
},
  {
  nodeId := "s3:s3_frontier:4ae3a92f8ce278d9",
  branchId := "P14:r12423737:d24",
  sourceParent := 14,
  targetParent := 21,
  valuation := 1,
  gainNum := 6553893,
  gainDen := 45978169,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P14:r12423737:d24",
    sourceParent := 14,
    targetParent := 21,
    valuation := 1,
    branchResidue := 12423737,
    branchDepth := 24,
    sourceModulus := 16777216,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P14:r12423737:d24",
    sourceParent := 14,
    targetParent := 21,
    valuation := 1,
    gainNum := 6553893,
    gainDen := 45978169,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P14:r12423737:d24",
    gainNum := 6553893,
    gainDen := 45978169,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "b14ad601bd1fa66c09e1dd0e0d7654cdcc32284ffbffe973ee2fc8220dd0a8a2"
},
  {
  nodeId := "s3:s3_frontier:4b01a6024d95192a",
  branchId := "P17:r11028287:d24",
  sourceParent := 17,
  targetParent := 26,
  valuation := 4,
  gainNum := 5305539,
  gainDen := 11028287,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P17:r11028287:d24",
    sourceParent := 17,
    targetParent := 26,
    valuation := 4,
    branchResidue := 11028287,
    branchDepth := 24,
    sourceModulus := 16777216,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P17:r11028287:d24",
    sourceParent := 17,
    targetParent := 26,
    valuation := 4,
    gainNum := 5305539,
    gainDen := 11028287,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P17:r11028287:d24",
    gainNum := 5305539,
    gainDen := 11028287,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "f18970021bdc9dc5b5c00dea6363e1d2b3fd4bab6d6c0fc4b68eeaeaa36c5f38"
},
  {
  nodeId := "s3:s3_frontier:4eadfac62799baa6",
  branchId := "P14:r9876937:d24",
  sourceParent := 14,
  targetParent := 22,
  valuation := 6,
  gainNum := 3930159,
  gainDen := 882292169,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P14:r9876937:d24",
    sourceParent := 14,
    targetParent := 22,
    valuation := 6,
    branchResidue := 9876937,
    branchDepth := 24,
    sourceModulus := 16777216,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P14:r9876937:d24",
    sourceParent := 14,
    targetParent := 22,
    valuation := 6,
    gainNum := 3930159,
    gainDen := 882292169,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P14:r9876937:d24",
    gainNum := 3930159,
    gainDen := 882292169,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "7fdce2936c9cbeeec9e5e91021dc521dda1f5e52d6b1aa121013c5dad43e4c9e"
},
  {
  nodeId := "s3:s3_frontier:4f946cb203fa8420",
  branchId := "P2:r52195783:d26",
  sourceParent := 2,
  targetParent := 32,
  valuation := 7,
  gainNum := 17,
  gainDen := 16225432007,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P2:r52195783:d26",
    sourceParent := 2,
    targetParent := 32,
    valuation := 7,
    branchResidue := 52195783,
    branchDepth := 26,
    sourceModulus := 67108864,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P2:r52195783:d26",
    sourceParent := 2,
    targetParent := 32,
    valuation := 7,
    gainNum := 17,
    gainDen := 16225432007,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P2:r52195783:d26",
    gainNum := 17,
    gainDen := 16225432007,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "b000611b613dc73d0ffed00adb31d8026a04de9c235c5b25a75751f94c80ce4c"
},
  {
  nodeId := "s3:s3_frontier:50b106369c92f0cd",
  branchId := "P7:r52011671:d26",
  sourceParent := 7,
  targetParent := 24,
  valuation := 0,
  gainNum := 1695,
  gainDen := 52011671,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P7:r52011671:d26",
    sourceParent := 7,
    targetParent := 24,
    valuation := 0,
    branchResidue := 52011671,
    branchDepth := 26,
    sourceModulus := 67108864,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P7:r52011671:d26",
    sourceParent := 7,
    targetParent := 24,
    valuation := 0,
    gainNum := 1695,
    gainDen := 52011671,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P7:r52011671:d26",
    gainNum := 1695,
    gainDen := 52011671,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "748f6fe1e9e12e90e239ddb043ecc624437faa4994cc3d8e54c74f34187b0e4c"
},
  {
  nodeId := "s3:s3_frontier:52db3088f06b4ea2",
  branchId := "P7:r39706845:d26",
  sourceParent := 7,
  targetParent := 31,
  valuation := 6,
  gainNum := 2959,
  gainDen := 5811069149,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P7:r39706845:d26",
    sourceParent := 7,
    targetParent := 31,
    valuation := 6,
    branchResidue := 39706845,
    branchDepth := 26,
    sourceModulus := 67108864,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P7:r39706845:d26",
    sourceParent := 7,
    targetParent := 31,
    valuation := 6,
    gainNum := 2959,
    gainDen := 5811069149,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P7:r39706845:d26",
    gainNum := 2959,
    gainDen := 5811069149,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "7cf519d7e85153c8fec1d07fc88117db77cdba749d5f0eda7e589cb6d48a9eda"
},
  {
  nodeId := "s3:s3_frontier:55b61965b741a159",
  branchId := "P6:r21817285:d25",
  sourceParent := 6,
  targetParent := 30,
  valuation := 7,
  gainNum := 43,
  gainDen := 253338263,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P6:r21817285:d25",
    sourceParent := 6,
    targetParent := 30,
    valuation := 7,
    branchResidue := 21817285,
    branchDepth := 25,
    sourceModulus := 33554432,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P6:r21817285:d25",
    sourceParent := 6,
    targetParent := 30,
    valuation := 7,
    gainNum := 43,
    gainDen := 253338263,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P6:r21817285:d25",
    gainNum := 43,
    gainDen := 253338263,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "015b253a206a4382e16773096acc1307d3fb8d9ea69e208b02ef69e5592aed36"
},
  {
  nodeId := "s3:s3_frontier:5853c83203555b67",
  branchId := "P10:r53045881:d26",
  sourceParent := 10,
  targetParent := 25,
  valuation := 4,
  gainNum := 80419,
  gainDen := 1462332025,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P10:r53045881:d26",
    sourceParent := 10,
    targetParent := 25,
    valuation := 4,
    branchResidue := 53045881,
    branchDepth := 26,
    sourceModulus := 67108864,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P10:r53045881:d26",
    sourceParent := 10,
    targetParent := 25,
    valuation := 4,
    gainNum := 80419,
    gainDen := 1462332025,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P10:r53045881:d26",
    gainNum := 80419,
    gainDen := 1462332025,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "7c385dbda3d579e34b8718887d249ad5f6421cc1878def9e760842bf60360350"
},
  {
  nodeId := "s3:s3_frontier:5d62900f6d374b0f",
  branchId := "P9:r53252723:d26",
  sourceParent := 9,
  targetParent := 27,
  valuation := 4,
  gainNum := 19429,
  gainDen := 1059885683,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P9:r53252723:d26",
    sourceParent := 9,
    targetParent := 27,
    valuation := 4,
    branchResidue := 53252723,
    branchDepth := 26,
    sourceModulus := 67108864,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P9:r53252723:d26",
    sourceParent := 9,
    targetParent := 27,
    valuation := 4,
    gainNum := 19429,
    gainDen := 1059885683,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P9:r53252723:d26",
    gainNum := 19429,
    gainDen := 1059885683,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "b8c3854847eb4c9a0b59c2cdef3ab49d2950d43cb86ba0188f2b8097e2c372af"
},
  {
  nodeId := "s3:s3_frontier:5de13c7aa6e5ea94",
  branchId := "P12:r11914377:d24",
  sourceParent := 12,
  targetParent := 28,
  valuation := 7,
  gainNum := 550997,
  gainDen := 2226506889,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P12:r11914377:d24",
    sourceParent := 12,
    targetParent := 28,
    valuation := 7,
    branchResidue := 11914377,
    branchDepth := 24,
    sourceModulus := 16777216,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P12:r11914377:d24",
    sourceParent := 12,
    targetParent := 28,
    valuation := 7,
    gainNum := 550997,
    gainDen := 2226506889,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P12:r11914377:d24",
    gainNum := 550997,
    gainDen := 2226506889,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "507a4767fe76ed2c076bd34da408b261d012e39e3a2c4ba0f5f9f49aca1dbfcb"
},
  {
  nodeId := "s3:s3_frontier:5f01e6a842be27e9",
  branchId := "P12:r34008209:d26",
  sourceParent := 12,
  targetParent := 22,
  valuation := 3,
  gainNum := 432245,
  gainDen := 436661393,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P12:r34008209:d26",
    sourceParent := 12,
    targetParent := 22,
    valuation := 3,
    branchResidue := 34008209,
    branchDepth := 26,
    sourceModulus := 67108864,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P12:r34008209:d26",
    sourceParent := 12,
    targetParent := 22,
    valuation := 3,
    gainNum := 432245,
    gainDen := 436661393,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P12:r34008209:d26",
    gainNum := 432245,
    gainDen := 436661393,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "1c4410c0135267b1e82b1a005dfcd45a4bb1a3ceb8ff36236ba106bca9bf4ccf"
},
  {
  nodeId := "s3:s3_frontier:5f747359e2c60bfa",
  branchId := "P16:r23693441:d25",
  sourceParent := 16,
  targetParent := 25,
  valuation := 6,
  gainNum := 6928289,
  gainDen := 345633465,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P16:r23693441:d25",
    sourceParent := 16,
    targetParent := 25,
    valuation := 6,
    branchResidue := 23693441,
    branchDepth := 25,
    sourceModulus := 33554432,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P16:r23693441:d25",
    sourceParent := 16,
    targetParent := 25,
    valuation := 6,
    gainNum := 6928289,
    gainDen := 345633465,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P16:r23693441:d25",
    gainNum := 6928289,
    gainDen := 345633465,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "cefca34652a63d1ac8cebf7c6f6806b9ffc58a1e10ae9213673d7ebc3b74b66f"
},
  {
  nodeId := "s3:s3_frontier:6044aaeeab1b0ad2",
  branchId := "P12:r40120529:d26",
  sourceParent := 12,
  targetParent := 20,
  valuation := 0,
  gainNum := 94351,
  gainDen := 11914377,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P12:r40120529:d26",
    sourceParent := 12,
    targetParent := 20,
    valuation := 0,
    branchResidue := 40120529,
    branchDepth := 26,
    sourceModulus := 67108864,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P12:r40120529:d26",
    sourceParent := 12,
    targetParent := 20,
    valuation := 0,
    gainNum := 94351,
    gainDen := 11914377,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P12:r40120529:d26",
    gainNum := 94351,
    gainDen := 11914377,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "0a03a75ffa7b535469cdd6fbea8786ddc31811b37b484d46de3e1d5bf66d2fb2"
},
  {
  nodeId := "s3:s3_frontier:636df689c7ad1123",
  branchId := "P5:r21817285:d25",
  sourceParent := 5,
  targetParent := 30,
  valuation := 6,
  gainNum := 329,
  gainDen := 2907498437,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P5:r21817285:d25",
    sourceParent := 5,
    targetParent := 30,
    valuation := 6,
    branchResidue := 21817285,
    branchDepth := 25,
    sourceModulus := 33554432,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P5:r21817285:d25",
    sourceParent := 5,
    targetParent := 30,
    valuation := 6,
    gainNum := 329,
    gainDen := 2907498437,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P5:r21817285:d25",
    gainNum := 329,
    gainDen := 2907498437,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "acac93bc42d9289a9c39853f49bec17c7a8f18e7222d96cb8756b3b4193d5b8b"
},
  {
  nodeId := "s3:s3_frontier:6379870109783872",
  branchId := "P13:r33705691:d26",
  sourceParent := 13,
  targetParent := 19,
  valuation := 0,
  gainNum := 800755,
  gainDen := 33705691,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P13:r33705691:d26",
    sourceParent := 13,
    targetParent := 19,
    valuation := 0,
    branchResidue := 33705691,
    branchDepth := 26,
    sourceModulus := 67108864,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P13:r33705691:d26",
    sourceParent := 13,
    targetParent := 19,
    valuation := 0,
    gainNum := 800755,
    gainDen := 33705691,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P13:r33705691:d26",
    gainNum := 800755,
    gainDen := 33705691,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "5feab574989826f1e64f33a9ffe56c5248934fa6f65d251d18ee9df9b349dc47"
},
  {
  nodeId := "s3:s3_frontier:661d2adead250775",
  branchId := "P15:r26510867:d25",
  sourceParent := 15,
  targetParent := 22,
  valuation := 1,
  gainNum := 5668431,
  gainDen := 26510867,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P15:r26510867:d25",
    sourceParent := 15,
    targetParent := 22,
    valuation := 1,
    branchResidue := 26510867,
    branchDepth := 25,
    sourceModulus := 33554432,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P15:r26510867:d25",
    sourceParent := 15,
    targetParent := 22,
    valuation := 1,
    gainNum := 5668431,
    gainDen := 26510867,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P15:r26510867:d25",
    gainNum := 5668431,
    gainDen := 26510867,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "3c217f995938691924598383465a8f51d928f6bc333e956ac09d0925de153b14"
},
  {
  nodeId := "s3:s3_frontier:66f1e017a3d8b5dc",
  branchId := "P8:r25540441:d25",
  sourceParent := 8,
  targetParent := 23,
  valuation := 1,
  gainNum := 2497,
  gainDen := 25540441,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P8:r25540441:d25",
    sourceParent := 8,
    targetParent := 23,
    valuation := 1,
    branchResidue := 25540441,
    branchDepth := 25,
    sourceModulus := 33554432,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P8:r25540441:d25",
    sourceParent := 8,
    targetParent := 23,
    valuation := 1,
    gainNum := 2497,
    gainDen := 25540441,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P8:r25540441:d25",
    gainNum := 2497,
    gainDen := 25540441,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "3e4cf9a5791fa457ab184f0858c056b2309f4ae4451ae2b1681db8bcec4ec9c5"
},
  {
  nodeId := "s3:s3_frontier:67a5709cd5fb9830",
  branchId := "P13:r33705691:d26",
  sourceParent := 13,
  targetParent := 21,
  valuation := 2,
  gainNum := 1395931,
  gainDen := 235032283,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P13:r33705691:d26",
    sourceParent := 13,
    targetParent := 21,
    valuation := 2,
    branchResidue := 33705691,
    branchDepth := 26,
    sourceModulus := 67108864,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P13:r33705691:d26",
    sourceParent := 13,
    targetParent := 21,
    valuation := 2,
    gainNum := 1395931,
    gainDen := 235032283,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P13:r33705691:d26",
    gainNum := 1395931,
    gainDen := 235032283,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "5aa8c958354638d7d4682c0be7001f159d68d53c0add6173d1b3e1b7ee57c8f3"
},
  {
  nodeId := "s3:s3_frontier:6c78a40e991c2af6",
  branchId := "P9:r53252723:d26",
  sourceParent := 9,
  targetParent := 28,
  valuation := 5,
  gainNum := 39239,
  gainDen := 4281111155,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P9:r53252723:d26",
    sourceParent := 9,
    targetParent := 28,
    valuation := 5,
    branchResidue := 53252723,
    branchDepth := 26,
    sourceModulus := 67108864,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P9:r53252723:d26",
    sourceParent := 9,
    targetParent := 28,
    valuation := 5,
    gainNum := 39239,
    gainDen := 4281111155,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P9:r53252723:d26",
    gainNum := 39239,
    gainDen := 4281111155,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "025f09b7b073cbe5094adc4d74a2a0778c0f18596ab84a5b65f10b65837c5cdf"
},
  {
  nodeId := "s3:s3_frontier:6e6013ac60d59ea9",
  branchId := "P11:r53252723:d26",
  sourceParent := 11,
  targetParent := 27,
  valuation := 7,
  gainNum := 4889,
  gainDen := 237069723,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P11:r53252723:d26",
    sourceParent := 11,
    targetParent := 27,
    valuation := 7,
    branchResidue := 53252723,
    branchDepth := 26,
    sourceModulus := 67108864,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P11:r53252723:d26",
    sourceParent := 11,
    targetParent := 27,
    valuation := 7,
    gainNum := 4889,
    gainDen := 237069723,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P11:r53252723:d26",
    gainNum := 4889,
    gainDen := 237069723,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "14d879756307ce7cf4c04df2504b69c02ade373a421fc18afefdcd842c0b1f48"
},
  {
  nodeId := "s3:s3_frontier:6e6c3a1b845789a6",
  branchId := "P12:r43176689:d26",
  sourceParent := 12,
  targetParent := 26,
  valuation := 5,
  gainNum := 10685,
  gainDen := 43176689,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P12:r43176689:d26",
    sourceParent := 12,
    targetParent := 26,
    valuation := 5,
    branchResidue := 43176689,
    branchDepth := 26,
    sourceModulus := 67108864,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P12:r43176689:d26",
    sourceParent := 12,
    targetParent := 26,
    valuation := 5,
    gainNum := 10685,
    gainDen := 43176689,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P12:r43176689:d26",
    gainNum := 10685,
    gainDen := 43176689,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "4af475a2cf1dbb2611189f96e035e1cc5db3a086a9ac9f1ef280a21ea645b72c"
},
  {
  nodeId := "s3:s3_frontier:6ed787fd3695d327",
  branchId := "P14:r9876937:d24",
  sourceParent := 14,
  targetParent := 20,
  valuation := 4,
  gainNum := 1371729,
  gainDen := 76985801,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P14:r9876937:d24",
    sourceParent := 14,
    targetParent := 20,
    valuation := 4,
    branchResidue := 9876937,
    branchDepth := 24,
    sourceModulus := 16777216,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P14:r9876937:d24",
    sourceParent := 14,
    targetParent := 20,
    valuation := 4,
    gainNum := 1371729,
    gainDen := 76985801,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P14:r9876937:d24",
    gainNum := 1371729,
    gainDen := 76985801,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "dbec16d2f830029a168e81b7d85784e45ac51f3f732032bf29490165106805e9"
},
  {
  nodeId := "s3:s3_frontier:6facfc346df1c127",
  branchId := "P12:r62628045:d26",
  sourceParent := 12,
  targetParent := 26,
  valuation := 2,
  gainNum := 1054011,
  gainDen := 532390093,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P12:r62628045:d26",
    sourceParent := 12,
    targetParent := 26,
    valuation := 2,
    branchResidue := 62628045,
    branchDepth := 26,
    sourceModulus := 67108864,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P12:r62628045:d26",
    sourceParent := 12,
    targetParent := 26,
    valuation := 2,
    gainNum := 1054011,
    gainDen := 532390093,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P12:r62628045:d26",
    gainNum := 1054011,
    gainDen := 532390093,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "1fc078090ba9c2bf0e7a97e02ea0d170369194ca6754da0c7f4f33da8603e8ac"
},
  {
  nodeId := "s3:s3_frontier:7063699c40446194",
  branchId := "P12:r34008209:d26",
  sourceParent := 12,
  targetParent := 21,
  valuation := 2,
  gainNum := 333049,
  gainDen := 168225937,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P12:r34008209:d26",
    sourceParent := 12,
    targetParent := 21,
    valuation := 2,
    branchResidue := 34008209,
    branchDepth := 26,
    sourceModulus := 67108864,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P12:r34008209:d26",
    sourceParent := 12,
    targetParent := 21,
    valuation := 2,
    gainNum := 333049,
    gainDen := 168225937,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P12:r34008209:d26",
    gainNum := 333049,
    gainDen := 168225937,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "f9d6ae84782cd8745adedd4962bfc7111b9671a3b8e1c6a980f9f588ebcacb13"
},
  {
  nodeId := "s3:s3_frontier:71399d21ef13b898",
  branchId := "P12:r62628045:d26",
  sourceParent := 12,
  targetParent := 30,
  valuation := 6,
  gainNum := 77317,
  gainDen := 624855791,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P12:r62628045:d26",
    sourceParent := 12,
    targetParent := 30,
    valuation := 6,
    branchResidue := 62628045,
    branchDepth := 26,
    sourceModulus := 67108864,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P12:r62628045:d26",
    sourceParent := 12,
    targetParent := 30,
    valuation := 6,
    gainNum := 77317,
    gainDen := 624855791,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P12:r62628045:d26",
    gainNum := 77317,
    gainDen := 624855791,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "1154d320696e94c32df424e08b4d89d0f4042eb5a782ebff44f4e6e95e89c229"
},
  {
  nodeId := "s3:s3_frontier:71d6f4ba7af95860",
  branchId := "P14:r23693441:d25",
  sourceParent := 14,
  targetParent := 27,
  valuation := 5,
  gainNum := 9073609,
  gainDen := 2036959361,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P14:r23693441:d25",
    sourceParent := 14,
    targetParent := 27,
    valuation := 5,
    branchResidue := 23693441,
    branchDepth := 25,
    sourceModulus := 33554432,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P14:r23693441:d25",
    sourceParent := 14,
    targetParent := 27,
    valuation := 5,
    gainNum := 9073609,
    gainDen := 2036959361,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P14:r23693441:d25",
    gainNum := 9073609,
    gainDen := 2036959361,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "fea61e7d386ec9c64f32004c41e78921f87e8b45a10c6ad4195d94e2acfb3925"
},
  {
  nodeId := "s3:s3_frontier:71e558e716b18e81",
  branchId := "P5:r21817285:d25",
  sourceParent := 5,
  targetParent := 24,
  valuation := 0,
  gainNum := 401,
  gainDen := 55371717,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P5:r21817285:d25",
    sourceParent := 5,
    targetParent := 24,
    valuation := 0,
    branchResidue := 21817285,
    branchDepth := 25,
    sourceModulus := 33554432,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P5:r21817285:d25",
    sourceParent := 5,
    targetParent := 24,
    valuation := 0,
    gainNum := 401,
    gainDen := 55371717,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P5:r21817285:d25",
    gainNum := 401,
    gainDen := 55371717,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "749cc7cde9dfaf117194cf831784007fbe689b516a49cae64c7e27e3b7173191"
},
  {
  nodeId := "s3:s3_frontier:7200b983f7d15441",
  branchId := "P8:r39706845:d26",
  sourceParent := 8,
  targetParent := 29,
  valuation := 5,
  gainNum := 3731,
  gainDen := 1221195167,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P8:r39706845:d26",
    sourceParent := 8,
    targetParent := 29,
    valuation := 5,
    branchResidue := 39706845,
    branchDepth := 26,
    sourceModulus := 67108864,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P8:r39706845:d26",
    sourceParent := 8,
    targetParent := 29,
    valuation := 5,
    gainNum := 3731,
    gainDen := 1221195167,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P8:r39706845:d26",
    gainNum := 3731,
    gainDen := 1221195167,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "becf8b2a60f42de2668e048aba7cec259d85b2770a0343b46b756c28b7debea7"
},
  {
  nodeId := "s3:s3_frontier:723135dd408526a6",
  branchId := "P14:r32145719:d25",
  sourceParent := 14,
  targetParent := 26,
  valuation := 2,
  gainNum := 8319995,
  gainDen := 233472311,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P14:r32145719:d25",
    sourceParent := 14,
    targetParent := 26,
    valuation := 2,
    branchResidue := 32145719,
    branchDepth := 25,
    sourceModulus := 33554432,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P14:r32145719:d25",
    sourceParent := 14,
    targetParent := 26,
    valuation := 2,
    gainNum := 8319995,
    gainDen := 233472311,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P14:r32145719:d25",
    gainNum := 8319995,
    gainDen := 233472311,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "529fdbde9d5feedd817548ebd9912d521d4975355b80454df5ce91d5f541f808"
},
  {
  nodeId := "s3:s3_frontier:74466811a0f40e7e",
  branchId := "P8:r64316497:d26",
  sourceParent := 8,
  targetParent := 28,
  valuation := 6,
  gainNum := 5019,
  gainDen := 3285541969,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P8:r64316497:d26",
    sourceParent := 8,
    targetParent := 28,
    valuation := 6,
    branchResidue := 64316497,
    branchDepth := 26,
    sourceModulus := 67108864,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P8:r64316497:d26",
    sourceParent := 8,
    targetParent := 28,
    valuation := 6,
    gainNum := 5019,
    gainDen := 3285541969,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P8:r64316497:d26",
    gainNum := 5019,
    gainDen := 3285541969,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "12ba6fec4fa64644bd6f1beb930202d9a7ff351be176b2fb361bec846ba1ec96"
},
  {
  nodeId := "s3:s3_frontier:776068b77e3ac1e0",
  branchId := "P7:r9512459:d24",
  sourceParent := 7,
  targetParent := 27,
  valuation := 6,
  gainNum := 1933,
  gainDen := 949036555,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P7:r9512459:d24",
    sourceParent := 7,
    targetParent := 27,
    valuation := 6,
    branchResidue := 9512459,
    branchDepth := 24,
    sourceModulus := 16777216,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P7:r9512459:d24",
    sourceParent := 7,
    targetParent := 27,
    valuation := 6,
    gainNum := 1933,
    gainDen := 949036555,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P7:r9512459:d24",
    gainNum := 1933,
    gainDen := 949036555,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "594e9c1b62daa0925e9770ed06a25fea20f8e6ec51c97c54ad358790ff0d47e4"
},
  {
  nodeId := "s3:s3_frontier:79d7c90032686174",
  branchId := "P12:r62628045:d26",
  sourceParent := 12,
  targetParent := 24,
  valuation := 0,
  gainNum := 165319,
  gainDen := 20876015,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P12:r62628045:d26",
    sourceParent := 12,
    targetParent := 24,
    valuation := 0,
    branchResidue := 62628045,
    branchDepth := 26,
    sourceModulus := 67108864,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P12:r62628045:d26",
    sourceParent := 12,
    targetParent := 24,
    valuation := 0,
    gainNum := 165319,
    gainDen := 20876015,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P12:r62628045:d26",
    gainNum := 165319,
    gainDen := 20876015,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "bc3b9ac6a052c7075e6289581123b2027b08a8c9754879969b0d814f0831c1d3"
},
  {
  nodeId := "s3:s3_frontier:7b16cceccca0784e",
  branchId := "P13:r36761851:d26",
  sourceParent := 13,
  targetParent := 22,
  valuation := 1,
  gainNum := 2828165,
  gainDen := 238088443,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P13:r36761851:d26",
    sourceParent := 13,
    targetParent := 22,
    valuation := 1,
    branchResidue := 36761851,
    branchDepth := 26,
    sourceModulus := 67108864,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P13:r36761851:d26",
    sourceParent := 13,
    targetParent := 22,
    valuation := 1,
    gainNum := 2828165,
    gainDen := 238088443,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P13:r36761851:d26",
    gainNum := 2828165,
    gainDen := 238088443,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "e83c396789210a51ab5a50aa9dcf6f423c0c623b7e530556b57dce022bfc7037"
},
  {
  nodeId := "s3:s3_frontier:7ce126d6d458cb34",
  branchId := "P14:r9876937:d24",
  sourceParent := 14,
  targetParent := 23,
  valuation := 7,
  gainNum := 9139533,
  gainDen := 4103517641,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P14:r9876937:d24",
    sourceParent := 14,
    targetParent := 23,
    valuation := 7,
    branchResidue := 9876937,
    branchDepth := 24,
    sourceModulus := 16777216,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P14:r9876937:d24",
    sourceParent := 14,
    targetParent := 23,
    valuation := 7,
    gainNum := 9139533,
    gainDen := 4103517641,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P14:r9876937:d24",
    gainNum := 9139533,
    gainDen := 4103517641,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "074157c3f08a46ac780c07fb01d1d483e8c53c47d76f75fcb70d3a66d29c16c8"
},
  {
  nodeId := "s3:s3_frontier:7ef7637599045577",
  branchId := "P10:r53045881:d26",
  sourceParent := 10,
  targetParent := 21,
  valuation := 0,
  gainNum := 46675,
  gainDen := 53045881,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P10:r53045881:d26",
    sourceParent := 10,
    targetParent := 21,
    valuation := 0,
    branchResidue := 53045881,
    branchDepth := 26,
    sourceModulus := 67108864,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P10:r53045881:d26",
    sourceParent := 10,
    targetParent := 21,
    valuation := 0,
    gainNum := 46675,
    gainDen := 53045881,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P10:r53045881:d26",
    gainNum := 46675,
    gainDen := 53045881,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "6f0ea69830e21cd5b9c061a7c161311324d621b544c2a73410ef5b85ac4a21d3"
},
  {
  nodeId := "s3:s3_frontier:7f3137460f73732a",
  branchId := "P10:r40120529:d26",
  sourceParent := 10,
  targetParent := 24,
  valuation := 1,
  gainNum := 17651,
  gainDen := 40120529,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P10:r40120529:d26",
    sourceParent := 10,
    targetParent := 24,
    valuation := 1,
    branchResidue := 40120529,
    branchDepth := 26,
    sourceModulus := 67108864,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P10:r40120529:d26",
    sourceParent := 10,
    targetParent := 24,
    valuation := 1,
    gainNum := 17651,
    gainDen := 40120529,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P10:r40120529:d26",
    gainNum := 17651,
    gainDen := 40120529,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "c0e0206fd1eb495d45d087c7666933576fdf0002d129c26e8f03b201760e28af"
},
  {
  nodeId := "s3:s3_frontier:81530fe891382347",
  branchId := "P12:r43176689:d26",
  sourceParent := 12,
  targetParent := 28,
  valuation := 7,
  gainNum := 932693,
  gainDen := 15075562225,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P12:r43176689:d26",
    sourceParent := 12,
    targetParent := 28,
    valuation := 7,
    branchResidue := 43176689,
    branchDepth := 26,
    sourceModulus := 67108864,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P12:r43176689:d26",
    sourceParent := 12,
    targetParent := 28,
    valuation := 7,
    gainNum := 932693,
    gainDen := 15075562225,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P12:r43176689:d26",
    gainNum := 932693,
    gainDen := 15075562225,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "f51ef9475846a35df91e46f2b97c6e680cbba0cb56b60c26c46223765a8d0934"
},
  {
  nodeId := "s3:s3_frontier:8319b0dfc54ed83c",
  branchId := "P10:r26781493:d25",
  sourceParent := 10,
  targetParent := 29,
  valuation := 6,
  gainNum := 50559,
  gainDen := 1838720821,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P10:r26781493:d25",
    sourceParent := 10,
    targetParent := 29,
    valuation := 6,
    branchResidue := 26781493,
    branchDepth := 25,
    sourceModulus := 33554432,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P10:r26781493:d25",
    sourceParent := 10,
    targetParent := 29,
    valuation := 6,
    gainNum := 50559,
    gainDen := 1838720821,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P10:r26781493:d25",
    gainNum := 50559,
    gainDen := 1838720821,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "1bafdf674bbc7ef3760410be5d81c34b835d904132d3b058f11b16050512ebc0"
},
  {
  nodeId := "s3:s3_frontier:8516c074e54383e4",
  branchId := "P9:r26781493:d25",
  sourceParent := 9,
  targetParent := 30,
  valuation := 6,
  gainNum := 16853,
  gainDen := 1838720821,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P9:r26781493:d25",
    sourceParent := 9,
    targetParent := 30,
    valuation := 6,
    branchResidue := 26781493,
    branchDepth := 25,
    sourceModulus := 33554432,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P9:r26781493:d25",
    sourceParent := 9,
    targetParent := 30,
    valuation := 6,
    gainNum := 16853,
    gainDen := 1838720821,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P9:r26781493:d25",
    gainNum := 16853,
    gainDen := 1838720821,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "edc6dd2868e230feebbb62679289e46dbf859a67f18db8b1efc3d6343e781cbe"
},
  {
  nodeId := "s3:s3_frontier:8531ab50b2be6800",
  branchId := "P6:r52011671:d26",
  sourceParent := 6,
  targetParent := 25,
  valuation := 0,
  gainNum := 565,
  gainDen := 52011671,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P6:r52011671:d26",
    sourceParent := 6,
    targetParent := 25,
    valuation := 0,
    branchResidue := 52011671,
    branchDepth := 26,
    sourceModulus := 67108864,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P6:r52011671:d26",
    sourceParent := 6,
    targetParent := 25,
    valuation := 0,
    gainNum := 565,
    gainDen := 52011671,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P6:r52011671:d26",
    gainNum := 565,
    gainDen := 52011671,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "116e55839650a51c9d504258d1fb136a8e46f722724463aacc95051b2e2aefdf"
},
  {
  nodeId := "s3:s3_frontier:8b5fafd89f892a80",
  branchId := "P10:r53666407:d26",
  sourceParent := 10,
  targetParent := 25,
  valuation := 0,
  gainNum := 47221,
  gainDen := 53666407,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P10:r53666407:d26",
    sourceParent := 10,
    targetParent := 25,
    valuation := 0,
    branchResidue := 53666407,
    branchDepth := 26,
    sourceModulus := 67108864,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P10:r53666407:d26",
    sourceParent := 10,
    targetParent := 25,
    valuation := 0,
    gainNum := 47221,
    gainDen := 53666407,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P10:r53666407:d26",
    gainNum := 47221,
    gainDen := 53666407,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "3895592b5f1cad45be762fcb75dcd18fc1e7b2deb2471581aedb68561b911e94"
},
  {
  nodeId := "s3:s3_frontier:8c7fd4867f378aa1",
  branchId := "P10:r26781493:d25",
  sourceParent := 10,
  targetParent := 28,
  valuation := 5,
  gainNum := 14023,
  gainDen := 254992999,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P10:r26781493:d25",
    sourceParent := 10,
    targetParent := 28,
    valuation := 5,
    branchResidue := 26781493,
    branchDepth := 25,
    sourceModulus := 33554432,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P10:r26781493:d25",
    sourceParent := 10,
    targetParent := 28,
    valuation := 5,
    gainNum := 14023,
    gainDen := 254992999,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P10:r26781493:d25",
    gainNum := 14023,
    gainDen := 254992999,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "174c5ce91ab23e2441453274abfff3e31c73d97551e599b5acd8a888a457a419"
},
  {
  nodeId := "s3:s3_frontier:8d674a3606920233",
  branchId := "P13:r20876015:d25",
  sourceParent := 13,
  targetParent := 29,
  valuation := 6,
  gainNum := 2058225,
  gainDen := 2772339439,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P13:r20876015:d25",
    sourceParent := 13,
    targetParent := 29,
    valuation := 6,
    branchResidue := 20876015,
    branchDepth := 25,
    sourceModulus := 33554432,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P13:r20876015:d25",
    sourceParent := 13,
    targetParent := 29,
    valuation := 6,
    gainNum := 2058225,
    gainDen := 2772339439,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P13:r20876015:d25",
    gainNum := 2058225,
    gainDen := 2772339439,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "05ea4dab8b590724b12755df74b765d3b3ee4836997e7a2a7bb13e268ad87309"
},
  {
  nodeId := "s3:s3_frontier:8e69fd4723ea3f4c",
  branchId := "P8:r25540441:d25",
  sourceParent := 8,
  targetParent := 28,
  valuation := 6,
  gainNum := 12995,
  gainDen := 4253398873,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P8:r25540441:d25",
    sourceParent := 8,
    targetParent := 28,
    valuation := 6,
    branchResidue := 25540441,
    branchDepth := 25,
    sourceModulus := 33554432,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P8:r25540441:d25",
    sourceParent := 8,
    targetParent := 28,
    valuation := 6,
    gainNum := 12995,
    gainDen := 4253398873,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P8:r25540441:d25",
    gainNum := 12995,
    gainDen := 4253398873,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "6c4134ee93a8bb767543e53c5701b702bc64cabbaaf04533fa01f8909fbb008b"
},
  {
  nodeId := "s3:s3_frontier:8ff22d37d0413acd",
  branchId := "P7:r9512459:d24",
  sourceParent := 7,
  targetParent := 24,
  valuation := 3,
  gainNum := 155,
  gainDen := 9512459,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P7:r9512459:d24",
    sourceParent := 7,
    targetParent := 24,
    valuation := 3,
    branchResidue := 9512459,
    branchDepth := 24,
    sourceModulus := 16777216,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P7:r9512459:d24",
    sourceParent := 7,
    targetParent := 24,
    valuation := 3,
    gainNum := 155,
    gainDen := 9512459,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P7:r9512459:d24",
    gainNum := 155,
    gainDen := 9512459,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "c04e7ea2d9c562d03590008c185ad0855db20c1dc2511bb426026bbcb7ffa7e6"
},
  {
  nodeId := "s3:s3_frontier:902c3f329029d36a",
  branchId := "P14:r23693441:d25",
  sourceParent := 14,
  targetParent := 29,
  valuation := 7,
  gainNum := 5855629,
  gainDen := 5258184833,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P14:r23693441:d25",
    sourceParent := 14,
    targetParent := 29,
    valuation := 7,
    branchResidue := 23693441,
    branchDepth := 25,
    sourceModulus := 33554432,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P14:r23693441:d25",
    sourceParent := 14,
    targetParent := 29,
    valuation := 7,
    gainNum := 5855629,
    gainDen := 5258184833,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P14:r23693441:d25",
    gainNum := 5855629,
    gainDen := 5258184833,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "a456e8159f7259cfab6a349420f0d6ebc6c28739dcc67718225d822b5672ec7a"
},
  {
  nodeId := "s3:s3_frontier:93cb24bafb0c0951",
  branchId := "P13:r35743131:d26",
  sourceParent := 13,
  targetParent := 22,
  valuation := 2,
  gainNum := 3002355,
  gainDen := 505505179,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P13:r35743131:d26",
    sourceParent := 13,
    targetParent := 22,
    valuation := 2,
    branchResidue := 35743131,
    branchDepth := 26,
    sourceModulus := 67108864,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P13:r35743131:d26",
    sourceParent := 13,
    targetParent := 22,
    valuation := 2,
    gainNum := 3002355,
    gainDen := 505505179,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P13:r35743131:d26",
    gainNum := 3002355,
    gainDen := 505505179,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "765276a5000976ea811aed608609a983fef47cbe71de6d75c49d1dddf07b3243"
},
  {
  nodeId := "s3:s3_frontier:94febb0f8fdd0a63",
  branchId := "P15:r41027779:d26",
  sourceParent := 15,
  targetParent := 21,
  valuation := 2,
  gainNum := 23716453,
  gainDen := 443680963,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P15:r41027779:d26",
    sourceParent := 15,
    targetParent := 21,
    valuation := 2,
    branchResidue := 41027779,
    branchDepth := 26,
    sourceModulus := 67108864,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P15:r41027779:d26",
    sourceParent := 15,
    targetParent := 21,
    valuation := 2,
    gainNum := 23716453,
    gainDen := 443680963,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P15:r41027779:d26",
    gainNum := 23716453,
    gainDen := 443680963,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "7c9c80754daebc8406c20b01a80fdb4a08971077b2f28603aba49e4c7437175a"
},
  {
  nodeId := "s3:s3_frontier:9691bdab3143e352",
  branchId := "P13:r35743131:d26",
  sourceParent := 13,
  targetParent := 24,
  valuation := 4,
  gainNum := 1946331,
  gainDen := 1310811547,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P13:r35743131:d26",
    sourceParent := 13,
    targetParent := 24,
    valuation := 4,
    branchResidue := 35743131,
    branchDepth := 26,
    sourceModulus := 67108864,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P13:r35743131:d26",
    sourceParent := 13,
    targetParent := 24,
    valuation := 4,
    gainNum := 1946331,
    gainDen := 1310811547,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P13:r35743131:d26",
    gainNum := 1946331,
    gainDen := 1310811547,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "e4c2abf6dd74748cec3cb2cd701f30a467ff35d91dbf2385ed11f9adbb6203dd"
},
  {
  nodeId := "s3:s3_frontier:982abf74ce1c10cb",
  branchId := "P16:r23693441:d25",
  sourceParent := 16,
  targetParent := 26,
  valuation := 7,
  gainNum := 52700661,
  gainDen := 5258184833,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P16:r23693441:d25",
    sourceParent := 16,
    targetParent := 26,
    valuation := 7,
    branchResidue := 23693441,
    branchDepth := 25,
    sourceModulus := 33554432,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P16:r23693441:d25",
    sourceParent := 16,
    targetParent := 26,
    valuation := 7,
    gainNum := 52700661,
    gainDen := 5258184833,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P16:r23693441:d25",
    gainNum := 52700661,
    gainDen := 5258184833,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "6905f8cc04f5375d67acb79b43bff802749fce94625044dd962e38f35f45ec86"
},
  {
  nodeId := "s3:s3_frontier:9be24f9c565419bd",
  branchId := "P12:r40120529:d26",
  sourceParent := 12,
  targetParent := 27,
  valuation := 7,
  gainNum := 4889,
  gainDen := 79023241,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P12:r40120529:d26",
    sourceParent := 12,
    targetParent := 27,
    valuation := 7,
    branchResidue := 40120529,
    branchDepth := 26,
    sourceModulus := 67108864,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P12:r40120529:d26",
    sourceParent := 12,
    targetParent := 27,
    valuation := 7,
    gainNum := 4889,
    gainDen := 79023241,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P12:r40120529:d26",
    gainNum := 4889,
    gainDen := 79023241,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "9631589ea16ffabfb58528e9ac4fcd8beceec0f89e8b2b9a9cf05245619d7f67"
},
  {
  nodeId := "s3:s3_frontier:9c97294309c04b0d",
  branchId := "P7:r9512459:d24",
  sourceParent := 7,
  targetParent := 21,
  valuation := 0,
  gainNum := 3427,
  gainDen := 26289675,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P7:r9512459:d24",
    sourceParent := 7,
    targetParent := 21,
    valuation := 0,
    branchResidue := 9512459,
    branchDepth := 24,
    sourceModulus := 16777216,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P7:r9512459:d24",
    sourceParent := 7,
    targetParent := 21,
    valuation := 0,
    gainNum := 3427,
    gainDen := 26289675,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P7:r9512459:d24",
    gainNum := 3427,
    gainDen := 26289675,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "ae6e1b79483f8e6e8e5b210fa04c1fc39508787c777a1e1f92f798c7e91e5fef"
},
  {
  nodeId := "s3:s3_frontier:a03d44cfe62da8ea",
  branchId := "P13:r37271211:d26",
  sourceParent := 13,
  targetParent := 29,
  valuation := 7,
  gainNum := 1377039,
  gainDen := 7419246251,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P13:r37271211:d26",
    sourceParent := 13,
    targetParent := 29,
    valuation := 7,
    branchResidue := 37271211,
    branchDepth := 26,
    sourceModulus := 67108864,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P13:r37271211:d26",
    sourceParent := 13,
    targetParent := 29,
    valuation := 7,
    gainNum := 1377039,
    gainDen := 7419246251,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P13:r37271211:d26",
    gainNum := 1377039,
    gainDen := 7419246251,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "5b949923e394e3e3dfca77dc02b8782c3ad47afc3121488f420288a39ce52040"
},
  {
  nodeId := "s3:s3_frontier:a0e016f1404f38dc",
  branchId := "P13:r20876015:d25",
  sourceParent := 13,
  targetParent := 24,
  valuation := 1,
  gainNum := 495957,
  gainDen := 20876015,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P13:r20876015:d25",
    sourceParent := 13,
    targetParent := 24,
    valuation := 1,
    branchResidue := 20876015,
    branchDepth := 25,
    sourceModulus := 33554432,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P13:r20876015:d25",
    sourceParent := 13,
    targetParent := 24,
    valuation := 1,
    gainNum := 495957,
    gainDen := 20876015,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P13:r20876015:d25",
    gainNum := 495957,
    gainDen := 20876015,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "877b8fd462b5d81e5285d9139887997ee423bd3bd6a757af820627e3983d16d0"
},
  {
  nodeId := "s3:s3_frontier:a10fd251086527d4",
  branchId := "P12:r62628045:d26",
  sourceParent := 12,
  targetParent := 27,
  valuation := 3,
  gainNum := 87095,
  gainDen := 87984879,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P12:r62628045:d26",
    sourceParent := 12,
    targetParent := 27,
    valuation := 3,
    branchResidue := 62628045,
    branchDepth := 26,
    sourceModulus := 67108864,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P12:r62628045:d26",
    sourceParent := 12,
    targetParent := 27,
    valuation := 3,
    gainNum := 87095,
    gainDen := 87984879,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P12:r62628045:d26",
    gainNum := 87095,
    gainDen := 87984879,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "6986e1c65e2022df04b74592da6a11d194cf305738e67d32124c10aee71ccd62"
},
  {
  nodeId := "s3:s3_frontier:a1636f598068df23",
  branchId := "P13:r36761851:d26",
  sourceParent := 13,
  targetParent := 24,
  valuation := 3,
  gainNum := 87095,
  gainDen := 29328293,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P13:r36761851:d26",
    sourceParent := 13,
    targetParent := 24,
    valuation := 3,
    branchResidue := 36761851,
    branchDepth := 26,
    sourceModulus := 67108864,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P13:r36761851:d26",
    sourceParent := 13,
    targetParent := 24,
    valuation := 3,
    gainNum := 87095,
    gainDen := 29328293,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P13:r36761851:d26",
    gainNum := 87095,
    gainDen := 29328293,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "7613f95d08fe6fa60b1a50cbf3706d6de603c7ca14e4f3f8a329155e4fe43aff"
},
  {
  nodeId := "s3:s3_frontier:a4e710fd08bfb04b",
  branchId := "P6:r28537377:d25",
  sourceParent := 6,
  targetParent := 29,
  valuation := 7,
  gainNum := 43,
  gainDen := 253338263,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P6:r28537377:d25",
    sourceParent := 6,
    targetParent := 29,
    valuation := 7,
    branchResidue := 28537377,
    branchDepth := 25,
    sourceModulus := 33554432,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P6:r28537377:d25",
    sourceParent := 6,
    targetParent := 29,
    valuation := 7,
    gainNum := 43,
    gainDen := 253338263,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P6:r28537377:d25",
    gainNum := 43,
    gainDen := 253338263,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "28a538a9477845855ed7f3160520b8875abb2ed206f3f3e320ac86bad60356c0"
},
  {
  nodeId := "s3:s3_frontier:a673350b34fff169",
  branchId := "P15:r18997731:d25",
  sourceParent := 15,
  targetParent := 21,
  valuation := 1,
  gainNum := 4062007,
  gainDen := 18997731,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P15:r18997731:d25",
    sourceParent := 15,
    targetParent := 21,
    valuation := 1,
    branchResidue := 18997731,
    branchDepth := 25,
    sourceModulus := 33554432,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P15:r18997731:d25",
    sourceParent := 15,
    targetParent := 21,
    valuation := 1,
    gainNum := 4062007,
    gainDen := 18997731,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P15:r18997731:d25",
    gainNum := 4062007,
    gainDen := 18997731,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "8ebf66c7a467cd727ab4bf185b3b110fe59124711672ef76b0c70de08149f318"
},
  {
  nodeId := "s3:s3_frontier:a7c4405b9c8fddcb",
  branchId := "P7:r52011671:d26",
  sourceParent := 7,
  targetParent := 27,
  valuation := 3,
  gainNum := 3219,
  gainDen := 790209175,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P7:r52011671:d26",
    sourceParent := 7,
    targetParent := 27,
    valuation := 3,
    branchResidue := 52011671,
    branchDepth := 26,
    sourceModulus := 67108864,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P7:r52011671:d26",
    sourceParent := 7,
    targetParent := 27,
    valuation := 3,
    gainNum := 3219,
    gainDen := 790209175,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P7:r52011671:d26",
    gainNum := 3219,
    gainDen := 790209175,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "a896a2c1e44b50035b1164344e8b24a655533752a63dab09e5347d096c244055"
},
  {
  nodeId := "s3:s3_frontier:a8109ab5742a0696",
  branchId := "P9:r66178075:d26",
  sourceParent := 9,
  targetParent := 29,
  valuation := 7,
  gainNum := 7719,
  gainDen := 3368678815,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P9:r66178075:d26",
    sourceParent := 9,
    targetParent := 29,
    valuation := 7,
    branchResidue := 66178075,
    branchDepth := 26,
    sourceModulus := 67108864,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P9:r66178075:d26",
    sourceParent := 9,
    targetParent := 29,
    valuation := 7,
    gainNum := 7719,
    gainDen := 3368678815,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P9:r66178075:d26",
    gainNum := 7719,
    gainDen := 3368678815,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "4ea99e5c704f412bae644d82342e20b5415b1669ea9764265e223fc7107fdcc2"
},
  {
  nodeId := "s3:s3_frontier:a88a5d9aa928a974",
  branchId := "P14:r55974473:d26",
  sourceParent := 14,
  targetParent := 26,
  valuation := 7,
  gainNum := 3581027,
  gainDen := 6431316553,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P14:r55974473:d26",
    sourceParent := 14,
    targetParent := 26,
    valuation := 7,
    branchResidue := 55974473,
    branchDepth := 26,
    sourceModulus := 67108864,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P14:r55974473:d26",
    sourceParent := 14,
    targetParent := 26,
    valuation := 7,
    gainNum := 3581027,
    gainDen := 6431316553,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P14:r55974473:d26",
    gainNum := 3581027,
    gainDen := 6431316553,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "321bde14d4bc68eb62cc9bd99f1b40d428ccbcaaa3960dcd5af5bce4ada74569"
},
  {
  nodeId := "s3:s3_frontier:aa0339dd7a74e457",
  branchId := "P14:r11914377:d24",
  sourceParent := 14,
  targetParent := 23,
  valuation := 5,
  gainNum := 261285,
  gainDen := 29328293,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P14:r11914377:d24",
    sourceParent := 14,
    targetParent := 23,
    valuation := 5,
    branchResidue := 11914377,
    branchDepth := 24,
    sourceModulus := 16777216,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P14:r11914377:d24",
    sourceParent := 14,
    targetParent := 23,
    valuation := 5,
    gainNum := 261285,
    gainDen := 29328293,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P14:r11914377:d24",
    gainNum := 261285,
    gainDen := 29328293,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "285e238703bfcc5bdf418e3e322562dc30bb5fcb5348cc651fb3845aec94d117"
},
  {
  nodeId := "s3:s3_frontier:aa42fdcb5d977d6b",
  branchId := "P12:r43176689:d26",
  sourceParent := 12,
  targetParent := 24,
  valuation := 3,
  gainNum := 574181,
  gainDen := 580047601,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P12:r43176689:d26",
    sourceParent := 12,
    targetParent := 24,
    valuation := 3,
    branchResidue := 43176689,
    branchDepth := 26,
    sourceModulus := 67108864,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P12:r43176689:d26",
    sourceParent := 12,
    targetParent := 24,
    valuation := 3,
    gainNum := 574181,
    gainDen := 580047601,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P12:r43176689:d26",
    gainNum := 574181,
    gainDen := 580047601,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "7fb92e4eefbe3ff2010a587c4a2c449fe23a48440648e61a5a2d71fb7f3882df"
},
  {
  nodeId := "s3:s3_frontier:ad293a621281ccd6",
  branchId := "P5:r21817285:d25",
  sourceParent := 5,
  targetParent := 25,
  valuation := 1,
  gainNum := 79,
  gainDen := 21817285,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P5:r21817285:d25",
    sourceParent := 5,
    targetParent := 25,
    valuation := 1,
    branchResidue := 21817285,
    branchDepth := 25,
    sourceModulus := 33554432,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P5:r21817285:d25",
    sourceParent := 5,
    targetParent := 25,
    valuation := 1,
    gainNum := 79,
    gainDen := 21817285,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P5:r21817285:d25",
    gainNum := 79,
    gainDen := 21817285,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "a57ccfd821629bcc14b01f8cb14fcb1865368e45acb0737f8638875ab8542e28"
},
  {
  nodeId := "s3:s3_frontier:adda704373553f90",
  branchId := "P7:r39706845:d26",
  sourceParent := 7,
  targetParent := 27,
  valuation := 2,
  gainNum := 1417,
  gainDen := 173924573,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P7:r39706845:d26",
    sourceParent := 7,
    targetParent := 27,
    valuation := 2,
    branchResidue := 39706845,
    branchDepth := 26,
    sourceModulus := 67108864,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P7:r39706845:d26",
    sourceParent := 7,
    targetParent := 27,
    valuation := 2,
    gainNum := 1417,
    gainDen := 173924573,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P7:r39706845:d26",
    gainNum := 1417,
    gainDen := 173924573,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "b820748b16430d79794dbe53470ba6d89567bd3c144ca08db904923107fb9797"
},
  {
  nodeId := "s3:s3_frontier:af98630ed63a21f3",
  branchId := "P6:r28537377:d25",
  sourceParent := 6,
  targetParent := 24,
  valuation := 2,
  gainNum := 155,
  gainDen := 28537377,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P6:r28537377:d25",
    sourceParent := 6,
    targetParent := 24,
    valuation := 2,
    branchResidue := 28537377,
    branchDepth := 25,
    sourceModulus := 33554432,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P6:r28537377:d25",
    sourceParent := 6,
    targetParent := 24,
    valuation := 2,
    gainNum := 155,
    gainDen := 28537377,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P6:r28537377:d25",
    gainNum := 155,
    gainDen := 28537377,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "60395f91022c667a9342793e0e9d7622667344e36a21e8f2f600f36b45c47e5a"
},
  {
  nodeId := "s3:s3_frontier:b027799942b46054",
  branchId := "P15:r3971459:d22",
  sourceParent := 15,
  targetParent := 21,
  valuation := 5,
  gainNum := 2533011,
  gainDen := 23693441,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P15:r3971459:d22",
    sourceParent := 15,
    targetParent := 21,
    valuation := 5,
    branchResidue := 3971459,
    branchDepth := 22,
    sourceModulus := 4194304,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P15:r3971459:d22",
    sourceParent := 15,
    targetParent := 21,
    valuation := 5,
    gainNum := 2533011,
    gainDen := 23693441,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P15:r3971459:d22",
    gainNum := 2533011,
    gainDen := 23693441,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "87cc41d00d76da271f15d9d101be3344edcc9ae8a01e150dfe3ca18288db651d"
},
  {
  nodeId := "s3:s3_frontier:b07b252fc163cb04",
  branchId := "P14:r9876937:d24",
  sourceParent := 14,
  targetParent := 19,
  valuation := 3,
  gainNum := 442731,
  gainDen := 12423737,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P14:r9876937:d24",
    sourceParent := 14,
    targetParent := 19,
    valuation := 3,
    branchResidue := 9876937,
    branchDepth := 24,
    sourceModulus := 16777216,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P14:r9876937:d24",
    sourceParent := 14,
    targetParent := 19,
    valuation := 3,
    gainNum := 442731,
    gainDen := 12423737,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P14:r9876937:d24",
    gainNum := 442731,
    gainDen := 12423737,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "16e8001571293be72c8d147b0ec5d504f5c5a8f5e4fc2f527970e107c88ce927"
},
  {
  nodeId := "s3:s3_frontier:b167e6ef5043debc",
  branchId := "P12:r44704769:d26",
  sourceParent := 12,
  targetParent := 28,
  valuation := 6,
  gainNum := 96873,
  gainDen := 782902273,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P12:r44704769:d26",
    sourceParent := 12,
    targetParent := 28,
    valuation := 6,
    branchResidue := 44704769,
    branchDepth := 26,
    sourceModulus := 67108864,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P12:r44704769:d26",
    sourceParent := 12,
    targetParent := 28,
    valuation := 6,
    gainNum := 96873,
    gainDen := 782902273,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P12:r44704769:d26",
    gainNum := 96873,
    gainDen := 782902273,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "b6a20006633a40e15b0e2467fd27e441db75efc928d83958b0a21cf6cd28c979"
},
  {
  nodeId := "s3:s3_frontier:b35596b5e92309a7",
  branchId := "P7:r39706845:d26",
  sourceParent := 7,
  targetParent := 26,
  valuation := 1,
  gainNum := 647,
  gainDen := 39706845,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P7:r39706845:d26",
    sourceParent := 7,
    targetParent := 26,
    valuation := 1,
    branchResidue := 39706845,
    branchDepth := 26,
    sourceModulus := 67108864,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P7:r39706845:d26",
    sourceParent := 7,
    targetParent := 26,
    valuation := 1,
    gainNum := 647,
    gainDen := 39706845,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P7:r39706845:d26",
    gainNum := 647,
    gainDen := 39706845,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "2a9576cda41d86e2d77bd25780ba6565e9c843a29b2cd5bb644ee7ffff5539c9"
},
  {
  nodeId := "s3:s3_frontier:b41c6abe582aee65",
  branchId := "P12:r43176689:d26",
  sourceParent := 12,
  targetParent := 22,
  valuation := 1,
  gainNum := 702401,
  gainDen := 177394417,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P12:r43176689:d26",
    sourceParent := 12,
    targetParent := 22,
    valuation := 1,
    branchResidue := 43176689,
    branchDepth := 26,
    sourceModulus := 67108864,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P12:r43176689:d26",
    sourceParent := 12,
    targetParent := 22,
    valuation := 1,
    gainNum := 702401,
    gainDen := 177394417,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P12:r43176689:d26",
    gainNum := 702401,
    gainDen := 177394417,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "df6941e082e7502838731c0a5a5b0ac2a3a08bd0cb34f231022e4561aa720d90"
},
  {
  nodeId := "s3:s3_frontier:b4608b1096a136ce",
  branchId := "P14:r32145719:d25",
  sourceParent := 14,
  targetParent := 30,
  valuation := 6,
  gainNum := 9189131,
  gainDen := 4125786423,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P14:r32145719:d25",
    sourceParent := 14,
    targetParent := 30,
    valuation := 6,
    branchResidue := 32145719,
    branchDepth := 25,
    sourceModulus := 33554432,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P14:r32145719:d25",
    sourceParent := 14,
    targetParent := 30,
    valuation := 6,
    gainNum := 9189131,
    gainDen := 4125786423,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P14:r32145719:d25",
    gainNum := 9189131,
    gainDen := 4125786423,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "b7df2d19663cc136ef45dc987f71f09b2931956b52ab66fea6f698dd018879d7"
},
  {
  nodeId := "s3:s3_frontier:b80c00a0f9057757",
  branchId := "P12:r40120529:d26",
  sourceParent := 12,
  targetParent := 24,
  valuation := 4,
  gainNum := 126207,
  gainDen := 254992999,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P12:r40120529:d26",
    sourceParent := 12,
    targetParent := 24,
    valuation := 4,
    branchResidue := 40120529,
    branchDepth := 26,
    sourceModulus := 67108864,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P12:r40120529:d26",
    sourceParent := 12,
    targetParent := 24,
    valuation := 4,
    gainNum := 126207,
    gainDen := 254992999,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P12:r40120529:d26",
    gainNum := 126207,
    gainDen := 254992999,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "981a0a95dfe8bbac3e3bbfaff6a1f8b8f474fcf88371904bcda5a77ad451cbfe"
},
  {
  nodeId := "s3:s3_frontier:ba196a26ec0dd893",
  branchId := "P17:r2110859:d22",
  sourceParent := 17,
  targetParent := 22,
  valuation := 5,
  gainNum := 66601085,
  gainDen := 69219723,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P17:r2110859:d22",
    sourceParent := 17,
    targetParent := 22,
    valuation := 5,
    branchResidue := 2110859,
    branchDepth := 22,
    sourceModulus := 4194304,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P17:r2110859:d22",
    sourceParent := 17,
    targetParent := 22,
    valuation := 5,
    gainNum := 66601085,
    gainDen := 69219723,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P17:r2110859:d22",
    gainNum := 66601085,
    gainDen := 69219723,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "d97f413be592291b6b602b0dea5bff6440450393cc68ead5679b148aceae7414"
},
  {
  nodeId := "s3:s3_frontier:ba61befb6a02c8b5",
  branchId := "P7:r58731763:d26",
  sourceParent := 7,
  targetParent := 25,
  valuation := 3,
  gainNum := 2973,
  gainDen := 729820403,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P7:r58731763:d26",
    sourceParent := 7,
    targetParent := 25,
    valuation := 3,
    branchResidue := 58731763,
    branchDepth := 26,
    sourceModulus := 67108864,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P7:r58731763:d26",
    sourceParent := 7,
    targetParent := 25,
    valuation := 3,
    gainNum := 2973,
    gainDen := 729820403,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P7:r58731763:d26",
    gainNum := 2973,
    gainDen := 729820403,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "ec049af627b4410e256ec7ea8b2f85a0106d9aff515c56d216e32de6080b4c04"
},
  {
  nodeId := "s3:s3_frontier:bdaf1ed0d75f3cbc",
  branchId := "P8:r39706845:d26",
  sourceParent := 8,
  targetParent := 30,
  valuation := 6,
  gainNum := 8877,
  gainDen := 5811069149,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P8:r39706845:d26",
    sourceParent := 8,
    targetParent := 30,
    valuation := 6,
    branchResidue := 39706845,
    branchDepth := 26,
    sourceModulus := 67108864,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P8:r39706845:d26",
    sourceParent := 8,
    targetParent := 30,
    valuation := 6,
    gainNum := 8877,
    gainDen := 5811069149,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P8:r39706845:d26",
    gainNum := 8877,
    gainDen := 5811069149,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "65b349e65531502c87fc0737aa4f4e8e45b034ae914637aa5308331b4b4213b1"
},
  {
  nodeId := "s3:s3_frontier:beaccbaea1ed81ee",
  branchId := "P15:r26510867:d25",
  sourceParent := 15,
  targetParent := 23,
  valuation := 2,
  gainNum := 3336223,
  gainDen := 31206577,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P15:r26510867:d25",
    sourceParent := 15,
    targetParent := 23,
    valuation := 2,
    branchResidue := 26510867,
    branchDepth := 25,
    sourceModulus := 33554432,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P15:r26510867:d25",
    sourceParent := 15,
    targetParent := 23,
    valuation := 2,
    gainNum := 3336223,
    gainDen := 31206577,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P15:r26510867:d25",
    gainNum := 3336223,
    gainDen := 31206577,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "1a45bc96b139f5741b14aa90ccd4c51a17e940aaf153500bcb6a02b53d036a72"
},
  {
  nodeId := "s3:s3_frontier:bee1b3a5badbe55b",
  branchId := "P9:r53252723:d26",
  sourceParent := 9,
  targetParent := 25,
  valuation := 2,
  gainNum := 18667,
  gainDen := 254579315,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P9:r53252723:d26",
    sourceParent := 9,
    targetParent := 25,
    valuation := 2,
    branchResidue := 53252723,
    branchDepth := 26,
    sourceModulus := 67108864,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P9:r53252723:d26",
    sourceParent := 9,
    targetParent := 25,
    valuation := 2,
    gainNum := 18667,
    gainDen := 254579315,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P9:r53252723:d26",
    gainNum := 18667,
    gainDen := 254579315,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "a5f5c21bcb8e951c19e0a2ee3e6e9b13723e0ade3b2ecfc34d75d2443e136c2f"
},
  {
  nodeId := "s3:s3_frontier:bf5b7e9a0a610f97",
  branchId := "P15:r41027779:d26",
  sourceParent := 15,
  targetParent := 24,
  valuation := 5,
  gainNum := 19107077,
  gainDen := 2859600067,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P15:r41027779:d26",
    sourceParent := 15,
    targetParent := 24,
    valuation := 5,
    branchResidue := 41027779,
    branchDepth := 26,
    sourceModulus := 67108864,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P15:r41027779:d26",
    sourceParent := 15,
    targetParent := 24,
    valuation := 5,
    gainNum := 19107077,
    gainDen := 2859600067,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P15:r41027779:d26",
    gainNum := 19107077,
    gainDen := 2859600067,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "fd31498a459d5ad88206e947de414f86551ad7ddba92f6b93a9b7f866400241f"
},
  {
  nodeId := "s3:s3_frontier:bfa223193c4e0b2f",
  branchId := "P8:r64316497:d26",
  sourceParent := 8,
  targetParent := 29,
  valuation := 7,
  gainNum := 12351,
  gainDen := 16170443857,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P8:r64316497:d26",
    sourceParent := 8,
    targetParent := 29,
    valuation := 7,
    branchResidue := 64316497,
    branchDepth := 26,
    sourceModulus := 67108864,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P8:r64316497:d26",
    sourceParent := 8,
    targetParent := 29,
    valuation := 7,
    gainNum := 12351,
    gainDen := 16170443857,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P8:r64316497:d26",
    gainNum := 12351,
    gainDen := 16170443857,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "bf01e7b6a9bd274b76f15a88f816b0d57e539191c7f582b9c01c9a3d0843836f"
},
  {
  nodeId := "s3:s3_frontier:c0ddb02cb4660b81",
  branchId := "P14:r11914377:d24",
  sourceParent := 14,
  targetParent := 19,
  valuation := 1,
  gainNum := 6481287,
  gainDen := 45468809,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P14:r11914377:d24",
    sourceParent := 14,
    targetParent := 19,
    valuation := 1,
    branchResidue := 11914377,
    branchDepth := 24,
    sourceModulus := 16777216,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P14:r11914377:d24",
    sourceParent := 14,
    targetParent := 19,
    valuation := 1,
    gainNum := 6481287,
    gainDen := 45468809,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P14:r11914377:d24",
    gainNum := 6481287,
    gainDen := 45468809,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "c8677b430add6841109840aeb98d0cfea92df44ff939dd5a9fb15340e115bc0d"
},
  {
  nodeId := "s3:s3_frontier:c1082c004294e32e",
  branchId := "P12:r11914377:d24",
  sourceParent := 12,
  targetParent := 26,
  valuation := 5,
  gainNum := 87095,
  gainDen := 87984879,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P12:r11914377:d24",
    sourceParent := 12,
    targetParent := 26,
    valuation := 5,
    branchResidue := 11914377,
    branchDepth := 24,
    sourceModulus := 16777216,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P12:r11914377:d24",
    sourceParent := 12,
    targetParent := 26,
    valuation := 5,
    gainNum := 87095,
    gainDen := 87984879,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P12:r11914377:d24",
    gainNum := 87095,
    gainDen := 87984879,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "c703598fb312b35b66a97becf38ff9c19d36aee8c29dd9456a24a4952580de50"
},
  {
  nodeId := "s3:s3_frontier:c37625b4dfc162df",
  branchId := "P14:r11914377:d24",
  sourceParent := 14,
  targetParent := 18,
  valuation := 0,
  gainNum := 1168515,
  gainDen := 4098799,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P14:r11914377:d24",
    sourceParent := 14,
    targetParent := 18,
    valuation := 0,
    branchResidue := 11914377,
    branchDepth := 24,
    sourceModulus := 16777216,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P14:r11914377:d24",
    sourceParent := 14,
    targetParent := 18,
    valuation := 0,
    gainNum := 1168515,
    gainDen := 4098799,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P14:r11914377:d24",
    gainNum := 1168515,
    gainDen := 4098799,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "8ca07d99b863e3526f1f676315e9da99241a995a80db6c0633ec49964e11fdf0"
},
  {
  nodeId := "s3:s3_frontier:c51759e4c24f698f",
  branchId := "P6:r21817285:d25",
  sourceParent := 6,
  targetParent := 29,
  valuation := 6,
  gainNum := 987,
  gainDen := 2907498437,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P6:r21817285:d25",
    sourceParent := 6,
    targetParent := 29,
    valuation := 6,
    branchResidue := 21817285,
    branchDepth := 25,
    sourceModulus := 33554432,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P6:r21817285:d25",
    sourceParent := 6,
    targetParent := 29,
    valuation := 6,
    gainNum := 987,
    gainDen := 2907498437,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P6:r21817285:d25",
    gainNum := 987,
    gainDen := 2907498437,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "4c8393d4705cf6d5d1ca3808bb5a20b54df1dc44b17186b7de5c33c6808656d9"
},
  {
  nodeId := "s3:s3_frontier:c597cc15bc7bfe9a",
  branchId := "P20:r38436209:d26",
  sourceParent := 20,
  targetParent := 21,
  valuation := 6,
  gainNum := 358089715,
  gainDen := 441089393,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P20:r38436209:d26",
    sourceParent := 20,
    targetParent := 21,
    valuation := 6,
    branchResidue := 38436209,
    branchDepth := 26,
    sourceModulus := 67108864,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P20:r38436209:d26",
    sourceParent := 20,
    targetParent := 21,
    valuation := 6,
    gainNum := 358089715,
    gainDen := 441089393,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P20:r38436209:d26",
    gainNum := 358089715,
    gainDen := 441089393,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "06d84b1c9ac08219eace2ab9ddcc3467cac4282a20f187433722571f66af73c2"
},
  {
  nodeId := "s3:s3_frontier:c6583ae9d2230ac6",
  branchId := "P12:r34008209:d26",
  sourceParent := 12,
  targetParent := 26,
  valuation := 7,
  gainNum := 392381,
  gainDen := 6342241425,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P12:r34008209:d26",
    sourceParent := 12,
    targetParent := 26,
    valuation := 7,
    branchResidue := 34008209,
    branchDepth := 26,
    sourceModulus := 67108864,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P12:r34008209:d26",
    sourceParent := 12,
    targetParent := 26,
    valuation := 7,
    gainNum := 392381,
    gainDen := 6342241425,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P12:r34008209:d26",
    gainNum := 392381,
    gainDen := 6342241425,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "e9dd3fbee540832bfd68835ea21ae010e7b7789c35e08869431a8d0973100959"
},
  {
  nodeId := "s3:s3_frontier:c71ee3d70ebf10a9",
  branchId := "P11:r35743131:d26",
  sourceParent := 11,
  targetParent := 28,
  valuation := 5,
  gainNum := 196703,
  gainDen := 2384553371,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P11:r35743131:d26",
    sourceParent := 11,
    targetParent := 28,
    valuation := 5,
    branchResidue := 35743131,
    branchDepth := 26,
    sourceModulus := 67108864,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P11:r35743131:d26",
    sourceParent := 11,
    targetParent := 28,
    valuation := 5,
    gainNum := 196703,
    gainDen := 2384553371,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P11:r35743131:d26",
    gainNum := 196703,
    gainDen := 2384553371,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "988ca646523a18f74306bab8cf02f27c4173a8686c5b8c2e8f6af8244613f042"
},
  {
  nodeId := "s3:s3_frontier:c76abfc3536bc196",
  branchId := "P8:r25540441:d25",
  sourceParent := 8,
  targetParent := 27,
  valuation := 5,
  gainNum := 901,
  gainDen := 147453343,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P8:r25540441:d25",
    sourceParent := 8,
    targetParent := 27,
    valuation := 5,
    branchResidue := 25540441,
    branchDepth := 25,
    sourceModulus := 33554432,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P8:r25540441:d25",
    sourceParent := 8,
    targetParent := 27,
    valuation := 5,
    gainNum := 901,
    gainDen := 147453343,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P8:r25540441:d25",
    gainNum := 901,
    gainDen := 147453343,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "9b672b6062b79791fad2220d83f7ad10ce1a31f23078334ed8f15ab8ae6f9b5e"
},
  {
  nodeId := "s3:s3_frontier:c83f2c305a3cf7e0",
  branchId := "P18:r23073241:d25",
  sourceParent := 18,
  targetParent := 27,
  valuation := 7,
  gainNum := 135257077,
  gainDen := 1499468249,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P18:r23073241:d25",
    sourceParent := 18,
    targetParent := 27,
    valuation := 7,
    branchResidue := 23073241,
    branchDepth := 25,
    sourceModulus := 33554432,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P18:r23073241:d25",
    sourceParent := 18,
    targetParent := 27,
    valuation := 7,
    gainNum := 135257077,
    gainDen := 1499468249,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P18:r23073241:d25",
    gainNum := 135257077,
    gainDen := 1499468249,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "ae6c328e52c62e9392b1b638eeb9d4bfd825472d5dcc18c7ebfd2fcca5dee72b"
},
  {
  nodeId := "s3:s3_frontier:c8fd669f166dd85a",
  branchId := "P6:r52011671:d26",
  sourceParent := 6,
  targetParent := 31,
  valuation := 6,
  gainNum := 43,
  gainDen := 253338263,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P6:r52011671:d26",
    sourceParent := 6,
    targetParent := 31,
    valuation := 6,
    branchResidue := 52011671,
    branchDepth := 26,
    sourceModulus := 67108864,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P6:r52011671:d26",
    sourceParent := 6,
    targetParent := 31,
    valuation := 6,
    gainNum := 43,
    gainDen := 253338263,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P6:r52011671:d26",
    gainNum := 43,
    gainDen := 253338263,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "1b87ffeb1696318e9d2918fa90d76c184e9ee0f59c73130a64d772f52c6842f0"
},
  {
  nodeId := "s3:s3_frontier:c94cd47e76c5fb6f",
  branchId := "P4:r62137837:d26",
  sourceParent := 4,
  targetParent := 27,
  valuation := 3,
  gainNum := 141,
  gainDen := 934553069,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P4:r62137837:d26",
    sourceParent := 4,
    targetParent := 27,
    valuation := 3,
    branchResidue := 62137837,
    branchDepth := 26,
    sourceModulus := 67108864,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P4:r62137837:d26",
    sourceParent := 4,
    targetParent := 27,
    valuation := 3,
    gainNum := 141,
    gainDen := 934553069,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P4:r62137837:d26",
    gainNum := 141,
    gainDen := 934553069,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "527e154eb8c22d9598ad2a36b5341f14632cd5901eb66ed1d17d1e72620f3ed3"
},
  {
  nodeId := "s3:s3_frontier:c9eedf174e0ba3e7",
  branchId := "P7:r39706845:d26",
  sourceParent := 7,
  targetParent := 28,
  valuation := 3,
  gainNum := 3989,
  gainDen := 979230941,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P7:r39706845:d26",
    sourceParent := 7,
    targetParent := 28,
    valuation := 3,
    branchResidue := 39706845,
    branchDepth := 26,
    sourceModulus := 67108864,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P7:r39706845:d26",
    sourceParent := 7,
    targetParent := 28,
    valuation := 3,
    gainNum := 3989,
    gainDen := 979230941,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P7:r39706845:d26",
    gainNum := 3989,
    gainDen := 979230941,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "21417bba4798cc73a6a198a049fa394d1eebfe53baeac3c542e52f83d4f59a0f"
},
  {
  nodeId := "s3:s3_frontier:cb9bd595c3d83693",
  branchId := "P15:r41027779:d26",
  sourceParent := 15,
  targetParent := 26,
  valuation := 7,
  gainNum := 22712903,
  gainDen := 13597018307,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P15:r41027779:d26",
    sourceParent := 15,
    targetParent := 26,
    valuation := 7,
    branchResidue := 41027779,
    branchDepth := 26,
    sourceModulus := 67108864,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P15:r41027779:d26",
    sourceParent := 15,
    targetParent := 26,
    valuation := 7,
    gainNum := 22712903,
    gainDen := 13597018307,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P15:r41027779:d26",
    gainNum := 22712903,
    gainDen := 13597018307,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "21c2e1bfa362d438f91c1743171d58491abe23d911423b1acf77d8c9bf4840c1"
},
  {
  nodeId := "s3:s3_frontier:cd7778b989aa1146",
  branchId := "P14:r23693441:d25",
  sourceParent := 14,
  targetParent := 25,
  valuation := 3,
  gainNum := 2813653,
  gainDen := 157911169,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P14:r23693441:d25",
    sourceParent := 14,
    targetParent := 25,
    valuation := 3,
    branchResidue := 23693441,
    branchDepth := 25,
    sourceModulus := 33554432,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P14:r23693441:d25",
    sourceParent := 14,
    targetParent := 25,
    valuation := 3,
    gainNum := 2813653,
    gainDen := 157911169,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P14:r23693441:d25",
    gainNum := 2813653,
    gainDen := 157911169,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "a3921ae53e6fc44f1856f06c5609f1680066c71298c0885881d0e84808e30ff4"
},
  {
  nodeId := "s3:s3_frontier:cdf973f8b34e5160",
  branchId := "P12:r43176689:d26",
  sourceParent := 12,
  targetParent := 21,
  valuation := 0,
  gainNum := 873361,
  gainDen := 110285553,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P12:r43176689:d26",
    sourceParent := 12,
    targetParent := 21,
    valuation := 0,
    branchResidue := 43176689,
    branchDepth := 26,
    sourceModulus := 67108864,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P12:r43176689:d26",
    sourceParent := 12,
    targetParent := 21,
    valuation := 0,
    gainNum := 873361,
    gainDen := 110285553,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P12:r43176689:d26",
    gainNum := 873361,
    gainDen := 110285553,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "5b578f53e7094cdc714e1bf057712348cbfc6a9b4ede5ac6a6292f2f48463169"
},
  {
  nodeId := "s3:s3_frontier:cf2b97b99985a2c6",
  branchId := "P14:r55974473:d26",
  sourceParent := 14,
  targetParent := 20,
  valuation := 1,
  gainNum := 4386185,
  gainDen := 123083337,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P14:r55974473:d26",
    sourceParent := 14,
    targetParent := 20,
    valuation := 1,
    branchResidue := 55974473,
    branchDepth := 26,
    sourceModulus := 67108864,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P14:r55974473:d26",
    sourceParent := 14,
    targetParent := 20,
    valuation := 1,
    gainNum := 4386185,
    gainDen := 123083337,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P14:r55974473:d26",
    gainNum := 4386185,
    gainDen := 123083337,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "8c2fa80f9521ab3ed9b558b3769a5e0c91a61801c4fb7289309581fe0e941b0b"
},
  {
  nodeId := "s3:s3_frontier:d22eb1cba70d9768",
  branchId := "P12:r34008209:d26",
  sourceParent := 12,
  targetParent := 23,
  valuation := 4,
  gainNum := 481843,
  gainDen := 973532305,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P12:r34008209:d26",
    sourceParent := 12,
    targetParent := 23,
    valuation := 4,
    branchResidue := 34008209,
    branchDepth := 26,
    sourceModulus := 67108864,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P12:r34008209:d26",
    sourceParent := 12,
    targetParent := 23,
    valuation := 4,
    gainNum := 481843,
    gainDen := 973532305,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P12:r34008209:d26",
    gainNum := 481843,
    gainDen := 973532305,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "ff38804b17a6116e9adffbb31d2c82c73a1dd1c19ec9970e490948b2aac92e0b"
},
  {
  nodeId := "s3:s3_frontier:d6b1283b806ead96",
  branchId := "P19:r21039907:d25",
  sourceParent := 19,
  targetParent := 28,
  valuation := 7,
  gainNum := 1640123799,
  gainDen := 6060837667,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P19:r21039907:d25",
    sourceParent := 19,
    targetParent := 28,
    valuation := 7,
    branchResidue := 21039907,
    branchDepth := 25,
    sourceModulus := 33554432,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P19:r21039907:d25",
    sourceParent := 19,
    targetParent := 28,
    valuation := 7,
    gainNum := 1640123799,
    gainDen := 6060837667,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P19:r21039907:d25",
    gainNum := 1640123799,
    gainDen := 6060837667,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "3aad086771b5e0f4f15a9bb644aed3825b8f098ecf3b35439fbb0076baba1954"
},
  {
  nodeId := "s3:s3_frontier:d814b0a12d140508",
  branchId := "P13:r3971459:d22",
  sourceParent := 13,
  targetParent := 21,
  valuation := 2,
  gainNum := 1971727,
  gainDen := 20748675,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P13:r3971459:d22",
    sourceParent := 13,
    targetParent := 21,
    valuation := 2,
    branchResidue := 3971459,
    branchDepth := 22,
    sourceModulus := 4194304,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P13:r3971459:d22",
    sourceParent := 13,
    targetParent := 21,
    valuation := 2,
    gainNum := 1971727,
    gainDen := 20748675,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P13:r3971459:d22",
    gainNum := 1971727,
    gainDen := 20748675,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "e846e4e0677df288e057cffa4fb765418da6ca5c15306c8e411a2608e5d4edfb"
},
  {
  nodeId := "s3:s3_frontier:d910ba7a1f6ceb8d",
  branchId := "P3:r62137837:d26",
  sourceParent := 3,
  targetParent := 28,
  valuation := 3,
  gainNum := 47,
  gainDen := 934553069,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P3:r62137837:d26",
    sourceParent := 3,
    targetParent := 28,
    valuation := 3,
    branchResidue := 62137837,
    branchDepth := 26,
    sourceModulus := 67108864,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P3:r62137837:d26",
    sourceParent := 3,
    targetParent := 28,
    valuation := 3,
    gainNum := 47,
    gainDen := 934553069,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P3:r62137837:d26",
    gainNum := 47,
    gainDen := 934553069,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "8fa6e5753ddc2d93573fce7bba19281a4e39da41030140c45bb91c61a5a0745d"
},
  {
  nodeId := "s3:s3_frontier:db0846bd3e09daee",
  branchId := "P6:r28537377:d25",
  sourceParent := 6,
  targetParent := 28,
  valuation := 6,
  gainNum := 1331,
  gainDen := 3920851489,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P6:r28537377:d25",
    sourceParent := 6,
    targetParent := 28,
    valuation := 6,
    branchResidue := 28537377,
    branchDepth := 25,
    sourceModulus := 33554432,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P6:r28537377:d25",
    sourceParent := 6,
    targetParent := 28,
    valuation := 6,
    gainNum := 1331,
    gainDen := 3920851489,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P6:r28537377:d25",
    gainNum := 1331,
    gainDen := 3920851489,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "32b65318312bd8eea1811ef6e99f800df7124bc0229ff103b599fb2202cded36"
},
  {
  nodeId := "s3:s3_frontier:db7bb270cb03c0f0",
  branchId := "P10:r40120529:d26",
  sourceParent := 10,
  targetParent := 30,
  valuation := 7,
  gainNum := 4889,
  gainDen := 711209169,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P10:r40120529:d26",
    sourceParent := 10,
    targetParent := 30,
    valuation := 7,
    branchResidue := 40120529,
    branchDepth := 26,
    sourceModulus := 67108864,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P10:r40120529:d26",
    sourceParent := 10,
    targetParent := 30,
    valuation := 7,
    gainNum := 4889,
    gainDen := 711209169,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P10:r40120529:d26",
    gainNum := 4889,
    gainDen := 711209169,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "3068885dce79eb5f5410cc7fbfdb630227dabb7ff60a3eac5033bffc001bba13"
},
  {
  nodeId := "s3:s3_frontier:df810451ba94b9fd",
  branchId := "P13:r36761851:d26",
  sourceParent := 13,
  targetParent := 27,
  valuation := 6,
  gainNum := 1333945,
  gainDen := 3593531643,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P13:r36761851:d26",
    sourceParent := 13,
    targetParent := 27,
    valuation := 6,
    branchResidue := 36761851,
    branchDepth := 26,
    sourceModulus := 67108864,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P13:r36761851:d26",
    sourceParent := 13,
    targetParent := 27,
    valuation := 6,
    gainNum := 1333945,
    gainDen := 3593531643,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P13:r36761851:d26",
    gainNum := 1333945,
    gainDen := 3593531643,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "c94c844ef214a92b1ed00f9a20813781ddc0257c2c77bae0f5b273acec46eaa0"
},
  {
  nodeId := "s3:s3_frontier:e25c3428b4baaf9a",
  branchId := "P13:r37271211:d26",
  sourceParent := 13,
  targetParent := 25,
  valuation := 3,
  gainNum := 87095,
  gainDen := 29328293,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P13:r37271211:d26",
    sourceParent := 13,
    targetParent := 25,
    valuation := 3,
    branchResidue := 37271211,
    branchDepth := 26,
    sourceModulus := 67108864,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P13:r37271211:d26",
    sourceParent := 13,
    targetParent := 25,
    valuation := 3,
    gainNum := 87095,
    gainDen := 29328293,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P13:r37271211:d26",
    gainNum := 87095,
    gainDen := 29328293,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "a7d9479a278b18dd3824fad66a99ed0af75a46ec0d66150e51bae2023ac7762a"
},
  {
  nodeId := "s3:s3_frontier:e31700cbd3afb5cd",
  branchId := "P8:r25540441:d25",
  sourceParent := 8,
  targetParent := 29,
  valuation := 7,
  gainNum := 3217,
  gainDen := 2105915225,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P8:r25540441:d25",
    sourceParent := 8,
    targetParent := 29,
    valuation := 7,
    branchResidue := 25540441,
    branchDepth := 25,
    sourceModulus := 33554432,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P8:r25540441:d25",
    sourceParent := 8,
    targetParent := 29,
    valuation := 7,
    gainNum := 3217,
    gainDen := 2105915225,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P8:r25540441:d25",
    gainNum := 3217,
    gainDen := 2105915225,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "b9b6cc5686894d3fb89a87b22027e5e0bcb7370126d6bbe06e85431454ba5f40"
},
  {
  nodeId := "s3:s3_frontier:e37aa7314fede774",
  branchId := "P13:r3971459:d22",
  sourceParent := 13,
  targetParent := 20,
  valuation := 1,
  gainNum := 2349131,
  gainDen := 12360067,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P13:r3971459:d22",
    sourceParent := 13,
    targetParent := 20,
    valuation := 1,
    branchResidue := 3971459,
    branchDepth := 22,
    sourceModulus := 4194304,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P13:r3971459:d22",
    sourceParent := 13,
    targetParent := 20,
    valuation := 1,
    gainNum := 2349131,
    gainDen := 12360067,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P13:r3971459:d22",
    gainNum := 2349131,
    gainDen := 12360067,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "bdc35fd08c516c6186eddd36ccfc22158fa65e85c249f346433fb1d4594e474a"
},
  {
  nodeId := "s3:s3_frontier:e54d9f41c26c9e24",
  branchId := "P11:r53252723:d26",
  sourceParent := 11,
  targetParent := 23,
  valuation := 3,
  gainNum := 57525,
  gainDen := 174338257,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P11:r53252723:d26",
    sourceParent := 11,
    targetParent := 23,
    valuation := 3,
    branchResidue := 53252723,
    branchDepth := 26,
    sourceModulus := 67108864,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P11:r53252723:d26",
    sourceParent := 11,
    targetParent := 23,
    valuation := 3,
    gainNum := 57525,
    gainDen := 174338257,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P11:r53252723:d26",
    gainNum := 57525,
    gainDen := 174338257,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "9e2c5fbb00a2ab1cd10bfdd4699221bac256dcc56e033ed709533a17fbf887f2"
},
  {
  nodeId := "s3:s3_frontier:e59f4c0757f40af8",
  branchId := "P11:r35743131:d26",
  sourceParent := 11,
  targetParent := 30,
  valuation := 7,
  gainNum := 4889,
  gainDen := 237069723,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P11:r35743131:d26",
    sourceParent := 11,
    targetParent := 30,
    valuation := 7,
    branchResidue := 35743131,
    branchDepth := 26,
    sourceModulus := 67108864,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P11:r35743131:d26",
    sourceParent := 11,
    targetParent := 30,
    valuation := 7,
    gainNum := 4889,
    gainDen := 237069723,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P11:r35743131:d26",
    gainNum := 4889,
    gainDen := 237069723,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "64d9846e1c5d846b2c3be46c9bbd75965ce20ad380baa90cc31b2bb59c3a43af"
},
  {
  nodeId := "s3:s3_frontier:e6219b048b885da0",
  branchId := "P9:r13235615:d24",
  sourceParent := 9,
  targetParent := 27,
  valuation := 5,
  gainNum := 8363,
  gainDen := 228108085,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P9:r13235615:d24",
    sourceParent := 9,
    targetParent := 27,
    valuation := 5,
    branchResidue := 13235615,
    branchDepth := 24,
    sourceModulus := 16777216,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P9:r13235615:d24",
    sourceParent := 9,
    targetParent := 27,
    valuation := 5,
    gainNum := 8363,
    gainDen := 228108085,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P9:r13235615:d24",
    gainNum := 8363,
    gainDen := 228108085,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "fcf09ed5f21a97bd601d70c6ff014059a6b7926f14bb06e309143006405424d2"
},
  {
  nodeId := "s3:s3_frontier:e6c3b690e46fe628",
  branchId := "P10:r40120529:d26",
  sourceParent := 10,
  targetParent := 26,
  valuation := 3,
  gainNum := 19175,
  gainDen := 174338257,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P10:r40120529:d26",
    sourceParent := 10,
    targetParent := 26,
    valuation := 3,
    branchResidue := 40120529,
    branchDepth := 26,
    sourceModulus := 67108864,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P10:r40120529:d26",
    sourceParent := 10,
    targetParent := 26,
    valuation := 3,
    gainNum := 19175,
    gainDen := 174338257,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P10:r40120529:d26",
    gainNum := 19175,
    gainDen := 174338257,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "bd38250415aaf4c03a449e4452ba16ed1cf6d6c400eef8a97b5e823a609ed7f8"
},
  {
  nodeId := "s3:s3_frontier:e7df9d32074bc9f5",
  branchId := "P12:r44704769:d26",
  sourceParent := 12,
  targetParent := 23,
  valuation := 1,
  gainNum := 147577,
  gainDen := 37271211,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P12:r44704769:d26",
    sourceParent := 12,
    targetParent := 23,
    valuation := 1,
    branchResidue := 44704769,
    branchDepth := 26,
    sourceModulus := 67108864,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P12:r44704769:d26",
    sourceParent := 12,
    targetParent := 23,
    valuation := 1,
    gainNum := 147577,
    gainDen := 37271211,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P12:r44704769:d26",
    gainNum := 147577,
    gainDen := 37271211,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "f0bc1605bd31f9a72e7d3c398e3eb5e4880d62c60d77f2792d0e840143ac7354"
},
  {
  nodeId := "s3:s3_frontier:e87002501dbfc181",
  branchId := "P10:r40120529:d26",
  sourceParent := 10,
  targetParent := 28,
  valuation := 5,
  gainNum := 78605,
  gainDen := 2858692817,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P10:r40120529:d26",
    sourceParent := 10,
    targetParent := 28,
    valuation := 5,
    branchResidue := 40120529,
    branchDepth := 26,
    sourceModulus := 67108864,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P10:r40120529:d26",
    sourceParent := 10,
    targetParent := 28,
    valuation := 5,
    gainNum := 78605,
    gainDen := 2858692817,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P10:r40120529:d26",
    gainNum := 78605,
    gainDen := 2858692817,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "7a7a9f2b06cf94e06f73fbb779157d80c2b5e034672941ae54e374b92307b6e7"
},
  {
  nodeId := "s3:s3_frontier:e8db101b60e3a713",
  branchId := "P11:r53666407:d26",
  sourceParent := 11,
  targetParent := 31,
  valuation := 7,
  gainNum := 204549,
  gainDen := 9918669415,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P11:r53666407:d26",
    sourceParent := 11,
    targetParent := 31,
    valuation := 7,
    branchResidue := 53666407,
    branchDepth := 26,
    sourceModulus := 67108864,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P11:r53666407:d26",
    sourceParent := 11,
    targetParent := 31,
    valuation := 7,
    gainNum := 204549,
    gainDen := 9918669415,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P11:r53666407:d26",
    gainNum := 204549,
    gainDen := 9918669415,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "4e41c18b3bd9146125c14d3daada660986e16cbdd0837c54f03023ba2b4dc6f1"
},
  {
  nodeId := "s3:s3_frontier:e9755893acb0271b",
  branchId := "P20:r39862641:d26",
  sourceParent := 20,
  targetParent := 23,
  valuation := 7,
  gainNum := 550203679,
  gainDen := 1355464827,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P20:r39862641:d26",
    sourceParent := 20,
    targetParent := 23,
    valuation := 7,
    branchResidue := 39862641,
    branchDepth := 26,
    sourceModulus := 67108864,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P20:r39862641:d26",
    sourceParent := 20,
    targetParent := 23,
    valuation := 7,
    gainNum := 550203679,
    gainDen := 1355464827,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P20:r39862641:d26",
    gainNum := 550203679,
    gainDen := 1355464827,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "d40af2af0c03afc0f938b0b9b3a57c443dd672290dac909bd81875ef009664b9"
},
  {
  nodeId := "s3:s3_frontier:e9c377a5172fb3fc",
  branchId := "P14:r55974473:d26",
  sourceParent := 14,
  targetParent := 22,
  valuation := 3,
  gainNum := 4683773,
  gainDen := 525736521,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P14:r55974473:d26",
    sourceParent := 14,
    targetParent := 22,
    valuation := 3,
    branchResidue := 55974473,
    branchDepth := 26,
    sourceModulus := 67108864,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P14:r55974473:d26",
    sourceParent := 14,
    targetParent := 22,
    valuation := 3,
    gainNum := 4683773,
    gainDen := 525736521,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P14:r55974473:d26",
    gainNum := 4683773,
    gainDen := 525736521,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "f825c73d8e18df29a22c50dc5aa8df94a83994dc0f493014b042060feb7e8de5"
},
  {
  nodeId := "s3:s3_frontier:eacc24c5110ae668",
  branchId := "P8:r39706845:d26",
  sourceParent := 8,
  targetParent := 28,
  valuation := 4,
  gainNum := 901,
  gainDen := 147453343,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P8:r39706845:d26",
    sourceParent := 8,
    targetParent := 28,
    valuation := 4,
    branchResidue := 39706845,
    branchDepth := 26,
    sourceModulus := 67108864,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P8:r39706845:d26",
    sourceParent := 8,
    targetParent := 28,
    valuation := 4,
    gainNum := 901,
    gainDen := 147453343,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P8:r39706845:d26",
    gainNum := 901,
    gainDen := 147453343,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "1fad1a406d008c64769549a1841b21cd1bd550994cf245f5c814436e01b9a7e0"
},
  {
  nodeId := "s3:s3_frontier:eaedad23db1ca8e9",
  branchId := "P12:r43176689:d26",
  sourceParent := 12,
  targetParent := 25,
  valuation := 4,
  gainNum := 552811,
  gainDen := 1116918513,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P12:r43176689:d26",
    sourceParent := 12,
    targetParent := 25,
    valuation := 4,
    branchResidue := 43176689,
    branchDepth := 26,
    sourceModulus := 67108864,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P12:r43176689:d26",
    sourceParent := 12,
    targetParent := 25,
    valuation := 4,
    gainNum := 552811,
    gainDen := 1116918513,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P12:r43176689:d26",
    gainNum := 552811,
    gainDen := 1116918513,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "e26c0f3a16a53ee8d80ca04d2e56ddc760111d7aafb1451434ec44d8f44d1e11"
},
  {
  nodeId := "s3:s3_frontier:ec69ea25675958ff",
  branchId := "P12:r20876015:d25",
  sourceParent := 12,
  targetParent := 24,
  valuation := 0,
  gainNum := 862079,
  gainDen := 54430447,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P12:r20876015:d25",
    sourceParent := 12,
    targetParent := 24,
    valuation := 0,
    branchResidue := 20876015,
    branchDepth := 25,
    sourceModulus := 33554432,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P12:r20876015:d25",
    sourceParent := 12,
    targetParent := 24,
    valuation := 0,
    gainNum := 862079,
    gainDen := 54430447,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P12:r20876015:d25",
    gainNum := 862079,
    gainDen := 54430447,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "b838388fb94f45aba2b9e2cbb6684e768e1959dc038756331789b8bfe98ef3af"
},
  {
  nodeId := "s3:s3_frontier:ec8e98c9c3f1833a",
  branchId := "P16:r23693441:d25",
  sourceParent := 16,
  targetParent := 22,
  valuation := 3,
  gainNum := 25322877,
  gainDen := 157911169,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P16:r23693441:d25",
    sourceParent := 16,
    targetParent := 22,
    valuation := 3,
    branchResidue := 23693441,
    branchDepth := 25,
    sourceModulus := 33554432,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P16:r23693441:d25",
    sourceParent := 16,
    targetParent := 22,
    valuation := 3,
    gainNum := 25322877,
    gainDen := 157911169,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P16:r23693441:d25",
    gainNum := 25322877,
    gainDen := 157911169,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "9df100dd41353ad80fdcfe3f17b918872bdd8d55b7dc20444f87c33a9d3ca5c7"
},
  {
  nodeId := "s3:s3_frontier:ef911da747d666f0",
  branchId := "P7:r39706845:d26",
  sourceParent := 7,
  targetParent := 30,
  valuation := 5,
  gainNum := 3731,
  gainDen := 3663585501,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P7:r39706845:d26",
    sourceParent := 7,
    targetParent := 30,
    valuation := 5,
    branchResidue := 39706845,
    branchDepth := 26,
    sourceModulus := 67108864,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P7:r39706845:d26",
    sourceParent := 7,
    targetParent := 30,
    valuation := 5,
    gainNum := 3731,
    gainDen := 3663585501,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P7:r39706845:d26",
    gainNum := 3731,
    gainDen := 3663585501,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "ad7bba8120f251b7339f7078a9bc8d17d8a8614da4323339e4c1492ab41f176a"
},
  {
  nodeId := "s3:s3_frontier:efe17a7cde81ccee",
  branchId := "P15:r26510867:d25",
  sourceParent := 15,
  targetParent := 24,
  valuation := 3,
  gainNum := 1768513,
  gainDen := 33084861,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P15:r26510867:d25",
    sourceParent := 15,
    targetParent := 24,
    valuation := 3,
    branchResidue := 26510867,
    branchDepth := 25,
    sourceModulus := 33554432,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P15:r26510867:d25",
    sourceParent := 15,
    targetParent := 24,
    valuation := 3,
    gainNum := 1768513,
    gainDen := 33084861,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P15:r26510867:d25",
    gainNum := 1768513,
    gainDen := 33084861,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "aa586a5e3e00196f459ae7f3268d94ce8a12bc2b2441e736e6fb9504fdc0c86c"
},
  {
  nodeId := "s3:s3_frontier:f03ffa7c7ad669be",
  branchId := "P11:r53252723:d26",
  sourceParent := 11,
  targetParent := 21,
  valuation := 1,
  gainNum := 52953,
  gainDen := 40120529,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P11:r53252723:d26",
    sourceParent := 11,
    targetParent := 21,
    valuation := 1,
    branchResidue := 53252723,
    branchDepth := 26,
    sourceModulus := 67108864,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P11:r53252723:d26",
    sourceParent := 11,
    targetParent := 21,
    valuation := 1,
    gainNum := 52953,
    gainDen := 40120529,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P11:r53252723:d26",
    gainNum := 52953,
    gainDen := 40120529,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "f4e99d2eb62216f674ef43e6087b5d56e9d1ab1cccaa202d116bcec91027fb5a"
},
  {
  nodeId := "s3:s3_frontier:f085785b2401551f",
  branchId := "P12:r43176689:d26",
  sourceParent := 12,
  targetParent := 27,
  valuation := 6,
  gainNum := 271063,
  gainDen := 2190660337,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P12:r43176689:d26",
    sourceParent := 12,
    targetParent := 27,
    valuation := 6,
    branchResidue := 43176689,
    branchDepth := 26,
    sourceModulus := 67108864,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P12:r43176689:d26",
    sourceParent := 12,
    targetParent := 27,
    valuation := 6,
    gainNum := 271063,
    gainDen := 2190660337,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P12:r43176689:d26",
    gainNum := 271063,
    gainDen := 2190660337,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "f63f8a430530c1df92ac76231c9fadb213e83fbe8d2d4a8db80577b90d4b0eb6"
},
  {
  nodeId := "s3:s3_frontier:f1ed6ea3ccd89f13",
  branchId := "P8:r64316497:d26",
  sourceParent := 8,
  targetParent := 23,
  valuation := 1,
  gainNum := 647,
  gainDen := 13235615,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P8:r64316497:d26",
    sourceParent := 8,
    targetParent := 23,
    valuation := 1,
    branchResidue := 64316497,
    branchDepth := 26,
    sourceModulus := 67108864,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P8:r64316497:d26",
    sourceParent := 8,
    targetParent := 23,
    valuation := 1,
    gainNum := 647,
    gainDen := 13235615,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P8:r64316497:d26",
    gainNum := 647,
    gainDen := 13235615,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "b7c1f0bc3aaffb20ba7563469249e3331ce4bef4aadace6ec2d8a0a71009af95"
},
  {
  nodeId := "s3:s3_frontier:f3697df2e16f2b0f",
  branchId := "P14:r12423737:d24",
  sourceParent := 14,
  targetParent := 27,
  valuation := 7,
  gainNum := 3913833,
  gainDen := 1757254201,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P14:r12423737:d24",
    sourceParent := 14,
    targetParent := 27,
    valuation := 7,
    branchResidue := 12423737,
    branchDepth := 24,
    sourceModulus := 16777216,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P14:r12423737:d24",
    sourceParent := 14,
    targetParent := 27,
    valuation := 7,
    gainNum := 3913833,
    gainDen := 1757254201,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P14:r12423737:d24",
    gainNum := 3913833,
    gainDen := 1757254201,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "3f346374cd4077324126c59c3b0f698701cdf7e88404e7f89efcc84241a6380c"
},
  {
  nodeId := "s3:s3_frontier:f3af846919e0aa0d",
  branchId := "P7:r58731763:d26",
  sourceParent := 7,
  targetParent := 22,
  valuation := 0,
  gainNum := 4101,
  gainDen := 125840627,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P7:r58731763:d26",
    sourceParent := 7,
    targetParent := 22,
    valuation := 0,
    branchResidue := 58731763,
    branchDepth := 26,
    sourceModulus := 67108864,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P7:r58731763:d26",
    sourceParent := 7,
    targetParent := 22,
    valuation := 0,
    gainNum := 4101,
    gainDen := 125840627,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P7:r58731763:d26",
    gainNum := 4101,
    gainDen := 125840627,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "01aa1c9382da03115b58ae1fca13fb2b8582d605c3bd4403fbd9923018339104"
},
  {
  nodeId := "s3:s3_frontier:f67aafd65ba24607",
  branchId := "P16:r23693441:d25",
  sourceParent := 16,
  targetParent := 20,
  valuation := 1,
  gainNum := 6471643,
  gainDen := 10089145,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P16:r23693441:d25",
    sourceParent := 16,
    targetParent := 20,
    valuation := 1,
    branchResidue := 23693441,
    branchDepth := 25,
    sourceModulus := 33554432,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P16:r23693441:d25",
    sourceParent := 16,
    targetParent := 20,
    valuation := 1,
    gainNum := 6471643,
    gainDen := 10089145,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P16:r23693441:d25",
    gainNum := 6471643,
    gainDen := 10089145,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "34cc9dc2e04f471de87de15f27eb3bf91a87ec7c6d5e9709e14639d72fb50aea"
},
  {
  nodeId := "s3:s3_frontier:f7232fca3141faf0",
  branchId := "P14:r32145719:d25",
  sourceParent := 14,
  targetParent := 31,
  valuation := 7,
  gainNum := 2203081,
  gainDen := 1978302775,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P14:r32145719:d25",
    sourceParent := 14,
    targetParent := 31,
    valuation := 7,
    branchResidue := 32145719,
    branchDepth := 25,
    sourceModulus := 33554432,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P14:r32145719:d25",
    sourceParent := 14,
    targetParent := 31,
    valuation := 7,
    gainNum := 2203081,
    gainDen := 1978302775,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P14:r32145719:d25",
    gainNum := 2203081,
    gainDen := 1978302775,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "e8e584ae4a99e49b102c134872cf56f04055983564d7da716a2c3ec106bd1e13"
},
  {
  nodeId := "s3:s3_frontier:f7a60709c4c6be8b",
  branchId := "P14:r55974473:d26",
  sourceParent := 14,
  targetParent := 23,
  valuation := 4,
  gainNum := 4733371,
  gainDen := 1062607433,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P14:r55974473:d26",
    sourceParent := 14,
    targetParent := 23,
    valuation := 4,
    branchResidue := 55974473,
    branchDepth := 26,
    sourceModulus := 67108864,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P14:r55974473:d26",
    sourceParent := 14,
    targetParent := 23,
    valuation := 4,
    gainNum := 4733371,
    gainDen := 1062607433,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P14:r55974473:d26",
    gainNum := 4733371,
    gainDen := 1062607433,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "17e201e0c9666988487293a70b86f4f3ac23f3f2fd167751941a49173dc66f0e"
},
  {
  nodeId := "s3:s3_frontier:f909ff6b61a2dc15",
  branchId := "P11:r53666407:d26",
  sourceParent := 11,
  targetParent := 26,
  valuation := 2,
  gainNum := 345423,
  gainDen := 523428455,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P11:r53666407:d26",
    sourceParent := 11,
    targetParent := 26,
    valuation := 2,
    branchResidue := 53666407,
    branchDepth := 26,
    sourceModulus := 67108864,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P11:r53666407:d26",
    sourceParent := 11,
    targetParent := 26,
    valuation := 2,
    gainNum := 345423,
    gainDen := 523428455,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P11:r53666407:d26",
    gainNum := 345423,
    gainDen := 523428455,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "a24a7b8bb2116a37633d62041c08cd25d155c3477698d377d8df84f30706754d"
},
  {
  nodeId := "s3:s3_frontier:f92a5074073f77f1",
  branchId := "P16:r11028287:d24",
  sourceParent := 16,
  targetParent := 28,
  valuation := 5,
  gainNum := 22407617,
  gainDen := 279463743,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P16:r11028287:d24",
    sourceParent := 16,
    targetParent := 28,
    valuation := 5,
    branchResidue := 11028287,
    branchDepth := 24,
    sourceModulus := 16777216,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P16:r11028287:d24",
    sourceParent := 16,
    targetParent := 28,
    valuation := 5,
    gainNum := 22407617,
    gainDen := 279463743,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P16:r11028287:d24",
    gainNum := 22407617,
    gainDen := 279463743,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "3b17b00e377f8376e52805601887ab3e808c96b61a2f8a8ffadc43a611c21704"
},
  {
  nodeId := "s3:s3_frontier:f9a3a368bb2df334",
  branchId := "P6:r28537377:d25",
  sourceParent := 6,
  targetParent := 27,
  valuation := 5,
  gainNum := 475,
  gainDen := 699626017,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P6:r28537377:d25",
    sourceParent := 6,
    targetParent := 27,
    valuation := 5,
    branchResidue := 28537377,
    branchDepth := 25,
    sourceModulus := 33554432,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P6:r28537377:d25",
    sourceParent := 6,
    targetParent := 27,
    valuation := 5,
    gainNum := 475,
    gainDen := 699626017,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P6:r28537377:d25",
    gainNum := 475,
    gainDen := 699626017,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "95714b834e21af30dba5afc4daf28827b0b5c2b4159c1bc0e795888fc0332b27"
},
  {
  nodeId := "s3:s3_frontier:fab1d1de1d50ffe7",
  branchId := "P11:r62421203:d26",
  sourceParent := 11,
  targetParent := 25,
  valuation := 4,
  gainNum := 198517,
  gainDen := 1203271891,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P11:r62421203:d26",
    sourceParent := 11,
    targetParent := 25,
    valuation := 4,
    branchResidue := 62421203,
    branchDepth := 26,
    sourceModulus := 67108864,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P11:r62421203:d26",
    sourceParent := 11,
    targetParent := 25,
    valuation := 4,
    gainNum := 198517,
    gainDen := 1203271891,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P11:r62421203:d26",
    gainNum := 198517,
    gainDen := 1203271891,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "2c4732a7154440af8b9463d8b309b3a55bc79f59b4876fca4727f7a56ec99343"
},
  {
  nodeId := "s3:s3_frontier:fae9971652cadf80",
  branchId := "P3:r62137837:d26",
  sourceParent := 3,
  targetParent := 29,
  valuation := 4,
  gainNum := 37,
  gainDen := 1471423981,
  exactCongruenceCertificate :=
{
    typeName := "S3_EXACT_CONGRUENCE",
    branchId := "P3:r62137837:d26",
    sourceParent := 3,
    targetParent := 29,
    valuation := 4,
    branchResidue := 62137837,
    branchDepth := 26,
    sourceModulus := 67108864,
    theoremName := "mixed_modulus_debt_transition_exactness",
    statement := "branch source/depth/residue and target valuation identify the exact mixed-modulus debt transition"
  },
  debtMeasureDefinition :=
{
    typeName := "MIXED_LOG_GAIN_RANK",
    measureId := "mixed_log_gain_rank",
    branchId := "P3:r62137837:d26",
    sourceParent := 3,
    targetParent := 29,
    valuation := 4,
    gainNum := 37,
    gainDen := 1471423981,
    decreaseInequality := "gain_num < gain_den"
  },
  localDescentCertificate :=
{
    typeName := "LOCAL_DESCENT_FROM_DEBT_GAIN",
    branchId := "P3:r62137837:d26",
    gainNum := 37,
    gainDen := 1471423981,
    rule := "positive denominator and gain ratio below one implies local debt descent"
  },
  certificateHash := "b98fd155156e52265072e986f529fa6113b4de790dbab63b03288659e2233e63"
}
]

def run024S4Certs : List S4TransitionCert :=
[
  {
  transitionId := "s4_parent_transition_00d713d77b0eca92",
  branchId := "P21:r61990091:d26",
  sourceParent := 21,
  targetParent := 23,
  valuation := 1,
  c := 9662482842,
  coefficient := 10460353203,
  divValuation := 1,
  kDivisibilityModulus := 2,
  kDivisibilityResidue := 0,
  excludedNextPowerModulus := 4,
  excludedNextPowerResidue := 2,
  oddModulus := 10460353203,
  inversePowerTwoMod3a := 5230176602,
  targetOddResidueMod3a := 4831241421,
  parentFloor := 22,
  membershipTargetParent := 23,
  certificateHash := "b02a8599b96034f6af7c24d4749c74fc18a4dfc0f1ef0716415f0d4b67c920bb"
},
  {
  transitionId := "s4_parent_transition_02814752dd490bdb",
  branchId := "P15:r48031555:d26",
  sourceParent := 15,
  targetParent := 19,
  valuation := 1,
  c := 10269885,
  coefficient := 14348907,
  divValuation := 1,
  kDivisibilityModulus := 2,
  kDivisibilityResidue := 1,
  excludedNextPowerModulus := 4,
  excludedNextPowerResidue := 1,
  oddModulus := 14348907,
  inversePowerTwoMod3a := 7174454,
  targetOddResidueMod3a := 12309396,
  parentFloor := 18,
  membershipTargetParent := 19,
  certificateHash := "c752d4ee72abdeb5cab499c2cce94b734a03a327ced8d4740a4aae524f5237a9"
},
  {
  transitionId := "s4_parent_transition_03fad997fd4b018c",
  branchId := "P9:r53252723:d26",
  sourceParent := 9,
  targetParent := 23,
  valuation := 0,
  c := 15619,
  coefficient := 19683,
  divValuation := 0,
  kDivisibilityModulus := 1,
  kDivisibilityResidue := 0,
  excludedNextPowerModulus := 2,
  excludedNextPowerResidue := 1,
  oddModulus := 19683,
  inversePowerTwoMod3a := 1,
  targetOddResidueMod3a := 15619,
  parentFloor := 23,
  membershipTargetParent := 23,
  certificateHash := "80a68d2a422dacf37d2f854f3610c418386f533ec625e020e4675ed99f72c11e"
},
  {
  transitionId := "s4_parent_transition_06f5a9967a24eb03",
  branchId := "P13:r29328293:d25",
  sourceParent := 13,
  targetParent := 24,
  valuation := 0,
  c := 1393520,
  coefficient := 1594323,
  divValuation := 0,
  kDivisibilityModulus := 1,
  kDivisibilityResidue := 0,
  excludedNextPowerModulus := 2,
  excludedNextPowerResidue := 0,
  oddModulus := 1594323,
  inversePowerTwoMod3a := 1,
  targetOddResidueMod3a := 1393520,
  parentFloor := 24,
  membershipTargetParent := 24,
  certificateHash := "a55f9f08f82480544db96b371e06a606aa39422e2c078020ba1e8a41aeae8042"
},
  {
  transitionId := "s4_parent_transition_0807fb707c1ebf40",
  branchId := "P6:r28537377:d25",
  sourceParent := 6,
  targetParent := 22,
  valuation := 0,
  c := 620,
  coefficient := 729,
  divValuation := 0,
  kDivisibilityModulus := 1,
  kDivisibilityResidue := 0,
  excludedNextPowerModulus := 2,
  excludedNextPowerResidue := 0,
  oddModulus := 729,
  inversePowerTwoMod3a := 1,
  targetOddResidueMod3a := 620,
  parentFloor := 22,
  membershipTargetParent := 22,
  certificateHash := "b963f507974272199449a837eb56c588dd0ba9caa3e067ca9e145da9ec579c59"
},
  {
  transitionId := "s4_parent_transition_0ba98f3c5018042b",
  branchId := "P24:r65338017:d26",
  sourceParent := 24,
  targetParent := 20,
  valuation := 1,
  c := 274976877211,
  coefficient := 282429536481,
  divValuation := 1,
  kDivisibilityModulus := 2,
  kDivisibilityResidue := 1,
  excludedNextPowerModulus := 4,
  excludedNextPowerResidue := 1,
  oddModulus := 282429536481,
  inversePowerTwoMod3a := 141214768241,
  targetOddResidueMod3a := 278703206846,
  parentFloor := 19,
  membershipTargetParent := 20,
  certificateHash := "92b9faacab64f45eb974c43959cfbe9731979d9af74f4bd5185c071c0b95488e"
},
  {
  transitionId := "s4_parent_transition_0db44a39edee5b85",
  branchId := "P22:r46520809:d26",
  sourceParent := 22,
  targetParent := 21,
  valuation := 1,
  c := 21753792171,
  coefficient := 31381059609,
  divValuation := 1,
  kDivisibilityModulus := 2,
  kDivisibilityResidue := 1,
  excludedNextPowerModulus := 4,
  excludedNextPowerResidue := 1,
  oddModulus := 31381059609,
  inversePowerTwoMod3a := 15690529805,
  targetOddResidueMod3a := 26567425890,
  parentFloor := 20,
  membershipTargetParent := 21,
  certificateHash := "10d38e3e12b60ec424e7d969cd82f9fa25ca520ea4168dd42fdb4cc83b5b14ab"
},
  {
  transitionId := "s4_parent_transition_0de9e54c5a8dfa71",
  branchId := "P23:r8412829:d24",
  sourceParent := 23,
  targetParent := 23,
  valuation := 0,
  c := 47207502424,
  coefficient := 94143178827,
  divValuation := 0,
  kDivisibilityModulus := 1,
  kDivisibilityResidue := 0,
  excludedNextPowerModulus := 2,
  excludedNextPowerResidue := 0,
  oddModulus := 94143178827,
  inversePowerTwoMod3a := 1,
  targetOddResidueMod3a := 47207502424,
  parentFloor := 23,
  membershipTargetParent := 23,
  certificateHash := "91cf4f23998e5a21873656520b5f0112e7e8ba52ddc810c5a847b4af433fc8c6"
},
  {
  transitionId := "s4_parent_transition_1406ce137ca56387",
  branchId := "P18:r26045717:d25",
  sourceParent := 18,
  targetParent := 24,
  valuation := 1,
  c := 300724638,
  coefficient := 387420489,
  divValuation := 1,
  kDivisibilityModulus := 2,
  kDivisibilityResidue := 0,
  excludedNextPowerModulus := 4,
  excludedNextPowerResidue := 2,
  oddModulus := 387420489,
  inversePowerTwoMod3a := 193710245,
  targetOddResidueMod3a := 150362319,
  parentFloor := 23,
  membershipTargetParent := 24,
  certificateHash := "bed7ee4a60a895adf5da89d8cdb2d4a00c59e0a7ee1c197b0c2bdb0857de2caf"
},
  {
  transitionId := "s4_parent_transition_17f4da3596f79a15",
  branchId := "P22:r44195593:d26",
  sourceParent := 22,
  targetParent := 21,
  valuation := 0,
  c := 20666488087,
  coefficient := 31381059609,
  divValuation := 0,
  kDivisibilityModulus := 1,
  kDivisibilityResidue := 0,
  excludedNextPowerModulus := 2,
  excludedNextPowerResidue := 1,
  oddModulus := 31381059609,
  inversePowerTwoMod3a := 1,
  targetOddResidueMod3a := 20666488087,
  parentFloor := 21,
  membershipTargetParent := 21,
  certificateHash := "4217f9b58d62a9d42dcdc32a6202acf43d30a323e97d1dc6c27ad620bd127a58"
},
  {
  transitionId := "s4_parent_transition_191daff4d8979099",
  branchId := "P24:r13730593:d24",
  sourceParent := 24,
  targetParent := 14,
  valuation := 1,
  c := 231142343080,
  coefficient := 282429536481,
  divValuation := 1,
  kDivisibilityModulus := 2,
  kDivisibilityResidue := 0,
  excludedNextPowerModulus := 4,
  excludedNextPowerResidue := 0,
  oddModulus := 282429536481,
  inversePowerTwoMod3a := 141214768241,
  targetOddResidueMod3a := 115571171540,
  parentFloor := 13,
  membershipTargetParent := 14,
  certificateHash := "7aa66b397b4ff24e3194fdf2f8e57b3baa265839628874e3eeb410b93135486b"
},
  {
  transitionId := "s4_parent_transition_1b11545e7125eb94",
  branchId := "P14:r56993193:d26",
  sourceParent := 14,
  targetParent := 22,
  valuation := 1,
  c := 4062007,
  coefficient := 4782969,
  divValuation := 1,
  kDivisibilityModulus := 2,
  kDivisibilityResidue := 1,
  excludedNextPowerModulus := 4,
  excludedNextPowerResidue := 1,
  oddModulus := 4782969,
  inversePowerTwoMod3a := 2391485,
  targetOddResidueMod3a := 4422488,
  parentFloor := 21,
  membershipTargetParent := 22,
  certificateHash := "74ecce5c96653382f6fdabb30fa932ae47f2ff3c50b9c4a9089a9c5ffb62af29"
},
  {
  transitionId := "s4_parent_transition_1bb845fa72c2fca8",
  branchId := "P21:r19295995:d25",
  sourceParent := 21,
  targetParent := 18,
  valuation := 0,
  c := 6015387866,
  coefficient := 10460353203,
  divValuation := 0,
  kDivisibilityModulus := 1,
  kDivisibilityResidue := 0,
  excludedNextPowerModulus := 2,
  excludedNextPowerResidue := 0,
  oddModulus := 10460353203,
  inversePowerTwoMod3a := 1,
  targetOddResidueMod3a := 6015387866,
  parentFloor := 18,
  membershipTargetParent := 18,
  certificateHash := "5bda5ae6bdfa7407a9978d82b4776422fde95c4a27c30fa6155b05ae766292ce"
},
  {
  transitionId := "s4_parent_transition_1c217065cafcd099",
  branchId := "P21:r60246179:d26",
  sourceParent := 21,
  targetParent := 23,
  valuation := 0,
  c := 9390656821,
  coefficient := 10460353203,
  divValuation := 0,
  kDivisibilityModulus := 1,
  kDivisibilityResidue := 0,
  excludedNextPowerModulus := 2,
  excludedNextPowerResidue := 1,
  oddModulus := 10460353203,
  inversePowerTwoMod3a := 1,
  targetOddResidueMod3a := 9390656821,
  parentFloor := 23,
  membershipTargetParent := 23,
  certificateHash := "5e8bc95cb002548443974e8ce05c599d0eee136046bded86aba31af4c87597d1"
},
  {
  transitionId := "s4_parent_transition_1c9910c9fde6ea15",
  branchId := "P15:r18997731:d25",
  sourceParent := 15,
  targetParent := 21,
  valuation := 1,
  c := 8124014,
  coefficient := 14348907,
  divValuation := 1,
  kDivisibilityModulus := 2,
  kDivisibilityResidue := 0,
  excludedNextPowerModulus := 4,
  excludedNextPowerResidue := 2,
  oddModulus := 14348907,
  inversePowerTwoMod3a := 7174454,
  targetOddResidueMod3a := 4062007,
  parentFloor := 20,
  membershipTargetParent := 21,
  certificateHash := "3eb0101828693256210666c9bf8e18e7352d27518837b0390ed594e29e8f140e"
},
  {
  transitionId := "s4_parent_transition_1e6ad3aaaeec0aaf",
  branchId := "P20:r10350509:d24",
  sourceParent := 20,
  targetParent := 22,
  valuation := 0,
  c := 2151131232,
  coefficient := 3486784401,
  divValuation := 0,
  kDivisibilityModulus := 1,
  kDivisibilityResidue := 0,
  excludedNextPowerModulus := 2,
  excludedNextPowerResidue := 0,
  oddModulus := 3486784401,
  inversePowerTwoMod3a := 1,
  targetOddResidueMod3a := 2151131232,
  parentFloor := 22,
  membershipTargetParent := 22,
  certificateHash := "88f912f3c70b1eb82fb9108b95b38bc6fd65ee68cb4f7c26feefe375df60df71"
},
  {
  transitionId := "s4_parent_transition_1ea4c13f8ced645e",
  branchId := "P19:r54618707:d26",
  sourceParent := 19,
  targetParent := 17,
  valuation := 0,
  c := 945943870,
  coefficient := 1162261467,
  divValuation := 0,
  kDivisibilityModulus := 1,
  kDivisibilityResidue := 0,
  excludedNextPowerModulus := 2,
  excludedNextPowerResidue := 0,
  oddModulus := 1162261467,
  inversePowerTwoMod3a := 1,
  targetOddResidueMod3a := 945943870,
  parentFloor := 17,
  membershipTargetParent := 17,
  certificateHash := "0cd25f1957ff8c3b5e417951fedab8936ac6a4a0b057c27f9df687b562f6580c"
},
  {
  transitionId := "s4_parent_transition_203334ac53d5f9da",
  branchId := "P23:r23687523:d25",
  sourceParent := 23,
  targetParent := 13,
  valuation := 0,
  c := 66459736638,
  coefficient := 94143178827,
  divValuation := 0,
  kDivisibilityModulus := 1,
  kDivisibilityResidue := 0,
  excludedNextPowerModulus := 2,
  excludedNextPowerResidue := 0,
  oddModulus := 94143178827,
  inversePowerTwoMod3a := 1,
  targetOddResidueMod3a := 66459736638,
  parentFloor := 13,
  membershipTargetParent := 13,
  certificateHash := "d782d800d70a2994461a7e42d0771a0396a3515f9d2c174adf117c699de1823d"
},
  {
  transitionId := "s4_parent_transition_210f91385ac0188a",
  branchId := "P21:r11861115:d24",
  sourceParent := 21,
  targetParent := 13,
  valuation := 1,
  c := 7395234840,
  coefficient := 10460353203,
  divValuation := 1,
  kDivisibilityModulus := 2,
  kDivisibilityResidue := 0,
  excludedNextPowerModulus := 4,
  excludedNextPowerResidue := 0,
  oddModulus := 10460353203,
  inversePowerTwoMod3a := 5230176602,
  targetOddResidueMod3a := 3697617420,
  parentFloor := 12,
  membershipTargetParent := 13,
  certificateHash := "d8c5f1d2589ac6237273c8b65d563a06e5d53e5ffd568e18a425571df9d33c77"
},
  {
  transitionId := "s4_parent_transition_24ad428ad57fc99f",
  branchId := "P22:r60472105:d26",
  sourceParent := 22,
  targetParent := 19,
  valuation := 1,
  c := 28277616675,
  coefficient := 31381059609,
  divValuation := 1,
  kDivisibilityModulus := 2,
  kDivisibilityResidue := 1,
  excludedNextPowerModulus := 4,
  excludedNextPowerResidue := 1,
  oddModulus := 31381059609,
  inversePowerTwoMod3a := 15690529805,
  targetOddResidueMod3a := 29829338142,
  parentFloor := 18,
  membershipTargetParent := 19,
  certificateHash := "3efe175b9ac0cc727ec9a75866d7ce43a4661d53eaeb6dcf13e91ba012e7e6ca"
},
  {
  transitionId := "s4_parent_transition_28a6d9f60c8dd5e9",
  branchId := "P19:r31051527:d25",
  sourceParent := 19,
  targetParent := 23,
  valuation := 0,
  c := 1075565616,
  coefficient := 1162261467,
  divValuation := 0,
  kDivisibilityModulus := 1,
  kDivisibilityResidue := 0,
  excludedNextPowerModulus := 2,
  excludedNextPowerResidue := 0,
  oddModulus := 1162261467,
  inversePowerTwoMod3a := 1,
  targetOddResidueMod3a := 1075565616,
  parentFloor := 23,
  membershipTargetParent := 23,
  certificateHash := "941db79f362da2cb95d9a897235b086b64eddeb04dd56199b5aea5646a7280a0"
},
  {
  transitionId := "s4_parent_transition_29d1aa27a1529076",
  branchId := "P24:r44001825:d26",
  sourceParent := 24,
  targetParent := 18,
  valuation := 0,
  c := 185182914720,
  coefficient := 282429536481,
  divValuation := 0,
  kDivisibilityModulus := 1,
  kDivisibilityResidue := 0,
  excludedNextPowerModulus := 2,
  excludedNextPowerResidue := 0,
  oddModulus := 282429536481,
  inversePowerTwoMod3a := 1,
  targetOddResidueMod3a := 185182914720,
  parentFloor := 18,
  membershipTargetParent := 18,
  certificateHash := "e420c0e7f33d725e12fdaaa48f34d452bc0c48d0e602f8dcbca6cbec66298645"
},
  {
  transitionId := "s4_parent_transition_29e79b406e4b155b",
  branchId := "P20:r16034097:d24",
  sourceParent := 20,
  targetParent := 19,
  valuation := 1,
  c := 3332343060,
  coefficient := 3486784401,
  divValuation := 1,
  kDivisibilityModulus := 2,
  kDivisibilityResidue := 0,
  excludedNextPowerModulus := 4,
  excludedNextPowerResidue := 0,
  oddModulus := 3486784401,
  inversePowerTwoMod3a := 1743392201,
  targetOddResidueMod3a := 1666171530,
  parentFloor := 18,
  membershipTargetParent := 19,
  certificateHash := "ae727618968a02404257b97dbf1c1f3108f70864fed62fb72a69ccc95f753e95"
},
  {
  transitionId := "s4_parent_transition_2b544bf43e6d34f8",
  branchId := "P24:r42451681:d26",
  sourceParent := 24,
  targetParent := 21,
  valuation := 1,
  c := 178659090216,
  coefficient := 282429536481,
  divValuation := 1,
  kDivisibilityModulus := 2,
  kDivisibilityResidue := 0,
  excludedNextPowerModulus := 4,
  excludedNextPowerResidue := 0,
  oddModulus := 282429536481,
  inversePowerTwoMod3a := 141214768241,
  targetOddResidueMod3a := 89329545108,
  parentFloor := 20,
  membershipTargetParent := 21,
  certificateHash := "f977c11288b16c3ea475546342b2eb483c63f40f0425e45817d1da0396265e33"
},
  {
  transitionId := "s4_parent_transition_2e45b85c0077d34e",
  branchId := "P20:r57887985:d26",
  sourceParent := 20,
  targetParent := 20,
  valuation := 1,
  c := 3007693933,
  coefficient := 3486784401,
  divValuation := 1,
  kDivisibilityModulus := 2,
  kDivisibilityResidue := 1,
  excludedNextPowerModulus := 4,
  excludedNextPowerResidue := 3,
  oddModulus := 3486784401,
  inversePowerTwoMod3a := 1743392201,
  targetOddResidueMod3a := 3247239167,
  parentFloor := 19,
  membershipTargetParent := 20,
  certificateHash := "c4b1ad555b6a45862c83419d487159d0384d0fc0a064bda2a5cae2f11e374786"
},
  {
  transitionId := "s4_parent_transition_2ecbcc773a0267fa",
  branchId := "P18:r29638393:d25",
  sourceParent := 18,
  targetParent := 17,
  valuation := 1,
  c := 342205784,
  coefficient := 387420489,
  divValuation := 1,
  kDivisibilityModulus := 2,
  kDivisibilityResidue := 0,
  excludedNextPowerModulus := 4,
  excludedNextPowerResidue := 0,
  oddModulus := 387420489,
  inversePowerTwoMod3a := 193710245,
  targetOddResidueMod3a := 171102892,
  parentFloor := 16,
  membershipTargetParent := 17,
  certificateHash := "44a1298f8bc11a0735af52f38c5f789fec6c5fcbcd8bb83bfaafe25ca65abdb7"
},
  {
  transitionId := "s4_parent_transition_2f42bec78a2933b8",
  branchId := "P10:r40120529:d26",
  sourceParent := 10,
  targetParent := 24,
  valuation := 1,
  c := 35302,
  coefficient := 59049,
  divValuation := 1,
  kDivisibilityModulus := 2,
  kDivisibilityResidue := 0,
  excludedNextPowerModulus := 4,
  excludedNextPowerResidue := 2,
  oddModulus := 59049,
  inversePowerTwoMod3a := 29525,
  targetOddResidueMod3a := 17651,
  parentFloor := 23,
  membershipTargetParent := 24,
  certificateHash := "69923adee4bdf713e2c6c461a5283426f19fa801bcd0814cf6ae8ebc0a6a3d4d"
},
  {
  transitionId := "s4_parent_transition_31f46f7034e9d25d",
  branchId := "P11:r35743131:d26",
  sourceParent := 11,
  targetParent := 24,
  valuation := 1,
  c := 94351,
  coefficient := 177147,
  divValuation := 1,
  kDivisibilityModulus := 2,
  kDivisibilityResidue := 1,
  excludedNextPowerModulus := 4,
  excludedNextPowerResidue := 3,
  oddModulus := 177147,
  inversePowerTwoMod3a := 88574,
  targetOddResidueMod3a := 135749,
  parentFloor := 23,
  membershipTargetParent := 24,
  certificateHash := "0bc322b7ccdd0f6a147afedebe03fd30481f474596470fb2d92ee586c2feb01e"
},
  {
  transitionId := "s4_parent_transition_3426b8286d8034a7",
  branchId := "P23:r25238487:d25",
  sourceParent := 23,
  targetParent := 23,
  valuation := 0,
  c := 70811253636,
  coefficient := 94143178827,
  divValuation := 0,
  kDivisibilityModulus := 1,
  kDivisibilityResidue := 0,
  excludedNextPowerModulus := 2,
  excludedNextPowerResidue := 0,
  oddModulus := 94143178827,
  inversePowerTwoMod3a := 1,
  targetOddResidueMod3a := 70811253636,
  parentFloor := 23,
  membershipTargetParent := 23,
  certificateHash := "35880863b7e6f72cce2182c21a609b10e75342e9a8c4fc2fb69671e39dc0e8fc"
},
  {
  transitionId := "s4_parent_transition_392e7d39f51b6c91",
  branchId := "P19:r52430323:d26",
  sourceParent := 19,
  targetParent := 21,
  valuation := 0,
  c := 908043148,
  coefficient := 1162261467,
  divValuation := 0,
  kDivisibilityModulus := 1,
  kDivisibilityResidue := 0,
  excludedNextPowerModulus := 2,
  excludedNextPowerResidue := 0,
  oddModulus := 1162261467,
  inversePowerTwoMod3a := 1,
  targetOddResidueMod3a := 908043148,
  parentFloor := 21,
  membershipTargetParent := 21,
  certificateHash := "1fab572c3bf9b8afac0136eaa5d2eac1f80d1500704c2838aa49b840cf387217"
},
  {
  transitionId := "s4_parent_transition_39862fd8328d8128",
  branchId := "P15:r32145719:d25",
  sourceParent := 15,
  targetParent := 23,
  valuation := 0,
  c := 13746498,
  coefficient := 14348907,
  divValuation := 0,
  kDivisibilityModulus := 1,
  kDivisibilityResidue := 0,
  excludedNextPowerModulus := 2,
  excludedNextPowerResidue := 0,
  oddModulus := 14348907,
  inversePowerTwoMod3a := 1,
  targetOddResidueMod3a := 13746498,
  parentFloor := 23,
  membershipTargetParent := 23,
  certificateHash := "f6aae519a8099d78cbd21ce628dc2bb43c4addc09d3230f5260e2864562e5f13"
},
  {
  transitionId := "s4_parent_transition_3b65a434ff2fdd58",
  branchId := "P19:r22134099:d25",
  sourceParent := 19,
  targetParent := 18,
  valuation := 1,
  c := 766682934,
  coefficient := 1162261467,
  divValuation := 1,
  kDivisibilityModulus := 2,
  kDivisibilityResidue := 0,
  excludedNextPowerModulus := 4,
  excludedNextPowerResidue := 2,
  oddModulus := 1162261467,
  inversePowerTwoMod3a := 581130734,
  targetOddResidueMod3a := 383341467,
  parentFloor := 17,
  membershipTargetParent := 18,
  certificateHash := "7f690d8757491f95e28ff5694a899313f3a39653dc86c86b4128a85eb73920b1"
},
  {
  transitionId := "s4_parent_transition_3bc8e0054e349117",
  branchId := "P19:r21039907:d25",
  sourceParent := 19,
  targetParent := 22,
  valuation := 1,
  c := 728782212,
  coefficient := 1162261467,
  divValuation := 1,
  kDivisibilityModulus := 2,
  kDivisibilityResidue := 0,
  excludedNextPowerModulus := 4,
  excludedNextPowerResidue := 0,
  oddModulus := 1162261467,
  inversePowerTwoMod3a := 581130734,
  targetOddResidueMod3a := 364391106,
  parentFloor := 21,
  membershipTargetParent := 22,
  certificateHash := "d2c38c3f884f3e44c5b8e991c90dfc1b3fdae38f6ec4c4274cbbf9af536b4078"
},
  {
  transitionId := "s4_parent_transition_3c5eb40805d45f78",
  branchId := "P23:r41191779:d26",
  sourceParent := 23,
  targetParent := 15,
  valuation := 0,
  c := 57785585770,
  coefficient := 94143178827,
  divValuation := 0,
  kDivisibilityModulus := 1,
  kDivisibilityResidue := 0,
  excludedNextPowerModulus := 2,
  excludedNextPowerResidue := 0,
  oddModulus := 94143178827,
  inversePowerTwoMod3a := 1,
  targetOddResidueMod3a := 57785585770,
  parentFloor := 15,
  membershipTargetParent := 15,
  certificateHash := "51a2792336563ec89813be294f610af389044d09fddd5d03ea818cb53f290b2b"
},
  {
  transitionId := "s4_parent_transition_436f635b20d3312e",
  branchId := "P6:r21817285:d25",
  sourceParent := 6,
  targetParent := 24,
  valuation := 1,
  c := 474,
  coefficient := 729,
  divValuation := 1,
  kDivisibilityModulus := 2,
  kDivisibilityResidue := 0,
  excludedNextPowerModulus := 4,
  excludedNextPowerResidue := 2,
  oddModulus := 729,
  inversePowerTwoMod3a := 365,
  targetOddResidueMod3a := 237,
  parentFloor := 23,
  membershipTargetParent := 24,
  certificateHash := "ddb1a428bf304b7f45fe07b95113aa4d63367ba47dfb92165ad60144344c1f74"
},
  {
  transitionId := "s4_parent_transition_438a19804119a819",
  branchId := "P9:r26781493:d25",
  sourceParent := 9,
  targetParent := 25,
  valuation := 1,
  c := 15710,
  coefficient := 19683,
  divValuation := 1,
  kDivisibilityModulus := 2,
  kDivisibilityResidue := 0,
  excludedNextPowerModulus := 4,
  excludedNextPowerResidue := 2,
  oddModulus := 19683,
  inversePowerTwoMod3a := 9842,
  targetOddResidueMod3a := 7855,
  parentFloor := 24,
  membershipTargetParent := 25,
  certificateHash := "dbe16cb5624558a90b84daed86b263aa4abe1f0a5982eaf007ca605747060b1e"
},
  {
  transitionId := "s4_parent_transition_4401f1b1812ff589",
  branchId := "P15:r3971459:d22",
  sourceParent := 15,
  targetParent := 17,
  valuation := 1,
  c := 13586544,
  coefficient := 14348907,
  divValuation := 1,
  kDivisibilityModulus := 2,
  kDivisibilityResidue := 0,
  excludedNextPowerModulus := 4,
  excludedNextPowerResidue := 0,
  oddModulus := 14348907,
  inversePowerTwoMod3a := 7174454,
  targetOddResidueMod3a := 6793272,
  parentFloor := 16,
  membershipTargetParent := 17,
  certificateHash := "226f0626ff00cb3652bde2b54cb9c96b133d91afc282ed94d6aaff8f8332d9d0"
},
  {
  transitionId := "s4_parent_transition_444282cae9449071",
  branchId := "P21:r8606597:d24",
  sourceParent := 21,
  targetParent := 24,
  valuation := 1,
  c := 5366089612,
  coefficient := 10460353203,
  divValuation := 1,
  kDivisibilityModulus := 2,
  kDivisibilityResidue := 0,
  excludedNextPowerModulus := 4,
  excludedNextPowerResidue := 0,
  oddModulus := 10460353203,
  inversePowerTwoMod3a := 5230176602,
  targetOddResidueMod3a := 2683044806,
  parentFloor := 23,
  membershipTargetParent := 24,
  certificateHash := "e0488522ccec2312100dab1bb1f97f1ad952a310a7b610b6193bcf9bc991fc2f"
},
  {
  transitionId := "s4_parent_transition_453f8349a32cd4fc",
  branchId := "P7:r9512459:d24",
  sourceParent := 7,
  targetParent := 22,
  valuation := 1,
  c := 1240,
  coefficient := 2187,
  divValuation := 1,
  kDivisibilityModulus := 2,
  kDivisibilityResidue := 0,
  excludedNextPowerModulus := 4,
  excludedNextPowerResidue := 0,
  oddModulus := 2187,
  inversePowerTwoMod3a := 1094,
  targetOddResidueMod3a := 620,
  parentFloor := 21,
  membershipTargetParent := 22,
  certificateHash := "3a87727b2b9691bbb57fe1f2213877a44671c7d6bcb4dc11d2cd364c3a6f35e4"
},
  {
  transitionId := "s4_parent_transition_45be2de04a3c3467",
  branchId := "P6:r21817285:d25",
  sourceParent := 6,
  targetParent := 23,
  valuation := 0,
  c := 474,
  coefficient := 729,
  divValuation := 0,
  kDivisibilityModulus := 1,
  kDivisibilityResidue := 0,
  excludedNextPowerModulus := 2,
  excludedNextPowerResidue := 0,
  oddModulus := 729,
  inversePowerTwoMod3a := 1,
  targetOddResidueMod3a := 474,
  parentFloor := 23,
  membershipTargetParent := 23,
  certificateHash := "8637d56c3da3604bcf7688192fe768c0ba1fb34326bd69bf6b3f2304ea559c86"
},
  {
  transitionId := "s4_parent_transition_4614fafefc30fc9b",
  branchId := "P20:r25819791:d25",
  sourceParent := 20,
  targetParent := 24,
  valuation := 0,
  c := 2683044806,
  coefficient := 3486784401,
  divValuation := 0,
  kDivisibilityModulus := 1,
  kDivisibilityResidue := 0,
  excludedNextPowerModulus := 2,
  excludedNextPowerResidue := 0,
  oddModulus := 3486784401,
  inversePowerTwoMod3a := 1,
  targetOddResidueMod3a := 2683044806,
  parentFloor := 24,
  membershipTargetParent := 24,
  certificateHash := "38297543a5caee41fec9db5921560e4cee497cbc13cb5ab2403b1079e45439ca"
},
  {
  transitionId := "s4_parent_transition_4806f11912d672ed",
  branchId := "P10:r26781493:d25",
  sourceParent := 10,
  targetParent := 24,
  valuation := 1,
  c := 47130,
  coefficient := 59049,
  divValuation := 1,
  kDivisibilityModulus := 2,
  kDivisibilityResidue := 0,
  excludedNextPowerModulus := 4,
  excludedNextPowerResidue := 2,
  oddModulus := 59049,
  inversePowerTwoMod3a := 29525,
  targetOddResidueMod3a := 23565,
  parentFloor := 23,
  membershipTargetParent := 24,
  certificateHash := "aad1e180c073c3ef0394d2b3e5427a71ec7779867e4e5cc96e965e60faa56ffa"
},
  {
  transitionId := "s4_parent_transition_4b098b4ba1d5a746",
  branchId := "P18:r16034097:d24",
  sourceParent := 18,
  targetParent := 21,
  valuation := 0,
  c := 370260340,
  coefficient := 387420489,
  divValuation := 0,
  kDivisibilityModulus := 1,
  kDivisibilityResidue := 0,
  excludedNextPowerModulus := 2,
  excludedNextPowerResidue := 0,
  oddModulus := 387420489,
  inversePowerTwoMod3a := 1,
  targetOddResidueMod3a := 370260340,
  parentFloor := 21,
  membershipTargetParent := 21,
  certificateHash := "03ef5741ffcbde6c46d8031e84f7872251b9c2a4e24d3926d89563403d467834"
},
  {
  transitionId := "s4_parent_transition_4c38e4a7266d75bf",
  branchId := "P23:r58889803:d26",
  sourceParent := 23,
  targetParent := 24,
  valuation := 1,
  c := 82613129242,
  coefficient := 94143178827,
  divValuation := 1,
  kDivisibilityModulus := 2,
  kDivisibilityResidue := 0,
  excludedNextPowerModulus := 4,
  excludedNextPowerResidue := 2,
  oddModulus := 94143178827,
  inversePowerTwoMod3a := 47071589414,
  targetOddResidueMod3a := 41306564621,
  parentFloor := 23,
  membershipTargetParent := 24,
  certificateHash := "7b98c43f0c68fe54dfd1abc7f03d82db59d6367cec475def472134baf0e77e73"
},
  {
  transitionId := "s4_parent_transition_4cd2efd7c78d5ac7",
  branchId := "P16:r33084861:d25",
  sourceParent := 16,
  targetParent := 23,
  valuation := 0,
  c := 42444312,
  coefficient := 43046721,
  divValuation := 0,
  kDivisibilityModulus := 1,
  kDivisibilityResidue := 0,
  excludedNextPowerModulus := 2,
  excludedNextPowerResidue := 0,
  oddModulus := 43046721,
  inversePowerTwoMod3a := 1,
  targetOddResidueMod3a := 42444312,
  parentFloor := 23,
  membershipTargetParent := 23,
  certificateHash := "c5b1df73134d0b01e818533cef0a535e89c5411907e8f688dc55f5bac5f4e2f5"
},
  {
  transitionId := "s4_parent_transition_4f422df724f5bb91",
  branchId := "P23:r25238487:d25",
  sourceParent := 23,
  targetParent := 24,
  valuation := 1,
  c := 70811253636,
  coefficient := 94143178827,
  divValuation := 1,
  kDivisibilityModulus := 2,
  kDivisibilityResidue := 0,
  excludedNextPowerModulus := 4,
  excludedNextPowerResidue := 0,
  oddModulus := 94143178827,
  inversePowerTwoMod3a := 47071589414,
  targetOddResidueMod3a := 35405626818,
  parentFloor := 23,
  membershipTargetParent := 24,
  certificateHash := "90635d768376698686e817030ad68a578574c2da34c7a62a1da555e3928c9185"
},
  {
  transitionId := "s4_parent_transition_5166b4b9aacc6bbb",
  branchId := "P14:r32145719:d25",
  sourceParent := 14,
  targetParent := 25,
  valuation := 1,
  c := 4582166,
  coefficient := 4782969,
  divValuation := 1,
  kDivisibilityModulus := 2,
  kDivisibilityResidue := 0,
  excludedNextPowerModulus := 4,
  excludedNextPowerResidue := 2,
  oddModulus := 4782969,
  inversePowerTwoMod3a := 2391485,
  targetOddResidueMod3a := 2291083,
  parentFloor := 24,
  membershipTargetParent := 25,
  certificateHash := "7fcd019c8b87aab91dcbe881fdfd83b98869c68c1b09c17dab8632f41f16ba8a"
},
  {
  transitionId := "s4_parent_transition_53e83acc56da9a50",
  branchId := "P14:r23693441:d25",
  sourceParent := 14,
  targetParent := 22,
  valuation := 0,
  c := 3377348,
  coefficient := 4782969,
  divValuation := 0,
  kDivisibilityModulus := 1,
  kDivisibilityResidue := 0,
  excludedNextPowerModulus := 2,
  excludedNextPowerResidue := 0,
  oddModulus := 4782969,
  inversePowerTwoMod3a := 1,
  targetOddResidueMod3a := 3377348,
  parentFloor := 22,
  membershipTargetParent := 22,
  certificateHash := "437956fabf460bcb2d4c7ba4da279a9f741b05bf31d96a6f54ec2022e033c329"
},
  {
  transitionId := "s4_parent_transition_5543ea7e65a7bcb9",
  branchId := "P18:r23219449:d25",
  sourceParent := 18,
  targetParent := 16,
  valuation := 1,
  c := 268092462,
  coefficient := 387420489,
  divValuation := 1,
  kDivisibilityModulus := 2,
  kDivisibilityResidue := 0,
  excludedNextPowerModulus := 4,
  excludedNextPowerResidue := 2,
  oddModulus := 387420489,
  inversePowerTwoMod3a := 193710245,
  targetOddResidueMod3a := 134046231,
  parentFloor := 15,
  membershipTargetParent := 16,
  certificateHash := "b1a3ec420cbb0b7bbc1d9e35e7ed2aa2aabd861f6b58ff3ea00e79614182b1bd"
},
  {
  transitionId := "s4_parent_transition_5a145150de15a7a7",
  branchId := "P21:r61990091:d26",
  sourceParent := 21,
  targetParent := 22,
  valuation := 0,
  c := 9662482842,
  coefficient := 10460353203,
  divValuation := 0,
  kDivisibilityModulus := 1,
  kDivisibilityResidue := 0,
  excludedNextPowerModulus := 2,
  excludedNextPowerResidue := 0,
  oddModulus := 10460353203,
  inversePowerTwoMod3a := 1,
  targetOddResidueMod3a := 9662482842,
  parentFloor := 22,
  membershipTargetParent := 22,
  certificateHash := "e255f5649cc09fb42c0372ecd84f869f25004f638e72bc520823f53e6a496f4e"
},
  {
  transitionId := "s4_parent_transition_5b443c65aaf01e2e",
  branchId := "P16:r23693441:d25",
  sourceParent := 16,
  targetParent := 20,
  valuation := 1,
  c := 30396132,
  coefficient := 43046721,
  divValuation := 1,
  kDivisibilityModulus := 2,
  kDivisibilityResidue := 0,
  excludedNextPowerModulus := 4,
  excludedNextPowerResidue := 0,
  oddModulus := 43046721,
  inversePowerTwoMod3a := 21523361,
  targetOddResidueMod3a := 15198066,
  parentFloor := 19,
  membershipTargetParent := 20,
  certificateHash := "cf3a1cd5d80779fde46cc70f025d2c9060f82276b8b3618b457c302ec2ecf402"
},
  {
  transitionId := "s4_parent_transition_5b9bcd945f331b14",
  branchId := "P21:r11861115:d24",
  sourceParent := 21,
  targetParent := 12,
  valuation := 0,
  c := 7395234840,
  coefficient := 10460353203,
  divValuation := 0,
  kDivisibilityModulus := 1,
  kDivisibilityResidue := 0,
  excludedNextPowerModulus := 2,
  excludedNextPowerResidue := 0,
  oddModulus := 10460353203,
  inversePowerTwoMod3a := 1,
  targetOddResidueMod3a := 7395234840,
  parentFloor := 12,
  membershipTargetParent := 12,
  certificateHash := "f15fa409f658b26d084535ed320fc68da66bdc9525c6e30a836c12bc6747cd78"
},
  {
  transitionId := "s4_parent_transition_5ca59b4dfd7f9649",
  branchId := "P11:r53666407:d26",
  sourceParent := 11,
  targetParent := 24,
  valuation := 0,
  c := 141663,
  coefficient := 177147,
  divValuation := 0,
  kDivisibilityModulus := 1,
  kDivisibilityResidue := 0,
  excludedNextPowerModulus := 2,
  excludedNextPowerResidue := 1,
  oddModulus := 177147,
  inversePowerTwoMod3a := 1,
  targetOddResidueMod3a := 141663,
  parentFloor := 24,
  membershipTargetParent := 24,
  certificateHash := "fc8a150159168b6cf4784a55ee374aaf0fa264d251fcdd8698164a046fe308c7"
},
  {
  transitionId := "s4_parent_transition_5ea0d1c6b4c2b3c7",
  branchId := "P8:r39706845:d26",
  sourceParent := 8,
  targetParent := 24,
  valuation := 0,
  c := 3882,
  coefficient := 6561,
  divValuation := 0,
  kDivisibilityModulus := 1,
  kDivisibilityResidue := 0,
  excludedNextPowerModulus := 2,
  excludedNextPowerResidue := 0,
  oddModulus := 6561,
  inversePowerTwoMod3a := 1,
  targetOddResidueMod3a := 3882,
  parentFloor := 24,
  membershipTargetParent := 24,
  certificateHash := "63fa7d21dcb032ce8cbc474a6f47262daf9f00b037cbf1eb7cd62c0c433b2c08"
},
  {
  transitionId := "s4_parent_transition_5ef1814f131f85bc",
  branchId := "P13:r36761851:d26",
  sourceParent := 13,
  targetParent := 22,
  valuation := 1,
  c := 873361,
  coefficient := 1594323,
  divValuation := 1,
  kDivisibilityModulus := 2,
  kDivisibilityResidue := 1,
  excludedNextPowerModulus := 4,
  excludedNextPowerResidue := 1,
  oddModulus := 1594323,
  inversePowerTwoMod3a := 797162,
  targetOddResidueMod3a := 1233842,
  parentFloor := 21,
  membershipTargetParent := 22,
  certificateHash := "801995cc830ec179746ec59adb953cbc60c138fdeba5e0161cdff9aa2de405b8"
},
  {
  transitionId := "s4_parent_transition_66b163e9c8649bf3",
  branchId := "P18:r26045717:d25",
  sourceParent := 18,
  targetParent := 23,
  valuation := 0,
  c := 300724638,
  coefficient := 387420489,
  divValuation := 0,
  kDivisibilityModulus := 1,
  kDivisibilityResidue := 0,
  excludedNextPowerModulus := 2,
  excludedNextPowerResidue := 0,
  oddModulus := 387420489,
  inversePowerTwoMod3a := 1,
  targetOddResidueMod3a := 300724638,
  parentFloor := 23,
  membershipTargetParent := 23,
  certificateHash := "6a4d5955b64c41dcf0eb036c4d85904233ff467b1125b7e30d968e54708917fe"
},
  {
  transitionId := "s4_parent_transition_6cbcc71be16709b8",
  branchId := "P23:r3988323:d22",
  sourceParent := 23,
  targetParent := 13,
  valuation := 0,
  c := 89519835808,
  coefficient := 94143178827,
  divValuation := 0,
  kDivisibilityModulus := 1,
  kDivisibilityResidue := 0,
  excludedNextPowerModulus := 2,
  excludedNextPowerResidue := 0,
  oddModulus := 94143178827,
  inversePowerTwoMod3a := 1,
  targetOddResidueMod3a := 89519835808,
  parentFloor := 13,
  membershipTargetParent := 13,
  certificateHash := "019d224d8ee49c88bcb1a721a17afa8e68f3abd9de9191ed97804f620a2922c5"
},
  {
  transitionId := "s4_parent_transition_70c33eb61a26f5fd",
  branchId := "P12:r43176689:d26",
  sourceParent := 12,
  targetParent := 21,
  valuation := 0,
  c := 341920,
  coefficient := 531441,
  divValuation := 0,
  kDivisibilityModulus := 1,
  kDivisibilityResidue := 0,
  excludedNextPowerModulus := 2,
  excludedNextPowerResidue := 0,
  oddModulus := 531441,
  inversePowerTwoMod3a := 1,
  targetOddResidueMod3a := 341920,
  parentFloor := 21,
  membershipTargetParent := 21,
  certificateHash := "dfb33837cdeb55d54cf1317711ec277b9bf02675df8a6e623fe185bf66f3b6b8"
},
  {
  transitionId := "s4_parent_transition_71a84cc4603cf571",
  branchId := "P22:r42451681:d26",
  sourceParent := 22,
  targetParent := 24,
  valuation := 1,
  c := 19851010024,
  coefficient := 31381059609,
  divValuation := 1,
  kDivisibilityModulus := 2,
  kDivisibilityResidue := 0,
  excludedNextPowerModulus := 4,
  excludedNextPowerResidue := 0,
  oddModulus := 31381059609,
  inversePowerTwoMod3a := 15690529805,
  targetOddResidueMod3a := 9925505012,
  parentFloor := 23,
  membershipTargetParent := 24,
  certificateHash := "3b7c2c86c9efdaa3b7aedb13415aea6a08ad1597202e545b271cb6f8d1dd9904"
},
  {
  transitionId := "s4_parent_transition_73499df187f4649c",
  branchId := "P20:r7378033:d23",
  sourceParent := 20,
  targetParent := 15,
  valuation := 0,
  c := 3066731736,
  coefficient := 3486784401,
  divValuation := 0,
  kDivisibilityModulus := 1,
  kDivisibilityResidue := 0,
  excludedNextPowerModulus := 2,
  excludedNextPowerResidue := 0,
  oddModulus := 3486784401,
  inversePowerTwoMod3a := 1,
  targetOddResidueMod3a := 3066731736,
  parentFloor := 15,
  membershipTargetParent := 15,
  certificateHash := "9c5c71158d0258ff6292ca00faa4ae9f2fc147564da9dda9e9758135e26de27b"
},
  {
  transitionId := "s4_parent_transition_74bb19d201b2981a",
  branchId := "P24:r7895841:d23",
  sourceParent := 24,
  targetParent := 12,
  valuation := 1,
  c := 265838946552,
  coefficient := 282429536481,
  divValuation := 1,
  kDivisibilityModulus := 2,
  kDivisibilityResidue := 0,
  excludedNextPowerModulus := 4,
  excludedNextPowerResidue := 0,
  oddModulus := 282429536481,
  inversePowerTwoMod3a := 141214768241,
  targetOddResidueMod3a := 132919473276,
  parentFloor := 11,
  membershipTargetParent := 12,
  certificateHash := "4c6468ebff15235b14b7882ee2b68ec7d053edd0780a8755a0eab39069ab22fa"
},
  {
  transitionId := "s4_parent_transition_7730b60f9e4b57f5",
  branchId := "P13:r3971459:d22",
  sourceParent := 13,
  targetParent := 20,
  valuation := 1,
  c := 1509616,
  coefficient := 1594323,
  divValuation := 1,
  kDivisibilityModulus := 2,
  kDivisibilityResidue := 0,
  excludedNextPowerModulus := 4,
  excludedNextPowerResidue := 0,
  oddModulus := 1594323,
  inversePowerTwoMod3a := 797162,
  targetOddResidueMod3a := 754808,
  parentFloor := 19,
  membershipTargetParent := 20,
  certificateHash := "b32e6a03155799d9b9b56f6fc76628f5cb7e11efb6c74f5464c35316a49a29d8"
},
  {
  transitionId := "s4_parent_transition_776f3ed8de792173",
  branchId := "P18:r10089145:d24",
  sourceParent := 18,
  targetParent := 19,
  valuation := 1,
  c := 232979148,
  coefficient := 387420489,
  divValuation := 1,
  kDivisibilityModulus := 2,
  kDivisibilityResidue := 0,
  excludedNextPowerModulus := 4,
  excludedNextPowerResidue := 0,
  oddModulus := 387420489,
  inversePowerTwoMod3a := 193710245,
  targetOddResidueMod3a := 116489574,
  parentFloor := 18,
  membershipTargetParent := 19,
  certificateHash := "3cd3cf5c2d79c526f9eaf9f09e7bddfc4da966c93bb1c86b1a209bba585d492a"
},
  {
  transitionId := "s4_parent_transition_7aa0281a229caf2e",
  branchId := "P15:r32145719:d25",
  sourceParent := 15,
  targetParent := 24,
  valuation := 1,
  c := 13746498,
  coefficient := 14348907,
  divValuation := 1,
  kDivisibilityModulus := 2,
  kDivisibilityResidue := 0,
  excludedNextPowerModulus := 4,
  excludedNextPowerResidue := 2,
  oddModulus := 14348907,
  inversePowerTwoMod3a := 7174454,
  targetOddResidueMod3a := 6873249,
  parentFloor := 23,
  membershipTargetParent := 24,
  certificateHash := "0632fa5ca679b5b745307d8334382c1cbf2af8fb4456cea837eda5f05ecc5ecf"
},
  {
  transitionId := "s4_parent_transition_7aa96c11766113a8",
  branchId := "P17:r48102291:d26",
  sourceParent := 17,
  targetParent := 24,
  valuation := 1,
  c := 92565085,
  coefficient := 129140163,
  divValuation := 1,
  kDivisibilityModulus := 2,
  kDivisibilityResidue := 1,
  excludedNextPowerModulus := 4,
  excludedNextPowerResidue := 1,
  oddModulus := 129140163,
  inversePowerTwoMod3a := 64570082,
  targetOddResidueMod3a := 110852624,
  parentFloor := 23,
  membershipTargetParent := 24,
  certificateHash := "cb61baef5a2f8874e9decf4cb91df8bd356b379e8f3690e5f09569d657ae660b"
},
  {
  transitionId := "s4_parent_transition_7ad997c5a00c4847",
  branchId := "P19:r22134099:d25",
  sourceParent := 19,
  targetParent := 17,
  valuation := 0,
  c := 766682934,
  coefficient := 1162261467,
  divValuation := 0,
  kDivisibilityModulus := 1,
  kDivisibilityResidue := 0,
  excludedNextPowerModulus := 2,
  excludedNextPowerResidue := 0,
  oddModulus := 1162261467,
  inversePowerTwoMod3a := 1,
  targetOddResidueMod3a := 766682934,
  parentFloor := 17,
  membershipTargetParent := 17,
  certificateHash := "7b2440bb3c4603ad3d78c3c129edba74232854fa07842a2f51e22e04bd941e52"
},
  {
  transitionId := "s4_parent_transition_7f9c6a275ec9f370",
  branchId := "P23:r41191779:d26",
  sourceParent := 23,
  targetParent := 16,
  valuation := 1,
  c := 57785585770,
  coefficient := 94143178827,
  divValuation := 1,
  kDivisibilityModulus := 2,
  kDivisibilityResidue := 0,
  excludedNextPowerModulus := 4,
  excludedNextPowerResidue := 2,
  oddModulus := 94143178827,
  inversePowerTwoMod3a := 47071589414,
  targetOddResidueMod3a := 28892792885,
  parentFloor := 15,
  membershipTargetParent := 16,
  certificateHash := "55c2b86f813f075745e5f391ab887c09956b65a59d1dd3a899ea141b6bc1ee72"
},
  {
  transitionId := "s4_parent_transition_80c66e525c87625c",
  branchId := "P15:r33084861:d25",
  sourceParent := 15,
  targetParent := 25,
  valuation := 1,
  c := 14148104,
  coefficient := 14348907,
  divValuation := 1,
  kDivisibilityModulus := 2,
  kDivisibilityResidue := 0,
  excludedNextPowerModulus := 4,
  excludedNextPowerResidue := 0,
  oddModulus := 14348907,
  inversePowerTwoMod3a := 7174454,
  targetOddResidueMod3a := 7074052,
  parentFloor := 24,
  membershipTargetParent := 25,
  certificateHash := "706e1228727ac314a7c6f2f514ee52ca042dc1b409adc25a5d9a90e0adebf084"
},
  {
  transitionId := "s4_parent_transition_810f5428f3767d29",
  branchId := "P14:r12423737:d24",
  sourceParent := 14,
  targetParent := 21,
  valuation := 1,
  c := 3541848,
  coefficient := 4782969,
  divValuation := 1,
  kDivisibilityModulus := 2,
  kDivisibilityResidue := 0,
  excludedNextPowerModulus := 4,
  excludedNextPowerResidue := 0,
  oddModulus := 4782969,
  inversePowerTwoMod3a := 2391485,
  targetOddResidueMod3a := 1770924,
  parentFloor := 20,
  membershipTargetParent := 21,
  certificateHash := "58f465296bdb6cc9109b86143417ffb954c118f92825bba5acd775965fecb70c"
},
  {
  transitionId := "s4_parent_transition_81fc270267ae0b47",
  branchId := "P19:r52479059:d26",
  sourceParent := 19,
  targetParent := 16,
  valuation := 0,
  c := 908887209,
  coefficient := 1162261467,
  divValuation := 0,
  kDivisibilityModulus := 1,
  kDivisibilityResidue := 0,
  excludedNextPowerModulus := 2,
  excludedNextPowerResidue := 1,
  oddModulus := 1162261467,
  inversePowerTwoMod3a := 1,
  targetOddResidueMod3a := 908887209,
  parentFloor := 16,
  membershipTargetParent := 16,
  certificateHash := "ca380cff42827c1d5716e9826691da0cefed7624fec5a1035394818f63df544a"
},
  {
  transitionId := "s4_parent_transition_85db664a21bd7d0b",
  branchId := "P23:r60246179:d26",
  sourceParent := 23,
  targetParent := 20,
  valuation := 0,
  c := 84515911389,
  coefficient := 94143178827,
  divValuation := 0,
  kDivisibilityModulus := 1,
  kDivisibilityResidue := 0,
  excludedNextPowerModulus := 2,
  excludedNextPowerResidue := 1,
  oddModulus := 94143178827,
  inversePowerTwoMod3a := 1,
  targetOddResidueMod3a := 84515911389,
  parentFloor := 20,
  membershipTargetParent := 20,
  certificateHash := "39d1ebf9eb3761ed14e339005d5f052872714542a13550a98aa5b7b69eb931e3"
},
  {
  transitionId := "s4_parent_transition_874f308aaaed1445",
  branchId := "P12:r34008209:d26",
  sourceParent := 12,
  targetParent := 20,
  valuation := 1,
  c := 269314,
  coefficient := 531441,
  divValuation := 1,
  kDivisibilityModulus := 2,
  kDivisibilityResidue := 0,
  excludedNextPowerModulus := 4,
  excludedNextPowerResidue := 2,
  oddModulus := 531441,
  inversePowerTwoMod3a := 265721,
  targetOddResidueMod3a := 134657,
  parentFloor := 19,
  membershipTargetParent := 20,
  certificateHash := "cb6aff033e57245266d96daf0835c7322c108d35e36b60bf3826bc0fe2953ae3"
},
  {
  transitionId := "s4_parent_transition_898cfb7938766503",
  branchId := "P16:r6332577:d23",
  sourceParent := 16,
  targetParent := 19,
  valuation := 1,
  c := 32496056,
  coefficient := 43046721,
  divValuation := 1,
  kDivisibilityModulus := 2,
  kDivisibilityResidue := 0,
  excludedNextPowerModulus := 4,
  excludedNextPowerResidue := 0,
  oddModulus := 43046721,
  inversePowerTwoMod3a := 21523361,
  targetOddResidueMod3a := 16248028,
  parentFloor := 18,
  membershipTargetParent := 19,
  certificateHash := "4177bbd57b99a4712f38f7758bb7b22cbed95ae44be66b28729264d3528ba09a"
},
  {
  transitionId := "s4_parent_transition_8c3b1607df18f1ef",
  branchId := "P23:r59471107:d26",
  sourceParent := 23,
  targetParent := 21,
  valuation := 0,
  c := 83428607305,
  coefficient := 94143178827,
  divValuation := 0,
  kDivisibilityModulus := 1,
  kDivisibilityResidue := 0,
  excludedNextPowerModulus := 2,
  excludedNextPowerResidue := 1,
  oddModulus := 94143178827,
  inversePowerTwoMod3a := 1,
  targetOddResidueMod3a := 83428607305,
  parentFloor := 21,
  membershipTargetParent := 21,
  certificateHash := "823811f73eaf7e4f106840a17d39d5bd5c98f3988a7397860e02dba8af101bd6"
},
  {
  transitionId := "s4_parent_transition_8d017323e11dbb48",
  branchId := "P18:r16034097:d24",
  sourceParent := 18,
  targetParent := 22,
  valuation := 1,
  c := 370260340,
  coefficient := 387420489,
  divValuation := 1,
  kDivisibilityModulus := 2,
  kDivisibilityResidue := 0,
  excludedNextPowerModulus := 4,
  excludedNextPowerResidue := 0,
  oddModulus := 387420489,
  inversePowerTwoMod3a := 193710245,
  targetOddResidueMod3a := 185130170,
  parentFloor := 21,
  membershipTargetParent := 22,
  certificateHash := "ddc38650ea162c4eeb21299a04385c86563433840c39e21241ec94d5bb4b778a"
},
  {
  transitionId := "s4_parent_transition_8ddf9c022806dab0",
  branchId := "P11:r62628045:d26",
  sourceParent := 11,
  targetParent := 26,
  valuation := 1,
  c := 165319,
  coefficient := 177147,
  divValuation := 1,
  kDivisibilityModulus := 2,
  kDivisibilityResidue := 1,
  excludedNextPowerModulus := 4,
  excludedNextPowerResidue := 3,
  oddModulus := 177147,
  inversePowerTwoMod3a := 88574,
  targetOddResidueMod3a := 171233,
  parentFloor := 25,
  membershipTargetParent := 26,
  certificateHash := "06568fb35b764da614c526c23f9a087291678008eca360c807b233b5cd4b7634"
},
  {
  transitionId := "s4_parent_transition_9345b136c22eed21",
  branchId := "P16:r11028287:d24",
  sourceParent := 16,
  targetParent := 23,
  valuation := 0,
  c := 28296208,
  coefficient := 43046721,
  divValuation := 0,
  kDivisibilityModulus := 1,
  kDivisibilityResidue := 0,
  excludedNextPowerModulus := 2,
  excludedNextPowerResidue := 0,
  oddModulus := 43046721,
  inversePowerTwoMod3a := 1,
  targetOddResidueMod3a := 28296208,
  parentFloor := 23,
  membershipTargetParent := 23,
  certificateHash := "117327ad510306835a9a5b4e81f1fdd913a8d9e1d008c76a78f94b8cb6546997"
},
  {
  transitionId := "s4_parent_transition_93c8d05f255788c1",
  branchId := "P17:r26045717:d25",
  sourceParent := 17,
  targetParent := 24,
  valuation := 0,
  c := 100241546,
  coefficient := 129140163,
  divValuation := 0,
  kDivisibilityModulus := 1,
  kDivisibilityResidue := 0,
  excludedNextPowerModulus := 2,
  excludedNextPowerResidue := 0,
  oddModulus := 129140163,
  inversePowerTwoMod3a := 1,
  targetOddResidueMod3a := 100241546,
  parentFloor := 24,
  membershipTargetParent := 24,
  certificateHash := "f46534e3c352b3d79351f122b2008dda4e093328fef409d8fadbe1a78fb6c149"
},
  {
  transitionId := "s4_parent_transition_988d3e16038d104a",
  branchId := "P21:r65477915:d26",
  sourceParent := 21,
  targetParent := 22,
  valuation := 1,
  c := 10206134884,
  coefficient := 10460353203,
  divValuation := 1,
  kDivisibilityModulus := 2,
  kDivisibilityResidue := 0,
  excludedNextPowerModulus := 4,
  excludedNextPowerResidue := 0,
  oddModulus := 10460353203,
  inversePowerTwoMod3a := 5230176602,
  targetOddResidueMod3a := 5103067442,
  parentFloor := 21,
  membershipTargetParent := 22,
  certificateHash := "f8da1c567ab1de0238bad088ec6b86e0fea334ec7ef37a164cf1b1d7987a12e1"
},
  {
  transitionId := "s4_parent_transition_98cc8134ef284a4b",
  branchId := "P23:r59471107:d26",
  sourceParent := 23,
  targetParent := 22,
  valuation := 1,
  c := 83428607305,
  coefficient := 94143178827,
  divValuation := 1,
  kDivisibilityModulus := 2,
  kDivisibilityResidue := 1,
  excludedNextPowerModulus := 4,
  excludedNextPowerResidue := 1,
  oddModulus := 94143178827,
  inversePowerTwoMod3a := 47071589414,
  targetOddResidueMod3a := 88785893066,
  parentFloor := 21,
  membershipTargetParent := 22,
  certificateHash := "35ad6a773125bf341f5b2308a09980fe197c4f84fd7c39b04de3d80333758fb3"
},
  {
  transitionId := "s4_parent_transition_9cb70964d8126ce5",
  branchId := "P21:r60246179:d26",
  sourceParent := 21,
  targetParent := 24,
  valuation := 1,
  c := 9390656821,
  coefficient := 10460353203,
  divValuation := 1,
  kDivisibilityModulus := 2,
  kDivisibilityResidue := 1,
  excludedNextPowerModulus := 4,
  excludedNextPowerResidue := 1,
  oddModulus := 10460353203,
  inversePowerTwoMod3a := 5230176602,
  targetOddResidueMod3a := 9925505012,
  parentFloor := 23,
  membershipTargetParent := 24,
  certificateHash := "60c963d2873599706acbbc4680729dfe5841179ec80eb097db39e1753a5f84eb"
},
  {
  transitionId := "s4_parent_transition_9ccfd4012ae0eec4",
  branchId := "P8:r64316497:d26",
  sourceParent := 8,
  targetParent := 22,
  valuation := 0,
  c := 6288,
  coefficient := 6561,
  divValuation := 0,
  kDivisibilityModulus := 1,
  kDivisibilityResidue := 0,
  excludedNextPowerModulus := 2,
  excludedNextPowerResidue := 0,
  oddModulus := 6561,
  inversePowerTwoMod3a := 1,
  targetOddResidueMod3a := 6288,
  parentFloor := 22,
  membershipTargetParent := 22,
  certificateHash := "35c1b4a6915332f97f64265d6a2ae6a6dff61efbfcb6627f027b133791eb6b20"
},
  {
  transitionId := "s4_parent_transition_9e22d638e49d9ac2",
  branchId := "P24:r64369177:d26",
  sourceParent := 24,
  targetParent := 23,
  valuation := 0,
  c := 270899486896,
  coefficient := 282429536481,
  divValuation := 0,
  kDivisibilityModulus := 1,
  kDivisibilityResidue := 0,
  excludedNextPowerModulus := 2,
  excludedNextPowerResidue := 0,
  oddModulus := 282429536481,
  inversePowerTwoMod3a := 1,
  targetOddResidueMod3a := 270899486896,
  parentFloor := 23,
  membershipTargetParent := 23,
  certificateHash := "5a32a0af240700ac0c802cb8a19b1d57e12f318358375c62e0e0e5277f64d0db"
},
  {
  transitionId := "s4_parent_transition_9f95bc070cc28742",
  branchId := "P14:r55974473:d26",
  sourceParent := 14,
  targetParent := 19,
  valuation := 0,
  c := 3989401,
  coefficient := 4782969,
  divValuation := 0,
  kDivisibilityModulus := 1,
  kDivisibilityResidue := 0,
  excludedNextPowerModulus := 2,
  excludedNextPowerResidue := 1,
  oddModulus := 4782969,
  inversePowerTwoMod3a := 1,
  targetOddResidueMod3a := 3989401,
  parentFloor := 19,
  membershipTargetParent := 19,
  certificateHash := "590e0e218a21ec3c1f9ed07b27bdaf65de3484d594c92f570a17f032952f7def"
},
  {
  transitionId := "s4_parent_transition_a0f9c0245d334dd5",
  branchId := "P4:r62137837:d26",
  sourceParent := 4,
  targetParent := 24,
  valuation := 0,
  c := 75,
  coefficient := 81,
  divValuation := 0,
  kDivisibilityModulus := 1,
  kDivisibilityResidue := 0,
  excludedNextPowerModulus := 2,
  excludedNextPowerResidue := 1,
  oddModulus := 81,
  inversePowerTwoMod3a := 1,
  targetOddResidueMod3a := 75,
  parentFloor := 24,
  membershipTargetParent := 24,
  certificateHash := "4aec617e05dd9a228b8a59bf72c273319c8d47ab4124e2d77e099870a04fd79f"
},
  {
  transitionId := "s4_parent_transition_a3f69d4b6dbb7750",
  branchId := "P17:r55141435:d26",
  sourceParent := 17,
  targetParent := 23,
  valuation := 1,
  c := 106110780,
  coefficient := 129140163,
  divValuation := 1,
  kDivisibilityModulus := 2,
  kDivisibilityResidue := 0,
  excludedNextPowerModulus := 4,
  excludedNextPowerResidue := 0,
  oddModulus := 129140163,
  inversePowerTwoMod3a := 64570082,
  targetOddResidueMod3a := 53055390,
  parentFloor := 22,
  membershipTargetParent := 23,
  certificateHash := "6b76e8993e685c5963d852372b4997a8b0c5da7335044de0885ac182d77d04a4"
},
  {
  transitionId := "s4_parent_transition_a448b7c1f27b2041",
  branchId := "P17:r30267435:d25",
  sourceParent := 17,
  targetParent := 20,
  valuation := 1,
  c := 116489574,
  coefficient := 129140163,
  divValuation := 1,
  kDivisibilityModulus := 2,
  kDivisibilityResidue := 0,
  excludedNextPowerModulus := 4,
  excludedNextPowerResidue := 2,
  oddModulus := 129140163,
  inversePowerTwoMod3a := 64570082,
  targetOddResidueMod3a := 58244787,
  parentFloor := 19,
  membershipTargetParent := 20,
  certificateHash := "617194ed903637ee6c9dfa68a682f97a90c17a38ddc095aa54801111fef0a742"
},
  {
  transitionId := "s4_parent_transition_a4af4f003d861604",
  branchId := "P12:r11914377:d24",
  sourceParent := 12,
  targetParent := 21,
  valuation := 0,
  c := 377404,
  coefficient := 531441,
  divValuation := 0,
  kDivisibilityModulus := 1,
  kDivisibilityResidue := 0,
  excludedNextPowerModulus := 2,
  excludedNextPowerResidue := 0,
  oddModulus := 531441,
  inversePowerTwoMod3a := 1,
  targetOddResidueMod3a := 377404,
  parentFloor := 21,
  membershipTargetParent := 21,
  certificateHash := "99f275e3422873672ad2897fd1a3a53c47f9c8cdb74c5e50a6963f0c8883bf0f"
},
  {
  transitionId := "s4_parent_transition_a87d62bc3a48cd64",
  branchId := "P16:r58415169:d26",
  sourceParent := 16,
  targetParent := 19,
  valuation := 0,
  c := 37470184,
  coefficient := 43046721,
  divValuation := 0,
  kDivisibilityModulus := 1,
  kDivisibilityResidue := 0,
  excludedNextPowerModulus := 2,
  excludedNextPowerResidue := 0,
  oddModulus := 43046721,
  inversePowerTwoMod3a := 1,
  targetOddResidueMod3a := 37470184,
  parentFloor := 19,
  membershipTargetParent := 19,
  certificateHash := "178206bb77d3f607200f6926de5c743b58d44a511bc3ad32db22fe33bad035e9"
},
  {
  transitionId := "s4_parent_transition_a8d401c5f0c853b6",
  branchId := "P24:r64562945:d26",
  sourceParent := 24,
  targetParent := 22,
  valuation := 1,
  c := 271714964959,
  coefficient := 282429536481,
  divValuation := 1,
  kDivisibilityModulus := 2,
  kDivisibilityResidue := 1,
  excludedNextPowerModulus := 4,
  excludedNextPowerResidue := 1,
  oddModulus := 282429536481,
  inversePowerTwoMod3a := 141214768241,
  targetOddResidueMod3a := 277072250720,
  parentFloor := 21,
  membershipTargetParent := 22,
  certificateHash := "a69623f01500383af0ca060758bcd957176174915a89efec4596b583d0d1947a"
},
  {
  transitionId := "s4_parent_transition_a948aa87eff4a2ea",
  branchId := "P23:r60246179:d26",
  sourceParent := 23,
  targetParent := 21,
  valuation := 1,
  c := 84515911389,
  coefficient := 94143178827,
  divValuation := 1,
  kDivisibilityModulus := 2,
  kDivisibilityResidue := 1,
  excludedNextPowerModulus := 4,
  excludedNextPowerResidue := 1,
  oddModulus := 94143178827,
  inversePowerTwoMod3a := 47071589414,
  targetOddResidueMod3a := 89329545108,
  parentFloor := 20,
  membershipTargetParent := 21,
  certificateHash := "ee26feb236252f7615e7fad683c0fb30acd620cbb38f609af51cb19d6b8e6b81"
},
  {
  transitionId := "s4_parent_transition_a9e98cc7fb21f453",
  branchId := "P19:r54618707:d26",
  sourceParent := 19,
  targetParent := 18,
  valuation := 1,
  c := 945943870,
  coefficient := 1162261467,
  divValuation := 1,
  kDivisibilityModulus := 2,
  kDivisibilityResidue := 0,
  excludedNextPowerModulus := 4,
  excludedNextPowerResidue := 2,
  oddModulus := 1162261467,
  inversePowerTwoMod3a := 581130734,
  targetOddResidueMod3a := 472971935,
  parentFloor := 17,
  membershipTargetParent := 18,
  certificateHash := "52ce242bc3e5ef3fd752068f5db7d0a32f404f3dcd58b3c851aff7e546a39376"
},
  {
  transitionId := "s4_parent_transition_aa1c2011c59200a1",
  branchId := "P19:r48102291:d26",
  sourceParent := 19,
  targetParent := 20,
  valuation := 0,
  c := 833085765,
  coefficient := 1162261467,
  divValuation := 0,
  kDivisibilityModulus := 1,
  kDivisibilityResidue := 0,
  excludedNextPowerModulus := 2,
  excludedNextPowerResidue := 1,
  oddModulus := 1162261467,
  inversePowerTwoMod3a := 1,
  targetOddResidueMod3a := 833085765,
  parentFloor := 20,
  membershipTargetParent := 20,
  certificateHash := "3343189e42ca439358bddce1e8da61296be6fcbf96e515ffaaafa63ab14e4c9c"
},
  {
  transitionId := "s4_parent_transition_acb3b77ed6bee4b8",
  branchId := "P13:r29328293:d25",
  sourceParent := 13,
  targetParent := 25,
  valuation := 1,
  c := 1393520,
  coefficient := 1594323,
  divValuation := 1,
  kDivisibilityModulus := 2,
  kDivisibilityResidue := 0,
  excludedNextPowerModulus := 4,
  excludedNextPowerResidue := 0,
  oddModulus := 1594323,
  inversePowerTwoMod3a := 797162,
  targetOddResidueMod3a := 696760,
  parentFloor := 24,
  membershipTargetParent := 25,
  certificateHash := "12e749a501a7675beeb0aa7d4864492f5bc2d62ca5870ac5b87482b2b7b44b7b"
},
  {
  transitionId := "s4_parent_transition_ace57692188d01dc",
  branchId := "P19:r52430323:d26",
  sourceParent := 19,
  targetParent := 22,
  valuation := 1,
  c := 908043148,
  coefficient := 1162261467,
  divValuation := 1,
  kDivisibilityModulus := 2,
  kDivisibilityResidue := 0,
  excludedNextPowerModulus := 4,
  excludedNextPowerResidue := 0,
  oddModulus := 1162261467,
  inversePowerTwoMod3a := 581130734,
  targetOddResidueMod3a := 454021574,
  parentFloor := 21,
  membershipTargetParent := 22,
  certificateHash := "88d425b6ab46f0975afd97d623f1bb7691a96e53a119a957b796ea0a3e8c9a02"
},
  {
  transitionId := "s4_parent_transition_b04cf1496e5af295",
  branchId := "P16:r6332577:d23",
  sourceParent := 16,
  targetParent := 18,
  valuation := 0,
  c := 32496056,
  coefficient := 43046721,
  divValuation := 0,
  kDivisibilityModulus := 1,
  kDivisibilityResidue := 0,
  excludedNextPowerModulus := 2,
  excludedNextPowerResidue := 0,
  oddModulus := 43046721,
  inversePowerTwoMod3a := 1,
  targetOddResidueMod3a := 32496056,
  parentFloor := 18,
  membershipTargetParent := 18,
  certificateHash := "df22cd8931ab46172a572896b0154811515c86b1938c1ba3669b64ac1be65e83"
},
  {
  transitionId := "s4_parent_transition_b128d8c3863b4b1f",
  branchId := "P15:r26510867:d25",
  sourceParent := 15,
  targetParent := 22,
  valuation := 1,
  c := 11336862,
  coefficient := 14348907,
  divValuation := 1,
  kDivisibilityModulus := 2,
  kDivisibilityResidue := 0,
  excludedNextPowerModulus := 4,
  excludedNextPowerResidue := 2,
  oddModulus := 14348907,
  inversePowerTwoMod3a := 7174454,
  targetOddResidueMod3a := 5668431,
  parentFloor := 21,
  membershipTargetParent := 22,
  certificateHash := "1294c71a7bbdc7187dc5662d5d6514807c718e090604c23dabd44533a4c03abb"
},
  {
  transitionId := "s4_parent_transition_b22a18621303ffab",
  branchId := "P15:r33084861:d25",
  sourceParent := 15,
  targetParent := 24,
  valuation := 0,
  c := 14148104,
  coefficient := 14348907,
  divValuation := 0,
  kDivisibilityModulus := 1,
  kDivisibilityResidue := 0,
  excludedNextPowerModulus := 2,
  excludedNextPowerResidue := 0,
  oddModulus := 14348907,
  inversePowerTwoMod3a := 1,
  targetOddResidueMod3a := 14148104,
  parentFloor := 24,
  membershipTargetParent := 24,
  certificateHash := "47fee67cce3456ff5815e2f527676c44341931d2e7c48b634bd91a4fa21ac40b"
},
  {
  transitionId := "s4_parent_transition_b759f5483bad615a",
  branchId := "P23:r61796323:d26",
  sourceParent := 23,
  targetParent := 20,
  valuation := 1,
  c := 86690519557,
  coefficient := 94143178827,
  divValuation := 1,
  kDivisibilityModulus := 2,
  kDivisibilityResidue := 1,
  excludedNextPowerModulus := 4,
  excludedNextPowerResidue := 1,
  oddModulus := 94143178827,
  inversePowerTwoMod3a := 47071589414,
  targetOddResidueMod3a := 90416849192,
  parentFloor := 19,
  membershipTargetParent := 20,
  certificateHash := "cf4c0246a05e84e5c4fa87a6b4b6a38afeb11a32ce50334aba9dcdf513b22255"
},
  {
  transitionId := "s4_parent_transition_bec479111ae6c0ae",
  branchId := "P13:r20876015:d25",
  sourceParent := 13,
  targetParent := 23,
  valuation := 0,
  c := 991914,
  coefficient := 1594323,
  divValuation := 0,
  kDivisibilityModulus := 1,
  kDivisibilityResidue := 0,
  excludedNextPowerModulus := 2,
  excludedNextPowerResidue := 0,
  oddModulus := 1594323,
  inversePowerTwoMod3a := 1,
  targetOddResidueMod3a := 991914,
  parentFloor := 23,
  membershipTargetParent := 23,
  certificateHash := "59e2c755e1fba7b31c3e6e842525196c85d098f485a3de8b7e6d09ad6ce8de4b"
},
  {
  transitionId := "s4_parent_transition_bf7cd6d16b97f54c",
  branchId := "P24:r39996193:d26",
  sourceParent := 24,
  targetParent := 13,
  valuation := 1,
  c := 168325100094,
  coefficient := 282429536481,
  divValuation := 1,
  kDivisibilityModulus := 2,
  kDivisibilityResidue := 0,
  excludedNextPowerModulus := 4,
  excludedNextPowerResidue := 2,
  oddModulus := 282429536481,
  inversePowerTwoMod3a := 141214768241,
  targetOddResidueMod3a := 84162550047,
  parentFloor := 12,
  membershipTargetParent := 13,
  certificateHash := "4c5f834024196cee031dd14709667338eaa37188d20be83209479a678fab5ee9"
},
  {
  transitionId := "s4_parent_transition_c5577cbbffbf33dd",
  branchId := "P17:r26045717:d25",
  sourceParent := 17,
  targetParent := 25,
  valuation := 1,
  c := 100241546,
  coefficient := 129140163,
  divValuation := 1,
  kDivisibilityModulus := 2,
  kDivisibilityResidue := 0,
  excludedNextPowerModulus := 4,
  excludedNextPowerResidue := 2,
  oddModulus := 129140163,
  inversePowerTwoMod3a := 64570082,
  targetOddResidueMod3a := 50120773,
  parentFloor := 24,
  membershipTargetParent := 25,
  certificateHash := "5ef3ae8000a5f5a73435f5269424feb15c0d80c7b9cfa9246d2b5274c8809017"
},
  {
  transitionId := "s4_parent_transition_c8886c7ca2fc96b1",
  branchId := "P19:r5344699:d23",
  sourceParent := 19,
  targetParent := 20,
  valuation := 0,
  c := 740520680,
  coefficient := 1162261467,
  divValuation := 0,
  kDivisibilityModulus := 1,
  kDivisibilityResidue := 0,
  excludedNextPowerModulus := 2,
  excludedNextPowerResidue := 0,
  oddModulus := 1162261467,
  inversePowerTwoMod3a := 1,
  targetOddResidueMod3a := 740520680,
  parentFloor := 20,
  membershipTargetParent := 20,
  certificateHash := "2ef6558c013a0641fd68ff333ecb041fe5de06ae3df31e24708c36fa3227a329"
},
  {
  transitionId := "s4_parent_transition_cc2a6a6bc82aa806",
  branchId := "P19:r5344699:d23",
  sourceParent := 19,
  targetParent := 21,
  valuation := 1,
  c := 740520680,
  coefficient := 1162261467,
  divValuation := 1,
  kDivisibilityModulus := 2,
  kDivisibilityResidue := 0,
  excludedNextPowerModulus := 4,
  excludedNextPowerResidue := 0,
  oddModulus := 1162261467,
  inversePowerTwoMod3a := 581130734,
  targetOddResidueMod3a := 370260340,
  parentFloor := 20,
  membershipTargetParent := 21,
  certificateHash := "a6dd5e50739b78050f23de2ae9b294a76dd040af433ff22aed8279b42b70bf10"
},
  {
  transitionId := "s4_parent_transition_cd9a489bd9cc28cb",
  branchId := "P7:r58731763:d26",
  sourceParent := 7,
  targetParent := 22,
  valuation := 0,
  c := 1914,
  coefficient := 2187,
  divValuation := 0,
  kDivisibilityModulus := 1,
  kDivisibilityResidue := 0,
  excludedNextPowerModulus := 2,
  excludedNextPowerResidue := 0,
  oddModulus := 2187,
  inversePowerTwoMod3a := 1,
  targetOddResidueMod3a := 1914,
  parentFloor := 22,
  membershipTargetParent := 22,
  certificateHash := "88854737d82bdb0b5c1963b420ce5e0f5adacc4bd43a6d353da3c13abe411c03"
},
  {
  transitionId := "s4_parent_transition_ce84b8547ecb1b53",
  branchId := "P24:r63335201:d26",
  sourceParent := 24,
  targetParent := 13,
  valuation := 0,
  c := 266547969898,
  coefficient := 282429536481,
  divValuation := 0,
  kDivisibilityModulus := 1,
  kDivisibilityResidue := 0,
  excludedNextPowerModulus := 2,
  excludedNextPowerResidue := 0,
  oddModulus := 282429536481,
  inversePowerTwoMod3a := 1,
  targetOddResidueMod3a := 266547969898,
  parentFloor := 13,
  membershipTargetParent := 13,
  certificateHash := "4f36cb420a3c382d1dd98300f2dac97a879726c58d37d7debe1d36afde013201"
},
  {
  transitionId := "s4_parent_transition_cebf71f634ae8bf0",
  branchId := "P22:r44195593:d26",
  sourceParent := 22,
  targetParent := 22,
  valuation := 1,
  c := 20666488087,
  coefficient := 31381059609,
  divValuation := 1,
  kDivisibilityModulus := 2,
  kDivisibilityResidue := 1,
  excludedNextPowerModulus := 4,
  excludedNextPowerResidue := 1,
  oddModulus := 31381059609,
  inversePowerTwoMod3a := 15690529805,
  targetOddResidueMod3a := 26023773848,
  parentFloor := 21,
  membershipTargetParent := 22,
  certificateHash := "6f69e100d95475b05e89d1b4ff20616a2df6d88f492a4320fd4019f3345ed344"
},
  {
  transitionId := "s4_parent_transition_cfdece65caa776a9",
  branchId := "P18:r10089145:d24",
  sourceParent := 18,
  targetParent := 18,
  valuation := 0,
  c := 232979148,
  coefficient := 387420489,
  divValuation := 0,
  kDivisibilityModulus := 1,
  kDivisibilityResidue := 0,
  excludedNextPowerModulus := 2,
  excludedNextPowerResidue := 0,
  oddModulus := 387420489,
  inversePowerTwoMod3a := 1,
  targetOddResidueMod3a := 232979148,
  parentFloor := 18,
  membershipTargetParent := 18,
  certificateHash := "0832d63233ab1bb4c383894951506aa89278e13bfc851e3a1ffbd65724ac9ebb"
},
  {
  transitionId := "s4_parent_transition_d0b21f490bfc0f35",
  branchId := "P13:r33705691:d26",
  sourceParent := 13,
  targetParent := 20,
  valuation := 1,
  c := 800755,
  coefficient := 1594323,
  divValuation := 1,
  kDivisibilityModulus := 2,
  kDivisibilityResidue := 1,
  excludedNextPowerModulus := 4,
  excludedNextPowerResidue := 3,
  oddModulus := 1594323,
  inversePowerTwoMod3a := 797162,
  targetOddResidueMod3a := 1197539,
  parentFloor := 19,
  membershipTargetParent := 20,
  certificateHash := "361c781af5dcfede300a57f8e099402d091c58159d6528dbfca1932f3f2e1ced"
},
  {
  transitionId := "s4_parent_transition_d109c8e9c7697302",
  branchId := "P21:r47198587:d26",
  sourceParent := 21,
  targetParent := 18,
  valuation := 0,
  c := 7356910269,
  coefficient := 10460353203,
  divValuation := 0,
  kDivisibilityModulus := 1,
  kDivisibilityResidue := 0,
  excludedNextPowerModulus := 2,
  excludedNextPowerResidue := 1,
  oddModulus := 10460353203,
  inversePowerTwoMod3a := 1,
  targetOddResidueMod3a := 7356910269,
  parentFloor := 18,
  membershipTargetParent := 18,
  certificateHash := "032e2cae382391d112fe0762b926dfe911ee2496321854c19fff2eb6214cf33b"
},
  {
  transitionId := "s4_parent_transition_d13c987d61c84aa3",
  branchId := "P20:r51752545:d26",
  sourceParent := 20,
  targetParent := 23,
  valuation := 1,
  c := 2688914040,
  coefficient := 3486784401,
  divValuation := 1,
  kDivisibilityModulus := 2,
  kDivisibilityResidue := 0,
  excludedNextPowerModulus := 4,
  excludedNextPowerResidue := 0,
  oddModulus := 3486784401,
  inversePowerTwoMod3a := 1743392201,
  targetOddResidueMod3a := 1344457020,
  parentFloor := 22,
  membershipTargetParent := 23,
  certificateHash := "9a92072900c9412f0b3be823888e3600e47391206c99df0fb2533fec1a9ee0ad"
},
  {
  transitionId := "s4_parent_transition_d2880cc3f5b21657",
  branchId := "P22:r56466473:d26",
  sourceParent := 22,
  targetParent := 15,
  valuation := 0,
  c := 26404526161,
  coefficient := 31381059609,
  divValuation := 0,
  kDivisibilityModulus := 1,
  kDivisibilityResidue := 0,
  excludedNextPowerModulus := 2,
  excludedNextPowerResidue := 1,
  oddModulus := 31381059609,
  inversePowerTwoMod3a := 1,
  targetOddResidueMod3a := 26404526161,
  parentFloor := 15,
  membershipTargetParent := 15,
  certificateHash := "9f04ea1a9a9a821f73869c9c9c668a7a8a0d534e445b2ccac10391a51dae701c"
},
  {
  transitionId := "s4_parent_transition_d300f738fbefb665",
  branchId := "P17:r30267435:d25",
  sourceParent := 17,
  targetParent := 19,
  valuation := 0,
  c := 116489574,
  coefficient := 129140163,
  divValuation := 0,
  kDivisibilityModulus := 1,
  kDivisibilityResidue := 0,
  excludedNextPowerModulus := 2,
  excludedNextPowerResidue := 0,
  oddModulus := 129140163,
  inversePowerTwoMod3a := 1,
  targetOddResidueMod3a := 116489574,
  parentFloor := 19,
  membershipTargetParent := 19,
  certificateHash := "7ac8d9474877cf29a49573bb7cf08ab2d7c5b76d906ccd7288331c749ad4e147"
},
  {
  transitionId := "s4_parent_transition_d3adf6da090dda7a",
  branchId := "P7:r52011671:d26",
  sourceParent := 7,
  targetParent := 24,
  valuation := 0,
  c := 1695,
  coefficient := 2187,
  divValuation := 0,
  kDivisibilityModulus := 1,
  kDivisibilityResidue := 0,
  excludedNextPowerModulus := 2,
  excludedNextPowerResidue := 1,
  oddModulus := 2187,
  inversePowerTwoMod3a := 1,
  targetOddResidueMod3a := 1695,
  parentFloor := 24,
  membershipTargetParent := 24,
  certificateHash := "486852dc8daa6ae6a341581f7e3c20e0f62952b97aa963ae05fbcb3d72a36cb9"
},
  {
  transitionId := "s4_parent_transition_d9df41ed6b9adbc1",
  branchId := "P7:r52011671:d26",
  sourceParent := 7,
  targetParent := 25,
  valuation := 1,
  c := 1695,
  coefficient := 2187,
  divValuation := 1,
  kDivisibilityModulus := 2,
  kDivisibilityResidue := 1,
  excludedNextPowerModulus := 4,
  excludedNextPowerResidue := 3,
  oddModulus := 2187,
  inversePowerTwoMod3a := 1094,
  targetOddResidueMod3a := 1941,
  parentFloor := 24,
  membershipTargetParent := 25,
  certificateHash := "ba10258ca5cfb4d24743013f90916098cb67ef9196b3a89e05db8e55ed43dec0"
},
  {
  transitionId := "s4_parent_transition_d9ec7acd1d4c29f9",
  branchId := "P14:r11914377:d24",
  sourceParent := 14,
  targetParent := 19,
  valuation := 1,
  c := 3396636,
  coefficient := 4782969,
  divValuation := 1,
  kDivisibilityModulus := 2,
  kDivisibilityResidue := 0,
  excludedNextPowerModulus := 4,
  excludedNextPowerResidue := 0,
  oddModulus := 4782969,
  inversePowerTwoMod3a := 2391485,
  targetOddResidueMod3a := 1698318,
  parentFloor := 18,
  membershipTargetParent := 19,
  certificateHash := "bc0463fa95b91682299b9a96bc2a86b34a740ba6ab2030f583b42de938ea15e1"
},
  {
  transitionId := "s4_parent_transition_da7be336d38e34a6",
  branchId := "P9:r53252723:d26",
  sourceParent := 9,
  targetParent := 24,
  valuation := 1,
  c := 15619,
  coefficient := 19683,
  divValuation := 1,
  kDivisibilityModulus := 2,
  kDivisibilityResidue := 1,
  excludedNextPowerModulus := 4,
  excludedNextPowerResidue := 3,
  oddModulus := 19683,
  inversePowerTwoMod3a := 9842,
  targetOddResidueMod3a := 17651,
  parentFloor := 23,
  membershipTargetParent := 24,
  certificateHash := "d5cb326ac92c59e0295aa02eadef98ff2dc8bb3de5fe3e02145ec8355eea2fa0"
},
  {
  transitionId := "s4_parent_transition_db5837b345995f6f",
  branchId := "P18:r29638393:d25",
  sourceParent := 18,
  targetParent := 16,
  valuation := 0,
  c := 342205784,
  coefficient := 387420489,
  divValuation := 0,
  kDivisibilityModulus := 1,
  kDivisibilityResidue := 0,
  excludedNextPowerModulus := 2,
  excludedNextPowerResidue := 0,
  oddModulus := 387420489,
  inversePowerTwoMod3a := 1,
  targetOddResidueMod3a := 342205784,
  parentFloor := 16,
  membershipTargetParent := 16,
  certificateHash := "b7296a50f694acedaeb8388e31387f6715fadf6d1bb08f6e5e9ff1a48586bc70"
},
  {
  transitionId := "s4_parent_transition_dc556750c9612045",
  branchId := "P20:r39862641:d26",
  sourceParent := 20,
  targetParent := 16,
  valuation := 0,
  c := 2071148676,
  coefficient := 3486784401,
  divValuation := 0,
  kDivisibilityModulus := 1,
  kDivisibilityResidue := 0,
  excludedNextPowerModulus := 2,
  excludedNextPowerResidue := 0,
  oddModulus := 3486784401,
  inversePowerTwoMod3a := 1,
  targetOddResidueMod3a := 2071148676,
  parentFloor := 16,
  membershipTargetParent := 16,
  certificateHash := "2de7b8739b23f58a04d297c24b78187486b457139cffbf5d49f925c6a82ab0bc"
},
  {
  transitionId := "s4_parent_transition_dd6129d1d3ff8df4",
  branchId := "P20:r10350509:d24",
  sourceParent := 20,
  targetParent := 23,
  valuation := 1,
  c := 2151131232,
  coefficient := 3486784401,
  divValuation := 1,
  kDivisibilityModulus := 2,
  kDivisibilityResidue := 0,
  excludedNextPowerModulus := 4,
  excludedNextPowerResidue := 0,
  oddModulus := 3486784401,
  inversePowerTwoMod3a := 1743392201,
  targetOddResidueMod3a := 1075565616,
  parentFloor := 22,
  membershipTargetParent := 23,
  certificateHash := "12151323cc5218e9d2603d626e8fa34f6821c8a7073ba9632d759f2cf45f0602"
},
  {
  transitionId := "s4_parent_transition_dee096b853047aa7",
  branchId := "P11:r35743131:d26",
  sourceParent := 11,
  targetParent := 23,
  valuation := 0,
  c := 94351,
  coefficient := 177147,
  divValuation := 0,
  kDivisibilityModulus := 1,
  kDivisibilityResidue := 0,
  excludedNextPowerModulus := 2,
  excludedNextPowerResidue := 1,
  oddModulus := 177147,
  inversePowerTwoMod3a := 1,
  targetOddResidueMod3a := 94351,
  parentFloor := 23,
  membershipTargetParent := 23,
  certificateHash := "27e2574df6545b92e8cf6a45e83fc5e457b03544e6e25af579fc7b4c549548a0"
},
  {
  transitionId := "s4_parent_transition_dfec9b54efc03c88",
  branchId := "P12:r44704769:d26",
  sourceParent := 12,
  targetParent := 22,
  valuation := 0,
  c := 354021,
  coefficient := 531441,
  divValuation := 0,
  kDivisibilityModulus := 1,
  kDivisibilityResidue := 0,
  excludedNextPowerModulus := 2,
  excludedNextPowerResidue := 1,
  oddModulus := 531441,
  inversePowerTwoMod3a := 1,
  targetOddResidueMod3a := 354021,
  parentFloor := 22,
  membershipTargetParent := 22,
  certificateHash := "546461be57e4b40e66670e0c7d07dceda4ec4cee229579d4b47529805b31bde3"
},
  {
  transitionId := "s4_parent_transition_e0b56a63cba66d56",
  branchId := "P11:r67005443:d26",
  sourceParent := 11,
  targetParent := 22,
  valuation := 0,
  c := 176874,
  coefficient := 177147,
  divValuation := 0,
  kDivisibilityModulus := 1,
  kDivisibilityResidue := 0,
  excludedNextPowerModulus := 2,
  excludedNextPowerResidue := 0,
  oddModulus := 177147,
  inversePowerTwoMod3a := 1,
  targetOddResidueMod3a := 176874,
  parentFloor := 22,
  membershipTargetParent := 22,
  certificateHash := "6db5ea51c82c1098624c7fa4cca7d95b8b0d1855b3d6abe7cbc996de190b7570"
},
  {
  transitionId := "s4_parent_transition_e194933f28a685bf",
  branchId := "P18:r66402297:d26",
  sourceParent := 18,
  targetParent := 19,
  valuation := 1,
  c := 383341467,
  coefficient := 387420489,
  divValuation := 1,
  kDivisibilityModulus := 2,
  kDivisibilityResidue := 1,
  excludedNextPowerModulus := 4,
  excludedNextPowerResidue := 1,
  oddModulus := 387420489,
  inversePowerTwoMod3a := 193710245,
  targetOddResidueMod3a := 385380978,
  parentFloor := 18,
  membershipTargetParent := 19,
  certificateHash := "8f2a77cd770739b5972d5219e2b6af59386ce837f1218a4f86fc921a08d5a1e4"
},
  {
  transitionId := "s4_parent_transition_e30af5712962278d",
  branchId := "P16:r58415169:d26",
  sourceParent := 16,
  targetParent := 20,
  valuation := 1,
  c := 37470184,
  coefficient := 43046721,
  divValuation := 1,
  kDivisibilityModulus := 2,
  kDivisibilityResidue := 0,
  excludedNextPowerModulus := 4,
  excludedNextPowerResidue := 0,
  oddModulus := 43046721,
  inversePowerTwoMod3a := 21523361,
  targetOddResidueMod3a := 18735092,
  parentFloor := 19,
  membershipTargetParent := 20,
  certificateHash := "aa341e6da5c0b4ef8268599a561a6b1855d24b7df47d2a2ac617b2cc9f7e2922"
},
  {
  transitionId := "s4_parent_transition_e39e81959aba1c36",
  branchId := "P11:r67005443:d26",
  sourceParent := 11,
  targetParent := 23,
  valuation := 1,
  c := 176874,
  coefficient := 177147,
  divValuation := 1,
  kDivisibilityModulus := 2,
  kDivisibilityResidue := 0,
  excludedNextPowerModulus := 4,
  excludedNextPowerResidue := 2,
  oddModulus := 177147,
  inversePowerTwoMod3a := 88574,
  targetOddResidueMod3a := 88437,
  parentFloor := 22,
  membershipTargetParent := 23,
  certificateHash := "d7322e764c6078276714bcd6086bea8075cda8f0cf1e6bb31af85eebdfa8e73b"
},
  {
  transitionId := "s4_parent_transition_e3b1e4db8c7ec65f",
  branchId := "P13:r37271211:d26",
  sourceParent := 13,
  targetParent := 22,
  valuation := 0,
  c := 885462,
  coefficient := 1594323,
  divValuation := 0,
  kDivisibilityModulus := 1,
  kDivisibilityResidue := 0,
  excludedNextPowerModulus := 2,
  excludedNextPowerResidue := 0,
  oddModulus := 1594323,
  inversePowerTwoMod3a := 1,
  targetOddResidueMod3a := 885462,
  parentFloor := 22,
  membershipTargetParent := 22,
  certificateHash := "465e1917f7cc2ebedc74664b9c273ed763a4194347ad9235435241c24663c5ca"
},
  {
  transitionId := "s4_parent_transition_e7815d4a97c0451e",
  branchId := "P14:r11914377:d24",
  sourceParent := 14,
  targetParent := 18,
  valuation := 0,
  c := 3396636,
  coefficient := 4782969,
  divValuation := 0,
  kDivisibilityModulus := 1,
  kDivisibilityResidue := 0,
  excludedNextPowerModulus := 2,
  excludedNextPowerResidue := 0,
  oddModulus := 4782969,
  inversePowerTwoMod3a := 1,
  targetOddResidueMod3a := 3396636,
  parentFloor := 18,
  membershipTargetParent := 18,
  certificateHash := "9a3cf736d4e2d06a50e7f363831bf6322ba53bbac3f3902de27d6867d7a4d955"
},
  {
  transitionId := "s4_parent_transition_e7ab82e15d3d7fc4",
  branchId := "P20:r25819791:d25",
  sourceParent := 20,
  targetParent := 25,
  valuation := 1,
  c := 2683044806,
  coefficient := 3486784401,
  divValuation := 1,
  kDivisibilityModulus := 2,
  kDivisibilityResidue := 0,
  excludedNextPowerModulus := 4,
  excludedNextPowerResidue := 2,
  oddModulus := 3486784401,
  inversePowerTwoMod3a := 1743392201,
  targetOddResidueMod3a := 1341522403,
  parentFloor := 24,
  membershipTargetParent := 25,
  certificateHash := "207dfcaefa0ecb3434cc190c36c07d26c96c8508eb1d85675f3deb5c6bc3146d"
},
  {
  transitionId := "s4_parent_transition_e7e8814b63c65bab",
  branchId := "P14:r32145719:d25",
  sourceParent := 14,
  targetParent := 24,
  valuation := 0,
  c := 4582166,
  coefficient := 4782969,
  divValuation := 0,
  kDivisibilityModulus := 1,
  kDivisibilityResidue := 0,
  excludedNextPowerModulus := 2,
  excludedNextPowerResidue := 0,
  oddModulus := 4782969,
  inversePowerTwoMod3a := 1,
  targetOddResidueMod3a := 4582166,
  parentFloor := 24,
  membershipTargetParent := 24,
  certificateHash := "326e3bf18878fd273251d5cebf59db0c279a3a692bd24247e923bc2a9a5fdf87"
},
  {
  transitionId := "s4_parent_transition_eabadfdad7c96561",
  branchId := "P22:r49168425:d26",
  sourceParent := 22,
  targetParent := 16,
  valuation := 0,
  c := 22991855082,
  coefficient := 31381059609,
  divValuation := 0,
  kDivisibilityModulus := 1,
  kDivisibilityResidue := 0,
  excludedNextPowerModulus := 2,
  excludedNextPowerResidue := 0,
  oddModulus := 31381059609,
  inversePowerTwoMod3a := 1,
  targetOddResidueMod3a := 22991855082,
  parentFloor := 16,
  membershipTargetParent := 16,
  certificateHash := "2c49db8c5f6273d7c174e0b262bd648700b9bd495023e815b5c2bb4bb2a7c75d"
},
  {
  transitionId := "s4_parent_transition_ebd4681b2487805c",
  branchId := "P24:r47543519:d26",
  sourceParent := 24,
  targetParent := 25,
  valuation := 0,
  c := 200088233260,
  coefficient := 282429536481,
  divValuation := 0,
  kDivisibilityModulus := 1,
  kDivisibilityResidue := 0,
  excludedNextPowerModulus := 2,
  excludedNextPowerResidue := 0,
  oddModulus := 282429536481,
  inversePowerTwoMod3a := 1,
  targetOddResidueMod3a := 200088233260,
  parentFloor := 25,
  membershipTargetParent := 25,
  certificateHash := "0878c5ed379db27cc3bba5ff3ca6609d732e111bb1890141bbb93278d149fcf1"
},
  {
  transitionId := "s4_parent_transition_ef225fa30fef9150",
  branchId := "P9:r66178075:d26",
  sourceParent := 9,
  targetParent := 23,
  valuation := 1,
  c := 19410,
  coefficient := 19683,
  divValuation := 1,
  kDivisibilityModulus := 2,
  kDivisibilityResidue := 0,
  excludedNextPowerModulus := 4,
  excludedNextPowerResidue := 2,
  oddModulus := 19683,
  inversePowerTwoMod3a := 9842,
  targetOddResidueMod3a := 9705,
  parentFloor := 22,
  membershipTargetParent := 23,
  certificateHash := "904ce3a5f696b495a53dcad706c4c238b1a6deaaa2b273c7f788cba0b4a07e22"
},
  {
  transitionId := "s4_parent_transition_f30dadb13620db4b",
  branchId := "P14:r9876937:d24",
  sourceParent := 14,
  targetParent := 16,
  valuation := 0,
  c := 2815788,
  coefficient := 4782969,
  divValuation := 0,
  kDivisibilityModulus := 1,
  kDivisibilityResidue := 0,
  excludedNextPowerModulus := 2,
  excludedNextPowerResidue := 0,
  oddModulus := 4782969,
  inversePowerTwoMod3a := 1,
  targetOddResidueMod3a := 2815788,
  parentFloor := 16,
  membershipTargetParent := 16,
  certificateHash := "09db7c173d65ffe0a316f0303874959bbfcf4059241e2ca21ad5267d5a3c1af4"
},
  {
  transitionId := "s4_parent_transition_fae0ea6667f4a4ed",
  branchId := "P10:r53666407:d26",
  sourceParent := 10,
  targetParent := 25,
  valuation := 0,
  c := 47221,
  coefficient := 59049,
  divValuation := 0,
  kDivisibilityModulus := 1,
  kDivisibilityResidue := 0,
  excludedNextPowerModulus := 2,
  excludedNextPowerResidue := 1,
  oddModulus := 59049,
  inversePowerTwoMod3a := 1,
  targetOddResidueMod3a := 47221,
  parentFloor := 25,
  membershipTargetParent := 25,
  certificateHash := "72779729447f5c9d9872404913371efe699bc5541a4fc7b99bc7782f24431029"
}
]

def run024S6Certs : List S6LemmaCert :=
[
  {
  certificateId := "s6_lemma_cert_s6_coverage_lemma_0000",
  lemmaId := "s6_coverage_lemma_0000",
  blockerId := "s6_coverage_0a616b76_0000",
  blockerType := "coverage",
  dependencyIds := ["coverage:coverage_cert_0000", "induction:base_case_cert_0000", "no_escape:no_escape_cert_0000", "parent_residual:parent_residual_cert_P26_67108863_67108864", "s3:s3_frontier:0266ffc831aef802", "s4_transition:s4_parent_transition_98cc8134ef284a4b", "s6_lift:lifting_cert_0000"],
  certificateHash := "7a64c931109ea80d43c1dd502dbb8cd3f79fb41d2f991648e5b1c1a529f6ef8c"
},
  {
  certificateId := "s6_lemma_cert_s6_coverage_lemma_0007",
  lemmaId := "s6_coverage_lemma_0007",
  blockerId := "s6_coverage_0a616b76_0007",
  blockerType := "coverage",
  dependencyIds := ["coverage:coverage_cert_0007", "induction:base_case_cert_0007", "no_escape:no_escape_cert_0007", "s3:s3_frontier:0266ffc831aef802", "s4_transition:s4_parent_transition_98cc8134ef284a4b", "s6_lift:lifting_cert_0007"],
  certificateHash := "25059f8173ba9308f89c40a9a98c3a39d18e053ff3f25d5b4636903e7bc46526"
},
  {
  certificateId := "s6_lemma_cert_s6_coverage_lemma_0014",
  lemmaId := "s6_coverage_lemma_0014",
  blockerId := "s6_coverage_0a616b76_0014",
  blockerType := "coverage",
  dependencyIds := ["coverage:coverage_cert_0014", "induction:base_case_cert_0014", "no_escape:no_escape_cert_0014", "s3:s3_frontier:0266ffc831aef802", "s4_transition:s4_parent_transition_98cc8134ef284a4b", "s6_lift:lifting_cert_0014"],
  certificateHash := "67e3cfedbebd179967b02002fbc73850c48292f80f5558e847841ef453496870"
},
  {
  certificateId := "s6_lemma_cert_s6_coverage_lemma_0021",
  lemmaId := "s6_coverage_lemma_0021",
  blockerId := "s6_coverage_0a616b76_0021",
  blockerType := "coverage",
  dependencyIds := ["coverage:coverage_cert_0021", "induction:base_case_cert_0021", "no_escape:no_escape_cert_0021", "s3:s3_frontier:0266ffc831aef802", "s4_transition:s4_parent_transition_98cc8134ef284a4b", "s6_lift:lifting_cert_0021"],
  certificateHash := "65e8e8dae6f45deb0d450820a520ae22c03c1542d79e617012cce81cd101669b"
},
  {
  certificateId := "s6_lemma_cert_s6_global_descent_lemma_0002",
  lemmaId := "s6_global_descent_lemma_0002",
  blockerId := "s6_global_descent_0a616b76_0002",
  blockerType := "global_descent",
  dependencyIds := ["coverage:coverage_cert_0002", "induction:base_case_cert_0002", "no_escape:no_escape_cert_0002", "s3:s3_frontier:0266ffc831aef802", "s4_transition:s4_parent_transition_98cc8134ef284a4b", "s6_lift:lifting_cert_0002"],
  certificateHash := "fd2c5b2c1547e6243116592bc2125eacd919f93071b37ed1d763b8bb0d1a5e5c"
},
  {
  certificateId := "s6_lemma_cert_s6_global_descent_lemma_0009",
  lemmaId := "s6_global_descent_lemma_0009",
  blockerId := "s6_global_descent_0a616b76_0009",
  blockerType := "global_descent",
  dependencyIds := ["coverage:coverage_cert_0009", "induction:base_case_cert_0009", "no_escape:no_escape_cert_0009", "s3:s3_frontier:0266ffc831aef802", "s4_transition:s4_parent_transition_98cc8134ef284a4b", "s6_lift:lifting_cert_0009"],
  certificateHash := "b7bcc3e8409fb05682b28d5cdba1d95c01ed1380ecb630940b89223bc643ae97"
},
  {
  certificateId := "s6_lemma_cert_s6_global_descent_lemma_0016",
  lemmaId := "s6_global_descent_lemma_0016",
  blockerId := "s6_global_descent_0a616b76_0016",
  blockerType := "global_descent",
  dependencyIds := ["coverage:coverage_cert_0016", "induction:base_case_cert_0016", "no_escape:no_escape_cert_0016", "s3:s3_frontier:0266ffc831aef802", "s4_transition:s4_parent_transition_98cc8134ef284a4b", "s6_lift:lifting_cert_0016"],
  certificateHash := "de310e52670c9136dc8510327875fa69414f255e00b360108e640fa316a23b5e"
},
  {
  certificateId := "s6_lemma_cert_s6_global_descent_lemma_0023",
  lemmaId := "s6_global_descent_lemma_0023",
  blockerId := "s6_global_descent_0a616b76_0023",
  blockerType := "global_descent",
  dependencyIds := ["coverage:coverage_cert_0023", "induction:base_case_cert_0023", "no_escape:no_escape_cert_0023", "s3:s3_frontier:0266ffc831aef802", "s4_transition:s4_parent_transition_98cc8134ef284a4b", "s6_lift:lifting_cert_0023"],
  certificateHash := "1f1d97d111845d1aa8d5ee51f5518bbe90ac7e0bdeb0355fbd86a13a8b7e9c77"
},
  {
  certificateId := "s6_lemma_cert_s6_induction_lemma_0001",
  lemmaId := "s6_induction_lemma_0001",
  blockerId := "s6_induction_0a616b76_0001",
  blockerType := "induction",
  dependencyIds := ["coverage:coverage_cert_0001", "induction:base_case_cert_0001", "no_escape:no_escape_cert_0001", "s3:s3_frontier:0266ffc831aef802", "s4_transition:s4_parent_transition_98cc8134ef284a4b", "s6_lift:lifting_cert_0001"],
  certificateHash := "08be3b85d264a41db20eaec8c24488737df2f6ee22935aaae5a6030c1be5576b"
},
  {
  certificateId := "s6_lemma_cert_s6_induction_lemma_0008",
  lemmaId := "s6_induction_lemma_0008",
  blockerId := "s6_induction_0a616b76_0008",
  blockerType := "induction",
  dependencyIds := ["coverage:coverage_cert_0008", "induction:base_case_cert_0008", "no_escape:no_escape_cert_0008", "s3:s3_frontier:0266ffc831aef802", "s4_transition:s4_parent_transition_98cc8134ef284a4b", "s6_lift:lifting_cert_0008"],
  certificateHash := "fd3bea0fddfc6754115b820162fddf719279aad72b9974fa2657d2950a1c670e"
},
  {
  certificateId := "s6_lemma_cert_s6_induction_lemma_0015",
  lemmaId := "s6_induction_lemma_0015",
  blockerId := "s6_induction_0a616b76_0015",
  blockerType := "induction",
  dependencyIds := ["coverage:coverage_cert_0015", "induction:base_case_cert_0015", "no_escape:no_escape_cert_0015", "s3:s3_frontier:0266ffc831aef802", "s4_transition:s4_parent_transition_98cc8134ef284a4b", "s6_lift:lifting_cert_0015"],
  certificateHash := "92f40e75b4e2dcbd150cc0936ed23bf64268481e1a52ff9d6290be69a9563d9e"
},
  {
  certificateId := "s6_lemma_cert_s6_induction_lemma_0022",
  lemmaId := "s6_induction_lemma_0022",
  blockerId := "s6_induction_0a616b76_0022",
  blockerType := "induction",
  dependencyIds := ["coverage:coverage_cert_0022", "induction:base_case_cert_0022", "no_escape:no_escape_cert_0022", "s3:s3_frontier:0266ffc831aef802", "s4_transition:s4_parent_transition_98cc8134ef284a4b", "s6_lift:lifting_cert_0022"],
  certificateHash := "77f2c40eb529b59d1ad723a6c13214152232232d34912cbd9ba09aceba4791a1"
},
  {
  certificateId := "s6_lemma_cert_s6_no_escape_lemma_0003",
  lemmaId := "s6_no_escape_lemma_0003",
  blockerId := "s6_no_escape_0a616b76_0003",
  blockerType := "no_escape",
  dependencyIds := ["coverage:coverage_cert_0003", "induction:base_case_cert_0003", "no_escape:no_escape_cert_0003", "s3:s3_frontier:0266ffc831aef802", "s4_transition:s4_parent_transition_98cc8134ef284a4b", "s6_lift:lifting_cert_0003"],
  certificateHash := "eb8471819c50a52d8aa4bb5cb3c8eff56dcbd4a541d1bedbe775dad5e55102f9"
},
  {
  certificateId := "s6_lemma_cert_s6_no_escape_lemma_0010",
  lemmaId := "s6_no_escape_lemma_0010",
  blockerId := "s6_no_escape_0a616b76_0010",
  blockerType := "no_escape",
  dependencyIds := ["coverage:coverage_cert_0010", "induction:base_case_cert_0010", "no_escape:no_escape_cert_0010", "s3:s3_frontier:0266ffc831aef802", "s4_transition:s4_parent_transition_98cc8134ef284a4b", "s6_lift:lifting_cert_0010"],
  certificateHash := "2e6b4b7be2ab13768935744d453b49a44858dfafb6a846390c42e99da914e1cc"
},
  {
  certificateId := "s6_lemma_cert_s6_no_escape_lemma_0017",
  lemmaId := "s6_no_escape_lemma_0017",
  blockerId := "s6_no_escape_0a616b76_0017",
  blockerType := "no_escape",
  dependencyIds := ["coverage:coverage_cert_0017", "induction:base_case_cert_0017", "no_escape:no_escape_cert_0017", "s3:s3_frontier:0266ffc831aef802", "s4_transition:s4_parent_transition_98cc8134ef284a4b", "s6_lift:lifting_cert_0017"],
  certificateHash := "c2397d8ba6e4c18bc1c7a949aaf7ebd82108b15109255cf0d3aa81b92ad07bd6"
},
  {
  certificateId := "s6_lemma_cert_s6_no_escape_lemma_0024",
  lemmaId := "s6_no_escape_lemma_0024",
  blockerId := "s6_no_escape_0a616b76_0024",
  blockerType := "no_escape",
  dependencyIds := ["coverage:coverage_cert_0024", "induction:base_case_cert_0024", "no_escape:no_escape_cert_0024", "s3:s3_frontier:0266ffc831aef802", "s4_transition:s4_parent_transition_98cc8134ef284a4b", "s6_lift:lifting_cert_0024"],
  certificateHash := "046428ce2197194cd89f1a1cec6622e007bcd498618b54785f2e61e0827704df"
},
  {
  certificateId := "s6_lemma_cert_s6_parametric_lift_lemma_0005",
  lemmaId := "s6_parametric_lift_lemma_0005",
  blockerId := "s6_parametric_lift_0a616b76_0005",
  blockerType := "parametric_lift",
  dependencyIds := ["coverage:coverage_cert_0005", "induction:base_case_cert_0005", "no_escape:no_escape_cert_0005", "s3:s3_frontier:0266ffc831aef802", "s4_transition:s4_parent_transition_98cc8134ef284a4b", "s6_lift:lifting_cert_0005"],
  certificateHash := "eb72653c7e89d5a81890a113564188861556bff9796af262c912c3457d8c8ef1"
},
  {
  certificateId := "s6_lemma_cert_s6_parametric_lift_lemma_0012",
  lemmaId := "s6_parametric_lift_lemma_0012",
  blockerId := "s6_parametric_lift_0a616b76_0012",
  blockerType := "parametric_lift",
  dependencyIds := ["coverage:coverage_cert_0012", "induction:base_case_cert_0012", "no_escape:no_escape_cert_0012", "s3:s3_frontier:0266ffc831aef802", "s4_transition:s4_parent_transition_98cc8134ef284a4b", "s6_lift:lifting_cert_0012"],
  certificateHash := "e051b4dfaaecddf5d38d47b7ddec057936d0d1e83f0a7235020c444e94724593"
},
  {
  certificateId := "s6_lemma_cert_s6_parametric_lift_lemma_0019",
  lemmaId := "s6_parametric_lift_lemma_0019",
  blockerId := "s6_parametric_lift_0a616b76_0019",
  blockerType := "parametric_lift",
  dependencyIds := ["coverage:coverage_cert_0019", "induction:base_case_cert_0019", "no_escape:no_escape_cert_0019", "s3:s3_frontier:0266ffc831aef802", "s4_transition:s4_parent_transition_98cc8134ef284a4b", "s6_lift:lifting_cert_0019"],
  certificateHash := "65a0314a693133b2a58f94137430e40efe8345e8e126a25185eb440809e2aae9"
},
  {
  certificateId := "s6_lemma_cert_s6_parametric_lift_lemma_0026",
  lemmaId := "s6_parametric_lift_lemma_0026",
  blockerId := "s6_parametric_lift_0a616b76_0026",
  blockerType := "parametric_lift",
  dependencyIds := ["coverage:coverage_cert_0026", "induction:base_case_cert_0026", "no_escape:no_escape_cert_0026", "s3:s3_frontier:0266ffc831aef802", "s4_transition:s4_parent_transition_98cc8134ef284a4b", "s6_lift:lifting_cert_0026"],
  certificateHash := "524f2d1afd41137a5b2501269aa94d3eaff84d79f4dcc09915a09e31f927c7c5"
},
  {
  certificateId := "s6_lemma_cert_s6_parent_transition_lemma_0004",
  lemmaId := "s6_parent_transition_lemma_0004",
  blockerId := "s6_parent_transition_0a616b76_0004",
  blockerType := "parent_transition",
  dependencyIds := ["coverage:coverage_cert_0004", "induction:base_case_cert_0004", "no_escape:no_escape_cert_0004", "s3:s3_frontier:0266ffc831aef802", "s4_transition:s4_parent_transition_98cc8134ef284a4b", "s6_lift:lifting_cert_0004"],
  certificateHash := "f2d587ec7cb1de42410c041fb4a7d26de036e113cb49d8a9e9a95d8fdabc02e0"
},
  {
  certificateId := "s6_lemma_cert_s6_parent_transition_lemma_0011",
  lemmaId := "s6_parent_transition_lemma_0011",
  blockerId := "s6_parent_transition_0a616b76_0011",
  blockerType := "parent_transition",
  dependencyIds := ["coverage:coverage_cert_0011", "induction:base_case_cert_0011", "no_escape:no_escape_cert_0011", "s3:s3_frontier:0266ffc831aef802", "s4_transition:s4_parent_transition_98cc8134ef284a4b", "s6_lift:lifting_cert_0011"],
  certificateHash := "018f60275a6e4a1f4c086e6d2eea524cf7b6084b2cecf0518891e0a5988d100e"
},
  {
  certificateId := "s6_lemma_cert_s6_parent_transition_lemma_0018",
  lemmaId := "s6_parent_transition_lemma_0018",
  blockerId := "s6_parent_transition_0a616b76_0018",
  blockerType := "parent_transition",
  dependencyIds := ["coverage:coverage_cert_0018", "induction:base_case_cert_0018", "no_escape:no_escape_cert_0018", "s3:s3_frontier:0266ffc831aef802", "s4_transition:s4_parent_transition_98cc8134ef284a4b", "s6_lift:lifting_cert_0018"],
  certificateHash := "e8bebd55a7f747dd4f964840c66655e977b400b3e1d81dc4249946849afa7b0c"
},
  {
  certificateId := "s6_lemma_cert_s6_parent_transition_lemma_0025",
  lemmaId := "s6_parent_transition_lemma_0025",
  blockerId := "s6_parent_transition_0a616b76_0025",
  blockerType := "parent_transition",
  dependencyIds := ["coverage:coverage_cert_0025", "induction:base_case_cert_0025", "no_escape:no_escape_cert_0025", "s3:s3_frontier:0266ffc831aef802", "s4_transition:s4_parent_transition_98cc8134ef284a4b", "s6_lift:lifting_cert_0025"],
  certificateHash := "2124cea04e9e9e170ec790b5e6b13cb0e001e8042eff5bd055d32afc587fc761"
},
  {
  certificateId := "s6_lemma_cert_s6_strict_verifier_gap_lemma_0006",
  lemmaId := "s6_strict_verifier_gap_lemma_0006",
  blockerId := "s6_strict_verifier_gap_0a616b76_0006",
  blockerType := "strict_verifier_gap",
  dependencyIds := ["coverage:coverage_cert_0006", "induction:base_case_cert_0006", "no_escape:no_escape_cert_0006", "s3:s3_frontier:0266ffc831aef802", "s4_transition:s4_parent_transition_98cc8134ef284a4b", "s6_lift:lifting_cert_0006"],
  certificateHash := "3421954c800d3b67771b70ee755c2ba1205edee48b1dcbe27a8b200c98e9fb57"
},
  {
  certificateId := "s6_lemma_cert_s6_strict_verifier_gap_lemma_0013",
  lemmaId := "s6_strict_verifier_gap_lemma_0013",
  blockerId := "s6_strict_verifier_gap_0a616b76_0013",
  blockerType := "strict_verifier_gap",
  dependencyIds := ["coverage:coverage_cert_0013", "induction:base_case_cert_0013", "no_escape:no_escape_cert_0013", "s3:s3_frontier:0266ffc831aef802", "s4_transition:s4_parent_transition_98cc8134ef284a4b", "s6_lift:lifting_cert_0013"],
  certificateHash := "c9333a319baeb38f9aad5dc4721a394824e4167f14d12cafe26bf451fd5f612d"
},
  {
  certificateId := "s6_lemma_cert_s6_strict_verifier_gap_lemma_0020",
  lemmaId := "s6_strict_verifier_gap_lemma_0020",
  blockerId := "s6_strict_verifier_gap_0a616b76_0020",
  blockerType := "strict_verifier_gap",
  dependencyIds := ["coverage:coverage_cert_0020", "induction:base_case_cert_0020", "no_escape:no_escape_cert_0020", "s3:s3_frontier:0266ffc831aef802", "s4_transition:s4_parent_transition_98cc8134ef284a4b", "s6_lift:lifting_cert_0020"],
  certificateHash := "e5ce4f65a2acae74562469d8046630435f6a010d022d33930d55cf12aa977dae"
},
  {
  certificateId := "s6_lemma_cert_s6_strict_verifier_gap_lemma_0027",
  lemmaId := "s6_strict_verifier_gap_lemma_0027",
  blockerId := "s6_strict_verifier_gap_0a616b76_0027",
  blockerType := "strict_verifier_gap",
  dependencyIds := ["coverage:coverage_cert_0027", "induction:base_case_cert_0027", "no_escape:no_escape_cert_0027", "s3:s3_frontier:0266ffc831aef802", "s4_transition:s4_parent_transition_98cc8134ef284a4b", "s6_lift:lifting_cert_0027"],
  certificateHash := "a1e5ab84c1e8371fb9222574d9f979311e9c8be9455db187bb8912fc24a0cdb5"
}
]

def run024TopLevelCerts : TopLevelCertBundle :=
{
  universalEntryHash := "49348e6996b2f12b8bf56a9eea958901e626d837a5d985cc2a4bb3cb64174057",
  parentStateCoverageHash := "863af47429eb64c0d9f84e33c26a15c5cbe925db0a59b1b0c9d273e4389338ff",
  transitionSoundnessHash := "bec30cda9cdff9804df6ef930544e0874b53093216e480fe0786e9f457bd5c9d",
  wellFoundedRankingHash := "3f90b9cb858284817a9fa0485842342de4603bf5b77e68427055392215e0c20b",
  descentImplicationHash := "8a267cbdade7866de41fd8ef697604603466d39f502400953ec2dee1b163bd9c",
  theoremStatement := "forall n > 1 exists k >= 1 such that C^k(n) < n",
  descentImplicationStatement := "forall n > 1 exists t >= 0 such that C^t(n) = 1",
  acceptedNodeCount := 485,
  totalNodeCount := 485,
  openNodeCount := 0
}

def run024Manifest : Run024Manifest :=
{
  s3DebtExactCerts := run024S3DebtExactCerts,
  s4Certs := run024S4Certs,
  s6Certs := run024S6Certs,
  topLevel := run024TopLevelCerts
}

theorem run024_s3_debt_exact_cert_count : run024S3DebtExactCerts.length = 182 := by native_decide

theorem run024_s4_cert_count : run024S4Certs.length = 135 := by native_decide

theorem run024_s6_cert_count : run024S6Certs.length = 28 := by native_decide

theorem run024S3DebtExactCerts_check : checkAllS3DebtExactCerts run024S3DebtExactCerts = true := by native_decide

theorem run024S3DebtExactCerts_sound : AllS3DebtExactClaims run024S3DebtExactCerts :=
  checkAllS3DebtExactCerts_sound run024S3DebtExactCerts run024S3DebtExactCerts_check

theorem run024S4Certs_check : checkAllS4TransitionCerts run024S4Certs = true := by native_decide

theorem run024S4Certs_sound : AllS4TransitionClaims run024S4Certs :=
  checkAllS4TransitionCerts_sound run024S4Certs run024S4Certs_check

theorem run024Manifest_check : checkRun024Manifest run024Manifest = true := by native_decide

end Collatz
