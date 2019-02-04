const functions = require('firebase-functions');
const createIndex = require('./create-index.js');
const admin = require('firebase-admin');

admin.initializeApp(functions.config().firebase);
const db = admin.firestore();

exports.createIndex = functions.https.onRequest((request, response) => {
  if (request.method === 'POST') {
    return createIndex(db, request.query.termId).then(() => {
      return response.status(200).send();
    }).catch(error => {
      return response.status(500).send(error);
    });
  } else {
    return response.send(405).send();
  }
});
