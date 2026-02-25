//! Tests for quantum-results pallet

use crate::mock::{new_test_ext, Test};
use crate::pallet::{AlgorithmRegistry, QuantumAlgorithm, Pallet as QuantumResultsPallet};
use frame_support::assert_ok;
use frame_system::Origin;
use sp_core::H256;

type RuntimeOrigin = Origin<Test>;
type QuantumResults = QuantumResultsPallet<Test>;

#[test]
fn register_algorithm_works() {
    new_test_ext().execute_with(|| {
        let desc = b"VQE for molecular energy".to_vec();
        assert_ok!(QuantumResults::register_algorithm(
            RuntimeOrigin::signed(1),
            H256::zero(),
            QuantumAlgorithm::VQE,
            1,
            desc,
        ));
        assert!(AlgorithmRegistry::<Test>::get(H256::zero()).is_some());
    });
}
