#!/usr/bin/env bash
# exit on error
set -o errexit

# 1. Instalar dependências do Python
pip install -r requirements.txt

# 2. Instalar o Google Chrome para o Selenium
STORAGE_DIR=$HOME/.chrome
if [ ! -d "$STORAGE_DIR" ]; then
  echo "...Baixando Google Chrome..."
  mkdir -p $STORAGE_DIR
  cd $STORAGE_DIR
  wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
  
  # Extrair o conteúdo do pacote .deb sem precisar de ROOT
  ar x google-chrome-stable_current_amd64.deb
  tar xvf data.tar.xz
  
  echo "...Chrome instalado com sucesso em $STORAGE_DIR..."
else
  echo "...Chrome já está no cache..."
fi

# 3. Adicionar o Chrome ao PATH para que o Selenium o encontre
export PATH=$PATH:$HOME/.chrome/opt/google/chrome