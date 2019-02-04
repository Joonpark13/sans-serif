const elasticlunr = require('elasticlunr');

function createIndex(db, termId) {
  const index = elasticlunr(function() {
    this.addField('id');
    this.addField('subjectId');
    this.addField('name');
    this.setRef('firestoreId');
  });

  const termDoc = db.collection('terms').doc(termId);

  return termDoc.collection('courses').get().then(
    snapshot => {
      snapshot.forEach(doc => {
        const data = doc.data();
        index.addDoc({
          firestoreId: doc.id,
          id: data.id,
          subjectId: data.subjectId,
          name: data.name,
        });
      });
      return;
    }
  )
  .then(() => {
    termDoc.update({
      searchIndex: JSON.stringify(index),
    });
    return;
  })
  .catch(error => {
    console.log(error);
    return error;
  });
}

module.exports = createIndex;
