//! Weights for abena-coin pallet

use frame_support::weights::Weight;

pub struct SubstrateWeight<T>(sp_std::marker::PhantomData<T>);

impl<T: frame_system::Config> crate::WeightInfo for SubstrateWeight<T> {
    fn mint() -> Weight {
        Weight::from_parts(30_000_000, 0)
            .saturating_add(Weight::from_parts(0, 0))
    }

    fn burn() -> Weight {
        Weight::from_parts(30_000_000, 0)
            .saturating_add(Weight::from_parts(0, 0))
    }

    fn transfer() -> Weight {
        Weight::from_parts(40_000_000, 0)
            .saturating_add(Weight::from_parts(0, 0))
    }

    fn grant_reward() -> Weight {
        Weight::from_parts(50_000_000, 0)
            .saturating_add(Weight::from_parts(0, 0))
    }

    fn claim_achievement() -> Weight {
        Weight::from_parts(45_000_000, 0)
            .saturating_add(Weight::from_parts(0, 0))
    }

    fn approve() -> Weight {
        Weight::from_parts(30_000_000, 0)
    }
    fn transfer_from() -> Weight {
        Weight::from_parts(50_000_000, 0)
    }
    fn stake() -> Weight {
        Weight::from_parts(45_000_000, 0)
    }
    fn unstake() -> Weight {
        Weight::from_parts(45_000_000, 0)
    }
    fn claim_vested_tokens() -> Weight {
        Weight::from_parts(60_000_000, 0)
    }
    fn distribute_patient_reward() -> Weight {
        Weight::from_parts(40_000_000, 0)
    }
    fn vote() -> Weight {
        Weight::from_parts(25_000_000, 0)
    }
    fn pay_on_behalf() -> Weight {
        Weight::from_parts(40_000_000, 0)
    }
    fn add_vesting_schedule() -> Weight {
        Weight::from_parts(55_000_000, 0)
    }
    fn fund_reward_pool() -> Weight {
        Weight::from_parts(30_000_000, 0)
    }
    fn create_achievement() -> Weight {
        Weight::from_parts(60_000_000, 0)
    }
    fn claim_gamification_achievement() -> Weight {
        Weight::from_parts(70_000_000, 0)
    }
    fn verify_achievement() -> Weight {
        Weight::from_parts(40_000_000, 0)
    }
    fn award_streak_bonus() -> Weight {
        Weight::from_parts(45_000_000, 0)
    }
    fn update_streak() -> Weight {
        Weight::from_parts(35_000_000, 0)
    }
    fn register_referral() -> Weight {
        Weight::from_parts(40_000_000, 0)
    }
    fn set_seasonal_multiplier() -> Weight {
        Weight::from_parts(25_000_000, 0)
    }
    fn submit_proposal() -> Weight {
        Weight::from_parts(60_000_000, 0)
    }
    fn vote_on_proposal() -> Weight {
        Weight::from_parts(55_000_000, 0)
    }
    fn delegate_votes() -> Weight {
        Weight::from_parts(30_000_000, 0)
    }
    fn execute_proposal() -> Weight {
        Weight::from_parts(70_000_000, 0)
    }
    fn treasury_allocate() -> Weight {
        Weight::from_parts(40_000_000, 0)
    }
    fn claim_treasury_grant() -> Weight {
        Weight::from_parts(45_000_000, 0)
    }
    fn collect_to_treasury() -> Weight {
        Weight::from_parts(35_000_000, 0)
    }
    fn update_voting_parameters() -> Weight {
        Weight::from_parts(30_000_000, 0)
    }
}

