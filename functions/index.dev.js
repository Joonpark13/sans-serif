const admin = require('firebase-admin');
const createIndex = require('./create-index.js');
const serviceAccount = require('../sans-serif-northwestern-728315dd9469.json');

admin.initializeApp({
  credential: admin.credential.cert(serviceAccount)
});
const db = admin.firestore();

createIndex(db, '4730');
