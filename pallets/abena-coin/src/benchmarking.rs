//! Benchmarks for pallet-abena-coin.
//!
//! Targets (expanded from baseline):
//!   mint                        – create tokens from Root
//!   burn                        – destroy caller's tokens
//!   transfer                    – move tokens between accounts (baseline)
//!   grant_reward                – reward an account (Root)
//!   claim_achievement           – claim a gamification badge
//!   stake                       – stake tokens to earn staking tier
//!   unstake                     – unstake tokens
//!   distribute_patient_reward   – Root distributes reward to one patient
//!   distribute_rewards_bulk     – block benchmark: distribute to n patients (linear)
//!   submit_proposal             – create a governance proposal
//!   vote_on_proposal            – cast one vote with large voting power
//!   vote_on_proposal_many       – cast vote when n voters already voted (linear)
//!   delegate_votes              – delegate voting power

use super::*;
use frame_benchmarking::{account, benchmarks, whitelisted_caller};
use frame_support::traits::Get;
use frame_system::RawOrigin;
use sp_runtime::traits::{Hash as HashTrait, SaturatedConversion, Zero};

const SEED: u32 = 0;
// 1 billion micro-ABENA (well within BalanceOf<T> for any reasonable configuration)
const LARGE_AMOUNT: u128 = 1_000_000_000u128;
// Bronze minimum stake: 100_000 ABENA * 10^18 (matches min_stake_for_tier internals)
const BRONZE_MIN_STAKE: u128 = 100_000u128 * 1_000_000_000_000_000_000u128;

fn make_hash<T: Config>(seed: u32) -> T::Hash {
    let mut b = [0u8; 32];
    b[0..4].copy_from_slice(&seed.to_le_bytes());
    T::Hashing::hash(&b)
}

/// Fund `who` directly in storage with `amount` (bypasses all checks).
fn fund<T: Config>(who: &T::AccountId, amount: BalanceOf<T>) {
    Balances::<T>::insert(who, amount);
    TotalSupply::<T>::mutate(|s| *s += amount);
}

/// Submit a governance proposal and return its ID.
fn submit_proposal_helper<T: Config>(
    proposer: T::AccountId,
) -> Result<u32, sp_runtime::DispatchError> {
    let deposit: BalanceOf<T> = T::MinProposalDeposit::get();
    fund::<T>(&proposer, deposit + deposit); // give extra to cover deposit
    let desc_hash = make_hash::<T>(99u32);
    Pallet::<T>::submit_proposal(
        RawOrigin::Signed(proposer).into(),
        ProposalType::TreasurySpend,
        desc_hash,
        None,
        None,
    )?;
    // Proposal ID counter starts at 0 and increments.
    Ok(NextProposalId::<T>::get().saturating_sub(1))
}

benchmarks! {

    // ── mint ─────────────────────────────────────────────────────────────
    mint {
        let caller: T::AccountId = whitelisted_caller();
        let amount: BalanceOf<T> = 1_000u128.saturated_into();
    }: _(RawOrigin::Root, caller.clone(), amount)
    verify {
        assert!(Balances::<T>::contains_key(&caller));
    }

    // ── burn ─────────────────────────────────────────────────────────────
    burn {
        let caller: T::AccountId = whitelisted_caller();
        let amount: BalanceOf<T> = 1_000u128.saturated_into();
        Pallet::<T>::mint(RawOrigin::Root.into(), caller.clone(), amount)?;
    }: _(RawOrigin::Signed(caller.clone()), amount)
    verify {
        assert_eq!(Balances::<T>::get(&caller), Zero::zero());
    }

    // ── transfer ─────────────────────────────────────────────────────────
    // Baseline: single transfer between two fresh accounts.
    transfer {
        let from: T::AccountId = whitelisted_caller();
        let to: T::AccountId   = account("to", 0, SEED);
        let amount: BalanceOf<T> = 1_000u128.saturated_into();
        Pallet::<T>::mint(RawOrigin::Root.into(), from.clone(), amount)?;
    }: _(RawOrigin::Signed(from.clone()), to.clone(), amount)
    verify {
        assert_eq!(Balances::<T>::get(&from), Zero::zero());
        assert_eq!(Balances::<T>::get(&to), amount);
    }

    // ── grant_reward ──────────────────────────────────────────────────────
    grant_reward {
        let acct: T::AccountId = whitelisted_caller();
        let reward_type = RewardType::HealthRecordCreated;
        let amount: BalanceOf<T> = 100u128.saturated_into();
    }: _(RawOrigin::Root, acct.clone(), reward_type, amount)
    verify {
        assert!(Balances::<T>::contains_key(&acct));
    }

    // ── claim_achievement ─────────────────────────────────────────────────
    claim_achievement {
        let caller: T::AccountId = whitelisted_caller();
        let achievement = AchievementType::HealthRecordCreator;
    }: _(RawOrigin::Signed(caller.clone()), achievement)
    verify {
        assert!(Achievements::<T>::contains_key(&caller));
    }

    // ── stake ─────────────────────────────────────────────────────────────
    // Stake the minimum Bronze amount (100_000 ABENA * 10^18 raw units).
    stake {
        let caller: T::AccountId = whitelisted_caller();
        let min_stake: BalanceOf<T> = BRONZE_MIN_STAKE.saturated_into();
        // Fund with 2× the stake so the balance check passes.
        let fund_amount: BalanceOf<T> = (BRONZE_MIN_STAKE * 2).saturated_into();
        fund::<T>(&caller, fund_amount);
    }: _(RawOrigin::Signed(caller.clone()), min_stake)
    verify {
        assert!(StakedBalances::<T>::get(&caller) >= min_stake);
    }

    // ── unstake ───────────────────────────────────────────────────────────
    unstake {
        let caller: T::AccountId = whitelisted_caller();
        let min_stake: BalanceOf<T> = BRONZE_MIN_STAKE.saturated_into();
        let fund_amount: BalanceOf<T> = (BRONZE_MIN_STAKE * 2).saturated_into();
        fund::<T>(&caller, fund_amount);
        Pallet::<T>::stake(RawOrigin::Signed(caller.clone()).into(), min_stake)?;
    }: _(RawOrigin::Signed(caller.clone()), min_stake)
    verify {
        assert_eq!(StakedBalances::<T>::get(&caller), Zero::zero());
    }

    // ── distribute_patient_reward ─────────────────────────────────────────
    // Root distributes a reward to a single patient.
    // Reward pool must be funded first.
    distribute_patient_reward {
        let patient: T::AccountId = whitelisted_caller();
        let reward_amount: BalanceOf<T> = 100u128.saturated_into();
        // Fund the reward pool directly.
        RewardPool::<T>::put(reward_amount + reward_amount);
    }: _(RawOrigin::Root, patient.clone(), reward_amount)
    verify {
        assert_eq!(Balances::<T>::get(&patient), reward_amount);
    }

    // ── distribute_rewards_bulk ───────────────────────────────────────────
    // Block benchmark: measure cost of distributing to n patients in a loop.
    distribute_rewards_bulk {
        let n in 1 .. 1_000u32;

        let reward_per_patient: BalanceOf<T> = 10u128.saturated_into();
        let pool_total: BalanceOf<T> = (10u128 * n as u128).saturated_into();
        RewardPool::<T>::put(pool_total);

        // Pre-create patient accounts.
        let patients: sp_std::vec::Vec<T::AccountId> = (0..n)
            .map(|i| account("patient", i, SEED))
            .collect();
    }: {
        for patient in patients.iter() {
            let _ = Pallet::<T>::distribute_patient_reward(
                RawOrigin::Root.into(),
                patient.clone(),
                reward_per_patient,
            );
        }
    }
    verify {
        // At least the last patient received their reward.
        let last = account::<T::AccountId>("patient", n - 1, SEED);
        assert_eq!(Balances::<T>::get(&last), reward_per_patient);
    }

    // ── submit_proposal ───────────────────────────────────────────────────
    // Create a governance proposal; proposer needs to hold the deposit.
    submit_proposal {
        let proposer: T::AccountId = whitelisted_caller();
        let deposit: BalanceOf<T>  = T::MinProposalDeposit::get();
        fund::<T>(&proposer, deposit + deposit);
        let desc_hash = make_hash::<T>(1u32);
    }: _(
        RawOrigin::Signed(proposer.clone()),
        ProposalType::TreasurySpend,
        desc_hash,
        None,
        None
    )
    verify {
        let pid = NextProposalId::<T>::get().saturating_sub(1);
        assert!(Proposals::<T>::contains_key(pid));
    }

    // ── vote_on_proposal ──────────────────────────────────────────────────
    // Cast a vote with large voting power (models "1 million ABENA" scenario).
    vote_on_proposal {
        let voter: T::AccountId = whitelisted_caller();
        let voting_power: BalanceOf<T> = LARGE_AMOUNT.saturated_into();
        fund::<T>(&voter, voting_power);

        let proposer: T::AccountId = account("proposer", 0, SEED);
        let proposal_id = submit_proposal_helper::<T>(proposer)?;
    }: _(
        RawOrigin::Signed(voter.clone()),
        proposal_id,
        VoteDirection::Yes,
        voting_power,
        0u32.into()
    )
    verify {
        assert!(Votes::<T>::contains_key(proposal_id, &voter));
    }

    // ── vote_on_proposal_many ──────────────────────────────────────────────
    // Worst-case: n voters have already voted; one more voter casts the n+1-th vote.
    vote_on_proposal_many {
        let n in 1 .. 500u32;

        let proposer: T::AccountId = account("proposer", 0, SEED);
        let proposal_id = submit_proposal_helper::<T>(proposer)?;

        // Pre-cast n votes (O(1) per entry; no iteration in vote_on_proposal).
        for i in 0..n {
            let v: T::AccountId = account("voter", i, SEED);
            let power: BalanceOf<T> = 100u128.saturated_into();
            fund::<T>(&v, power);
            Votes::<T>::insert(
                proposal_id,
                &v,
                VoteRecord::<T> {
                    direction: VoteDirection::Yes,
                    voting_power: power,
                    conviction_blocks: 0u32.into(),
                },
            );
        }

        let new_voter: T::AccountId = account("new_voter", n, SEED);
        let power: BalanceOf<T> = 100u128.saturated_into();
        fund::<T>(&new_voter, power);
    }: vote_on_proposal(
        RawOrigin::Signed(new_voter.clone()),
        proposal_id,
        VoteDirection::Yes,
        power,
        0u32.into()
    )
    verify {
        assert!(Votes::<T>::contains_key(proposal_id, &new_voter));
    }

    // ── delegate_votes ────────────────────────────────────────────────────
    // Delegate voting power to another account.
    delegate_votes {
        let delegator: T::AccountId = whitelisted_caller();
        let delegate: T::AccountId  = account("delegate", 0, SEED);
        fund::<T>(&delegator, 1_000u128.saturated_into());
    }: _(RawOrigin::Signed(delegator.clone()), delegate.clone())
    verify {
        assert_eq!(DelegatedVotes::<T>::get(&delegator), Some(delegate));
    }

    impl_benchmark_test_suite!(
        Pallet,
        crate::mock::new_test_ext(),
        crate::mock::Test,
    );
}
