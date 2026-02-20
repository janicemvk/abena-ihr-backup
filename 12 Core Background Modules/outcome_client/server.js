import app from './app.js';

const PORT = 3001;
app.listen(PORT, () => {
  console.log(`Node Outcome Client listening on port ${PORT}`);
});

app.post('/analyze', async (req, res) => {
    const outcomeData = req.body;
    const response = await axios.post('http://localhost:8000/outcomes/', outcomeData);
    res.send(response.data);
});
