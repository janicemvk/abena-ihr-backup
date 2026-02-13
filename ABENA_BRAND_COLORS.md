# ABENA IHR Brand Colors & Design System

**Source:** http://abenaihr.com  
**Purpose:** MVP Professional Presentation for Investors

---

## 🎨 **Primary Color Palette**

Based on ABENA's website, here's the professional color scheme:

### **Primary Colors:**
```css
--abena-primary: #1E40AF;        /* Deep Professional Blue */
--abena-primary-light: #3B82F6;  /* Bright Blue */
--abena-primary-dark: #1E3A8A;   /* Dark Navy Blue */

--abena-secondary: #10B981;      /* Professional Green (Health/Wellness) */
--abena-secondary-light: #34D399; /* Light Green */
--abena-secondary-dark: #059669;  /* Dark Green */

--abena-accent: #8B5CF6;         /* Purple (Innovation/Tech) */
--abena-accent-light: #A78BFA;   /* Light Purple */
--abena-accent-dark: #7C3AED;    /* Dark Purple */
```

### **Neutral Colors:**
```css
--abena-gray-50: #F9FAFB;
--abena-gray-100: #F3F4F6;
--abena-gray-200: #E5E7EB;
--abena-gray-300: #D1D5DB;
--abena-gray-400: #9CA3AF;
--abena-gray-500: #6B7280;
--abena-gray-600: #4B5563;
--abena-gray-700: #374151;
--abena-gray-800: #1F2937;
--abena-gray-900: #111827;
```

### **Semantic Colors:**
```css
--abena-success: #10B981;        /* Green - Positive Health */
--abena-warning: #F59E0B;        /* Amber - Caution */
--abena-error: #EF4444;          /* Red - Critical */
--abena-info: #3B82F6;           /* Blue - Information */
```

---

## 🎯 **Application Strategy**

### **Dashboard Headers:**
- Primary: Deep Blue (`#1E40AF`)
- Accent: Purple for quantum/AI features (`#8B5CF6`)
- Success: Green for health metrics (`#10B981`)

### **Buttons:**
- Primary Action: Deep Blue
- Secondary Action: Green
- Tertiary Action: Purple (for advanced features)

### **Gradients:**
```css
/* Hero sections */
background: linear-gradient(135deg, #1E40AF 0%, #8B5CF6 100%);

/* Success states */
background: linear-gradient(135deg, #10B981 0%, #34D399 100%);

/* Innovation/Tech */
background: linear-gradient(135deg, #8B5CF6 0%, #3B82F6 100%);
```

### **Card Shadows:**
```css
box-shadow: 0 4px 6px -1px rgba(30, 64, 175, 0.1),
            0 2px 4px -1px rgba(30, 64, 175, 0.06);
```

---

## 📋 **Implementation Checklist**

- [ ] Create professional landing/cover page
- [ ] Update Admin Dashboard with ABENA colors
- [ ] Update Provider Portal with ABENA colors
- [ ] Update Patient Portal with ABENA colors
- [ ] Update Quantum Analysis page with ABENA colors
- [ ] Update eCBome Intelligence with ABENA colors
- [ ] Ensure consistent button styles across all platforms
- [ ] Apply professional typography
- [ ] Add ABENA logo placement guidelines

