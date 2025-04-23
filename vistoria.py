import streamlit as st
from streamlit_cropper import st_cropper
from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors
from docx import Document
from docx.shared import Inches
import datetime
import io
import os
from PIL import ImageOps
st.set_page_config(page_title="Vistoria", layout="centered")
st.title("Sistema de Vistoria de Veículos")

# Dados do veículo
st.subheader("🔧 Dados do Veículo")
placa = st.text_input("Placa")
modelo = st.text_input("Marca/Modelo")
cor = st.text_input("Cor")
ano = st.text_input("Ano")
procedimento = st.text_input("Procedimento")
observacoes = st.text_area("Observações")
responsavel = "OIP ROBSON OLIVEIRA DE SOUSA"

campos_fotos = [
    "Lateral Traseira Direita",
    "Lateral Traseira Esquerda",
    "lateral Frente Direita",
    "Lateral Frente Esquerda",
    "Interior (Painel)",
    "Interior Traseira(Banco Traseiros)",
    "Capô Aberto"
]

st.subheader("Etapa 2: Envio e corte das Imagens")
st.markdown("Selecione a posição da imagem, envie ou capture a imagem, e corte se necessário.")

if 'imagens_cortadas' not in st.session_state:
    st.session_state.imagens_cortadas = {}

# Exibir status
with st.expander(" Status das imagens preenchidas"):
    for campo in campos_fotos:
        if campo in st.session_state.imagens_cortadas:
            st.markdown(f"✅ **{campo}** - imagem enviada")
        else:
            st.markdown(f"❌ **{campo}** - imagem pendente")



# Upload de imagem
st.title("Upload das imagens de vistoria")

# Lista com os campos fixos
campos = [
    "Lateral Traseira Direita",
    "Lateral Traseira Esquerda",
    "lateral Frente Direita",
    "Lateral Frente Esquerda",
    "Interior (Painel)",
    "Interior Traseira(Banco Traseiros)",
    "Capô Aberto"
]

# Tamanho final desejado
TARGET_SIZE = (606, 303)

# Inicializa session_state se não existir
if 'imagens_cortadas' not in st.session_state:
    st.session_state.imagens_cortadas = {}

# Loop por todos os campos e exibe um uploader para cada
for campo in campos:
    st.subheader(f"📸 {campo}")
    
    uploaded_file = st.file_uploader(
        f"Envie imagem - {campo}",
        type=["jpg", "jpeg", "png"],
        key=f"upload_{campo}"
    )

    if uploaded_file:
        imagem = Image.open(uploaded_file)

        st.write("🖼️ Imagem ajustada para 16x8cm (sem corte):")

        # Redimensionar mantendo proporção e preenchendo com branco
        imagem_ajustada = ImageOps.pad(imagem, TARGET_SIZE, color=(255, 255, 255), centering=(0.5, 0.5))

        st.image(imagem_ajustada, caption=f"Imagem ajustada - {campo}", use_container_width=True)

        st.session_state.imagens_cortadas[campo] = imagem_ajustada
        st.success(f"✅ Imagem de '{campo}' salva com sucesso.")


# Geração do PDF com assinatura na última imagem
def gerar_pdf():
    def cabecalho_e_rodape(c, num_pagina):
        y_header = height - 60
        if os.path.exists(brasao_policia_path):
            c.drawImage(brasao_policia_path, margin, y_header - 103, width=120, height=120, preserveAspectRatio=True, mask='auto')
        if os.path.exists(brasao_ceara_path):
            c.drawImage(brasao_ceara_path, width - margin - 90, y_header - 65, width=84, height=84, preserveAspectRatio=True, mask='auto')

        linha = y_header
        c.setFillColor(colors.black)
        c.setFont("Times-Roman", 14)
        c.drawCentredString(width / 2, linha, "GOVERNO DO ESTADO DO CEARÁ")
        linha -= 16
        c.setFont("Times-Roman", 12)
        c.drawCentredString(width / 2, linha, "POLÍCIA CIVIL")
        linha -= 16
        c.setFont("Times-Roman", 11)
        c.drawCentredString(width / 2, linha, "DEPARTAMENTEO DE POLICIA JUDICIÁRIA DO INTERIOR NORTE ")
        linha -= 16
        c.drawCentredString(width / 2, linha, "DELEGACIA DE ITAPIPOCA")

        # Linha abaixo do cabeçalho
        c.setStrokeColor(colors.lightgrey)
        c.setLineWidth(0.5)
        c.line(margin, linha - 18, width - margin, linha - 18)

        # Rodapé
        rodape_texto = "Rua Coronel Bento Alves, S/n, Fazendinha | CEP: 62.502-268 - Itapipoca/CE | Fone: (88) 3631-3232"
        email = "Email: dritapipoca@policiacivil.ce.gov.br"
        c.setFont("Helvetica", 8)
        c.setFillColor(colors.grey)
        c.drawCentredString(width / 2, 28, rodape_texto)
        c.drawCentredString(width / 2, 16, email)
        c.drawCentredString(width / 2, 4, f"Página {num_pagina}")

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    margin = 40
    data_atual = datetime.datetime.now().strftime("%d/%m/%Y")
    num_pagina = 1

    brasao_policia_path = "brasao_policia.png"
    brasao_ceara_path = "brasao_ceara.png"

    # Página inicial
    cabecalho_e_rodape(c, num_pagina)

    y = height - 180
    c.setFont("Times-Roman", 14)
    c.drawCentredString(width / 2, y, "VISTORIA VEICULAR")
    y -= 50

    # Seção - dados do veículo
    c.setFillColor(colors.whitesmoke)
    c.rect(margin, y - 135, width - 2 * margin, 135, stroke=0, fill=1)
    c.setFillColor(colors.black)

    c.setFont("Times-Roman", 12)
    c.drawString(margin, y, "DADOS DO VEÍCULO")
    y -= 25

    c.setFont("Times-Roman", 11)
    label_x = margin
    value_x = margin + 130

    def draw_dado(label, valor):
        nonlocal y
        c.drawString(label_x, y, f"{label}")
        c.drawString(value_x, y, f"{valor}")
        y -= 18

    draw_dado("PLACA OSTENTADA:", placa or "")
    draw_dado("MARCA/MODELO:", modelo or "")
    draw_dado("COR:", cor or "")
    draw_dado("ANO:", ano or "")
    draw_dado("PROCEDIMENTO:", procedimento or "")
    draw_dado("VISTORIADO EM :", data_atual or "")

    # Observações
    y -= 10
    c.setStrokeColor(colors.lightgrey)
    c.line(margin, y, width - margin, y)
    y -= 30

    c.setFont("Times-Roman", 11)
    c.drawString(margin, y, "OBSERVAÇÕES:")
    y -= 20
    c.setFont("Times-Roman", 10)
    for linha in observacoes.split("\n"):
        c.drawString(margin, y, linha)
        y -= 15

    y -= 20
    c.setFont("Times-Roman", 11)
    c.drawString(margin, y, "FOTOS DO VEÍCULO:")
    y -= 20
    c.setFont("Times-Roman", 10)
    c.drawString(margin, y, "")

    c.showPage()
    num_pagina += 1

    for i in range(0, len(campos_fotos), 2):
        cabecalho_e_rodape(c, num_pagina)
        y_positions = [height - 150, height - 450]

        for j in range(2):
            idx = i + j
            if idx < len(campos_fotos):
                campo = campos_fotos[idx]
                img = st.session_state.imagens_cortadas.get(campo)
                c.setFont("Helvetica-Bold", 10)
                c.drawCentredString(width / 2, y_positions[j] + 10, campo)

                if img:
                    img_io = io.BytesIO()
                    if img.mode != 'RGB':
                        img = img.convert('RGB')
                    img.save(img_io, format='JPEG')
                    img_io.seek(0)
                    reader = ImageReader(img_io)

                    # Moldura em volta da imagem
                    x_img = margin
                    y_img = y_positions[j] - 240
                    img_w = width - 2 * margin
                    img_h = 210

                    c.setStrokeColor(colors.grey)
                    c.rect(x_img - 2, y_img - 2, img_w + 4, img_h + 4, fill=0, stroke=1)

                    c.drawImage(reader, x_img, y_img, width=img_w, height=img_h, preserveAspectRatio=True)

        # Assinatura ao final
        if i + 2 >= len(campos_fotos):
            linha_y = 120
            nome_y = linha_y - 15
            titulo_y = nome_y - 15

            c.setStrokeColor(colors.black)
            c.line(width / 2 - 150, linha_y, width / 2 + 150, linha_y)

            c.setFont("Times-Roman", 10)
            c.drawCentredString(width / 2, nome_y, responsavel)

            c.setFont("Times-Roman", 11)
            c.drawCentredString(width / 2, titulo_y, "OFICIAL INVESTIGADOR RESPONSÁVEL")

        c.showPage()
        num_pagina += 1

    c.save()
    buffer.seek(0)
    return buffer

# Botões
if st.button("📄 Gerar Vistoria PDF"):
    buffer = gerar_pdf()
    st.success("✅ Vistoria gerada com sucesso.")
    st.download_button("⬇️ Baixar Vistoria PDF", data=buffer, file_name=f"Vistoria_{placa or 'sem_placa'}.pdf", mime="application/pdf")

