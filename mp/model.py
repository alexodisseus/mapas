from flask_sqlalchemy import SQLAlchemy

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



def cadastrar_banca(pavilhao_nome, ilha_coluna_nome, banca_nome, tipo_contrato, nome_permissionario):
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
        return banca_existente  # Opcional: ou retorne None, ou levante exceção

    # Criar a banca
    banca = Banca(
        nome=banca_nome,
        tipo=tipo_contrato,
        permissionario=nome_permissionario,
        ilha_coluna_id=ilha.id
    )
    db.session.add(banca)
    db.session.commit()
    return banca



def list_all_mapas():
    return Pavilhao.query.all()


def get_mapa_by_pavilhao(id_pavilhao):
    return Pavilhao.query.get(id_pavilhao)
