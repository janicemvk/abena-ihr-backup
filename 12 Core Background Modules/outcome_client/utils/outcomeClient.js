// outcomeClient.js
import axios from 'axios';

/**
 * Sends an outcome entry to the Outcome Tracking Python module.
 * @param {Object} payload - The outcome payload
 * @param {string} payload.patient_id - UUID string
 * @param {string} payload.measurement_date - Date string "YYYY-MM-DD"
 * @param {string} payload.outcome_type - One of the expected outcome types
 * @param {number} payload.outcome_value - Score (0–100)
 * @param {string} payload.measurement_method - e.g., "automated"
 */
export async function sendOutcomeToPythonAPI({
  patient_id,
  measurement_date,
  outcome_type,
  outcome_value,
  measurement_method
}) {
  try {
    const response = await axios.post('http://localhost:8000/outcomes/', {
      patient_id,
      measurement_date,
      outcome_type,
      outcome_value,
      measurement_method
    });

    console.log(`✅ Sent outcome (${outcome_type}) to Python API:`, response.data);
    return response.data;
  } catch (error) {
    console.error(`❌ Failed to send outcome (${outcome_type}):`, error.response?.data || error.message);
    throw error;
  }
}
