import os
import asyncio
from dotenv import load_dotenv
from telethon import TelegramClient, events

# 1. Carregar chaves
load_dotenv()
api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')

# Configurações do Monitor
PALAVRAS_CHAVE = ["refrigerador", "geladeira"]
GRUPOS_ALVO = []      # Vazio = monitora todos os grupos/chats
GRUPO_ALERTA = "me"   # "me" envia para Mensagens Salvas (ou coloque o ID/username do canal de destino)

async def main():
    if not api_id or not api_hash:
        print("❌ Erro: API_ID ou API_HASH não encontrados no .env")
        return

    # 2. Criar o cliente Telethon
    client = TelegramClient('monitor_promo', int(api_id), api_hash)

    # 3. Lógica do Monitor
    @client.on(events.NewMessage(chats=GRUPOS_ALVO if GRUPOS_ALVO else None))
    async def verificador_de_mensagens(event):
        # Proteção contra loop infinito: ignora mensagens enviadas pela própria conta
        if event.out:
            return

        # Garante que mensagens sem texto (ex: apenas fotos/stickers) não quebrem a verificação
        texto = (event.raw_text or "").lower()
        if not texto:
            return

        # Verifica se alguma das palavras-chave está no texto da mensagem
        palavras_encontradas = [p for p in PALAVRAS_CHAVE if p.lower() in texto]

        if palavras_encontradas:
            try:
                chat = await event.get_chat()
                nome_grupo = getattr(chat, 'title', None) or getattr(chat, 'first_name', 'Chat Privado')
            except Exception:
                nome_grupo = "Desconhecido"

            id_grupo = event.chat_id

            alerta = (
                f"🚨 **PALAVRA ENCONTRADA**: {', '.join(palavras_encontradas)}\n"
                f"📍 **Origem**: {nome_grupo} (ID: `{id_grupo}`)\n"
                f"💬 **Mensagem**: {event.raw_text}"
            )

            print(f"\n🚨 Notificação enviada para: {GRUPO_ALERTA}")
            print(f"📍 Origem: {nome_grupo} (ID: {id_grupo})")
            print(f"🔑 Palavras detectadas: {palavras_encontradas}")
            print("-" * 40)

            # Envia a mensagem para o destinatário de alerta
            await client.send_message(GRUPO_ALERTA, alerta)

    # 4. Iniciar o cliente
    await client.start()
    print("✅ Monitor iniciado com sucesso! Aguardando mensagens...")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
