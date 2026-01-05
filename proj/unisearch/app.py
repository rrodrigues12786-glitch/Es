import requests
from flask import Flask, render_template, request, jsonify
from flask_caching import Cache

app = Flask(__name__)
cache_config = {
    "CACHE_TYPE": "SimpleCache",  # Guarda na memória RAM
    "CACHE_DEFAULT_TIMEOUT": 300  # 5 minutos de memória (300 segundos)
}
app.config.from_mapping(cache_config)
cache = Cache(app)
MULE_API_URL = "https://university-search-api-a8xadj.5sc6y6-2.usa-e2.cloudhub.io/api/v1/universities"
MULE_AUTH_URL = "https://university-search-api-a8xadj.5sc6y6-2.usa-e2.cloudhub.io/api/v1/auth"
MULE_USERS_URL = "https://university-search-api-a8xadj.5sc6y6-2.usa-e2.cloudhub.io/api/v1/users"

@app.route("/")
def index():
    """
    Renderiza a página inicial da aplicação.
    """
    return render_template("index.html")


@app.route("/universidades")
def universidades():
    """
    Renderiza a página principal de pesquisa e listagem de universidades.
    """
    return render_template("universidades.html")


@app.route("/api/universidades")
def api_universidades():
    """
    Comunica com a API MuleSoft para obter a lista de universidades.
    Aplica filtros de cidade e curso, e gere a paginação dos resultados.
    """
    cidade_filtro = request.args.get("cidade")
    curso_filtro = request.args.get("curso")
    page = request.args.get("page", 1, type=int)
 
    limit = 20  
    offset = (page - 1) * limit

    params_mule = {
        'limit': limit,
        'offset': offset
    }
    
    if cidade_filtro:
        params_mule['state'] = cidade_filtro
    if curso_filtro:
        params_mule['search_term'] = curso_filtro
    
    try:
        print(f"MULE REQUEST")
        print(f"URL: {MULE_API_URL}")
        print(f"Params: {params_mule}")
        print(f"--------------------")
        
        response = requests.get(MULE_API_URL, params=params_mule)
        if response.status_code != 200:
            print(f"Mule Error: {response.status_code} - {response.text}")
            return jsonify({"erro": "Erro no MuleSoft"}), 500
            
        dados_mule = response.json()
        
        lista_final = []
        for uni in dados_mule:
            uni_frontend = {
                "id": uni.get("school_id"),
                "nome": uni.get("name"),
                "cidade": f"{uni.get('city')}, {uni.get('state')}",
                "rating": "4.5", 
                "tipo": "Real",  
                "presenca": f"Custo: ${uni.get('annual_cost', 'N/A')}" 
            }

            if cidade_filtro:
                if cidade_filtro.lower() in uni_frontend["cidade"].lower():
                    lista_final.append(uni_frontend)
            else:
                lista_final.append(uni_frontend)

        return jsonify(lista_final)

    except Exception as e:
        print(f"Erro: {e}")
        return jsonify([]), 500


@app.route("/universidade/<int:id>")
def pagina_universidade(id):
    """
    Renderiza a página HTML de detalhes de uma universidade específica.
    O ID é passado para o template para identificar qual a universidade a carregar.
    """
    return render_template("universidade.html", id_uni=id)


@app.route("/api/universidade/<int:id>")
@cache.cached(timeout=600)
def api_universidade_detalhe(id):
    """
    Efetua um pedido ao MuleSoft para obter os detalhes completos 
    de uma universidade e os alojamentos próximos, baseado no ID fornecido.
    """
    try:
        url_mule = f"{MULE_API_URL}/{id}"
        
        print(f"A pedir detalhes ao Mule: {url_mule}")
        response = requests.get(url_mule)
        
        if response.status_code != 200:
            return jsonify({"erro": "Universidade não encontrada"}), 404
            
        return jsonify(response.json())
        
    except Exception as e:
        print(f"Erro: {e}")
        return jsonify({"erro": "Erro interno"}), 500


@app.route("/contactos")
def contactos():
    """
    Renderiza a página de contactos da aplicação.
    """
    return render_template("contactos.html")


@app.route("/login")
def login():
    """
    Renderiza a página de autenticação (login) para os utilizadores.
    """
    return render_template("login.html")


@app.route("/teste-geral")
def teste_geral():
    """
    Rota de teste para verificar o funcionamento básico de pedidos GET 
    e respostas em formato JSON.
    """
    nome_recebido = request.args.get("nome") 
    
    if nome_recebido:
        return jsonify({
            "status": "sucesso",
            "mensagem": f"Olá, {nome_recebido}! O jsonify e o request funcionam.",
            "tipo": "json"
        })
    else:
        return render_template("index.html")


@app.route("/sobre-nos")
def sobre_nos():
    """
    Renderiza a página informativa 'Sobre Nós'.
    """
    return render_template("sobre.html")


UNIVERSIDADES_MOCK = [
    {
        "id": 1, 
        "nome": "Universidade de Lisboa", 
        "cidade": "Lisboa", 
        "rating": "4.5", 
        "tipo": "Público", 
        "presenca": "Presencial"
    },
    {
        "id": 2, 
        "nome": "Universidade do Porto", 
        "cidade": "Porto", 
        "rating": "4.7", 
        "tipo": "Público", 
        "presenca": "Presencial"
    },
    {
        "id": 3, 
        "nome": "Harvard University", 
        "cidade": "Cambridge, MA", 
        "rating": "5.0", 
        "tipo": "Privado", 
        "presenca": "Híbrido"
    },
    {
        "id": 4, 
        "nome": "Yale University", 
        "cidade": "New Haven, CT", 
        "rating": "4.9", 
        "tipo": "Privado", 
        "presenca": "Presencial"
    },
]

CURSOS_MOCK = [
    {"id": 1, "nome": "Engenharia Informática", "universidade_id": 1},
    {"id": 2, "nome": "Gestão", "universidade_id": 2},
    {"id": 3, "nome": "Direito", "universidade_id": 3},
    {"id": 4, "nome": "Medicina", "universidade_id": 4},
]

ALOJAMENTOS_MOCK = [
    {"id": 1, "nome": "Residência Universitária A", "cidade": "Lisboa", "tipo": "Residência Universitária"},
    {"id": 2, "nome": "Residência Universitária B", "cidade": "Porto", "tipo": "Residência Universitária"},
    {"id": 3, "nome": "Apartamento Partilhado C", "cidade": "Coimbra", "tipo": "Apartamento"},
]


@app.route("/api/cursos")
def api_cursos():
    """
    Retorna uma lista de cursos (dados simulados), com a opção de filtrar 
    pelo ID da universidade.
    """
    universidade_id = request.args.get("universidade_id", type=int)

    cursos = CURSOS_MOCK

    if universidade_id is not None:
        cursos = [
            c for c in CURSOS_MOCK
            if c["universidade_id"] == universidade_id
        ]
    return jsonify(cursos)


@app.route("/api/alojamentos")
def api_alojamentos():
    """
    Retorna uma lista de alojamentos (dados simulados), com a opção de filtrar 
    pela cidade.
    """
    cidade = request.args.get("cidade")

    alojamentos = ALOJAMENTOS_MOCK

    if cidade:
        cidade_lower = cidade.lower()
        alojamentos = [
            a for a in ALOJAMENTOS_MOCK
            if a["cidade"].lower() == cidade_lower
        ]
    return jsonify(alojamentos)


@app.route("/api/health")
def api_health():
    """
    Endpoint de verificação do estado da API (Health Check), retorna estado 200 OK.
    """
    return jsonify({"status": "ok", "mensagem": "API UniSearch a funcionar"})


@app.route("/termos")
def termos():
    """
    Renderiza a página de Termos e Condições de uso.
    """
    return render_template("termos.html")


@app.route("/privacidade")
def privacidade():
    """
    Renderiza a página de Política de Privacidade.
    """
    return render_template("privacidade.html")


@app.route("/faqs")
def faqs():
    """
    Renderiza a página de Perguntas Frequentes (FAQs).
    """
    return render_template("faqs.html")


@app.route("/api/login", methods=["POST"])
def api_login():
    """
    Recebe as credenciais (email e password) via JSON e reencaminha o pedido
    de autenticação para a API MuleSoft.
    """
    data = request.get_json()
  
    if not data or not data.get("email") or not data.get("password"):
        return jsonify({"erro": "Email e password são obrigatórios"}), 400

    try:
        response = requests.post(f"{MULE_AUTH_URL}/login", json=data)
        
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify(response.json()), response.status_code

    except Exception as e:
        print(f"Erro no Login: {e}")
        return jsonify({"erro": "Erro interno ao contactar servidor"}), 500


@app.route("/api/register", methods=["POST"])
def api_register():
    """
    Recebe os dados de um novo utilizador via JSON e envia o pedido de 
    registo para a API MuleSoft.
    """
    data = request.get_json()
    
    if not data or not data.get("email") or not data.get("password"):
        return jsonify({"erro": "Dados incompletos"}), 400

    try:
        response = requests.post(f"{MULE_AUTH_URL}/register", json=data)
        
        if response.status_code == 200 or response.status_code == 201:
            return jsonify(response.json())
        else:
            return jsonify(response.json()), response.status_code

    except Exception as e:
        print(f"Erro no Registo: {e}")
        return jsonify({"erro": "Erro interno ao contactar servidor"}), 500


@app.route("/favoritos")
def pagina_favoritos():
    """
    Renderiza a página HTML de gestão de favoritos do utilizador.
    """
    return render_template("favoritos.html")


@app.route("/api/users/<int:user_id>/favorites", methods=["GET"])
def api_get_favorites(user_id):
    """
    Obtém a lista de universidades favoritas de um utilizador específico
    através da API MuleSoft.
    """
    try:
        response = requests.get(f"{MULE_USERS_URL}/{user_id}/favorites")
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


@app.route("/api/users/<int:user_id>/favorites", methods=["POST"])
def api_add_favorite(user_id):
    """
    Adiciona uma universidade aos favoritos de um utilizador específico
    enviando os dados para a API MuleSoft.
    """
    data = request.get_json()
    
    try:
        response = requests.post(f"{MULE_USERS_URL}/{user_id}/favorites", json=data)
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


@app.route("/api/users/<int:user_id>/favorites/<int:uni_id>", methods=["DELETE"])
def api_delete_favorite(user_id, uni_id):
    """
    Remove uma universidade específica dos favoritos de um utilizador
    através da API MuleSoft.
    """
    try:
        response = requests.delete(f"{MULE_USERS_URL}/{user_id}/favorites/{uni_id}")
        if response.status_code == 204:
            return jsonify({"message": "Removido com sucesso"}), 200
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
