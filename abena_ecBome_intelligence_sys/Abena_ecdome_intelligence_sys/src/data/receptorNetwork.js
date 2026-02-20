export const receptorNetwork = {
  'CB1': {
    name: 'Cannabinoid Receptor 1',
    location: ['Central Nervous System', 'Peripheral Nervous System', 'Adipose Tissue'],
    functions: [
      'Neurotransmission modulation',
      'Appetite regulation',
      'Pain perception',
      'Memory and learning',
      'Motor control'
    ],
    interactions: [
      'Endocannabinoids (AEA, 2-AG)',
      'Phytocannabinoids (THC, CBD)',
      'GABAergic neurons',
      'Glutamatergic neurons'
    ],
    polymorphisms: [
      {
        rsID: 'rs1049353',
        effect: 'Altered receptor density',
        clinical: 'May affect response to cannabinoids'
      },
      {
        rsID: 'rs806368',
        effect: 'Modified signaling',
        clinical: 'Potential impact on pain perception'
      }
    ],
    therapeuticTargets: [
      'Pain management',
      'Anxiety disorders',
      'Epilepsy',
      'Multiple sclerosis',
      'Obesity'
    ]
  },
  'CB2': {
    name: 'Cannabinoid Receptor 2',
    location: ['Immune System', 'Peripheral Tissues', 'Microglia'],
    functions: [
      'Immune modulation',
      'Inflammation regulation',
      'Bone metabolism',
      'Wound healing'
    ],
    interactions: [
      'Endocannabinoids',
      'Immune cells',
      'Inflammatory mediators',
      'Bone cells'
    ],
    polymorphisms: [
      {
        rsID: 'rs2501432',
        effect: 'Altered immune response',
        clinical: 'May affect inflammatory conditions'
      }
    ],
    therapeuticTargets: [
      'Inflammatory diseases',
      'Autoimmune disorders',
      'Osteoporosis',
      'Neuropathic pain'
    ]
  },
  'TRPV1': {
    name: 'Transient Receptor Potential Vanilloid 1',
    location: ['Sensory Neurons', 'Epithelial Cells', 'CNS'],
    functions: [
      'Pain perception',
      'Temperature sensing',
      'Inflammation modulation',
      'Neurotransmission'
    ],
    interactions: [
      'Capsaicin',
      'Endocannabinoids',
      'Protons',
      'Heat'
    ],
    polymorphisms: [
      {
        rsID: 'rs8065080',
        effect: 'Altered pain sensitivity',
        clinical: 'May affect chronic pain conditions'
      }
    ],
    therapeuticTargets: [
      'Chronic pain',
      'Inflammatory conditions',
      'Neuropathic pain',
      'Migraine'
    ]
  },
  'GPR18': {
    name: 'G Protein-Coupled Receptor 18',
    location: ['Immune Cells', 'CNS', 'Peripheral Tissues'],
    functions: [
      'Immune regulation',
      'Cell migration',
      'Inflammation control',
      'Tissue repair'
    ],
    interactions: [
      'N-Arachidonoyl glycine',
      'Immune mediators',
      'Endocannabinoids'
    ],
    polymorphisms: [
      {
        rsID: 'rs11544331',
        effect: 'Modified immune response',
        clinical: 'May affect inflammatory diseases'
      }
    ],
    therapeuticTargets: [
      'Inflammatory disorders',
      'Autoimmune conditions',
      'Tissue repair',
      'Immune modulation'
    ]
  },
  'GPR55': {
    name: 'G Protein-Coupled Receptor 55',
    location: ['CNS', 'Bone', 'Gastrointestinal Tract'],
    functions: [
      'Bone metabolism',
      'Pain modulation',
      'Gastrointestinal motility',
      'Neurotransmission'
    ],
    interactions: [
      'LPI',
      'Endocannabinoids',
      'Osteoclasts',
      'Osteoblasts'
    ],
    polymorphisms: [
      {
        rsID: 'rs3749073',
        effect: 'Altered bone metabolism',
        clinical: 'May affect osteoporosis risk'
      }
    ],
    therapeuticTargets: [
      'Osteoporosis',
      'Pain management',
      'Gastrointestinal disorders',
      'Neurological conditions'
    ]
  },
  'GPR119': {
    name: 'G Protein-Coupled Receptor 119',
    location: ['Pancreas', 'Gastrointestinal Tract', 'CNS'],
    functions: [
      'Glucose homeostasis',
      'Insulin secretion',
      'Appetite regulation',
      'Energy metabolism'
    ],
    interactions: [
      'OEA',
      'PEA',
      'Insulin',
      'Glucagon'
    ],
    polymorphisms: [
      {
        rsID: 'rs1545285',
        effect: 'Modified glucose metabolism',
        clinical: 'May affect diabetes risk'
      }
    ],
    therapeuticTargets: [
      'Type 2 diabetes',
      'Obesity',
      'Metabolic syndrome',
      'Appetite control'
    ]
  },
  'PPARα': {
    name: 'Peroxisome Proliferator-Activated Receptor Alpha',
    location: ['Liver', 'Muscle', 'Heart', 'Kidney'],
    functions: [
      'Lipid metabolism',
      'Energy homeostasis',
      'Inflammation control',
      'Cardiovascular regulation'
    ],
    interactions: [
      'Fatty acids',
      'Endocannabinoids',
      'Lipid mediators',
      'Nuclear receptors'
    ],
    polymorphisms: [
      {
        rsID: 'rs1800206',
        effect: 'Altered lipid metabolism',
        clinical: 'May affect cardiovascular risk'
      }
    ],
    therapeuticTargets: [
      'Dyslipidemia',
      'Cardiovascular disease',
      'Metabolic disorders',
      'Inflammatory conditions'
    ]
  },
  'PPARγ': {
    name: 'Peroxisome Proliferator-Activated Receptor Gamma',
    location: ['Adipose Tissue', 'Immune Cells', 'Vascular Endothelium'],
    functions: [
      'Adipogenesis',
      'Glucose metabolism',
      'Inflammation control',
      'Vascular function'
    ],
    interactions: [
      'Fatty acids',
      'Endocannabinoids',
      'Adipokines',
      'Inflammatory mediators'
    ],
    polymorphisms: [
      {
        rsID: 'rs1801282',
        effect: 'Modified adipogenesis',
        clinical: 'May affect metabolic syndrome risk'
      }
    ],
    therapeuticTargets: [
      'Type 2 diabetes',
      'Metabolic syndrome',
      'Inflammatory diseases',
      'Cardiovascular conditions'
    ]
  },
  TRPV2: {
    name: 'TRPV2 (Transient Receptor Potential Vanilloid 2)',
    location: 'Heart, immune cells, nervous system',
    functions: ['Pain perception', 'Immune response', 'Cardiac function'],
    interactions: ['Immune cells', 'Cardiac cells'],
    polymorphisms: ['TRPV2 rs3813769'],
    therapeuticTargets: ['Pain', 'Inflammation', 'Cardiac health']
  },
  TRPV3: {
    name: 'TRPV3',
    location: 'Skin, nervous system',
    functions: ['Temperature sensation', 'Skin health'],
    interactions: ['Skin cells', 'Temperature'],
    polymorphisms: ['TRPV3 rs7217270'],
    therapeuticTargets: ['Skin disorders', 'Temperature sensitivity']
  },
  TRPV4: {
    name: 'TRPV4',
    location: 'Skin, blood vessels, nervous system',
    functions: ['Osmoregulation', 'Pain', 'Inflammation'],
    interactions: ['Vascular system', 'Skin cells'],
    polymorphisms: ['TRPV4 rs3742030'],
    therapeuticTargets: ['Pain', 'Edema', 'Skin disorders']
  },
  TRPA1: {
    name: 'TRPA1',
    location: 'Sensory neurons, lungs, gut',
    functions: ['Pain', 'Inflammation', 'Chemical sensing'],
    interactions: ['Sensory neurons', 'Inflammatory mediators'],
    polymorphisms: ['TRPA1 rs11988795'],
    therapeuticTargets: ['Pain', 'Asthma', 'Gut disorders']
  },
  MuOpioid: {
    name: 'μ-Opioid Receptor (MOR)',
    location: 'Brain, Spinal cord, Digestive tract',
    functions: ['Pain relief', 'Reward processing', 'Respiratory depression', 'Euphoria'],
    interactions: ['Dopamine', 'GABA', 'CB1'],
    polymorphisms: ['OPRM1 rs1799971'],
    therapeuticTargets: ['Pain', 'Addiction', 'Respiratory function']
  },
  DeltaOpioid: {
    name: 'δ-Opioid Receptor (DOR)',
    location: 'Brain, Peripheral nervous system',
    functions: ['Mood regulation', 'Analgesia', 'Neuroprotection'],
    interactions: ['Serotonin', 'GABA', 'CB1'],
    polymorphisms: ['OPRD1 rs1042114'],
    therapeuticTargets: ['Depression', 'Pain', 'Neuroprotection']
  },
  KappaOpioid: {
    name: 'κ-Opioid Receptor (KOR)',
    location: 'Brain, Spinal cord',
    functions: ['Pain relief', 'Stress response', 'Dysphoria'],
    interactions: ['Stress hormones', 'CB1'],
    polymorphisms: ['OPRK1 rs702764'],
    therapeuticTargets: ['Pain', 'Stress', 'Mood disorders']
  }
}; 