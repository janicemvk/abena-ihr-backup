# Help Information System - Integration Guide

## Overview

The Help Information System provides contextual help for medical terms and data points throughout the ABENA dashboard. It displays explanations in both **medical terminology** and **plain language** (layman's terms), making the platform accessible to healthcare professionals and patients alike.

## Components

### 1. **HelpInfo** (Core Component)
The main component that renders help icons with tooltips or modals.

**Location:** `src/components/Common/HelpInfo.js`

### 2. **SectionHeader** (Wrapper Component)
Pre-built section header with integrated help info.

**Location:** `src/components/Common/SectionHeader.js`

### 3. **DataCard** (Data Display Component)
Data card component with built-in help support.

**Location:** `src/components/Common/DataCard.js`

---

## Quick Start

### Basic Usage - Help Icon

```jsx
import HelpInfo from '../Common/HelpInfo';

// Simple inline tooltip
<HelpInfo topic="heart_rate" size="sm" position="inline" />

// Modal popup for more detailed info
<HelpInfo topic="ecdome_score" size="md" position="modal" />
```

### Using with Section Headers

```jsx
import SectionHeader from '../Common/SectionHeader';
import { Heart } from 'lucide-react';

<SectionHeader
  icon={Heart}
  title="Vital Signs"
  subtitle="Current patient measurements"
  helpTopic="vital_signs"  // Use predefined topic
  helpPosition="modal"      // or "inline"
/>
```

### Using with Data Cards

```jsx
import DataCard from '../Common/DataCard';
import { Heart } from 'lucide-react';

<DataCard
  label="Heart Rate"
  value={72}
  unit="bpm"
  icon={Heart}
  helpTopic="heart_rate"
  status="normal"  // normal, warning, critical, info
/>
```

---

## Available Help Topics

### Vital Signs
- `heart_rate` - Heart rate (bpm)
- `blood_pressure` - Blood pressure (mmHg)
- `oxygen_saturation` - SpO₂ (%)
- `temperature` - Body temperature (°F)
- `glucose` - Blood glucose (mg/dL)

### eCDome System
- `ecdome_score` - Overall eCDome score
- `anandamide` - Anandamide (AEA) levels
- `cb1_receptors` - CB1 receptor activity
- `cb2_receptors` - CB2 receptor activity
- `2ag` - 2-AG levels

### General
- `bmi` - Body Mass Index
- `clinical_recommendations` - Clinical recommendations
- `predictive_alerts` - Predictive alerts

---

## Custom Help Content

If you need help content that's not in the database, provide custom content:

```jsx
<HelpInfo 
  helpContent={{
    title: 'Custom Metric',
    subtitle: 'Optional subtitle',
    medical: 'Technical medical explanation of the metric...',
    simple: 'Easy-to-understand explanation for patients...',
    normalRange: 'Normal range: 10-20 units',
    significance: 'Why this metric matters clinically...',
    relatedTopics: ['Topic 1', 'Topic 2']
  }}
  size="sm"
  position="inline"
/>
```

---

## Component Props Reference

### HelpInfo Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `topic` | string | - | Predefined help topic key |
| `helpContent` | object | - | Custom help content object |
| `size` | string | `'sm'` | Icon size: `'xs'`, `'sm'`, `'md'`, `'lg'` |
| `position` | string | `'inline'` | Display mode: `'inline'` (tooltip) or `'modal'` (popup) |

### SectionHeader Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `icon` | Component | - | Lucide React icon component |
| `title` | string | - | Section title |
| `subtitle` | string | - | Optional subtitle |
| `helpTopic` | string | - | Help topic key |
| `helpContent` | object | - | Custom help content |
| `helpPosition` | string | `'modal'` | Help display mode |
| `actions` | node | - | Action buttons/elements |
| `className` | string | `''` | Additional CSS classes |

### DataCard Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `label` | string | - | Data label |
| `value` | string/number | - | Data value |
| `unit` | string | - | Unit of measurement |
| `icon` | Component | - | Lucide React icon |
| `helpTopic` | string | - | Help topic key |
| `helpContent` | object | - | Custom help content |
| `status` | string | - | Status color: `'normal'`, `'warning'`, `'critical'`, `'info'` |
| `trend` | string | - | Trend indicator: `'up'`, `'down'`, `'stable'` |
| `className` | string | `''` | Additional CSS classes |

---

## Integration Examples

### Example 1: Vital Signs Section

```jsx
import React from 'react';
import { Heart, Activity, Thermometer, Wind } from 'lucide-react';
import SectionHeader from '../Common/SectionHeader';
import DataCard from '../Common/DataCard';

const VitalSignsSection = ({ vitals }) => {
  return (
    <div className="dashboard-card">
      <SectionHeader
        icon={Heart}
        title="Vital Signs"
        subtitle="Current measurements"
        helpTopic="vital_signs"
        helpPosition="modal"
      />

      <div className="grid grid-cols-4 gap-4 mt-6">
        <DataCard
          label="Heart Rate"
          value={vitals.heartRate}
          unit="bpm"
          icon={Heart}
          helpTopic="heart_rate"
          status="normal"
        />
        <DataCard
          label="Blood Pressure"
          value={vitals.bloodPressure}
          unit="mmHg"
          icon={Activity}
          helpTopic="blood_pressure"
          status="normal"
        />
        <DataCard
          label="O₂ Saturation"
          value={vitals.oxygenSaturation}
          unit="%"
          icon={Wind}
          helpTopic="oxygen_saturation"
          status="normal"
        />
        <DataCard
          label="Temperature"
          value={vitals.temperature}
          unit="°F"
          icon={Thermometer}
          helpTopic="temperature"
          status="normal"
        />
      </div>
    </div>
  );
};
```

### Example 2: Inline Help in Custom Component

```jsx
import React from 'react';
import HelpInfo from '../Common/HelpInfo';

const CustomMetric = ({ value }) => {
  return (
    <div className="flex items-center space-x-2">
      <span className="font-semibold">Custom Metric:</span>
      <span className="text-2xl">{value}</span>
      <HelpInfo 
        helpContent={{
          title: 'Custom Metric',
          medical: 'This metric represents...',
          simple: 'In simple terms, this means...'
        }}
        size="sm"
        position="inline"
      />
    </div>
  );
};
```

### Example 3: Table with Help Icons

```jsx
import React from 'react';
import HelpInfo from '../Common/HelpInfo';

const LabResultsTable = ({ results }) => {
  return (
    <table className="w-full">
      <thead>
        <tr>
          <th>Test</th>
          <th>Result</th>
          <th>Reference Range</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td className="flex items-center space-x-2">
            <span>Blood Glucose</span>
            <HelpInfo topic="glucose" size="xs" position="inline" />
          </td>
          <td>{results.glucose} mg/dL</td>
          <td>70-100 mg/dL</td>
        </tr>
        {/* More rows... */}
      </tbody>
    </table>
  );
};
```

---

## Adding New Help Topics

To add new help topics to the database:

1. Open `src/components/Common/HelpInfo.js`
2. Find the `helpDatabase` object in the `getHelpContent` function
3. Add your new topic:

```javascript
'your_topic_key': {
  title: 'Topic Title',
  subtitle: 'Optional subtitle',
  medical: 'Medical/technical explanation...',
  simple: 'Plain language explanation...',
  normalRange: 'Normal values or ranges',
  significance: 'Clinical significance...',
  relatedTopics: ['Related Topic 1', 'Related Topic 2']
}
```

---

## Best Practices

### 1. **Choose Appropriate Display Mode**

- **Inline Tooltip** (`position="inline"`): 
  - Best for quick reference
  - Use for individual data points
  - Appears on hover/click

- **Modal Popup** (`position="modal"`):
  - Best for detailed explanations
  - Use for section headers
  - Requires explicit click to open

### 2. **Size Guidelines**

- `xs` (12px): Dense tables, compact displays
- `sm` (16px): Standard inline use, data cards
- `md` (20px): Section headers, prominent features
- `lg` (24px): Hero sections, main headings

### 3. **Writing Help Content**

**Medical Explanation:**
- Use proper medical terminology
- Include relevant pathophysiology
- Reference clinical significance
- Target: Healthcare professionals

**Simple Explanation:**
- Use everyday language
- Include analogies when helpful
- Avoid jargon
- Target: Patients and general public

### 4. **Consistent Placement**

- Always place help icons to the **right** of labels
- Use consistent spacing (e.g., `space-x-2`)
- Align vertically with text: `items-center`

---

## Styling and Theming

The help components use Tailwind CSS and match the existing dashboard theme:

- **Primary Color**: Blue (`blue-500`, `blue-600`)
- **Medical Content**: Blue backgrounds (`blue-50`, `blue-100`)
- **Simple Content**: Green backgrounds (`green-50`, `green-100`)
- **Hover States**: Darker shades for interactive elements

To customize colors, modify the component files directly or use Tailwind's customization features.

---

## Accessibility

The help system includes accessibility features:

- **ARIA Labels**: Descriptive labels for screen readers
- **Keyboard Navigation**: All interactive elements are keyboard-accessible
- **Focus Indicators**: Visible focus rings on help icons
- **Semantic HTML**: Proper heading hierarchy and structure

---

## Performance Considerations

- Help content is loaded lazily (only when needed)
- Tooltips unmount when closed to save memory
- No external API calls - all content is local
- Lightweight: ~50KB total for all components

---

## Browser Compatibility

Tested and working on:
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

---

## Troubleshooting

### Help Icon Not Appearing

1. Check that you've imported the component:
   ```jsx
   import HelpInfo from '../Common/HelpInfo';
   ```

2. Verify the topic exists in the help database or provide custom content

3. Check console for warnings about missing content

### Tooltip Not Showing

1. Ensure `position="inline"` is set
2. Check that parent container doesn't have `overflow: hidden`
3. Verify z-index isn't being overridden

### Modal Not Opening

1. Ensure `position="modal"` is set
2. Check for JavaScript errors in console
3. Verify Framer Motion is installed (`framer-motion`)

---

## Examples in Production

See these components for real-world implementations:

1. **VitalSignsWithHelp.js** - Comprehensive vital signs with help
2. **ECDomeScoreWithHelp.js** - eCDome analysis with detailed help
3. Complete examples in `/src/components/ClinicalDashboard/`

---

## Support & Contributing

For questions or to add new help topics:

1. Check existing help topics in `HelpInfo.js`
2. Follow the structure of existing topics
3. Include both medical and simple explanations
4. Add related topics for better discovery

---

## Version History

- **v1.0.0** (2025-10-30): Initial release with 15+ predefined topics
- Support for custom help content
- Three display components (HelpInfo, SectionHeader, DataCard)

---

## Future Enhancements

Planned features:
- [ ] Multi-language support
- [ ] Video explanations for complex topics
- [ ] Interactive diagrams
- [ ] Patient-specific content levels
- [ ] Search functionality for help topics
- [ ] Analytics on most-viewed help topics

