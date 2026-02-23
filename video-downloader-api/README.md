# Video Downloader API

API gratuita para download de vídeos do TikTok, Instagram e mais de 1000 sites usando yt-dlp.

## Como subir no Render.com (gratuito)

### Passo 1 - Criar repositório no GitHub
1. Acesse github.com e crie um novo repositório (ex: `video-downloader-api`)
2. Faça upload dos arquivos: `main.py`, `requirements.txt`, `render.yaml`

### Passo 2 - Deploy no Render.com
1. Acesse render.com e crie uma conta gratuita
2. Clique em **New > Web Service**
3. Conecte seu repositório do GitHub
4. Configure:
   - **Name**: video-downloader-api
   - **Runtime**: Python
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Free
5. Clique em **Create Web Service**

Aguarde ~3 minutos para o deploy finalizar. Você receberá uma URL no formato:
`https://video-downloader-api.onrender.com`

## Endpoints

### GET /
Verifica se a API está rodando.

### POST /info
Retorna informações do vídeo.
```json
{ "url": "https://www.tiktok.com/@user/video/123" }
```

### POST /download-link
Retorna o link direto do MP4.
```json
{ "url": "https://www.tiktok.com/@user/video/123" }
```
**Resposta:**
```json
{
  "success": true,
  "download_url": "https://...",
  "title": "Nome do vídeo",
  "thumbnail": "https://...",
  "platform": "TikTok"
}
```

### POST /batch-links
Retorna links para múltiplos vídeos (máx 20).
```json
{ "urls": ["https://tiktok.com/...", "https://instagram.com/..."] }
```

## Prompt para o Lovable

Use este prompt para integrar no seu SaaS:

```
Crie uma página chamada "Baixar Vídeos" com o seguinte:
- Campo de texto grande onde posso colar múltiplos links (um por linha) do TikTok e Instagram
- Botão "Processar Vídeos"
- Ao clicar, chame POST https://SUA-URL.onrender.com/batch-links com { "urls": [...] }
- Mostre uma lista com o status de cada vídeo: thumbnail, título, plataforma
- Para cada vídeo com sucesso, mostre um botão "Baixar MP4" que abre o download_url em nova aba
- Para erros, mostre a mensagem em vermelho
- Loading state enquanto processa
```

## Plataformas suportadas
- TikTok ✅
- Instagram (Reels, Posts) ✅
- YouTube ✅
- Twitter/X ✅
- E mais de 1000 outros sites
