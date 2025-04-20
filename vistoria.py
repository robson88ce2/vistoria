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

selected_campo = st.selectbox("📍 Escolha qual imagem deseja enviar ou capturar:", campos_fotos)


# Upload de imagem
st.markdown(" Envie uma imagem do seu dispositivo:")

uploaded_file = st.file_uploader(
    f"Envie imagem - {selected_campo}",
    type=["jpg", "jpeg", "png"],
    key=f"upload_{selected_campo}"
)

imagem = None

if uploaded_file:
    imagem = Image.open(uploaded_file)

# Corte e exibição
# Corte e exibição
if imagem:
    st.write("✂️ Corte a imagem abaixo:")
    # Define proporção padrão de 8x16 cm (1:2)
    cropped_img = st_cropper(imagem, aspect_ratio=(16, 8), box_color='#FF0000', key=f"crop_{selected_campo}")
    st.image(cropped_img, caption=f"Imagem cortada - {selected_campo}", use_container_width=True)
    st.session_state.imagens_cortadas[selected_campo] = cropped_img
    st.success(f"✅ Imagem de '{selected_campo}' salva com sucesso.")


# Geração do PDF com assinatura na última imagem
def gerar_pdf():
    def cabecalho_e_rodape(c, num_pagina):
        y_header = height - 60
        if os.path.exists(brasao_policia_path):
            c.drawImage(brasao_policia_path, margin, y_header - 110, width=120, height=120, preserveAspectRatio=True, mask='auto')
        if os.path.exists(brasao_ceara_path):
            c.drawImage(brasao_ceara_path, width - margin - 90, y_header - 80, width=94, height=94, preserveAspectRatio=True, mask='auto')

        linha = y_header
        c.setFillColor(colors.black)
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(width / 2, linha, "GOVERNO DO ESTADO DO CEARÁ")
        linha -= 16
        c.setFont("Helvetica-Bold", 12)
        c.drawCentredString(width / 2, linha, "POLÍCIA CIVIL")
        linha -= 16
        c.setFont("Helvetica-Oblique", 11)
        c.drawCentredString(width / 2, linha, "Departamento de Polícia Judiciária do Interior Norte")
        linha -= 16
        c.drawCentredString(width / 2, linha, "Delegacia de Itapipoca")

        rodape_texto = "Rua Coronel Bento Alves, S/n, Fazendinha | CEP: 62.502-268 - Itapipoca/CE | Fone: (88) 3631-3232"
        email = "Email: dritapipoca@policiacivil.ce.gov.br"
        c.setFont("Helvetica", 8)
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
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(width / 2, y, "VISTORIA VEICULAR")
    y -= 50

    c.setFont("Helvetica-Bold", 11)
    c.drawString(margin, y, "VEÍCULO VISTORIADO")
    y -= 25

    c.setFont("Courier", 10)
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
    draw_dado("Vistoria realizada em:", data_atual or "")

    c.setFont("Helvetica-Bold", 11)
    c.drawString(margin, y, "OBSERVAÇÕES:")
    y -= 20
    c.setFont("Courier", 10)
    for linha in observacoes.split("\n"):
        c.drawString(margin, y, linha)
        y -= 15

    y -= 20
    c.setFont("Helvetica-Bold", 11)
    c.drawString(margin, y, "FOTOS DO VEÍCULO:")
    y -= 20
    c.setFont("Helvetica", 10)
    c.drawString(margin, y, "As imagens a seguir correspondem aos ângulos descritos abaixo.")

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
                    c.drawImage(reader, margin, y_positions[j] - 240, width=width - 2 * margin, height=210, preserveAspectRatio=True)

        # Se for a última imagem da lista, coloca a assinatura nesta página
        if i + 2 >= len(campos_fotos):
            linha_y = 120
            nome_y = linha_y - 15
            titulo_y = nome_y - 15

            c.line(width / 2 - 150, linha_y, width / 2 + 150, linha_y)

            c.setFont("Helvetica", 10)
            c.drawCentredString(width / 2, nome_y, responsavel)

            c.setFont("Helvetica-Bold", 11)
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


st.subheader(" Pré-visualização das imagens salvas")
cols = st.columns(3)
for i, campo in enumerate(st.session_state.imagens_cortadas):
    with cols[i % 3]:
        st.image(st.session_state.imagens_cortadas[campo], caption=campo, use_container_width=True)