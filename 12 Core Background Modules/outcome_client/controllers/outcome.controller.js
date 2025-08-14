import axios from 'axios';

export const createOutcome = async (req, res) => {
  try {
    const response = await axios.post('http://localhost:8000/outcomes/', req.body);
    res.status(response.status).json(response.data);
  } catch (error) {
    console.error('Error forwarding to Outcome API:', error.message);
    res.status(500).json({ error: 'Failed to create outcome' });
  }
};
