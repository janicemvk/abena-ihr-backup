import React, { useState, useEffect } from 'react';
import { 
  ShoppingCart, Star, Package, Truck, Gift, 
  Leaf, Droplets, Pill, Sparkles, Award,
  Heart, Clock, CheckCircle, X as CloseIcon,
  Filter, Search, Tag, Info, ExternalLink
} from 'lucide-react';

interface RewardItem {
  id: string;
  name: string;
  description: string;
  category: 'cbd' | 'wellness' | 'digital' | 'physical';
  subcategory: string;
  xpCost: number;
  originalValue: number;
  imageUrl: string;
  availability: number;
  rarity: 'COMMON' | 'RARE' | 'EPIC' | 'LEGENDARY';
  benefits: string[];
  shipping: {
    required: boolean;
    estimatedDays?: number;
  };
  restrictions: {
    ageRequired?: number;
    locationRestrictions?: string[];
    maxPerUser?: number;
  };
  supplier: {
    name: string;
    verified: boolean;
    rating: number;
  };
  tags: string[];
}

interface UserRedemption {
  id: string;
  rewardId: string;
  redeemedAt: string;
  status: 'processing' | 'shipped' | 'delivered' | 'cancelled';
  trackingNumber?: string;
  estimatedDelivery?: string;
}

interface RewardsMarketplaceProps {
  userXP: number;
  userLevel: number;
  onRedemption: (reward: RewardItem) => void;
  redemptions: UserRedemption[];
}

const REWARD_ITEMS: RewardItem[] = [
  {
    id: 'cbd_sample_pack_1',
    name: 'Premium CBD Tincture Sample Pack',
    description: 'Try our premium CBD tinctures with this sample pack containing 3 different strengths and flavors.',
    category: 'cbd',
    subcategory: 'tinctures',
    xpCost: 2500,
    originalValue: 45.99,
    imageUrl: '/rewards/cbd-tincture-pack.jpg',
    availability: 50,
    rarity: 'RARE',
    benefits: ['Pain Relief', 'Anxiety Support', 'Sleep Aid', 'Natural Formula'],
    shipping: { required: true, estimatedDays: 5 },
    restrictions: { ageRequired: 21, maxPerUser: 1 },
    supplier: { name: 'Abena Wellness', verified: true, rating: 4.8 },
    tags: ['cbd', 'sample', 'premium', 'tincture']
  },
  {
    id: 'cbd_gummies_trial',
    name: 'CBD Gummies Trial Pack',
    description: 'Delicious fruit-flavored CBD gummies perfect for beginners. Each pack contains 10 gummies (10mg each).',
    category: 'cbd',
    subcategory: 'edibles',
    xpCost: 1800,
    originalValue: 29.99,
    imageUrl: '/rewards/cbd-gummies.jpg',
    availability: 75,
    rarity: 'COMMON',
    benefits: ['Stress Relief', 'Mood Support', 'Easy Dosing', 'Great Taste'],
    shipping: { required: true, estimatedDays: 3 },
    restrictions: { ageRequired: 21, maxPerUser: 2 },
    supplier: { name: 'Abena Wellness', verified: true, rating: 4.9 },
    tags: ['cbd', 'gummies', 'beginner', 'trial']
  },
  {
    id: 'topical_cream_sample',
    name: 'CBD Topical Relief Cream',
    description: 'Fast-acting topical CBD cream for targeted relief. Perfect for muscle soreness and joint discomfort.',
    category: 'cbd',
    subcategory: 'topicals',
    xpCost: 3200,
    originalValue: 59.99,
    imageUrl: '/rewards/cbd-topical.jpg',
    availability: 30,
    rarity: 'EPIC',
    benefits: ['Targeted Relief', 'Fast Acting', 'Non-Greasy', 'Laboratory Tested'],
    shipping: { required: true, estimatedDays: 7 },
    restrictions: { ageRequired: 18, maxPerUser: 1 },
    supplier: { name: 'Abena Wellness', verified: true, rating: 4.7 },
    tags: ['cbd', 'topical', 'relief', 'muscle']
  },
  {
    id: 'wellness_journal',
    name: 'Digital Wellness Journal',
    description: 'Premium digital journal template with guided prompts for tracking your wellness journey.',
    category: 'digital',
    subcategory: 'tools',
    xpCost: 800,
    originalValue: 19.99,
    imageUrl: '/rewards/wellness-journal.jpg',
    availability: 999,
    rarity: 'COMMON',
    benefits: ['Self-Reflection', 'Progress Tracking', 'Guided Prompts', 'Instant Access'],
    shipping: { required: false },
    restrictions: { maxPerUser: 1 },
    supplier: { name: 'Abena Digital', verified: true, rating: 4.6 },
    tags: ['digital', 'journal', 'wellness', 'tracking']
  },
  {
    id: 'premium_consultation',
    name: '1-on-1 Wellness Consultation',
    description: 'Personal consultation with certified wellness expert to discuss your health goals and create a plan.',
    category: 'digital',
    subcategory: 'services',
    xpCost: 5000,
    originalValue: 149.99,
    imageUrl: '/rewards/consultation.jpg',
    availability: 10,
    rarity: 'LEGENDARY',
    benefits: ['Personalized Advice', 'Expert Guidance', '60-Minute Session', 'Follow-up Plan'],
    shipping: { required: false },
    restrictions: { maxPerUser: 1 },
    supplier: { name: 'Abena Experts', verified: true, rating: 5.0 },
    tags: ['consultation', 'expert', 'personalized', 'wellness']
  }
];

const RARITY_STYLES = {
  COMMON: { 
    border: 'border-gray-300', 
    bg: 'bg-gray-50', 
    text: 'text-gray-700',
    glow: 'shadow-gray-200'
  },
  RARE: { 
    border: 'border-blue-300', 
    bg: 'bg-blue-50', 
    text: 'text-blue-700',
    glow: 'shadow-blue-200'
  },
  EPIC: { 
    border: 'border-purple-300', 
    bg: 'bg-purple-50', 
    text: 'text-purple-700',
    glow: 'shadow-purple-200'
  },
  LEGENDARY: { 
    border: 'border-yellow-300', 
    bg: 'bg-yellow-50', 
    text: 'text-yellow-700',
    glow: 'shadow-yellow-200'
  }
};

const RewardsMarketplace: React.FC<RewardsMarketplaceProps> = ({
  userXP,
  userLevel,
  onRedemption,
  redemptions
}) => {
  const [rewards, setRewards] = useState<RewardItem[]>(REWARD_ITEMS);
  const [filteredRewards, setFilteredRewards] = useState<RewardItem[]>(REWARD_ITEMS);
  const [selectedReward, setSelectedReward] = useState<RewardItem | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterCategory, setFilterCategory] = useState<string>('all');
  const [sortBy, setSortBy] = useState<'name' | 'xpCost' | 'rarity'>('xpCost');
  const [showFilters, setShowFilters] = useState(false);
  const [cart, setCart] = useState<RewardItem[]>([]);
  const [showRedemptionModal, setShowRedemptionModal] = useState(false);

  // Filter and sort rewards
  useEffect(() => {
    let filtered = rewards.filter(reward => {
      const matchesSearch = reward.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           reward.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           reward.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()));
      
      const matchesCategory = filterCategory === 'all' || reward.category === filterCategory;
      
      return matchesSearch && matchesCategory;
    });

    // Sort rewards
    filtered.sort((a, b) => {
      switch (sortBy) {
        case 'name':
          return a.name.localeCompare(b.name);
        case 'xpCost':
          return a.xpCost - b.xpCost;
        case 'rarity':
          const rarityOrder = { 'COMMON': 0, 'RARE': 1, 'EPIC': 2, 'LEGENDARY': 3 };
          return rarityOrder[b.rarity] - rarityOrder[a.rarity];
        default:
          return 0;
      }
    });

    setFilteredRewards(filtered);
  }, [rewards, searchTerm, filterCategory, sortBy]);

  const canAfford = (reward: RewardItem) => userXP >= reward.xpCost;
  const canRedeem = (reward: RewardItem) => {
    if (!canAfford(reward)) return false;
    if (reward.availability <= 0) return false;
    
    const userRedemptions = redemptions.filter(r => r.rewardId === reward.id);
    if (reward.restrictions.maxPerUser && userRedemptions.length >= reward.restrictions.maxPerUser) {
      return false;
    }
    
    return true;
  };

  const handleRedemption = (reward: RewardItem) => {
    if (canRedeem(reward)) {
      setSelectedReward(reward);
      setShowRedemptionModal(true);
    }
  };

  const confirmRedemption = () => {
    if (selectedReward) {
      onRedemption(selectedReward);
      setRewards(prev => prev.map(r => 
        r.id === selectedReward.id 
          ? { ...r, availability: r.availability - 1 }
          : r
      ));
      setShowRedemptionModal(false);
      setSelectedReward(null);
    }
  };

  const RewardCard: React.FC<{ reward: RewardItem }> = ({ reward }) => {
    const rarityStyle = RARITY_STYLES[reward.rarity];
    const affordable = canAfford(reward);
    const redeemable = canRedeem(reward);

    return (
      <div className={`bg-white rounded-xl shadow-sm border-2 ${rarityStyle.border} ${rarityStyle.glow} overflow-hidden transition-all duration-300 hover:shadow-md`}>
        <div className="relative">
          <div className="h-48 bg-gray-100 flex items-center justify-center">
            <Package className="w-16 h-16 text-gray-400" />
          </div>
          <div className={`absolute top-2 right-2 px-2 py-1 rounded-full text-xs font-bold ${rarityStyle.bg} ${rarityStyle.text}`}>
            {reward.rarity}
          </div>
          {reward.supplier.verified && (
            <div className="absolute top-2 left-2 bg-green-500 text-white px-2 py-1 rounded-full text-xs font-bold flex items-center gap-1">
              <CheckCircle className="w-3 h-3" />
              Verified
            </div>
          )}
        </div>
        
        <div className="p-4">
          <div className="mb-2">
            <h3 className="font-bold text-lg mb-1">{reward.name}</h3>
            <p className="text-sm text-gray-600 mb-2">{reward.description}</p>
            
            <div className="flex items-center gap-2 mb-2">
              <span className="text-xs bg-gray-100 px-2 py-1 rounded">{reward.subcategory}</span>
              {reward.shipping.required ? (
                <span className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded flex items-center gap-1">
                  <Truck className="w-3 h-3" />
                  Ships in {reward.shipping.estimatedDays} days
                </span>
              ) : (
                <span className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded">
                  Instant Access
                </span>
              )}
            </div>
          </div>

          <div className="mb-3">
            <div className="flex flex-wrap gap-1 mb-2">
              {reward.benefits.slice(0, 3).map((benefit, index) => (
                <span key={index} className="text-xs bg-green-50 text-green-700 px-2 py-1 rounded">
                  {benefit}
                </span>
              ))}
            </div>
          </div>

          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <Star className="w-4 h-4 text-yellow-500" />
              <span className="text-sm font-medium">{reward.supplier.rating}</span>
              <span className="text-xs text-gray-500">({reward.supplier.name})</span>
            </div>
            <div className="text-right">
              <div className="text-lg font-bold text-blue-600">{reward.xpCost.toLocaleString()} XP</div>
              <div className="text-xs text-gray-500 line-through">${reward.originalValue}</div>
            </div>
          </div>

          <div className="mb-3">
            <div className="flex justify-between text-xs text-gray-500 mb-1">
              <span>Available</span>
              <span>{reward.availability} left</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                style={{ width: `${Math.min((reward.availability / 100) * 100, 100)}%` }}
              />
            </div>
          </div>

          <button
            onClick={() => handleRedemption(reward)}
            disabled={!redeemable}
            className={`w-full py-2 px-4 rounded-lg font-medium transition-colors ${
              redeemable
                ? 'bg-blue-500 hover:bg-blue-600 text-white'
                : affordable
                  ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  : 'bg-red-100 text-red-600 cursor-not-allowed'
            }`}
          >
            {!affordable ? `Need ${(reward.xpCost - userXP).toLocaleString()} more XP` :
             reward.availability <= 0 ? 'Out of Stock' :
             'Redeem Now'}
          </button>
        </div>
      </div>
    );
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-green-500 to-blue-600 text-white rounded-xl p-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold mb-2 flex items-center gap-2">
              <Gift className="w-8 h-8" />
              Rewards Marketplace
            </h2>
            <p className="text-green-100">Redeem your XP for premium CBD samples and wellness rewards</p>
          </div>
          <div className="text-right">
            <div className="text-3xl font-bold">{userXP.toLocaleString()}</div>
            <div className="text-green-100">Available XP</div>
          </div>
        </div>
      </div>

      {/* Filters and Search */}
      <div className="bg-white rounded-xl shadow-sm p-4">
        <div className="flex flex-col md:flex-row gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
            <input
              type="text"
              placeholder="Search rewards..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          
          <div className="flex gap-2">
            <select
              value={filterCategory}
              onChange={(e) => setFilterCategory(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Categories</option>
              <option value="cbd">CBD Products</option>
              <option value="wellness">Wellness</option>
              <option value="digital">Digital</option>
              <option value="physical">Physical</option>
            </select>
            
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as any)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="xpCost">Sort by XP Cost</option>
              <option value="name">Sort by Name</option>
              <option value="rarity">Sort by Rarity</option>
            </select>
          </div>
        </div>
      </div>

      {/* Rewards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredRewards.map(reward => (
          <RewardCard key={reward.id} reward={reward} />
        ))}
      </div>

      {filteredRewards.length === 0 && (
        <div className="text-center py-12">
          <Package className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-gray-600 mb-2">No rewards found</h3>
          <p className="text-gray-500">Try adjusting your search or filters</p>
        </div>
      )}

      {/* Redemption Modal */}
      {showRedemptionModal && selectedReward && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-lg max-w-md w-full p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-bold">Confirm Redemption</h3>
              <button 
                onClick={() => setShowRedemptionModal(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <CloseIcon className="w-6 h-6" />
              </button>
            </div>
            
            <div className="mb-6">
              <h4 className="font-semibold mb-2">{selectedReward.name}</h4>
              <p className="text-gray-600 text-sm mb-4">{selectedReward.description}</p>
              
              <div className="bg-gray-50 rounded-lg p-4 mb-4">
                <div className="flex justify-between items-center mb-2">
                  <span>XP Cost:</span>
                  <span className="font-bold text-blue-600">{selectedReward.xpCost.toLocaleString()} XP</span>
                </div>
                <div className="flex justify-between items-center mb-2">
                  <span>Your XP:</span>
                  <span className="font-bold">{userXP.toLocaleString()} XP</span>
                </div>
                <div className="flex justify-between items-center border-t pt-2">
                  <span>Remaining XP:</span>
                  <span className="font-bold text-green-600">{(userXP - selectedReward.xpCost).toLocaleString()} XP</span>
                </div>
              </div>
              
              {selectedReward.shipping.required && (
                <div className="bg-blue-50 rounded-lg p-3 mb-4">
                  <div className="flex items-center gap-2 text-blue-700 text-sm">
                    <Truck className="w-4 h-4" />
                    <span>Ships in {selectedReward.shipping.estimatedDays} business days</span>
                  </div>
                </div>
              )}
              
              {selectedReward.restrictions.ageRequired && (
                <div className="bg-yellow-50 rounded-lg p-3 mb-4">
                  <div className="flex items-center gap-2 text-yellow-700 text-sm">
                    <Info className="w-4 h-4" />
                    <span>Age verification required (21+)</span>
                  </div>
                </div>
              )}
            </div>
            
            <div className="flex gap-3">
              <button
                onClick={() => setShowRedemptionModal(false)}
                className="flex-1 py-2 px-4 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={confirmRedemption}
                className="flex-1 py-2 px-4 bg-blue-500 hover:bg-blue-600 text-white rounded-lg transition-colors"
              >
                Confirm Redemption
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default RewardsMarketplace; 