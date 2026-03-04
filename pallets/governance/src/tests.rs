//! Comprehensive tests for the ABENA Governance pallet.

use crate::{mock::*, *};
use frame_support::{assert_err, assert_ok};

// ── create_guideline_proposal ────────────────────────────────────────────────

#[test]
fn create_guideline_proposal_stores_entry() {
    new_test_ext().execute_with(|| {
        assert_ok!(Governance::create_guideline_proposal(
            RuntimeOrigin::signed(1), 1u64, b"Content of guideline".to_vec(), 100
        ));
        assert!(GuidelineProposals::<Test>::contains_key(1u64));
    });
}

#[test]
fn create_guideline_proposal_sets_active_status() {
    new_test_ext().execute_with(|| {
        assert_ok!(Governance::create_guideline_proposal(
            RuntimeOrigin::signed(1), 1u64, b"Guideline".to_vec(), 50
        ));
        let proposal = GuidelineProposals::<Test>::get(1u64).unwrap();
        assert_eq!(proposal.status, ProposalStatus::Active);
    });
}

#[test]
fn create_guideline_proposal_stores_proposer() {
    new_test_ext().execute_with(|| {
        assert_ok!(Governance::create_guideline_proposal(
            RuntimeOrigin::signed(42), 1u64, b"Guideline".to_vec(), 50
        ));
        assert_eq!(GuidelineProposals::<Test>::get(1u64).unwrap().proposer, 42u64);
    });
}

#[test]
fn create_guideline_proposal_emits_event() {
    new_test_ext().execute_with(|| {
        assert_ok!(Governance::create_guideline_proposal(
            RuntimeOrigin::signed(1), 7u64, b"Content".to_vec(), 100
        ));
        System::assert_has_event(RuntimeEvent::Governance(
            Event::GuidelineProposalCreated { proposal_id: 7, proposer: 1 }
        ));
    });
}

#[test]
fn create_guideline_proposal_stores_voting_period() {
    new_test_ext().execute_with(|| {
        System::set_block_number(10);
        assert_ok!(Governance::create_guideline_proposal(
            RuntimeOrigin::signed(1), 1u64, b"G".to_vec(), 200
        ));
        let p = GuidelineProposals::<Test>::get(1u64).unwrap();
        assert_eq!(p.created_at, 10);
        assert_eq!(p.voting_period, 200);
    });
}

// ── create_protocol_proposal ─────────────────────────────────────────────────

#[test]
fn create_protocol_proposal_stores_entry() {
    new_test_ext().execute_with(|| {
        assert_ok!(Governance::create_protocol_proposal(
            RuntimeOrigin::signed(1), 1u64, b"Treatment Protocol v1".to_vec(), 100
        ));
        assert!(ProtocolProposals::<Test>::contains_key(1u64));
    });
}

#[test]
fn create_protocol_proposal_emits_event() {
    new_test_ext().execute_with(|| {
        assert_ok!(Governance::create_protocol_proposal(
            RuntimeOrigin::signed(2), 10u64, b"Protocol".to_vec(), 50
        ));
        System::assert_has_event(RuntimeEvent::Governance(
            Event::ProtocolProposalCreated { proposal_id: 10, proposer: 2 }
        ));
    });
}

#[test]
fn create_protocol_proposal_active_status() {
    new_test_ext().execute_with(|| {
        assert_ok!(Governance::create_protocol_proposal(
            RuntimeOrigin::signed(1), 5u64, b"Protocol".to_vec(), 100
        ));
        assert_eq!(ProtocolProposals::<Test>::get(5u64).unwrap().status, ProposalStatus::Active);
    });
}

#[test]
fn multiple_protocol_proposals_independent() {
    new_test_ext().execute_with(|| {
        for id in 1u64..=5 {
            assert_ok!(Governance::create_protocol_proposal(
                RuntimeOrigin::signed(id), id, format!("Protocol {}", id).into_bytes(), 100
            ));
        }
        for id in 1u64..=5 {
            assert!(ProtocolProposals::<Test>::contains_key(id));
        }
    });
}

// ── cast_vote ────────────────────────────────────────────────────────────────

#[test]
fn cast_vote_on_guideline_proposal_works() {
    new_test_ext().execute_with(|| {
        System::set_block_number(1);
        assert_ok!(Governance::create_guideline_proposal(
            RuntimeOrigin::signed(1), 1u64, b"Guideline".to_vec(), 100
        ));
        assert_ok!(Governance::cast_vote(RuntimeOrigin::signed(2), 1u64, Vote::Approve));
        assert!(Votes::<Test>::contains_key(1u64, 2u64));
    });
}

#[test]
fn cast_vote_on_protocol_proposal_works() {
    new_test_ext().execute_with(|| {
        System::set_block_number(1);
        assert_ok!(Governance::create_protocol_proposal(
            RuntimeOrigin::signed(1), 2u64, b"Protocol".to_vec(), 100
        ));
        assert_ok!(Governance::cast_vote(RuntimeOrigin::signed(3), 2u64, Vote::Reject));
        assert_eq!(Votes::<Test>::get(2u64, 3u64).unwrap(), Vote::Reject);
    });
}

#[test]
fn cast_vote_all_vote_types() {
    new_test_ext().execute_with(|| {
        System::set_block_number(1);
        for (voter, vote) in [(10u64, Vote::Approve), (11, Vote::Reject), (12, Vote::Abstain)] {
            assert_ok!(Governance::create_guideline_proposal(
                RuntimeOrigin::signed(voter), voter, b"G".to_vec(), 100
            ));
            assert_ok!(Governance::cast_vote(RuntimeOrigin::signed(voter + 1), voter, vote));
        }
    });
}

#[test]
fn cast_vote_fails_if_proposal_not_found() {
    new_test_ext().execute_with(|| {
        assert_err!(
            Governance::cast_vote(RuntimeOrigin::signed(1), 999u64, Vote::Approve),
            Error::<Test>::ProposalNotFound
        );
    });
}

#[test]
fn cast_vote_fails_if_vote_already_cast() {
    new_test_ext().execute_with(|| {
        System::set_block_number(1);
        assert_ok!(Governance::create_guideline_proposal(
            RuntimeOrigin::signed(1), 1u64, b"Guideline".to_vec(), 100
        ));
        assert_ok!(Governance::cast_vote(RuntimeOrigin::signed(2), 1u64, Vote::Approve));
        assert_err!(
            Governance::cast_vote(RuntimeOrigin::signed(2), 1u64, Vote::Reject),
            Error::<Test>::VoteAlreadyCast
        );
    });
}

#[test]
fn cast_vote_fails_when_voting_period_ended() {
    new_test_ext().execute_with(|| {
        System::set_block_number(1);
        assert_ok!(Governance::create_guideline_proposal(
            RuntimeOrigin::signed(1), 1u64, b"Guideline".to_vec(), 5
        ));
        System::set_block_number(100);
        assert_err!(
            Governance::cast_vote(RuntimeOrigin::signed(2), 1u64, Vote::Approve),
            Error::<Test>::VotingPeriodEnded
        );
    });
}

#[test]
fn cast_vote_emits_event() {
    new_test_ext().execute_with(|| {
        System::set_block_number(1);
        assert_ok!(Governance::create_guideline_proposal(
            RuntimeOrigin::signed(1), 1u64, b"G".to_vec(), 100
        ));
        assert_ok!(Governance::cast_vote(RuntimeOrigin::signed(5), 1u64, Vote::Abstain));
        System::assert_has_event(RuntimeEvent::Governance(
            Event::VoteCast { proposal_id: 1, voter: 5, vote: Vote::Abstain }
        ));
    });
}

#[test]
fn multiple_voters_can_cast_independent_votes() {
    new_test_ext().execute_with(|| {
        System::set_block_number(1);
        assert_ok!(Governance::create_guideline_proposal(
            RuntimeOrigin::signed(1), 1u64, b"Guideline".to_vec(), 100
        ));
        for voter in 2u64..=6 {
            let vote = if voter % 2 == 0 { Vote::Approve } else { Vote::Reject };
            assert_ok!(Governance::cast_vote(RuntimeOrigin::signed(voter), 1u64, vote));
        }
        // All 5 votes stored
        for voter in 2u64..=6 {
            assert!(Votes::<Test>::contains_key(1u64, voter));
        }
    });
}

// ── execute_emergency_intervention ──────────────────────────────────────────

#[test]
fn execute_emergency_intervention_stores_entry() {
    new_test_ext().execute_with(|| {
        assert_ok!(Governance::execute_emergency_intervention(
            RuntimeOrigin::signed(1),
            1u64,
            EmergencyInterventionType::SuspendProtocol,
            b"Critical safety issue".to_vec(),
        ));
        assert!(EmergencyInterventions::<Test>::contains_key(1u64));
    });
}

#[test]
fn execute_emergency_intervention_override_treatment() {
    new_test_ext().execute_with(|| {
        assert_ok!(Governance::execute_emergency_intervention(
            RuntimeOrigin::signed(1),
            2u64,
            EmergencyInterventionType::OverrideTreatment,
            b"Emergency override".to_vec(),
        ));
        let intervention = EmergencyInterventions::<Test>::get(2u64).unwrap();
        assert_eq!(intervention.intervention_type, EmergencyInterventionType::OverrideTreatment);
    });
}

#[test]
fn execute_emergency_intervention_emits_event() {
    new_test_ext().execute_with(|| {
        assert_ok!(Governance::execute_emergency_intervention(
            RuntimeOrigin::signed(10),
            5u64,
            EmergencyInterventionType::EmergencyAccess,
            b"Reason".to_vec(),
        ));
        System::assert_has_event(RuntimeEvent::Governance(
            Event::EmergencyInterventionExecuted { intervention_id: 5, executor: 10 }
        ));
    });
}

#[test]
fn execute_emergency_intervention_stores_executor() {
    new_test_ext().execute_with(|| {
        assert_ok!(Governance::execute_emergency_intervention(
            RuntimeOrigin::signed(99),
            1u64,
            EmergencyInterventionType::SuspendProtocol,
            b"Reason".to_vec(),
        ));
        assert_eq!(EmergencyInterventions::<Test>::get(1u64).unwrap().executor, 99u64);
    });
}

#[test]
fn execute_emergency_intervention_stores_block_number() {
    new_test_ext().execute_with(|| {
        System::set_block_number(77);
        assert_ok!(Governance::execute_emergency_intervention(
            RuntimeOrigin::signed(1),
            1u64,
            EmergencyInterventionType::SuspendProtocol,
            b"R".to_vec(),
        ));
        assert_eq!(EmergencyInterventions::<Test>::get(1u64).unwrap().executed_at, 77);
    });
}

// ── integration ──────────────────────────────────────────────────────────────

#[test]
fn integration_guideline_proposal_voting_workflow() {
    new_test_ext().execute_with(|| {
        System::set_block_number(1);

        // Create guideline proposal
        assert_ok!(Governance::create_guideline_proposal(
            RuntimeOrigin::signed(1),
            100u64,
            b"Updated integrative care guideline for diabetes management".to_vec(),
            50,
        ));

        // Multiple stakeholders vote
        assert_ok!(Governance::cast_vote(RuntimeOrigin::signed(2), 100u64, Vote::Approve));
        assert_ok!(Governance::cast_vote(RuntimeOrigin::signed(3), 100u64, Vote::Approve));
        assert_ok!(Governance::cast_vote(RuntimeOrigin::signed(4), 100u64, Vote::Reject));
        assert_ok!(Governance::cast_vote(RuntimeOrigin::signed(5), 100u64, Vote::Abstain));

        // Verify all votes recorded
        assert_eq!(Votes::<Test>::get(100u64, 2u64).unwrap(), Vote::Approve);
        assert_eq!(Votes::<Test>::get(100u64, 4u64).unwrap(), Vote::Reject);
        assert_eq!(Votes::<Test>::get(100u64, 5u64).unwrap(), Vote::Abstain);
    });
}

#[test]
fn integration_emergency_intervention_after_failed_vote() {
    new_test_ext().execute_with(|| {
        System::set_block_number(1);

        // Create protocol proposal
        assert_ok!(Governance::create_protocol_proposal(
            RuntimeOrigin::signed(1), 200u64, b"Risky treatment protocol".to_vec(), 10
        ));

        // Voting period ends with rejection
        assert_ok!(Governance::cast_vote(RuntimeOrigin::signed(2), 200u64, Vote::Reject));
        assert_ok!(Governance::cast_vote(RuntimeOrigin::signed(3), 200u64, Vote::Reject));

        // Emergency intervention triggered
        assert_ok!(Governance::execute_emergency_intervention(
            RuntimeOrigin::signed(1),
            50u64,
            EmergencyInterventionType::SuspendProtocol,
            b"Protocol rejected by majority; suspended for review".to_vec(),
        ));

        assert!(EmergencyInterventions::<Test>::contains_key(50u64));
    });
}

#[test]
fn guideline_and_protocol_proposals_have_independent_ids() {
    new_test_ext().execute_with(|| {
        System::set_block_number(1);
        // Same ID can be used for both types without conflict
        assert_ok!(Governance::create_guideline_proposal(
            RuntimeOrigin::signed(1), 1u64, b"G".to_vec(), 100
        ));
        assert_ok!(Governance::create_protocol_proposal(
            RuntimeOrigin::signed(1), 1u64, b"P".to_vec(), 100
        ));
        assert!(GuidelineProposals::<Test>::contains_key(1u64));
        assert!(ProtocolProposals::<Test>::contains_key(1u64));
    });
}
