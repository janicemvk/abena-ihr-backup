//! # ABENA Account Management Pallet
//!
//! Tiered account types for the ABENA IHR: Patient, Provider, and Institution.
//! Handles credential verification (licenses, certifications, accreditation),
//! deposit management for providers/institutions, and account lifecycle. Foundation
//! for role-based access across ABENA pallets.

#![cfg_attr(not(feature = "std"), no_std)]

use codec::{Encode, Decode, MaxEncodedLen};
use scale_info::TypeInfo;
use sp_runtime::RuntimeDebug;
use frame_system::pallet_prelude::BlockNumberFor;
use frame_support::weights::Weight;
use sp_runtime::BoundedVec;
use frame_support::traits::{ConstU32, Currency};

#[cfg(test)]
mod mock;

#[cfg(test)]
mod tests;

#[cfg(feature = "runtime-benchmarks")]
mod benchmarking;
pub mod weights;

#[frame_support::pallet]
pub mod pallet {
    use frame_support::{
        pallet_prelude::*,
        traits::{Currency, ReservableCurrency, ExistenceRequirement},
        traits::ConstU32,
    };
    use frame_system::pallet_prelude::*;
    use scale_info::TypeInfo;
    use sp_std::vec::Vec;
    use sp_runtime::traits::{Zero, Saturating};
    use codec::MaxEncodedLen;
    use sp_runtime::BoundedVec;
    use super::{AccountTier, AccountInfo, CredentialVerification, DepositInfo, VerificationStatus, CredentialType};
    use crate::WeightInfo;

    /// Balance type alias
    pub type BalanceOf<T> = <<T as Config>::Currency as Currency<<T as frame_system::Config>::AccountId>>::Balance;

    /// Configuration trait for the pallet.
    #[pallet::config]
    pub trait Config: frame_system::Config {
        /// The overarching event type.
        type RuntimeEvent: From<Event<Self>> + IsType<<Self as frame_system::Config>::RuntimeEvent>;
        /// Weight information for extrinsics
        type WeightInfo: crate::WeightInfo;
        /// Currency type for deposits
        type Currency: Currency<Self::AccountId> + ReservableCurrency<Self::AccountId>;
    }

    #[pallet::pallet]
    pub struct Pallet<T>(_);

    /// Account information by account ID
    /// Maps account to account info
    #[pallet::storage]
    pub type AccountInfos<T: Config> = StorageMap<
        _,
        Blake2_128Concat,
        T::AccountId,
        AccountInfo<T>,
        OptionQuery,
    >;

    /// Credential verifications
    /// Maps (account, credential_id) to verification
    #[pallet::storage]
    pub type CredentialVerifications<T: Config> = StorageDoubleMap<
        _,
        Blake2_128Concat,
        T::AccountId,
        Blake2_128Concat,
        u64,
        CredentialVerification<T>,
        OptionQuery,
    >;

    /// Deposit information
    /// Maps account to deposit info
    #[pallet::storage]
    pub type DepositInfos<T: Config> = StorageMap<
        _,
        Blake2_128Concat,
        T::AccountId,
        DepositInfo<T>,
        OptionQuery,
    >;

    /// Events emitted by this pallet
    #[pallet::event]
    #[pallet::generate_deposit(pub(super) fn deposit_event)]
    pub enum Event<T: Config> {
        /// Account registered with tier
        AccountRegistered {
            account: T::AccountId,
            tier: AccountTier,
        },
        /// Account tier updated
        AccountTierUpdated {
            account: T::AccountId,
            old_tier: AccountTier,
            new_tier: AccountTier,
        },
        /// Credential submitted for verification
        CredentialSubmitted {
            account: T::AccountId,
            credential_id: u64,
            credential_type: CredentialType,
        },
        /// Credential verified
        CredentialVerified {
            account: T::AccountId,
            credential_id: u64,
            verified_by: T::AccountId,
        },
        /// Credential verification rejected
        CredentialRejected {
            account: T::AccountId,
            credential_id: u64,
            reason: Vec<u8>,
        },
        /// Deposit made
        DepositMade {
            account: T::AccountId,
            amount: BalanceOf<T>,
            total_deposit: BalanceOf<T>,
        },
        /// Deposit withdrawn
        DepositWithdrawn {
            account: T::AccountId,
            amount: BalanceOf<T>,
            remaining_deposit: BalanceOf<T>,
        },
    }

    /// Errors that can occur in this pallet
    #[pallet::error]
    pub enum Error<T> {
        /// Account not found
        AccountNotFound,
        /// Account already registered
        AccountAlreadyRegistered,
        /// Invalid account tier
        InvalidTier,
        /// Credential not found
        CredentialNotFound,
        /// Credential already verified
        CredentialAlreadyVerified,
        /// Insufficient deposit
        InsufficientDeposit,
        /// Invalid credential type
        InvalidCredentialType,
        /// Content too large
        ContentTooLarge,
    }

    /// Hooks for the pallet
    #[pallet::hooks]
    impl<T: Config> Hooks<BlockNumberFor<T>> for Pallet<T> {}

    /// Extrinsics for the pallet
    #[pallet::call]
    impl<T: Config> Pallet<T> {
        /// Register account with tier
        #[pallet::call_index(0)]
        #[pallet::weight(T::WeightInfo::register_account())]
        pub fn register_account(
            origin: OriginFor<T>,
            tier: AccountTier,
        ) -> DispatchResult {
            let account = ensure_signed(origin)?;

            ensure!(
                !AccountInfos::<T>::contains_key(&account),
                Error::<T>::AccountAlreadyRegistered
            );

            let account_info = AccountInfo {
                account: account.clone(),
                tier,
                registered_at: <frame_system::Pallet<T>>::block_number(),
                verified: false,
            };

            AccountInfos::<T>::insert(&account, account_info);

            Self::deposit_event(Event::AccountRegistered {
                account,
                tier,
            });

            Ok(())
        }

        /// Update account tier
        #[pallet::call_index(1)]
        #[pallet::weight(T::WeightInfo::update_account_tier())]
        pub fn update_account_tier(
            origin: OriginFor<T>,
            account: T::AccountId,
            new_tier: AccountTier,
        ) -> DispatchResult {
            ensure_root(origin)?;

            let mut account_info = AccountInfos::<T>::get(&account)
                .ok_or(Error::<T>::AccountNotFound)?;

            let old_tier = account_info.tier;
            account_info.tier = new_tier.clone();

            AccountInfos::<T>::insert(&account, account_info);

            Self::deposit_event(Event::AccountTierUpdated {
                account,
                old_tier,
                new_tier,
            });

            Ok(())
        }

        /// Submit credential for verification
        #[pallet::call_index(2)]
        #[pallet::weight(T::WeightInfo::submit_credential())]
        pub fn submit_credential(
            origin: OriginFor<T>,
            credential_id: u64,
            credential_type: CredentialType,
            credential_data: Vec<u8>,
        ) -> DispatchResult {
            let account = ensure_signed(origin)?;

            // Ensure account is registered
            ensure!(
                AccountInfos::<T>::contains_key(&account),
                Error::<T>::AccountNotFound
            );

            let credential_data_bounded = BoundedVec::try_from(credential_data)
                .map_err(|_| Error::<T>::ContentTooLarge)?;

            let credential_type_clone = credential_type.clone();
            
            let verification = CredentialVerification {
                account: account.clone(),
                credential_id,
                credential_type: credential_type_clone.clone(),
                credential_data: credential_data_bounded,
                status: VerificationStatus::Pending,
                submitted_at: <frame_system::Pallet<T>>::block_number(),
                verified_at: None,
                verified_by: None,
            };

            CredentialVerifications::<T>::insert(&account, &credential_id, verification);

            Self::deposit_event(Event::CredentialSubmitted {
                account,
                credential_id,
                credential_type: credential_type_clone,
            });

            Ok(())
        }

        /// Verify credential
        #[pallet::call_index(3)]
        #[pallet::weight(T::WeightInfo::verify_credential())]
        pub fn verify_credential(
            origin: OriginFor<T>,
            account: T::AccountId,
            credential_id: u64,
        ) -> DispatchResult {
            let verifier = ensure_signed(origin)?;

            let mut verification = CredentialVerifications::<T>::get(&account, &credential_id)
                .ok_or(Error::<T>::CredentialNotFound)?;

            ensure!(
                verification.status == VerificationStatus::Pending,
                Error::<T>::CredentialAlreadyVerified
            );

            verification.status = VerificationStatus::Verified;
            verification.verified_at = Some(<frame_system::Pallet<T>>::block_number());
            verification.verified_by = Some(verifier.clone());

            CredentialVerifications::<T>::insert(&account, &credential_id, verification);

            // Update account info if all required credentials are verified
            if let Some(mut account_info) = AccountInfos::<T>::get(&account) {
                // Simplified: mark account as verified if credential is verified
                // In production, check all required credentials for the tier
                account_info.verified = true;
                AccountInfos::<T>::insert(&account, account_info);
            }

            Self::deposit_event(Event::CredentialVerified {
                account,
                credential_id,
                verified_by: verifier,
            });

            Ok(())
        }

        /// Reject credential verification
        #[pallet::call_index(4)]
        #[pallet::weight(T::WeightInfo::reject_credential())]
        pub fn reject_credential(
            origin: OriginFor<T>,
            account: T::AccountId,
            credential_id: u64,
            reason: Vec<u8>,
        ) -> DispatchResult {
            let rejector = ensure_signed(origin)?;

            let mut verification = CredentialVerifications::<T>::get(&account, &credential_id)
                .ok_or(Error::<T>::CredentialNotFound)?;

            ensure!(
                verification.status == VerificationStatus::Pending,
                Error::<T>::CredentialAlreadyVerified
            );

            let reason_bounded: BoundedVec<u8, ConstU32<1024>> = BoundedVec::try_from(reason)
                .map_err(|_| Error::<T>::ContentTooLarge)?;

            verification.status = VerificationStatus::Rejected;

            CredentialVerifications::<T>::insert(&account, &credential_id, verification);

            Self::deposit_event(Event::CredentialRejected {
                account,
                credential_id,
                reason: reason_bounded.to_vec(),
            });

            Ok(())
        }

        /// Make deposit
        #[pallet::call_index(5)]
        #[pallet::weight(T::WeightInfo::make_deposit())]
        pub fn make_deposit(
            origin: OriginFor<T>,
            amount: BalanceOf<T>,
        ) -> DispatchResult {
            let account = ensure_signed(origin)?;

            // Reserve the deposit amount
            T::Currency::reserve(&account, amount)
                .map_err(|_| Error::<T>::InsufficientDeposit)?;

            // Update deposit info
            let mut deposit_info = DepositInfos::<T>::get(&account)
                .unwrap_or_else(|| DepositInfo {
                    account: account.clone(),
                    total_deposit: Zero::zero(),
                    deposited_at: <frame_system::Pallet<T>>::block_number(),
                });

            deposit_info.total_deposit = deposit_info.total_deposit.saturating_add(amount);

            DepositInfos::<T>::insert(&account, deposit_info.clone());

            Self::deposit_event(Event::DepositMade {
                account,
                amount,
                total_deposit: deposit_info.total_deposit,
            });

            Ok(())
        }

        /// Withdraw deposit
        #[pallet::call_index(6)]
        #[pallet::weight(T::WeightInfo::withdraw_deposit())]
        pub fn withdraw_deposit(
            origin: OriginFor<T>,
            amount: BalanceOf<T>,
        ) -> DispatchResult {
            let account = ensure_signed(origin)?;

            let mut deposit_info = DepositInfos::<T>::get(&account)
                .ok_or(Error::<T>::AccountNotFound)?;

            ensure!(
                deposit_info.total_deposit >= amount,
                Error::<T>::InsufficientDeposit
            );

            // Unreserve and transfer back
            T::Currency::unreserve(&account, amount);
            T::Currency::transfer(
                &account,
                &account,
                amount,
                ExistenceRequirement::KeepAlive,
            )?;

            deposit_info.total_deposit = deposit_info.total_deposit.saturating_sub(amount);

            if deposit_info.total_deposit.is_zero() {
                DepositInfos::<T>::remove(&account);
            } else {
                DepositInfos::<T>::insert(&account, deposit_info.clone());
            }

            Self::deposit_event(Event::DepositWithdrawn {
                account,
                amount,
                remaining_deposit: deposit_info.total_deposit,
            });

            Ok(())
        }
    }
}

/// Weight information for extrinsics
pub trait WeightInfo {
    fn register_account() -> Weight;
    fn update_account_tier() -> Weight;
    fn submit_credential() -> Weight;
    fn verify_credential() -> Weight;
    fn reject_credential() -> Weight;
    fn make_deposit() -> Weight;
    fn withdraw_deposit() -> Weight;
}

/// Account tier
#[derive(Clone, Copy, Encode, Decode, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
pub enum AccountTier {
    /// Patient account
    Patient,
    /// Provider account
    Provider,
    /// Institution account
    Institution,
}

/// Account information
#[derive(Clone, Encode, Decode, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
#[scale_info(skip_type_params(T))]
pub struct AccountInfo<T: frame_system::Config> {
    /// Account ID
    pub account: T::AccountId,
    /// Account tier
    pub tier: AccountTier,
    /// Block when account was registered
    pub registered_at: BlockNumberFor<T>,
    /// Whether account is verified
    pub verified: bool,
}

/// Credential type
#[derive(Clone, Encode, Decode, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
pub enum CredentialType {
    /// Medical license
    MedicalLicense,
    /// Professional certification
    ProfessionalCertification,
    /// Institution accreditation
    InstitutionAccreditation,
    /// Identity document
    IdentityDocument,
    /// Other credential type
    Other(BoundedVec<u8, ConstU32<64>>),
}

/// Verification status
#[derive(Clone, Encode, Decode, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
pub enum VerificationStatus {
    /// Pending verification
    Pending,
    /// Verified
    Verified,
    /// Rejected
    Rejected,
}

/// Credential verification
#[derive(Clone, Encode, Decode, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
#[scale_info(skip_type_params(T))]
pub struct CredentialVerification<T: frame_system::Config> {
    /// Account that submitted the credential
    pub account: T::AccountId,
    /// Credential identifier
    pub credential_id: u64,
    /// Type of credential
    pub credential_type: CredentialType,
    /// Credential data (encoded)
    pub credential_data: BoundedVec<u8, ConstU32<4096>>,
    /// Verification status
    pub status: VerificationStatus,
    /// Block when credential was submitted
    pub submitted_at: BlockNumberFor<T>,
    /// Block when credential was verified (if verified)
    pub verified_at: Option<BlockNumberFor<T>>,
    /// Account that verified the credential (if verified)
    pub verified_by: Option<T::AccountId>,
}

/// Deposit information
#[derive(Clone, Encode, Decode, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
#[scale_info(skip_type_params(T))]
pub struct DepositInfo<T: frame_system::Config> 
where
    T: pallet::Config,
{
    /// Account that made the deposit
    pub account: T::AccountId,
    /// Total deposit amount  
    pub total_deposit: <<T as pallet::Config>::Currency as Currency<T::AccountId>>::Balance,
    /// Block when first deposit was made
    pub deposited_at: BlockNumberFor<T>,
}

pub use pallet::*;
