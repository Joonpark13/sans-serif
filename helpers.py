def get_collection(db, term_id):
    return db['term_{0}'.format(term_id)]
