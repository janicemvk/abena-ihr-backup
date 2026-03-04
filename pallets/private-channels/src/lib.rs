//! # ABENA Private Channels Pallet
//!
//! Brings Hyperledger-Fabric-style **channel isolation** to the ABENA Substrate chain.
//! Each channel is a named, permissioned namespace: only enrolled members can post or
//! read data entries; participants in one channel have zero visibility into another.
//!
//! ## Fabric analogy
//!
//! ```text
//! Fabric concept              │  ABENA implementation
//! ────────────────────────────┼──────────────────────────────────────────────
//! Channel                     │  ChannelInfo (StorageMap keyed by ChannelId)
//! Channel ledger              │  ChannelData StorageDoubleMap
//! Channel membership          │  ChannelMembers StorageDoubleMap
//! Endorsement policy          │  MemberRole (Admin / ReadWrite / ReadOnly)
//! Cross-channel data sharing  │  CrossChannelGrants StorageDoubleMap
//! ```
//!
//! ## Channel types
//!
//! | Type              | Example                                     |
//! |-------------------|---------------------------------------------|
//! | HospitalInsurer   | Accra General ↔ NHIA insurer                |
//! | InterHospital     | Accra General + Korle Bu (research sharing) |
//! | Research          | Multi-institution clinical-trial data       |
//! | PatientCentric    | Patient + their entire care team            |
//! | Regulatory        | Hospital ↔ Ghana FDA / MOH                  |
//! | Custom            | Arbitrary configuration                     |
//!
//! ## Data model
//!
//! Actual payloads are stored **off-chain** (IPFS / encrypted blob storage).
//! The pallet records only:
//! - A 32-byte **data hash** (SHA-256 of the ciphertext)
//! - A 32-byte **metadata hash** (SHA-256 of a JSON envelope: type, size, IV…)
//! - The `DataType` tag and the submitting member's `AccountId`
//!
//! This keeps on-chain storage minimal while providing cryptographic integrity
//! guarantees that authorised members can verify.

#![cfg_attr(not(feature = "std"), no_std)]

use codec::{Decode, Encode, MaxEncodedLen};
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
pub use weights::WeightInfo;

// ── Shared types ────────────────────────────────────────────────────────────

/// Numeric identifier for a channel (auto-incremented).
pub type ChannelId = u64;

/// Numeric identifier for a data entry within a channel (auto-incremented per channel).
pub type DataEntryId = u64;

/// Purpose / topology of the channel.
#[derive(Clone, Copy, PartialEq, Eq, Encode, Decode, RuntimeDebug, TypeInfo, MaxEncodedLen)]
#[cfg_attr(feature = "std", derive(serde::Serialize, serde::Deserialize))]
pub enum ChannelType {
    /// One hospital and one or more insurers.
    HospitalInsurer,
    /// Federated channel spanning multiple hospitals.
    InterHospital,
    /// Anonymised research data shared across institutions.
    Research,
    /// A patient and their full care team.
    PatientCentric,
    /// Hospital ↔ regulatory / government agency.
    Regulatory,
    /// Freely configured by the creator.
    Custom,
}

/// Operational status of a channel.
#[derive(Clone, Copy, PartialEq, Eq, Encode, Decode, RuntimeDebug, TypeInfo, MaxEncodedLen)]
#[cfg_attr(feature = "std", derive(serde::Serialize, serde::Deserialize))]
pub enum ChannelStatus {
    Active,
    Closed,
}

/// Permissions a member holds inside a channel.
#[derive(Clone, Copy, PartialEq, Eq, Encode, Decode, RuntimeDebug, TypeInfo, MaxEncodedLen)]
#[cfg_attr(feature = "std", derive(serde::Serialize, serde::Deserialize))]
pub enum MemberRole {
    /// May invite/remove members, post data, and close the channel.
    Admin,
    /// May post and acknowledge data entries.
    ReadWrite,
    /// May only query data entries (no posting).
    ReadOnly,
}

/// Taxonomy for a data entry posted to a channel.
#[derive(Clone, Copy, PartialEq, Eq, Encode, Decode, RuntimeDebug, TypeInfo, MaxEncodedLen)]
#[cfg_attr(feature = "std", derive(serde::Serialize, serde::Deserialize))]
pub enum DataType {
    HealthRecord,
    InsuranceClaim,
    LabResult,
    Prescription,
    ImagingStudy,
    ClinicalTrialData,
    ResearchDataset,
    ConsentDocument,
    Custom,
}

/// Metadata stored on-chain for a channel.
#[derive(Clone, Encode, Decode, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
pub struct ChannelInfo<AccountId, BlockNumber> {
    pub id: ChannelId,
    /// Human-readable name (≤ 64 bytes).
    pub name: BoundedVec<u8, ConstU32<64>>,
    pub channel_type: ChannelType,
    pub creator: AccountId,
    pub created_at: BlockNumber,
    pub status: ChannelStatus,
    /// Running count of enrolled members.
    pub member_count: u32,
    /// Running count of data entries posted.
    pub data_count: u32,
}

/// A member's record inside a channel.
#[derive(Clone, Encode, Decode, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
pub struct MemberInfo<BlockNumber> {
    pub role: MemberRole,
    pub enrolled_at: BlockNumber,
}

/// A data entry recorded inside a channel.
#[derive(Clone, Encode, Decode, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
pub struct DataEntry<AccountId, BlockNumber> {
    pub entry_id: DataEntryId,
    pub channel_id: ChannelId,
    pub posted_by: AccountId,
    /// SHA-256 of the off-chain encrypted payload.
    pub data_hash: [u8; 32],
    /// SHA-256 of the off-chain JSON metadata envelope.
    pub metadata_hash: [u8; 32],
    pub data_type: DataType,
    pub posted_at: BlockNumber,
    /// Whether this entry originated in another channel (via cross-channel grant).
    pub is_shared: bool,
}

/// A record of a cross-channel data grant.
#[derive(Clone, Encode, Decode, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
pub struct CrossChannelGrant<BlockNumber> {
    pub source_channel: ChannelId,
    pub target_channel: ChannelId,
    pub entry_id: DataEntryId,
    pub granted_at: BlockNumber,
}

// ── Pallet ─────────────────────────────────────────────────────────────────

#[frame_support::pallet]
pub mod pallet {
    use super::*;
    use frame_support::pallet_prelude::*;
    use frame_system::pallet_prelude::*;

    #[pallet::config]
    pub trait Config: frame_system::Config {
        type RuntimeEvent: From<Event<Self>> + IsType<<Self as frame_system::Config>::RuntimeEvent>;

        /// Maximum members per channel.
        #[pallet::constant]
        type MaxMembersPerChannel: Get<u32>;

        /// Maximum number of channels a single account may be enrolled in.
        #[pallet::constant]
        type MaxChannelsPerMember: Get<u32>;

        /// Maximum data entries per channel before it must be archived off-chain.
        #[pallet::constant]
        type MaxEntriesPerChannel: Get<u32>;

        type WeightInfo: WeightInfo;
    }

    #[pallet::pallet]
    pub struct Pallet<T>(_);

    // ── Storage ──────────────────────────────────────────────────────────

    /// Auto-incrementing channel ID counter.
    #[pallet::storage]
    #[pallet::getter(fn next_channel_id)]
    pub type NextChannelId<T: Config> = StorageValue<_, ChannelId, ValueQuery>;

    /// `ChannelId` → `ChannelInfo`.
    #[pallet::storage]
    #[pallet::getter(fn channel)]
    pub type Channels<T: Config> = StorageMap<
        _,
        Blake2_128Concat,
        ChannelId,
        ChannelInfo<T::AccountId, BlockNumberFor<T>>,
        OptionQuery,
    >;

    /// `(ChannelId, AccountId)` → `MemberInfo`.
    #[pallet::storage]
    #[pallet::getter(fn member_info)]
    pub type ChannelMembers<T: Config> = StorageDoubleMap<
        _,
        Blake2_128Concat,
        ChannelId,
        Blake2_128Concat,
        T::AccountId,
        MemberInfo<BlockNumberFor<T>>,
        OptionQuery,
    >;

    /// Reverse index: `AccountId` → list of enrolled `ChannelId`s.
    #[pallet::storage]
    #[pallet::getter(fn member_channels)]
    pub type MemberChannels<T: Config> = StorageMap<
        _,
        Blake2_128Concat,
        T::AccountId,
        BoundedVec<ChannelId, T::MaxChannelsPerMember>,
        ValueQuery,
    >;

    /// Auto-incrementing per-channel data entry counter.
    #[pallet::storage]
    pub type NextEntryId<T: Config> =
        StorageMap<_, Blake2_128Concat, ChannelId, DataEntryId, ValueQuery>;

    /// `(ChannelId, DataEntryId)` → `DataEntry`.
    #[pallet::storage]
    #[pallet::getter(fn data_entry)]
    pub type ChannelData<T: Config> = StorageDoubleMap<
        _,
        Blake2_128Concat,
        ChannelId,
        Blake2_128Concat,
        DataEntryId,
        DataEntry<T::AccountId, BlockNumberFor<T>>,
        OptionQuery,
    >;

    /// `(source_channel_id, entry_id)` → `CrossChannelGrant`.
    /// Records every cross-channel sharing action; the target channel's members
    /// discover the shared entry via a mirrored `ChannelData` record.
    #[pallet::storage]
    #[pallet::getter(fn cross_channel_grant)]
    pub type CrossChannelGrants<T: Config> = StorageDoubleMap<
        _,
        Blake2_128Concat,
        ChannelId,
        Blake2_128Concat,
        DataEntryId,
        CrossChannelGrant<BlockNumberFor<T>>,
        OptionQuery,
    >;

    // ── Events ───────────────────────────────────────────────────────────

    #[pallet::event]
    #[pallet::generate_deposit(pub(super) fn deposit_event)]
    pub enum Event<T: Config> {
        /// A new channel was created.
        ChannelCreated {
            channel_id: ChannelId,
            name: BoundedVec<u8, ConstU32<64>>,
            channel_type: ChannelType,
            creator: T::AccountId,
        },
        /// A member was added to a channel.
        MemberAdded {
            channel_id: ChannelId,
            member: T::AccountId,
            role: MemberRole,
        },
        /// A member was removed from a channel.
        MemberRemoved {
            channel_id: ChannelId,
            member: T::AccountId,
        },
        /// A member's role was updated.
        MemberRoleUpdated {
            channel_id: ChannelId,
            member: T::AccountId,
            new_role: MemberRole,
        },
        /// A data entry was posted to a channel.
        DataPosted {
            channel_id: ChannelId,
            entry_id: DataEntryId,
            posted_by: T::AccountId,
            data_type: DataType,
            data_hash: [u8; 32],
        },
        /// A data entry was shared from one channel to another.
        DataSharedCrossChannel {
            source_channel: ChannelId,
            target_channel: ChannelId,
            entry_id: DataEntryId,
            shared_by: T::AccountId,
        },
        /// A channel was closed.
        ChannelClosed {
            channel_id: ChannelId,
        },
    }

    // ── Errors ───────────────────────────────────────────────────────────

    #[pallet::error]
    pub enum Error<T> {
        /// No channel with that ID exists.
        ChannelNotFound,
        /// The channel has been closed and no longer accepts operations.
        ChannelClosed,
        /// The caller is not a member of this channel.
        NotAMember,
        /// The caller is a member but lacks the required role (Admin / ReadWrite).
        InsufficientRole,
        /// The account is already enrolled in this channel.
        AlreadyMember,
        /// The channel's member list is at capacity.
        ChannelFull,
        /// The account is enrolled in too many channels.
        TooManyChannels,
        /// The channel name is too long (max 64 bytes).
        NameTooLong,
        /// The data entry does not exist in the source channel.
        DataEntryNotFound,
        /// That data entry has already been shared to the target channel.
        AlreadyShared,
        /// The channel has reached its maximum data entry count.
        ChannelDataFull,
        /// An admin cannot remove themselves; transfer admin role first.
        CannotRemoveSelf,
    }

    // ── Extrinsics ───────────────────────────────────────────────────────

    #[pallet::call]
    impl<T: Config> Pallet<T> {
        /// Create a new private channel.
        ///
        /// The caller becomes the first `Admin` member. Additional members
        /// listed in `initial_members` are enrolled with `ReadWrite` role.
        #[pallet::call_index(0)]
        #[pallet::weight(T::WeightInfo::create_channel())]
        pub fn create_channel(
            origin: OriginFor<T>,
            name: sp_std::vec::Vec<u8>,
            channel_type: ChannelType,
            initial_members: sp_std::vec::Vec<T::AccountId>,
        ) -> DispatchResult {
            let who = ensure_signed(origin)?;

            let bounded_name: BoundedVec<u8, ConstU32<64>> =
                BoundedVec::try_from(name).map_err(|_| Error::<T>::NameTooLong)?;

            let channel_id = NextChannelId::<T>::get();
            NextChannelId::<T>::put(channel_id.saturating_add(1));

            let now = frame_system::Pallet::<T>::block_number();

            let info = ChannelInfo {
                id: channel_id,
                name: bounded_name.clone(),
                channel_type,
                creator: who.clone(),
                created_at: now,
                status: ChannelStatus::Active,
                member_count: 0,
                data_count: 0,
            };
            Channels::<T>::insert(channel_id, info);

            // Enrol the creator as Admin
            Self::enrol_member(channel_id, &who, MemberRole::Admin, now)?;

            // Enrol initial members as ReadWrite
            for member in &initial_members {
                if member != &who {
                    Self::enrol_member(channel_id, member, MemberRole::ReadWrite, now)?;
                }
            }

            Self::deposit_event(Event::ChannelCreated {
                channel_id,
                name: bounded_name,
                channel_type,
                creator: who,
            });
            Ok(())
        }

        /// Add a member to an existing channel.
        ///
        /// Requires the caller to be an `Admin` of the channel.
        #[pallet::call_index(1)]
        #[pallet::weight(T::WeightInfo::add_member())]
        pub fn add_member(
            origin: OriginFor<T>,
            channel_id: ChannelId,
            new_member: T::AccountId,
            role: MemberRole,
        ) -> DispatchResult {
            let who = ensure_signed(origin)?;
            Self::ensure_admin(channel_id, &who)?;

            ensure!(
                !ChannelMembers::<T>::contains_key(channel_id, &new_member),
                Error::<T>::AlreadyMember
            );

            let now = frame_system::Pallet::<T>::block_number();
            Self::enrol_member(channel_id, &new_member, role, now)?;

            Self::deposit_event(Event::MemberAdded { channel_id, member: new_member, role });
            Ok(())
        }

        /// Remove a member from a channel.
        ///
        /// Requires the caller to be an `Admin`. An admin cannot remove themselves.
        #[pallet::call_index(2)]
        #[pallet::weight(T::WeightInfo::remove_member())]
        pub fn remove_member(
            origin: OriginFor<T>,
            channel_id: ChannelId,
            member: T::AccountId,
        ) -> DispatchResult {
            let who = ensure_signed(origin)?;
            Self::ensure_admin(channel_id, &who)?;
            ensure!(who != member, Error::<T>::CannotRemoveSelf);

            ensure!(
                ChannelMembers::<T>::contains_key(channel_id, &member),
                Error::<T>::NotAMember
            );

            ChannelMembers::<T>::remove(channel_id, &member);
            MemberChannels::<T>::mutate(&member, |list| {
                list.retain(|&id| id != channel_id);
            });

            Channels::<T>::mutate(channel_id, |maybe_ch| {
                if let Some(ch) = maybe_ch {
                    ch.member_count = ch.member_count.saturating_sub(1);
                }
            });

            Self::deposit_event(Event::MemberRemoved { channel_id, member });
            Ok(())
        }

        /// Update a member's role within a channel.
        ///
        /// Requires the caller to be an `Admin`.
        #[pallet::call_index(3)]
        #[pallet::weight(T::WeightInfo::update_member_role())]
        pub fn update_member_role(
            origin: OriginFor<T>,
            channel_id: ChannelId,
            member: T::AccountId,
            new_role: MemberRole,
        ) -> DispatchResult {
            let who = ensure_signed(origin)?;
            Self::ensure_admin(channel_id, &who)?;

            ChannelMembers::<T>::try_mutate(channel_id, &member, |maybe_info| {
                let info = maybe_info.as_mut().ok_or(Error::<T>::NotAMember)?;
                info.role = new_role;
                Ok::<_, Error<T>>(())
            })?;

            Self::deposit_event(Event::MemberRoleUpdated { channel_id, member, new_role });
            Ok(())
        }

        /// Post a data entry (hash + metadata) to a channel.
        ///
        /// The caller must be an `Admin` or `ReadWrite` member.
        /// Only the SHA-256 hashes are stored on-chain; the ciphertext lives
        /// off-chain (e.g. IPFS or a hospital's encrypted object store).
        #[pallet::call_index(4)]
        #[pallet::weight(T::WeightInfo::post_data())]
        pub fn post_data(
            origin: OriginFor<T>,
            channel_id: ChannelId,
            data_hash: [u8; 32],
            metadata_hash: [u8; 32],
            data_type: DataType,
        ) -> DispatchResult {
            let who = ensure_signed(origin)?;
            Self::ensure_can_write(channel_id, &who)?;

            let entry_id = NextEntryId::<T>::get(channel_id);
            NextEntryId::<T>::insert(channel_id, entry_id.saturating_add(1));

            let now = frame_system::Pallet::<T>::block_number();

            let entry = DataEntry {
                entry_id,
                channel_id,
                posted_by: who.clone(),
                data_hash,
                metadata_hash,
                data_type,
                posted_at: now,
                is_shared: false,
            };

            ChannelData::<T>::try_mutate_exists(channel_id, entry_id, |slot| {
                ensure!(slot.is_none(), Error::<T>::ChannelDataFull);
                *slot = Some(entry);
                Ok::<_, Error<T>>(())
            })?;

            Channels::<T>::mutate(channel_id, |maybe_ch| {
                if let Some(ch) = maybe_ch {
                    ch.data_count = ch.data_count.saturating_add(1);
                }
            });

            Self::deposit_event(Event::DataPosted {
                channel_id,
                entry_id,
                posted_by: who,
                data_type,
                data_hash,
            });
            Ok(())
        }

        /// Share a data entry from this channel to another channel.
        ///
        /// The caller must be an `Admin` or `ReadWrite` member of the **source**
        /// channel AND a member (any role) of the **target** channel. A mirrored
        /// `DataEntry` (with `is_shared = true`) is written into the target channel
        /// so its members can discover and verify the data without leaving their
        /// own channel namespace.
        #[pallet::call_index(5)]
        #[pallet::weight(T::WeightInfo::share_data_cross_channel())]
        pub fn share_data_cross_channel(
            origin: OriginFor<T>,
            source_channel: ChannelId,
            entry_id: DataEntryId,
            target_channel: ChannelId,
        ) -> DispatchResult {
            let who = ensure_signed(origin)?;

            // Caller must be able to write in the source channel
            Self::ensure_can_write(source_channel, &who)?;

            // Caller must be a member of the target channel (any role)
            ensure!(
                ChannelMembers::<T>::contains_key(target_channel, &who),
                Error::<T>::NotAMember
            );

            // Target channel must be active
            let target = Channels::<T>::get(target_channel).ok_or(Error::<T>::ChannelNotFound)?;
            ensure!(target.status == ChannelStatus::Active, Error::<T>::ChannelClosed);

            // Source entry must exist
            let source_entry = ChannelData::<T>::get(source_channel, entry_id)
                .ok_or(Error::<T>::DataEntryNotFound)?;

            // No duplicate grants
            ensure!(
                !CrossChannelGrants::<T>::contains_key(source_channel, entry_id),
                Error::<T>::AlreadyShared
            );

            let now = frame_system::Pallet::<T>::block_number();

            // Record the grant
            CrossChannelGrants::<T>::insert(
                source_channel,
                entry_id,
                CrossChannelGrant {
                    source_channel,
                    target_channel,
                    entry_id,
                    granted_at: now,
                },
            );

            // Mirror the entry into the target channel
            let mirror_id = NextEntryId::<T>::get(target_channel);
            NextEntryId::<T>::insert(target_channel, mirror_id.saturating_add(1));

            let mirror = DataEntry {
                entry_id: mirror_id,
                channel_id: target_channel,
                posted_by: who.clone(),
                data_hash: source_entry.data_hash,
                metadata_hash: source_entry.metadata_hash,
                data_type: source_entry.data_type,
                posted_at: now,
                is_shared: true,
            };
            ChannelData::<T>::insert(target_channel, mirror_id, mirror);
            Channels::<T>::mutate(target_channel, |maybe_ch| {
                if let Some(ch) = maybe_ch {
                    ch.data_count = ch.data_count.saturating_add(1);
                }
            });

            Self::deposit_event(Event::DataSharedCrossChannel {
                source_channel,
                target_channel,
                entry_id,
                shared_by: who,
            });
            Ok(())
        }

        /// Close a channel permanently.
        ///
        /// Requires the caller to be an `Admin`. Closed channels cannot receive
        /// new members or data entries but their records are retained for audit.
        #[pallet::call_index(6)]
        #[pallet::weight(T::WeightInfo::close_channel())]
        pub fn close_channel(
            origin: OriginFor<T>,
            channel_id: ChannelId,
        ) -> DispatchResult {
            let who = ensure_signed(origin)?;
            Self::ensure_admin(channel_id, &who)?;

            Channels::<T>::try_mutate(channel_id, |maybe_ch| {
                let ch = maybe_ch.as_mut().ok_or(Error::<T>::ChannelNotFound)?;
                ensure!(ch.status == ChannelStatus::Active, Error::<T>::ChannelClosed);
                ch.status = ChannelStatus::Closed;
                Ok::<_, DispatchError>(())
            })?;

            Self::deposit_event(Event::ChannelClosed { channel_id });
            Ok(())
        }
    }

    // ── Internal helpers ─────────────────────────────────────────────────

    impl<T: Config> Pallet<T> {
        /// Enrol `member` in `channel_id` with `role`, updating all reverse indices.
        fn enrol_member(
            channel_id: ChannelId,
            member: &T::AccountId,
            role: MemberRole,
            now: BlockNumberFor<T>,
        ) -> DispatchResult {
            ensure!(
                !ChannelMembers::<T>::contains_key(channel_id, member),
                Error::<T>::AlreadyMember
            );

            let info = MemberInfo { role, enrolled_at: now };
            ChannelMembers::<T>::insert(channel_id, member, info);

            MemberChannels::<T>::try_mutate(member, |list| {
                list.try_push(channel_id).map_err(|_| Error::<T>::TooManyChannels)
            })?;

            Channels::<T>::mutate(channel_id, |maybe_ch| {
                if let Some(ch) = maybe_ch {
                    ch.member_count = ch.member_count.saturating_add(1);
                }
            });

            Ok(())
        }

        /// Assert `who` is an Admin in an Active channel.
        fn ensure_admin(channel_id: ChannelId, who: &T::AccountId) -> DispatchResult {
            let ch = Channels::<T>::get(channel_id).ok_or(Error::<T>::ChannelNotFound)?;
            ensure!(ch.status == ChannelStatus::Active, Error::<T>::ChannelClosed);

            let member = ChannelMembers::<T>::get(channel_id, who).ok_or(Error::<T>::NotAMember)?;
            ensure!(member.role == MemberRole::Admin, Error::<T>::InsufficientRole);
            Ok(())
        }

        /// Assert `who` can post data (Admin or ReadWrite) in an Active channel.
        fn ensure_can_write(channel_id: ChannelId, who: &T::AccountId) -> DispatchResult {
            let ch = Channels::<T>::get(channel_id).ok_or(Error::<T>::ChannelNotFound)?;
            ensure!(ch.status == ChannelStatus::Active, Error::<T>::ChannelClosed);

            let member = ChannelMembers::<T>::get(channel_id, who).ok_or(Error::<T>::NotAMember)?;
            ensure!(
                matches!(member.role, MemberRole::Admin | MemberRole::ReadWrite),
                Error::<T>::InsufficientRole
            );
            Ok(())
        }

        // ── Public query helpers ──────────────────────────────────────────

        /// Returns `true` if `who` is an active member of `channel_id`.
        pub fn is_member(channel_id: ChannelId, who: &T::AccountId) -> bool {
            ChannelMembers::<T>::contains_key(channel_id, who)
        }

        /// Returns `true` if `who` may read data from `channel_id`.
        /// (All enrolled members have read access.)
        pub fn can_read(channel_id: ChannelId, who: &T::AccountId) -> bool {
            Self::is_member(channel_id, who)
        }

        /// Returns `true` if `who` may post data to `channel_id`.
        pub fn can_write(channel_id: ChannelId, who: &T::AccountId) -> bool {
            ChannelMembers::<T>::get(channel_id, who)
                .map(|m| matches!(m.role, MemberRole::Admin | MemberRole::ReadWrite))
                .unwrap_or(false)
        }

        /// Returns all `ChannelId`s that `who` is enrolled in.
        pub fn channels_of(who: &T::AccountId) -> sp_std::vec::Vec<ChannelId> {
            MemberChannels::<T>::get(who).into_iter().collect()
        }
    }
}
