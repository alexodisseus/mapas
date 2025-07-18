from flask import Flask
from flask import Blueprint, render_template, request, session, redirect, url_for, flash


from flask import request, jsonify




import model

from datetime import datetime
from werkzeug.utils import secure_filename
from io import StringIO
import csv
import os


ALLOWED_EXTENSIONS = {'csv'}
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)



from flask import Flask, Blueprint, render_template, request, redirect, url_for, flash

lists = Blueprint('lists', __name__, url_prefix='/')

# Suponha que temos uma lista de dicionários para simular um banco de dados




ALLOWED_EXTENSIONS = {'csv'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



# Rota para exibir todas as listas (List)
@lists.route('/')
def list_lists():
    data = model.list_all_mapas()
    return render_template('lists/index.html' , data=data)
    
@lists.route('/frequencia/<int:id_pavilhao>')
def list_frequencia(id_pavilhao):
    
    data = model.get_frequencia_by_pavilhao(id_pavilhao)
    return render_template('lists/frequencia.html', data=data)


@lists.route('/mapa/<int:id_pavilhao>')
def list_mapas(id_pavilhao):
    data = model.get_mapas()
    cordenadas = model.get_mapas_cordenadas(id_pavilhao)

    return render_template('lists/mapas.html', data=data , cordenadas = cordenadas)


@lists.route('/mapa/listar')
def list_mapas_listar():
    data = model.get_mapas()

    return render_template('lists/mapas_listar.html', data=data)






@lists.route('/mapa/editar/<int:id_ilhacoluna>')
def list_mapas_editar(id_ilhacoluna):
    data = model.get_mapa_by_ilhacoluna(id_ilhacoluna)
    bancas = model.get_bancas_by_ilhacoluna(id_ilhacoluna)
    """
    print(bancas[0])
    cordenadas_ilha = model.get_mapas_cordenadas(id_pavilhao,id_ilhacoluna)
    """
    return render_template('lists/mapas_editar.html', data=data, bancas=bancas)




@lists.route('enviar/')
def list_send():

    return render_template('lists/send.html' )



@lists.route('/add/', methods=['GET', 'POST'])
def list_add():
    if request.method == 'POST':
        # Verificação básica do arquivo
        if 'csv_file' not in request.files:
            flash('Nenhum arquivo enviado', 'error')
            return redirect(request.url)
            
        file = request.files['csv_file']
        
        if file.filename == '':
            flash('Nenhum arquivo selecionado', 'error')
            return redirect(request.url)
            
        if not allowed_file(file.filename):
            flash('Tipo de arquivo não permitido. Envie apenas CSV.', 'error')
            return redirect(request.url)
        
        try:
            # Lê o conteúdo bruto do arquivo
            raw_data = file.read()
            file.seek(0)  # Reset file pointer
            
            # Lista de codificações para tentar (em ordem de probabilidade)
            encodings_to_try = ['iso-8859-1', 'windows-1252', 'cp1252']
            
            content = None
            for encoding in encodings_to_try:
                try:
                    content = raw_data.decode(encoding)
                    break  # Se decodificar com sucesso, para o loop
                except UnicodeDecodeError:
                    continue
            
            if content is None:
                flash('Não foi possível determinar a codificação do arquivo', 'error')
                return redirect(request.url)
            
            # Processa o CSV
            csv_data = []
            with StringIO(content) as stream:
                csv_reader = csv.reader(stream , delimiter=';')
                next(csv_reader)
                for row in csv_reader:
                    
                    resultado = [item for linha in row for item in linha.split(';')]

                    data = resultado
                    csv_data.append(data)
                    
                    
                    asd = model.cadastrar_banca(data[3], data[6], data[7], data[12], data[14] , data[11])

                    print(data[3], data[6], data[7], data[12], data[14], data[11])

            # Salva o arquivo temporariamente (opcional)
            filename = secure_filename(file.filename)
            temp_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(temp_path)
            
            flash(f'Arquivo processado com sucesso! {len(csv_data)} linhas importadas.', 'success')
            
            # Mostra as primeiras 10 linhas no template (opcional)
            return render_template('lists/send.html',
                               rows=csv_data[:10],
                               filename=filename)
            
        except csv.Error as e:
            flash(f'Erro no formato CSV: {str(e)}', 'error')
        except Exception as e:
            flash(f'Erro ao processar arquivo: {str(e)}', 'error')
        
        return redirect(request.url)
    
    # GET request
    return render_template('lists/send.html')

def allowed_file(filename):
    """Verifica se a extensão é permitida"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@lists.route('/cadastrar', methods=['GET', 'POST'])
def create_list():
        


    asd = model.cadastrar_banca( "MLP - V.SABADO", "ILHA - 34", "17", "AU FATURA", "MOHAMED COMÉRCIO DE FRUTAS LTDA.")    
    return redirect(url_for('lists.list_lists'))
    
    




















@lists.route('/salvar_celula', methods=['POST'])
def salvar_celula():
    try:
        data = request.get_json()
        print("DADOS RECEBIDOS:", data)
        # Verifica se é para limpar a célula
        if data.get('limpar'):
            """
            # Lógica para limpar a célula no banco de dados
            celula = Celula.query.filter_by(
                linha=data['linha'],
                coluna=data['coluna']
            ).first()
            
            if celula:
                db.session.delete(celula)
                db.session.commit()
            return jsonify({'success': True})
            """
            model.set_mapas_cordenadas_delete()

        # Lógica para salvar/atualizar a célula

        """
        celula = Celula.query.filter_by(
            linha=data['linha'],
            coluna=data['coluna']
        ).first()
        
        if celula:
            # Atualiza célula existente
            celula.nome = data['nome']
            celula.cor = data['cor']
            celula.banca_id = data['banca_id']
        else:
            # Cria nova célula
            celula = Celula(
                linha=data['linha'],
                coluna=data['coluna'],
                nome=data['nome'],
                cor=data['cor'],
                banca_id=data['banca_id'],
                ilha_id=data.get('ilha_id')  # Adicione conforme necessário
            )
            db.session.add(celula)
        
        print(celula)
        
        db.session.commit()
        """
        model.set_mapas_cordenadas(linha=data['linha'],
                coluna=data['coluna'],
                
                cor=data['cor'],
                banca_id=data['banca_id'],
                celula_id=data['celula_id'],
                ilhacoluna_id=data['ilhacoluna_id'])

        return jsonify({
            'success': True,
            'celula_id': data['celula_id']
        })
        
    except Exception as e:
        #db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400

# Função para configurar o blueprint
def configure(app):
    app.register_blueprint(lists)






