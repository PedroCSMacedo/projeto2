import streamlit as st
import sqlite3
import pandas as pd

# Criar banco de dados
conn = sqlite3.connect("garcom2.db")
cursor = conn.cursor()

# Tabelas
cursor.execute("""
CREATE TABLE IF NOT EXISTS itens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT,
    descricao TEXT,
    fornecedor TEXT,
    valor REAL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS listas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome_lista TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS itens_lista (
    id_lista INTEGER,
    id_item INTEGER,
    quantidade INTEGER,
    FOREIGN KEY (id_lista) REFERENCES listas(id),
    FOREIGN KEY (id_item) REFERENCES itens(id)
)
""")

# Barra lateral
barra_lateral = st.sidebar.selectbox("Página", ["Adicionar/Excluir Itens", "Criar Lista", "Visualizar Listas", "Visualizar Itens"])

# Página Inserir Item 
if barra_lateral == "Adicionar/Excluir Itens":
    st.title("Adicionar/Excluir Itens")
    adex = st.selectbox("Adicionar/excluir", ["Adicionar", "Excluir"])

    # Adicionar itens
    if adex == "Adicionar":
        def salvarDados():
            if nome and descricao and valor and fornecedor:
                try: 
                    cursor.execute("""
                    INSERT INTO itens (nome, descricao, fornecedor, valor) VALUES (?, ?, ?, ?)
                    """, (nome, descricao, fornecedor, valor))
                    conn.commit()
                    st.success("O item foi adicionado com sucesso!")
                except ValueError:
                    st.error("Escreva um valor válido em todos os campos")
            else:
                st.error("Todos os campos devem estar preenchidos!")

        nome = st.text_input("Nome do item:")
        descricao = st.text_area("Descrição do item:")
        fornecedor = st.text_input("Nome do fornecedor:")
        valor = st.number_input("Qual o valor do item:", min_value=0.0, step=0.01)

        if st.button("Salvar"):
            salvarDados()

    # Excluir itens
    elif adex == "Excluir":
        def deletarDados():
            if idDelet and idDelet.isdigit():
                try:
                    idDelet_int = int(idDelet)
                    cursor.execute("SELECT 1 FROM itens WHERE id = ?", (idDelet_int,))
                    if cursor.fetchone():
                        cursor.execute("DELETE FROM itens WHERE id = ?", (idDelet_int,))
                        conn.commit()
                        st.success("O item foi excluído com sucesso!")
                    else:
                        st.error("ID não encontrado")
                except sqlite3.Error:
                    st.error("Erro ao excluir o item")
            else:
                st.error("Digite um ID válido")

        idDelet = st.text_input("Excluir Item (digite o ID do item):")

        if 'confirm' not in st.session_state:
            st.session_state.confirm = False

        if not st.session_state.confirm:  
            if st.button("Excluir"):
                st.session_state.confirm = True

        if st.session_state.confirm:    
            st.write("Você deseja excluir este item permanentemente?")
            if st.button("Confirmar"):
                deletarDados()
                st.session_state.confirm = False
            if st.button("Cancelar"):
                st.error("Operação cancelada")
                st.session_state.confirm = False

# Página Criar Lista
elif barra_lateral == "Criar Lista":
    st.title("Criar Lista")

    # Criar nova lista
    nova_lista = st.text_input("Digite o nome da nova lista:")
    if st.button("Criar Lista"):
        if nova_lista:
            cursor.execute("INSERT INTO listas (nome_lista) VALUES (?)", (nova_lista,))
            conn.commit()
            st.success(f"Lista '{nova_lista}' criada com sucesso!")
        else:
            st.error("Digite um nome para a lista!")

    # Selecionar lista existente
    cursor.execute("SELECT id, nome_lista FROM listas")
    listas = cursor.fetchall()

    if listas:
        lista_selecionada = st.selectbox("Selecione uma lista para adicionar itens:", [f"{l[1]} (ID: {l[0]})" for l in listas])
        id_lista = int(lista_selecionada.split("(ID: ")[1].replace(")", ""))

        # Mostrar itens disponíveis
        cursor.execute("SELECT id, nome FROM itens")
        itens = cursor.fetchall()

        if itens:
            item_selecionado = st.selectbox("Selecione um item para adicionar:", [f"{i[1]} (ID: {i[0]})" for i in itens])
            id_item = int(item_selecionado.split("(ID: ")[1].replace(")", ""))

            quantidade = st.number_input("Quantidade:", min_value=1, step=1)

            if st.button("Adicionar Item à Lista"):
                cursor.execute("INSERT INTO itens_lista (id_lista, id_item, quantidade) VALUES (?, ?, ?)", (id_lista, id_item, quantidade))
                conn.commit()
                st.success("Item adicionado à lista com sucesso!")

# Página Visualizar Listas com Expander
elif barra_lateral == "Visualizar Listas":
    st.title("Visualizar Listas")

    cursor.execute("""
    SELECT l.id, l.nome_lista, i.id, i.nome, i.valor, il.quantidade
    FROM itens_lista il
    JOIN listas l ON il.id_lista = l.id
    JOIN itens i ON il.id_item = i.id
    """)
    dados = cursor.fetchall()

    if dados:
        listas_detalhadas = {}
        for linha in dados:
            lista_id, lista_nome, item_id, item_nome, item_valor, quantidade = linha
            if lista_id not in listas_detalhadas:
                listas_detalhadas[lista_id] = {"nome_lista": lista_nome, "itens": [], "valor_total": 0}
            listas_detalhadas[lista_id]["itens"].append({
                "item_id": item_id,
                "item_nome": item_nome,
                "item_valor": item_valor,
                "quantidade": quantidade
            })
            # Calcular valor total da lista
            listas_detalhadas[lista_id]["valor_total"] += item_valor * quantidade

        # Exibir listas e itens dentro de expanders
        for lista_id, lista_info in listas_detalhadas.items():
            with st.expander(f"{lista_info['nome_lista']} (ID: {lista_id}) - Valor Total: R${lista_info['valor_total']:.2f}"):
                for item in lista_info["itens"]:
                    st.write(f"**Nome do Item:** {item['item_nome']}")
                    st.write(f"**ID do Item:** {item['item_id']}")
                    st.write(f"**Valor:** R${item['item_valor']:.2f}")
                    st.write(f"**Quantidade:** {item['quantidade']}")
                    st.write("---")
    else:
        st.write("Nenhuma lista criada ou itens adicionados ainda.")

# Página Visualizar Itens
elif barra_lateral == "Visualizar Itens":
    st.title("Visualizar Itens")

    cursor.execute("SELECT * FROM itens")
    itens = cursor.fetchall()

    if itens:
        tabela = pd.DataFrame(itens, columns=["ID", "Nome", "Descrição", "Fornecedor", "Valor"])
        st.write(tabela)
    else:
        st.write("Adicione algum item ao banco de dados.")

conn.close()
