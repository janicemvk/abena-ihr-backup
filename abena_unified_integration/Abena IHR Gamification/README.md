# Abena IHR Gamification System

A comprehensive gamification system for the Abena Individualized Health Record (IHR) platform that transforms health data entry into an engaging, rewarding experience while maintaining medical credibility and data accuracy.

## Features

### Core Gamification Elements

- **Progressive Leveling System**
  - XP-based advancement (1000 XP per level)
  - Visual progress bars
  - Level-up animations
  - Feature unlocks with progression

- **Dynamic Quest System**
  - Daily micro-quests (2-5 minutes)
  - Weekly challenges
  - Streak-based quests
  - Personalized health goals

- **Badge & Achievement System**
  - 4 rarity tiers (Common, Rare, Epic, Legendary)
  - Health data achievements
  - Wellness practice badges
  - Community engagement rewards

- **Reward System**
  - Immediate XP rewards
  - Streak bonuses
  - Milestone rewards
  - Tangible rewards integration

- **Social Features (Privacy-First)**
  - Anonymous leaderboards
  - Community challenges
  - Optional achievement sharing
  - No health data exposure

## Technical Stack

- React with TypeScript
- Context API for state management
- Tailwind CSS for styling
- Lucide React for icons
- Framer Motion for animations

## Getting Started

1. Install dependencies:
   ```bash
   npm install
   ```

2. Start the development server:
   ```bash
   npm start
   ```

3. Build for production:
   ```bash
   npm run build
   ```

## Project Structure

```
src/
  ├── components/
  │   └── AbenaGamificationSystem.tsx
  ├── index.tsx
  └── index.css
```

## Components

- `GamificationProvider`: Context provider for global state
- `useGamification`: Custom hook for accessing gamification features
- `XPAnimation`: Celebratory animations for XP gains
- `ProgressBar`: Visual progress indicators
- `BadgeComponent`: Badge display with rarity styling
- `QuestComponent`: Interactive quest cards with progress
- `Dashboard`: Main gamification interface
- `TestInterface`: Built-in testing controls

## Development Guidelines

- Use functional components with hooks
- Implement proper error handling
- Add loading states for async operations
- Ensure accessibility compliance
- Create reusable, modular components
- Include comprehensive JSDoc comments
- Follow React best practices

## Success Metrics

- Engagement: +40% daily active users, +60% session time
- Data Quality: 90% completion rate, >95% accuracy
- Retention: 85% week-1, 70% month-1, 50% month-3
- Health Outcomes: Improved treatment adherence

## Medical Integrity

- XP rewards don't incentivize false data
- Focus on consistency over quantity
- Maintain clinical accuracy requirements
- No gamification of critical health alerts

## License

MIT License 