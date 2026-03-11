//! # ABENA Enterprise Identity Pallet
//!
//! Bridges enterprise identity providers (LDAP, Active Directory, SAML, OAuth) to
//! blockchain accounts. Links hospital employees and enterprise users to on-chain
//! identities via X.509 certificate attestation.
//!
//! ## Identity providers
//!
//! | Provider        | Use case                          |
//! |-----------------|-----------------------------------|
//! | ActiveDirectory | Microsoft AD domain auth          |
//! | LDAP            | Generic LDAP directory            |
//! | SAML            | SAML 2.0 IdP                      |
//! | OAuth           | OAuth2/OIDC (Azure AD, Google…)   |

#![cfg_attr(not(feature = "std"), no_std)]

use codec::{Decode, DecodeWithMemTracking, Encode, MaxEncodedLen};
use frame_support::traits::ConstU32;
use scale_info::TypeInfo;
use sp_runtime::{BoundedVec, RuntimeDebug};

#[cfg(test)]
mod mock;

#[cfg(test)]
mod tests;

#[cfg(feature = "runtime-benchmarks")]
mod benchmarking;
pub mod weights;

pub use pallet::*;

/// Weight information for extrinsics
pub trait WeightInfo {
    fn register_enterprise_user() -> frame_support::weights::Weight;
    fn revoke_enterprise_user() -> frame_support::weights::Weight;
}

/// Enterprise identifier (e.g. hospital ID, org ID).
pub type EnterpriseId = u64;

/// X.509 certificate fingerprint (SHA-256 of DER-encoded cert).
/// Stored on-chain; full cert verification is done off-chain.
pub type CertFingerprint = [u8; 32];

/// OAuth/OIDC provider variants.
#[derive(Clone, Encode, Decode, DecodeWithMemTracking, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
pub enum OAuthProvider {
    AzureAD,
    Google,
    Okta,
    Custom(BoundedVec<u8, ConstU32<64>>),
}

/// Identity provider type for enterprise SSO.
#[derive(Clone, Encode, Decode, DecodeWithMemTracking, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
pub enum IdentityProvider {
    /// Microsoft Active Directory
    ActiveDirectory {
        domain: BoundedVec<u8, ConstU32<256>>,
    },
    /// LDAP directory
    LDAP {
        server: BoundedVec<u8, ConstU32<256>>,
    },
    /// SAML 2.0 identity provider
    SAML {
        idp_url: BoundedVec<u8, ConstU32<512>>,
    },
    /// OAuth2/OIDC provider
    OAuth {
        provider: OAuthProvider,
    },
}

/// Enterprise user metadata (from IdP).
#[derive(Clone, Encode, Decode, DecodeWithMemTracking, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
pub struct EnterpriseUser {
    /// Enterprise/organization ID
    pub enterprise_id: EnterpriseId,
    /// Employee or user ID within the enterprise
    pub employee_id: BoundedVec<u8, ConstU32<64>>,
    /// Hash of metadata (name, role, etc.) — full data off-chain
    pub metadata_hash: [u8; 32],
}

/// Enterprise identity: links blockchain account to enterprise IdP user.
#[derive(Clone, Encode, Decode, DecodeWithMemTracking, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
#[scale_info(skip_type_params(T))]
pub struct EnterpriseIdentity<T: frame_system::Config> {
    /// Blockchain account ID
    pub blockchain_account: T::AccountId,
    /// Enterprise ID
    pub enterprise_id: EnterpriseId,
    /// Employee/user ID within enterprise (for reverse lookup)
    pub employee_id: BoundedVec<u8, ConstU32<64>>,
    /// Identity provider (AD, LDAP, SAML, OAuth)
    pub identity_provider: IdentityProvider,
    /// X.509 cert fingerprint (cert verified off-chain before registration)
    pub cert_fingerprint: CertFingerprint,
    /// Block when registered
    pub registered_at: frame_system::pallet_prelude::BlockNumberFor<T>,
}

#[frame_support::pallet]
pub mod pallet {
    use super::*;
    use frame_support::pallet_prelude::*;
    use frame_system::pallet_prelude::*;

    #[pallet::config]
    pub trait Config: frame_system::Config {
        type RuntimeEvent: From<Event<Self>> + IsType<<Self as frame_system::Config>::RuntimeEvent>;
        type WeightInfo: crate::WeightInfo;
        /// Origin that may register/revoke enterprise users (Root or governance)
        type RegisterOrigin: EnsureOrigin<Self::RuntimeOrigin>;
    }

    #[pallet::pallet]
    pub struct Pallet<T>(_);

    /// Enterprise identities: blockchain AccountId → EnterpriseIdentity
    #[pallet::storage]
    #[pallet::getter(fn enterprise_identities)]
    pub type EnterpriseIdentities<T: Config> = StorageMap<
        _,
        Blake2_128Concat,
        T::AccountId,
        EnterpriseIdentity<T>,
        OptionQuery,
    >;

    /// Reverse lookup: enterprise_id + employee_id → AccountId (for fast IdP→chain resolution)
    #[pallet::storage]
    #[pallet::getter(fn enterprise_user_account)]
    pub type EnterpriseUserAccounts<T: Config> = StorageDoubleMap<
        _,
        Blake2_128Concat,
        EnterpriseId,
        Blake2_128Concat,
        BoundedVec<u8, ConstU32<64>>,
        T::AccountId,
        OptionQuery,
    >;

    #[pallet::event]
    #[pallet::generate_deposit(pub(super) fn deposit_event)]
    pub enum Event<T: Config> {
        EnterpriseUserRegistered {
            account: T::AccountId,
            enterprise_id: EnterpriseId,
            identity_provider: IdentityProvider,
        },
        EnterpriseUserRevoked {
            account: T::AccountId,
            enterprise_id: EnterpriseId,
        },
    }

    #[pallet::error]
    pub enum Error<T> {
        AlreadyRegistered,
        UserNotFound,
        InvalidCertFingerprint,
        DataTooLarge,
    }

    #[pallet::call]
    impl<T: Config> Pallet<T> {
        /// Register an enterprise user and link to a blockchain account.
        /// Certificate verification is done off-chain; this extrinsic records the
        /// attested binding after the admin/registrar has verified the X.509 cert.
        #[pallet::call_index(0)]
        #[pallet::weight(T::WeightInfo::register_enterprise_user())]
        pub fn register_enterprise_user(
            origin: OriginFor<T>,
            account: T::AccountId,
            user: EnterpriseUser,
            identity_provider: IdentityProvider,
            cert_fingerprint: [u8; 32],
        ) -> DispatchResult {
            T::RegisterOrigin::ensure_origin(origin)?;

            ensure!(
                !EnterpriseIdentities::<T>::contains_key(&account),
                Error::<T>::AlreadyRegistered
            );

            let now = <frame_system::Pallet<T>>::block_number();
            let identity = EnterpriseIdentity {
                blockchain_account: account.clone(),
                enterprise_id: user.enterprise_id,
                employee_id: user.employee_id.clone(),
                identity_provider: identity_provider.clone(),
                cert_fingerprint,
                registered_at: now,
            };

            EnterpriseIdentities::<T>::insert(&account, &identity);
            EnterpriseUserAccounts::<T>::insert(
                user.enterprise_id,
                user.employee_id,
                account.clone(),
            );

            Self::deposit_event(Event::EnterpriseUserRegistered {
                account,
                enterprise_id: user.enterprise_id,
                identity_provider,
            });

            Ok(())
        }

        /// Revoke an enterprise identity (e.g. on employee offboarding).
        #[pallet::call_index(1)]
        #[pallet::weight(T::WeightInfo::revoke_enterprise_user())]
        pub fn revoke_enterprise_user(
            origin: OriginFor<T>,
            account: T::AccountId,
        ) -> DispatchResult {
            T::RegisterOrigin::ensure_origin(origin)?;

            let identity =
                EnterpriseIdentities::<T>::get(&account).ok_or(Error::<T>::UserNotFound)?;

            let enterprise_id = identity.enterprise_id;
            let employee_id = identity.employee_id.clone();

            EnterpriseIdentities::<T>::remove(&account);
            EnterpriseUserAccounts::<T>::remove(enterprise_id, employee_id);

            Self::deposit_event(Event::EnterpriseUserRevoked {
                account,
                enterprise_id,
            });

            Ok(())
        }
    }
}
