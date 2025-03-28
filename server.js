const express = require('express');
const cors = require('cors'); // ✅ ADD THIS
const fs = require('fs');
const path = require('path');
const app = express();
const PORT = 3001;

app.use(cors()); // ✅ ENABLE CORS
app.use(express.json({ limit: '10mb' }));

app.post('/save-results', (req, res) => {
  const { csv, filename } = req.body;

  if (!csv || !filename) {
    return res.status(400).send('Missing csv or filename');
  }

  const filePath = path.join(__dirname, 'outputs', filename);
  fs.writeFile(filePath, csv, (err) => {
    if (err) {
      console.error('❌ Failed to write file', err);
      return res.status(500).send('Error writing file');
    }
    res.send(`✅ CSV saved to ${filePath}`);
  });
});

app.listen(PORT, () => {
  console.log(`CSV Save API listening on port ${PORT}`);
});

// app.post('/create-test-file', (req, res) => {
//   const filename = `test_${Date.now()}.csv`;
//   const filePath = path.join(__dirname, 'outputs', filename);

//   fs.writeFile(filePath, '', (err) => {
//     if (err) {
//       console.error('❌ Failed to create test file', err);
//       return res.status(500).send('Error creating test file');
//     }
//     res.send(`✅ Created file: ${filename}`);
//   });
// });
