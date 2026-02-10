export const patientData = {
  endocannabinoidTrends: [
    { date: '2024-01', anandamide: 0.8, '2-AG': 0.7 },
    { date: '2024-02', anandamide: 0.75, '2-AG': 0.65 },
    { date: '2024-03', anandamide: 0.85, '2-AG': 0.75 },
    { date: '2024-04', anandamide: 0.9, '2-AG': 0.8 }
  ],
  receptorActivityTrends: [
    { date: '2024-01', CB1: 0.75, CB2: 0.65 },
    { date: '2024-02', CB1: 0.7, CB2: 0.6 },
    { date: '2024-03', CB1: 0.8, CB2: 0.7 },
    { date: '2024-04', CB1: 0.85, CB2: 0.75 }
  ]
};

export const drugInteractions = {
  'CBD': {
    interactions: [
      { drug: 'Warfarin', effect: 'May increase bleeding risk', severity: 'Moderate' },
      { drug: 'Clobazam', effect: 'May increase sedation', severity: 'Mild' },
      { drug: 'Valproate', effect: 'May increase liver enzyme levels', severity: 'Moderate' }
    ],
    contraindications: ['Severe liver disease', 'Pregnancy']
  },
  'THC': {
    interactions: [
      { drug: 'Benzodiazepines', effect: 'Increased sedation', severity: 'Moderate' },
      { drug: 'Opioids', effect: 'Enhanced analgesic effects', severity: 'Moderate' },
      { drug: 'Antidepressants', effect: 'Variable effects on mood', severity: 'Mild' }
    ],
    contraindications: ['Psychotic disorders', 'Severe cardiovascular disease']
  }
};

export const geneticPolymorphisms = {
  'CNR1': {
    rs1049353: {
      effect: 'Altered CB1 receptor function',
      clinicalSignificance: 'May affect response to cannabinoids',
      prevalence: '15-20% in general population'
    },
    rs806368: {
      effect: 'Modified endocannabinoid signaling',
      clinicalSignificance: 'Potential impact on pain perception',
      prevalence: '10-15% in general population'
    }
  },
  'FAAH': {
    rs324420: {
      effect: 'Reduced FAAH activity',
      clinicalSignificance: 'Increased anandamide levels',
      prevalence: '20-25% in general population'
    }
  }
};

export const microbiomeIntegration = {
  'Bifidobacterium': {
    role: 'Endocannabinoid modulation',
    effects: ['Anti-inflammatory', 'Gut barrier maintenance'],
    metabolites: ['Short-chain fatty acids', 'Tryptophan derivatives']
  },
  'Akkermansia': {
    role: 'Mucosal layer maintenance',
    effects: ['Metabolic regulation', 'Immune modulation'],
    metabolites: ['Propionate', 'Acetate']
  }
};

export const cannabisStrains = {
  'Indica': {
    characteristics: ['Sedating', 'Relaxing', 'Pain relief'],
    terpenes: ['Myrcene', 'Linalool', 'Caryophyllene'],
    commonUses: ['Sleep disorders', 'Chronic pain', 'Anxiety']
  },
  'Sativa': {
    characteristics: ['Energizing', 'Uplifting', 'Focus-enhancing'],
    terpenes: ['Pinene', 'Limonene', 'Terpinolene'],
    commonUses: ['Depression', 'Fatigue', 'ADHD']
  },
  'Hybrid': {
    characteristics: ['Balanced effects', 'Versatile', 'Customizable'],
    terpenes: ['Various combinations'],
    commonUses: ['Mixed conditions', 'Personalized treatment']
  }
};

export const treatmentModalities = {
  'Phytocannabinoid Therapy': {
    approach: 'Plant-derived cannabinoids',
    applications: ['Pain management', 'Neurological disorders', 'Inflammatory conditions'],
    considerations: ['Dosing precision', 'Strain selection', 'Route of administration']
  },
  'Endocannabinoid Enhancement': {
    approach: 'Supporting endogenous system',
    applications: ['Metabolic disorders', 'Immune regulation', 'Stress management'],
    considerations: ['Lifestyle factors', 'Nutritional support', 'Exercise protocols']
  },
  'Microbiome Modulation': {
    approach: 'Gut-eCBome axis optimization',
    applications: ['Digestive health', 'Immune function', 'Mental health'],
    considerations: ['Probiotic selection', 'Dietary modifications', 'Prebiotic support']
  }
}; 