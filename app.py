import streamlit as st
import sqlite3
from datetime import datetime

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
import io

# Banco de dados
conexao = sqlite3.connect("recebimentos.db")
cursor = conexao.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS recebimentos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data TEXT,
    hora TEXT,
    fornecedor TEXT,
    motorista TEXT,
    placa TEXT,
    peso REAL,
    numero_nf TEXT
)
""")
conexao.commit()

st.set_page_config(
    page_title="Recebimento de Cargas",
    page_icon=":🚛",
 layout="wide",
)

st.markdown("""
<div style="
    background-color: #176B3A;
    padding: 25px;
    border-radius: 12px;
    margin-bottom: 25px;
">

<div style="
    display: flex;
    align-items: center;
    gap: 15px;
">

<div style="font-size: 45px;">
    🚛

</div>

<div>
<h1 style="
    color: white;
    margin: 0;
    font-size: 32px;
">
Recebimento de Cargas
</h1>

<p style="
    color: #FFF3B0;
    margin: 5px 0 0 0;
    font-size: 16px;
">
Controle de entrada de materiais e notas fiscais
</p>

</div>

</div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="
    background-color: white;
    padding: 25px;
    border-radius: 12px;
    border: 1px solid #E0E0E0;
    box-shadow: 0px 2px 8px rgba(0,0,0,0.08);
    margin-top: 20px;
">

<h2 style="
    color: #176B3A;
    margin-top: 0;
">
📦 Novo Recebimento
</h2>

<p style="
    color: #666666;
    margin-bottom: 0;
">
Preencha as informações da entrada do caminhão.
</p>

</div>
""", unsafe_allow_html=True)

st.markdown("""
<style>

.stApp {
    background-color: #121212;
}

</style>
""", unsafe_allow_html=True)

st.write("")

coluna1, coluna2 = st.columns(2)

with coluna1:
    fornecedor = st.text_input(
        "Fornecedor",
        placeholder="Digite o nome do fornecedor"
    )

    motorista = st.text_input(
        "Motorista", 
        placeholder="Digite o nome do motorista"
        )


    peso = st.number_input(
        "Peso da entrada (kg)",
        min_value=0.0,
        step=1.0
    )

with coluna2:
    placa = st.text_input(
        "Placa",
        placeholder="ABC-1234"
    )

    numero_nf = st.text_input(
        "Número da Nota Fiscal",
        placeholder="Digite o número da NF"
    )

    st.write("")

if st.button("✓ REGISTRAR ENTRADA", type="primary"):

    agora = datetime.now()

    data = agora.strftime("%d/%m/%Y")
    hora = agora.strftime("%H:%M:%S")

    if not fornecedor or not motorista or not placa or not numero_nf:
        st.error("⚠️ Preencha todos os campos obrigatórios.")
    elif peso <= 0:
        st.error("⚠️ O peso precisa ser maior que zero.")
    else:
        cursor.execute("""
        INSERT INTO recebimentos
        (data, hora, fornecedor, motorista, placa, peso, numero_nf)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            data,
            hora,
            fornecedor,
            motorista,
            placa,
            peso,
            numero_nf
        ))

        conexao.commit()

        ticket = cursor.lastrowid

        st.success(
            f"✅ Entrada registrada com sucesso! "
            f"Ticket #{ticket:06d}"
        )

        st.write("")
st.write("")

st.markdown("""
<div style="
    background-color: #FFD600;
    padding: 20px;
    border-radius: 12px;
    border: 1px solid #E6D36A;
    margin-top: 25px;
">

<h2 style="
    color: #176B3A;
    margin: 0;
">
📋 Entradas Registradas
</h2>

<p style="
    color: #555555;
    margin-bottom: 0;
">
Consulte os tickets registrados no sistema.
</p>

</div>
""", unsafe_allow_html=True)

if st.button("🔎 CONSULTAR ENTRADAS"):

    cursor.execute("""
        SELECT
            id,
            data,
            hora,
            fornecedor,
            motorista,
            placa,
            peso,
            numero_nf
        FROM recebimentos
        ORDER BY id DESC
    """)

    entradas = cursor.fetchall()

    if len(entradas) == 0:

        st.info("📭 Nenhuma entrada registrada ainda.")

    else:

        st.subheader("📋 Tickets registrados")

        dados_tabela = []

        for entrada in entradas:


            dados_tabela.append({
                "🎫 Ticket": f"#{entrada[0]:06d}",
                "📅 Data": str(entrada[1]),
                "🕐 Hora": str(entrada[2]),
                "🏢 Fornecedor": str(entrada[3]),
                "👤 Motorista": str(entrada[4]),
                "🚛 Placa": str(entrada[5]),
                "⚖️ Peso (kg)": f"{entrada[6]}",
                "📄 NF": str(entrada[7])
            })

        st.table(dados_tabela)

        # ==============================
# EXCLUSÃO DE REGISTROS
# ==============================

if "confirmar_exclusao" not in st.session_state:
    st.session_state.confirmar_exclusao = False


if st.button("🗑️ LIMPAR TODOS OS REGISTROS"):

    st.session_state.confirmar_exclusao = True


if st.session_state.confirmar_exclusao:

    st.warning(
        "⚠️ ATENÇÃO! Você está prestes a excluir TODOS os registros. "
        "Essa ação não poderá ser desfeita."
    )

    coluna1, coluna2 = st.columns(2)

    with coluna1:

        if st.button("❌ CANCELAR"):

            st.session_state.confirmar_exclusao = False
            st.rerun()

    with coluna2:

        if st.button("🗑️ SIM, EXCLUIR TUDO"):

            cursor.execute("DELETE FROM recebimentos")
            conexao.commit()

            st.session_state.confirmar_exclusao = False

            st.success("✅ Todos os registros foram excluídos.")

            st.rerun()

            st.write("")

st.subheader("🖨️ Imprimir Ticket")

ticket_impressao = st.number_input(
    "Digite o número do ticket que deseja imprimir:",
    min_value=1,
    step=1
)

if st.button("🖨️ GERAR TICKET PARA IMPRESSÃO"):

    cursor.execute("""
        SELECT
            id,
            data,
            hora,
            fornecedor,
            motorista,
            placa,
            peso,
            numero_nf
        FROM recebimentos
        WHERE id = ?
    """, (ticket_impressao,))

    ticket = cursor.fetchone()

    if ticket is None:

        st.error("❌ Ticket não encontrado.")

    else:

        def gerar_pdf_ticket(ticket):
            buffer = io.BytesIO()
            pdf = canvas.Canvas(buffer, pagesize=A4)
            largura, altura = A4
            pdf.setTitle(f"Ticket #{ticket[0]:06d}")
            # ==============================
            # CORES
            # ==============================
            VERDE = (23 / 255, 107 / 255, 58 / 255)
            AMARELO = (1, 214 / 255, 0)
            CINZA = (80 / 255, 80 / 255, 80 / 255)
            # ==============================
            # FUNDO DO TICKET
            # ==============================
            pdf.setFillColorRGB(248 / 255, 248 / 255, 248 / 255)
            pdf.roundRect(
                20 * mm,
                35 * mm,
                largura - 40 * mm,
                altura - 70 * mm,
                8 * mm,
                fill=1,
                stroke=0
            )
            # ==============================
            # FAIXA VERDE SUPERIOR
            # ==============================
            pdf.setFillColorRGB(*VERDE)
            pdf.roundRect(
                20 * mm,
                altura - 65 * mm,
                largura - 40 * mm,
                30 * mm,
                8 * mm,
                fill=1,
                stroke=0
            )
            # ==============================
            # TÍTULO
            # ==============================
            pdf.setFillColorRGB(1, 1, 1)
            pdf.setFont("Helvetica-Bold", 20)
            pdf.drawCentredString(
                largura / 2,
                altura - 50 * mm,
                "RECEBIMENTO DE CARGAS"
            )
            pdf.setFont("Helvetica", 10)
            pdf.drawCentredString(
                largura / 2,
                altura - 57 * mm,
                "CONTROLE DE ENTRADA"
            )
            # ==============================
            # FAIXA AMARELA
            # ==============================
            pdf.setFillColorRGB(*AMARELO)
            pdf.roundRect(
                30 * mm,
                altura - 80 * mm,
                largura - 60 * mm,
                12 * mm,
                4 * mm,
                fill=1,
                stroke=0
            )
            pdf.setFillColorRGB(30 / 255, 30 / 255, 30 / 255)
            pdf.setFont("Helvetica-Bold", 13)
            pdf.drawString(
                37 * mm,
                altura - 75 * mm,
                "TICKET DE ENTRADA"
            )
            pdf.drawRightString(
                largura - 37 * mm,
                altura - 75 * mm,
                f"#{ticket[0]:06d}"
            )
            # ==============================
            # INFORMAÇÕES
            # ==============================
            y = altura - 105 * mm
            informacoes = [
                ("DATA", ticket[1]),
                ("HORÁRIO", ticket[2]),
                ("FORNECEDOR", ticket[3]),
                ("MOTORISTA", ticket[4]),
                ("PLACA", ticket[5]),
                ("PESO", f"{ticket[6]} kg"),
                ("NOTA FISCAL", ticket[7])
            ]
            for nome, valor in informacoes:
                pdf.setFillColorRGB(*CINZA)
                pdf.setFont("Helvetica-Bold", 9)
                pdf.drawString(
                    35 * mm,
                    y,
                    nome
                )
                pdf.setFillColorRGB(30 / 255, 30 / 255, 30 / 255)
                pdf.setFont("Helvetica", 11)
                pdf.drawString(
                    75 * mm,
                    y,
                    str(valor)
                )
                pdf.setStrokeColorRGB(
                    210 / 255,
                    210 / 255,
                    210 / 255
                )
                pdf.line(
                    35 * mm,
                    y - 3 * mm,
                    largura - 35 * mm,
                    y - 3 * mm
                )
                y -= 15 * mm
            # ==============================
            # STATUS
            # ==============================
            pdf.setFillColorRGB(*VERDE)
            pdf.roundRect(
                55 * mm,
                y - 5 * mm,
                largura - 110 * mm,
                15 * mm,
                5 * mm,
                fill=1,
                stroke=0
            )
            pdf.setFillColorRGB(1, 1, 1)
            pdf.setFont("Helvetica-Bold", 12)
            pdf.drawCentredString(
                largura / 2,
                y,
                "ENTRADA REGISTRADA"
            )
            # ==============================
            # ASSINATURA
            # ==============================
            y -= 35 * mm
            pdf.setFillColorRGB(*CINZA)
            pdf.setFont("Helvetica", 9)
            pdf.drawString(
                35 * mm,
                y,
                "ASSINATURA / CONFERÊNCIA"
            )
            pdf.setStrokeColorRGB(
                100 / 255,
                100 / 255,
                100 / 255
            )
            pdf.line(
                35 * mm,
                y - 8 * mm,
                largura - 35 * mm,
                y - 8 * mm
            )
            # ==============================
            # RODAPÉ
            # ==============================
            pdf.setFillColorRGB(*VERDE)
            pdf.setFont("Helvetica", 8)
            pdf.drawCentredString(
                largura / 2,
                45 * mm,
                "Documento gerado pelo sistema de recebimento"
            )
            pdf.save()
            buffer.seek(0)
            return buffer

        pdf_ticket = gerar_pdf_ticket(ticket)

        st.download_button(
            label="🖨️ ABRIR / IMPRIMIR TICKET",
            data=pdf_ticket,
            file_name=f"ticket_{ticket[0]:06d}.pdf",
            mime="application/pdf"
        )
