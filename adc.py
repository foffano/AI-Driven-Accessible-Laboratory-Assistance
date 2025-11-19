import os
import base64
import requests
import csv
import time

# --- CONFIGURAÇÕES ---

# Substitua pela sua chave da OpenRouter
OPENROUTER_API_KEY = "sk-or-v1-..." 

# Nome da pasta onde estão as imagens
DATASET_FOLDER = "dataset"

# O prompt que será enviado junto com cada imagem
PROMPT_TEXT = "Descreva detalhadamente o que você vê nesta imagem."

# Lista interna de modelos para testar
# Você pode adicionar ou remover modelos conforme a disponibilidade na OpenRouter
MODEL_LIST = [
    "google/gemini-flash-1.5",
    "openai/gpt-4o-mini",
    "meta-llama/llama-3.2-11b-vision-instruct",
    "anthropic/claude-3-haiku"
]

# URL da API OpenRouter
API_URL = "https://openrouter.ai/api/v1/chat/completions"

# --- FUNÇÕES AUXILIARES ---

def encode_image(image_path):
    """Lê uma imagem e converte para string Base64."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def get_image_files(folder):
    """Retorna lista de arquivos de imagem na pasta."""
    valid_extensions = ('.png', '.jpg', '.jpeg', '.webp', '.gif')
    return [f for f in os.listdir(folder) if f.lower().endswith(valid_extensions)]

def analyze_image(model, base64_image, prompt):
    """Envia a requisição para a API."""
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        # Cabeçalhos opcionais recomendados pela OpenRouter
        "HTTP-Referer": "http://localhost:8000", 
        "X-Title": "Script de Analise de Dataset",
    }

    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ]
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        response.raise_for_status() # Levanta erro se não for 200 OK
        data = response.json()
        return data['choices'][0]['message']['content']
    except Exception as e:
        print(f"Erro ao processar modelo {model}: {e}")
        return f"ERRO: {str(e)}"

# --- BLOCO PRINCIPAL ---

def main():
    # Verifica se a pasta existe
    if not os.path.exists(DATASET_FOLDER):
        print(f"Erro: A pasta '{DATASET_FOLDER}' não foi encontrada.")
        return

    images = get_image_files(DATASET_FOLDER)
    
    if not images:
        print(f"Nenhuma imagem encontrada na pasta '{DATASET_FOLDER}'.")
        return

    print(f"Encontradas {len(images)} imagens. Iniciando análise em {len(MODEL_LIST)} modelos...")

    # Loop pelos modelos
    for model in MODEL_LIST:
        # Cria um nome de arquivo seguro (substitui / por _)
        safe_model_name = model.replace("/", "_")
        csv_filename = f"resultados_{safe_model_name}.csv"
        
        print(f"\n--- Iniciando modelo: {model} ---")
        print(f"Salvando em: {csv_filename}")

        # Abre o CSV para escrita
        with open(csv_filename, mode='w', newline='', encoding='utf-8') as csv_file:
            writer = csv.writer(csv_file)
            # Cabeçalho do CSV
            writer.writerow(["id_image", "prompt", "model", "response"])

            # Loop pelas imagens
            for img_name in images:
                img_path = os.path.join(DATASET_FOLDER, img_name)
                
                print(f"Processando {img_name} com {model}...")
                
                # 1. Codificar imagem
                base64_img = encode_image(img_path)
                
                # 2. Enviar request
                res_text = analyze_image(model, base64_img, PROMPT_TEXT)
                
                # 3. Salvar linha no CSV
                writer.writerow([img_name, PROMPT_TEXT, model, res_text])
                
                # Pequena pausa para evitar Rate Limiting agressivo
                time.sleep(1) 

    print("\nProcesso finalizado! Verifique os arquivos .csv gerados.")

if __name__ == "__main__":
    main()