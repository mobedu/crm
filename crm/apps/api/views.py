from flask import request, jsonify

from flask_graphql import GraphQLView

from crm import app


@app.route('/api', methods=["POST"])
def api():
    if request.headers.get('Content-Type', '').lower() != 'application/json':
        return jsonify(errors=['Only accepts Content-Type: application/json']), 400

    data = request.json
    query = data.get('query', None)
    if not query:
        return jsonify(errors=['query field is missing']), 400
    if query:
        try:
            execresult = app.graphql_schema.execute(query)
            if execresult.errors:
                # BAD REQUEST ON ERRORS
                return jsonify(errors=[str(e) for e in execresult.errors]), 400
            result = list(execresult.data.items())[0][1]
            if result is None:
                return '', 404
            return jsonify(execresult.data), 200

        except Exception as ex:
            return jsonify(errors=[str(ex)]), 400


app.add_url_rule('/graphql', view_func=GraphQLView.as_view('graphql', schema=app.graphql_schema, graphiql=True))
