//! Tests for governance pallet

use crate::mock::*;
use crate::*;
use frame_support::{assert_err, assert_ok};

#[test]
fn create_guideline_proposal_works() {
    new_test_ext().execute_with(|| {
        let proposer = 1u64;
        let proposal_id = 1u64;
        let content = b"guideline content".to_vec();
        let voting_period = 100u64;

        assert_ok!(Governance::create_guideline_proposal(
            RuntimeOrigin::signed(proposer),
            proposal_id,
            content.clone(),
            voting_period
        ));

        let proposal = Governance::guideline_proposals(proposal_id);
        assert!(proposal.is_some());
        assert_eq!(proposal.unwrap().guideline_content, content);
    });
}

#[test]
fn create_protocol_proposal_works() {
    new_test_ext().execute_with(|| {
        let proposer = 1u64;
        let proposal_id = 2u64;
        let content = b"protocol content".to_vec();
        let voting_period = 100u64;

        assert_ok!(Governance::create_protocol_proposal(
            RuntimeOrigin::signed(proposer),
            proposal_id,
            content.clone(),
            voting_period
        ));

        let proposal = Governance::protocol_proposals(proposal_id);
        assert!(proposal.is_some());
        assert_eq!(proposal.unwrap().protocol_content, content);
    });
}

#[test]
fn cast_vote_works() {
    new_test_ext().execute_with(|| {
        let proposer = 1u64;
        let voter = 2u64;
        let proposal_id = 1u64;
        let content = b"guideline content".to_vec();
        let voting_period = 100u64;

        assert_ok!(Governance::create_guideline_proposal(
            RuntimeOrigin::signed(proposer),
            proposal_id,
            content,
            voting_period
        ));

        assert_ok!(Governance::cast_vote(
            RuntimeOrigin::signed(voter),
            proposal_id,
            Vote::Approve
        ));

        let vote = Governance::votes(proposal_id, voter);
        assert!(vote.is_some());
        assert_eq!(vote.unwrap(), Vote::Approve);
    });
}

#[test]
fn cannot_vote_twice() {
    new_test_ext().execute_with(|| {
        let proposer = 1u64;
        let voter = 2u64;
        let proposal_id = 1u64;
        let content = b"guideline content".to_vec();
        let voting_period = 100u64;

        assert_ok!(Governance::create_guideline_proposal(
            RuntimeOrigin::signed(proposer),
            proposal_id,
            content,
            voting_period
        ));

        assert_ok!(Governance::cast_vote(
            RuntimeOrigin::signed(voter),
            proposal_id,
            Vote::Approve
        ));

        assert_err!(
            Governance::cast_vote(
                RuntimeOrigin::signed(voter),
                proposal_id,
                Vote::Reject
            ),
            Error::<Test>::VoteAlreadyCast
        );
    });
}

#[test]
fn execute_emergency_intervention_works() {
    new_test_ext().execute_with(|| {
        let executor = 1u64;
        let intervention_id = 1u64;
        let intervention_type = EmergencyInterventionType::SuspendProtocol;
        let reason = b"Patient safety concern".to_vec();

        assert_ok!(Governance::execute_emergency_intervention(
            RuntimeOrigin::signed(executor),
            intervention_id,
            intervention_type.clone(),
            reason.clone()
        ));

        let intervention = Governance::emergency_interventions(intervention_id);
        assert!(intervention.is_some());
        assert_eq!(intervention.unwrap().intervention_type, intervention_type);
        assert_eq!(intervention.unwrap().reason, reason);
    });
}

