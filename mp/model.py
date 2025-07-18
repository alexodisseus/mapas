from flask_sqlalchemy import SQLAlchemy

from sqlalchemy import case, func, cast, Integer
from sqlalchemy.orm import joinedload





db = SQLAlchemy()



class Pavilhao(db.Model):
    __tablename__ = 'pavilhoes'  # Nome da tabela no banco (opcional)

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f'<Pavilhao {self.nome}>'


class IlhaColuna(db.Model):
    __tablename__ = 'ilhas_colunas'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    #totaldebancas = db.Column(db.Integer, default=0)  # Nova coluna

    pavilhao_id = db.Column(db.Integer, db.ForeignKey('pavilhoes.id'), nullable=False)
    pavilhao = db.relationship('Pavilhao', backref=db.backref('ilhas_colunas', lazy=True))

    def __repr__(self):
        return f'<IlhaColuna {self.nome} - Pavilhao ID: {self.pavilhao_id}>'


class Banca(db.Model):
    __tablename__ = 'bancas'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    permissionario = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)

    ilha_coluna_id = db.Column(db.Integer, db.ForeignKey('ilhas_colunas.id'), nullable=False)
    ilha_coluna = db.relationship('IlhaColuna', backref=db.backref('bancas', lazy=True))

    def __repr__(self):
        return f'<Banca {self.nome} - IlhaColuna ID: {self.ilha_coluna_id}>'


class Mapa(db.Model):
    __tablename__ = 'mapas'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)

    banca_id = db.Column(db.Integer, db.ForeignKey('bancas.id'), nullable=True)
    banca = db.relationship('Banca', backref=db.backref('mapas', lazy=True))

    coluna = db.Column(db.String(20), nullable=True)
    linha = db.Column(db.String(20), nullable=True)
    cor = db.Column(db.String(20), nullable=True)
    tipo = db.Column(db.String(50), nullable=True)

    ilhacoluna_id = db.Column(db.Integer, db.ForeignKey('ilhas_colunas.id'), nullable=False)
    ilhacoluna = db.relationship('IlhaColuna', backref=db.backref('mapas', lazy=True))

    def __repr__(self):
        return f'<Mapa {self.nome} - ID: {self.id}, Banca: {self.banca_id}>'



def cadastrar_banca(pavilhao_nome, ilha_coluna_nome, banca_nome, tipo_contrato, nome_permissionario, status):
    # Buscar ou criar o pavilhão
    pavilhao = Pavilhao.query.filter_by(nome=pavilhao_nome).first()
    if not pavilhao:
        pavilhao = Pavilhao(nome=pavilhao_nome)
        db.session.add(pavilhao)
        db.session.flush()

    # Buscar ou criar a ilha_coluna
    ilha = IlhaColuna.query.filter_by(nome=ilha_coluna_nome, pavilhao_id=pavilhao.id).first()
    if not ilha:
        ilha = IlhaColuna(nome=ilha_coluna_nome, pavilhao_id=pavilhao.id)
        db.session.add(ilha)
        db.session.flush()

    # Verificar se a banca já existe
    banca_existente = Banca.query.filter_by(nome=banca_nome, ilha_coluna_id=ilha.id).first()
    if banca_existente:
        return banca_existente

    # Ajustar o permissionário com base no status
    if status.strip().lower() != 'ocupada':
        nome_permissionario = 'Liberada'
        tipo_contrato = ''

    # Criar a banca
    banca = Banca(
        nome=banca_nome,
        tipo=tipo_contrato,
        permissionario=nome_permissionario,
        ilha_coluna_id=ilha.id
    )
    db.session.add(banca)

    # Atualizar total de bancas da ilha
    ilha.totaldebancas = db.session.query(Banca).filter_by(ilha_coluna_id=ilha.id).count() + 1

    db.session.commit()
    return banca



def list_all_mapas():
    return Pavilhao.query.all()

def get_mapas(id_pavilhao):
    data = IlhaColuna.query.filter_by(pavilhao_id=id_pavilhao).all()


    def sort_key(item):
        nome = item.nome.upper()
        if nome.startswith("ILHA"):
            grupo = 0
        elif nome.startswith("COLUNA"):
            grupo = 1
        elif nome.startswith("ALIMENTAÇÃO"):
            grupo = 2
        else:
            grupo = 99  # Para casos inesperados

        # Extrai o número do nome (ex: "ILHA 2" → 2)
        numeros = ''.join(filter(str.isdigit, nome))
        numero = int(numeros) if numeros else 0

        return (grupo, numero)

    return sorted(data, key=sort_key)



def get_frequencia_by_pavilhao(id_pavilhao):
    pavilhao = Pavilhao.query.get(id_pavilhao)
    if not pavilhao:
        return None

    prioridade = case(
        (IlhaColuna.nome.like('ILHA -%'), 1),
        (IlhaColuna.nome.like('COLUNA -%'), 2),
        (IlhaColuna.nome.like('ALIMENTAÇÃO -%'), 3),
        else_=4
    )

    numero_extraido = cast(
        func.substr(IlhaColuna.nome, func.instr(IlhaColuna.nome, '-') + 2),
        Integer
    )

    ilhas = (
        IlhaColuna.query
        .filter_by(pavilhao_id=id_pavilhao)
        .order_by(prioridade, numero_extraido)
        .all()
    )

    for ilha in ilhas:
        ilha.bancas_agrupadas = agrupar_bancas(ilha.bancas)

    pavilhao.ilhas_colunas = ilhas
    return pavilhao



def agrupar_bancas(bancas):
    agrupadas = []
    if not bancas:
        return agrupadas

    # Ordena as bancas por nome (convertido para inteiro)
    bancas = sorted(bancas, key=lambda b: int(b.nome))

    inicio = fim = bancas[0].nome
    tipo = bancas[0].tipo
    permissionario = bancas[0].permissionario

    for atual in bancas[1:]:
        if (
            atual.tipo == tipo and
            atual.permissionario == permissionario and
            int(atual.nome) == int(fim) + 1
        ):
            fim = atual.nome
        else:
            agrupadas.append({
                'intervalo': f"{inicio} à {fim}" if inicio != fim else str(inicio),
                'tipo': tipo,
                'permissionario': permissionario
            })
            inicio = fim = atual.nome
            tipo = atual.tipo
            permissionario = atual.permissionario

    agrupadas.append({
        'intervalo': f"{inicio} à {fim}" if inicio != fim else str(inicio),
        'tipo': tipo,
        'permissionario': permissionario
    })

    return agrupadas




def get_mapa_by_ilhacoluna(id_ilhacoluna):
    return IlhaColuna.query.filter_by(id=id_ilhacoluna).all()



def get_bancas_by_ilhacoluna(id_ilhacoluna, id_pavilhao):
    return (
        Banca.query
        .join(IlhaColuna)
        .filter(
            Banca.ilha_coluna_id == id_ilhacoluna,
            IlhaColuna.pavilhao_id == id_pavilhao
        )
        .order_by(cast(Banca.nome, Integer).asc())
        .all()
    )

def set_mapas_cordenadas(linha, coluna, cor, banca_id=None, celula_id=None, ilhacoluna_id=None):
    if ilhacoluna_id is None:
        raise ValueError("ilhacoluna_id é obrigatório")

    # Verifica se já existe um mapa com essa banca_id dentro da mesma ilhacoluna
    mapa_existente_banca = None
    if banca_id:
        mapa_existente_banca = Mapa.query.filter_by(banca_id=banca_id, ilhacoluna_id=ilhacoluna_id).first()

    if celula_id:
        mapa = Mapa.query.get(celula_id)
    else:
        mapa = Mapa.query.filter_by(linha=linha, coluna=coluna, ilhacoluna_id=ilhacoluna_id).first()

    if mapa_existente_banca and (not mapa or mapa_existente_banca.id != mapa.id):
        # Atualiza o registro existente da banca para nova posição
        mapa_existente_banca.linha = linha
        mapa_existente_banca.coluna = coluna
        mapa_existente_banca.cor = cor
        mapa = mapa_existente_banca
    elif mapa:
        mapa.cor = cor
        mapa.banca_id = banca_id
    else:
        # Cria novo mapa se não existir
        mapa = Mapa(
            linha=linha,
            coluna=coluna,
            cor=cor,
            banca_id=banca_id,
            ilhacoluna_id=ilhacoluna_id,
            nome=f"{linha}-{coluna}"
        )
        db.session.add(mapa)

    db.session.commit()
    return mapa.id

def set_mapas_cordenadas_delete(linha, coluna, ilhacoluna_id=None, celula_id=None):

    if celula_id:
        mapa = Mapa.query.get(celula_id)
    else:
        if ilhacoluna_id is None:
            raise ValueError("ilhacoluna_id é necessário para identificar a célula")
        mapa = Mapa.query.filter_by(linha=linha, coluna=coluna, ilhacoluna_id=ilhacoluna_id).first()

    if mapa:
        db.session.delete(mapa)
        db.session.commit()


def get_mapas_cordenadas(id_pavilhao=None, ilhacoluna_id=None):
    from sqlalchemy.orm import joinedload
    import re

    def extrair_numero(nome):
        match = re.search(r'(\d+)$', nome)
        return int(match.group(1)) if match else 0

    query = db.session.query(
        Mapa,
        IlhaColuna,
        Pavilhao
    ).join(
        IlhaColuna, Mapa.ilhacoluna_id == IlhaColuna.id
    ).join(
        Pavilhao, IlhaColuna.pavilhao_id == Pavilhao.id
    ).options(
        joinedload(Mapa.banca)
    )

    if id_pavilhao is not None:
        query = query.filter(Pavilhao.id == id_pavilhao)

    if ilhacoluna_id is not None:
        query = query.filter(IlhaColuna.id == ilhacoluna_id)

    # Removemos a ordenação SQL porque vamos ordenar no Python
    resultados = query.all()

    # Ordenação numérica por IlhaColuna.nome + linha + coluna
    resultados.sort(key=lambda x: (extrair_numero(x[1].nome), x[0].linha, x[0].coluna))

    mapas_formatados = []
    for mapa, ilha, pavilhao in resultados:
        mapas_formatados.append({
            'mapa_id': mapa.id,
            'mapa_nome': mapa.nome,
            'banca_id': mapa.banca_id,
            'banca_nome': mapa.banca.nome if mapa.banca else None,
            'permissionario': mapa.banca.permissionario if mapa.banca else None,
            'coordenadas': {
                'coluna': mapa.coluna,
                'linha': mapa.linha,
                'cor': mapa.cor,
                'tipo': mapa.tipo
            },
            'ilha_coluna': {
                'id': ilha.id,
                'nome': ilha.nome
            },
            'pavilhao': {
                'id': pavilhao.id,
                'nome': pavilhao.nome
            }
        })

    return mapas_formatados


