# Guia Passo a Passo: Gerando o Executável (Laboratory Assistant)

Este documento descreve o processo exato utilizado para compilar o aplicativo Python (`app.py`) em um arquivo executável (`.exe`) funcional no Windows.

## 1. Preparação do Código (`app.py`)

Antes de compilar, foi necessário ajustar o código para que ele encontre os arquivos corretamente tanto rodando como script quanto como executável (onde os arquivos são extraídos para uma pasta temporária).

**Alteração realizada no início do `app.py`:**

```python
import os
import sys
# ... outros imports ...

# ... (após inicializar app e socketio) ...

# Configuração de caminhos compatível com PyInstaller
if getattr(sys, 'frozen', False):
    # Se estiver rodando como executável (frozen)
    
    # 1. Definir base_path para onde o .exe está (para salvar settings.json ao lado do exe)
    base_path = os.path.dirname(sys.executable)
    
    # 2. Definir pastas de templates/static para a pasta temporária do PyInstaller (_MEIPASS)
    if hasattr(sys, '_MEIPASS'):
        app.template_folder = os.path.join(sys._MEIPASS, 'templates')
        app.static_folder = os.path.join(sys._MEIPASS, 'static')
else:
    # Se estiver rodando como script Python normal
    base_path = os.path.dirname(os.path.abspath(__file__))

# O arquivo de configurações fica sempre ao lado do executável/script
SETTINGS_FILE = os.path.join(base_path, 'settings.json')

# ... restante do código ...
```

## 2. Configuração do Ambiente (Virtual Environment)

Foi detectado um problema de compatibilidade entre o **Python 3.10** e o **PyInstaller** (erro no módulo `dis`). Por isso, utilizamos o **Python 3.13** instalado no sistema.

**Comandos executados no Terminal (PowerShell):**

1.  **Remover ambiente antigo (se houver):**
    ```powershell
    Remove-Item -Recurse -Force venv
    ```

2.  **Criar novo ambiente virtual usando Python 3.13:**
    ```powershell
    py -3.13 -m venv venv
    ```

## 3. Instalação das Dependências

Instalamos as bibliotecas necessárias dentro do ambiente virtual criado.

```powershell
venv\Scripts\pip install flask flask-socketio opencv-python requests pillow numpy gTTS pygame python-dotenv pyinstaller
```

## 4. Gerando o Executável

Utilizamos o **PyInstaller** com parâmetros específicos para incluir os arquivos HTML/CSS/JS e tratar dependências ocultas do SocketIO.

**Comando de Build:**

```powershell
venv\Scripts\pyinstaller --noconfirm --onefile --console --name "LaboratoryAssistant" --add-data "templates;templates" --add-data "static;static" --hidden-import "engineio.async_drivers.threading" app.py
```

### Explicação das Flags:
*   `--noconfirm`: Não pede confirmação para sobrescrever arquivos.
*   `--onefile`: Gera um único arquivo `.exe` em vez de uma pasta cheia de arquivos.
*   `--console`: Mantém a janela preta do terminal aberta (útil para ver logs do servidor Flask).
*   `--name "LaboratoryAssistant"`: Nome do arquivo final.
*   `--add-data "templates;templates"`: Copia a pasta `templates` para dentro do executável (Syntaxe: `origem;destino` no Windows).
*   `--add-data "static;static"`: Copia a pasta `static` (CSS/JS) para dentro do executável.
*   `--hidden-import "engineio.async_drivers.threading"`: Força a inclusão de drivers do `python-socketio` que o PyInstaller as vezes não detecta automaticamente.

## 5. Resultado Final

O arquivo gerado encontra-se na pasta `dist`:

*   **Caminho:** `\dist\LaboratoryAssistant.exe`

Ao executar este arquivo:
1.  Ele extrai os recursos internos para uma pasta temporária.
2.  Inicia o servidor Flask.
3.  Cria/Lê o `settings.json` no mesmo diretório onde o `.exe` está.
4.  Abre o navegador automaticamente.
