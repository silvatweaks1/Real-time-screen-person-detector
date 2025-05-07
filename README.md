# real-time-screen-person-detector

Um sistema de detecção de pessoas em tempo real que captura a tela do computador e sobrepõe caixas delimitadoras transparentes usando YOLOv4-tiny. Ideal para aplicações de segurança, monitoramento passivo e análises visuais em tempo real.

## 🚀 Funcionalidades

- Detecção de pessoas usando YOLOv4-tiny.
- Captura da tela com `mss` em alta frequência.
- Interface fullscreen invisível com `Tkinter`, sobrepondo a detecção sem interferir no uso da máquina.
- Caixa delimitadora animada com suavização (`smoothing`).
- Overlay clicável desativado (modo pass-through).
- Fechamento seguro com tecla ESC.

## 🧠 Tecnologias Utilizadas

- [OpenCV](https://opencv.org/) – Processamento de imagem e DNN.
- [YOLOv4-tiny](https://github.com/AlexeyAB/darknet) – Rede neural leve para detecção.
- [MSS](https://github.com/BoboTiG/python-mss) – Captura rápida da tela.
- [Tkinter](https://docs.python.org/3/library/tkinter.html) – Interface transparente.
- [Pillow](https://python-pillow.org/) – Manipulação de imagem para overlay.
- [PyWin32](https://pypi.org/project/pywin32/) – Controle de janelas no Windows.

## 📦 Pré-requisitos

- Python 3.8 ou superior
- Windows OS
- Modelos YOLOv4-tiny (`.weights`, `.cfg` e `.names`)
