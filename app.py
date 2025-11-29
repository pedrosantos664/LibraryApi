
import os
from flask import Flask, jsonify, request
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from dotenv import load_dotenv

load_dotenv() 

# ----------------- CONFIGURAÇÃO DO FLASK E MONGODB -----------------
app = Flask(__name__)

app.config["MONGO_URI"] = os.environ.get("MONGO_URI") 
mongo = PyMongo(app)

livros_collection = mongo.db.livros



# ----------------- FUNÇÃO DE AUXÍLIO -----------------
def to_json(livro):
    """Converte o documento MongoDB para um dicionário JSON amigável."""
    if livro:
        id_value = str(livro.pop('_id')) 
        
        livro_dict = {'id': id_value} 
        livro_dict.update(livro)
        return livro_dict
    return None

# ----------------- ROTAS CRUD -----------------

@app.route('/livros', methods=['POST'])
def criar_livro():
    dados = request.get_json()
    if not dados:
        return jsonify({"erro": "Nenhum dado fornecido"}), 400

    try:
        resultado = livros_collection.insert_one(dados)
        
        novo_livro = livros_collection.find_one({'_id': resultado.inserted_id})
        
        return jsonify(to_json(novo_livro)), 201
    except Exception as e:
        return jsonify({"erro": f"Erro ao inserir livro: {str(e)}"}), 500


@app.route('/livros', methods=['GET'])
def listar_livros():
    livros = livros_collection.find()
    lista_livros = [to_json(livro) for livro in livros]
    return jsonify(lista_livros), 200


@app.route('/livros/<id>', methods=['GET'])
def buscar_livro(id):
    try:
        
        livro = livros_collection.find_one({'_id': id})
        
        if not livro and ObjectId.is_valid(id):
             livro = livros_collection.find_one({'_id': ObjectId(id)})

        if livro:
            return jsonify(to_json(livro)), 200
        else:
            return jsonify({"erro": "Livro não encontrado"}), 404
            
    except Exception as e:
        return jsonify({"erro": f"ID inválido ou erro: {str(e)}"}), 400


@app.route('/livros/<id>', methods=['PUT'])
def atualizar_livro(id):
    dados = request.get_json()
    if not dados:
        return jsonify({"erro": "Nenhum dado fornecido para atualização"}), 400
    
    dados.pop('_id', None) 
    dados.pop('id', None)

    try:
        query = {'_id': id}
        if not livros_collection.find_one(query) and ObjectId.is_valid(id):
            query = {'_id': ObjectId(id)}

        resultado = livros_collection.update_one(query, {"$set": dados})

        if resultado.matched_count == 0:
            return jsonify({"erro": "Livro não encontrado para atualização"}), 404
        
        livro_atualizado = livros_collection.find_one(query)
        return jsonify(to_json(livro_atualizado)), 200

    except Exception as e:
        return jsonify({"erro": f"Erro ao atualizar livro: {str(e)}"}), 500


@app.route('/livros/<id>', methods=['DELETE'])
def deletar_livro(id):
    try:
        query = {'_id': id}
        if not livros_collection.find_one(query) and ObjectId.is_valid(id):
            query = {'_id': ObjectId(id)}
            
        resultado = livros_collection.delete_one(query)

        if resultado.deleted_count == 0:
            return jsonify({"erro": "Livro não encontrado para exclusão"}), 404
        
        return jsonify({"mensagem": "Livro excluído com sucesso"}), 200

    except Exception as e:
        return jsonify({"erro": f"Erro ao deletar livro: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(debug=True)
