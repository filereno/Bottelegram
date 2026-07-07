import os
import asyncio
from dotenv import load_dotenv
from telethon import TelegramClient, events

# 1. Carregar chaves
load_dotenv()
api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')

# OPCIONAL: Se quiser monitorar apenas grupos específicos, coloque os IDs aqui
# Exemplo: GRUPOS_ALVO = [-100123456, -100987654]
# Se deixar vazio [], ele monitora TUDO.

PALAVRAS_CHAVE = ["refrigerador", "geladeira", "bug"]
GRUPOS_ALVO = [] # Grupos que você quer MONITORAR (Vazio = Todos)
GRUPO_ALERTA = "me" # Comece com "me" para enviar para você mesmo (Salvos) até configurar o ID do grupo

async def main():
    if not api_id or not api_hash:
        print("❌ Erro: API_ID ou API_HASH não encontrados no .env")
        return

    # 2. Criar o cliente
    client = TelegramClient('monitor_promo', int(api_id), api_hash)

    # 3. Lógica do Monitor
    @client.on(events.NewMessage(chats=GRUPOS_ALVO if GRUPOS_ALVO else None))
    async def verificador_de_mensagens(event):
        texto = event.raw_text.lower()

        # Verifica se alguma das palavras-chave está na mensagem
        palavras_encontradas = [p for p in PALAVRAS_CHAVE if p.lower() in texto]

        if palavras_encontradas:
            chat = await event.get_chat()
            nome_grupo = getattr(chat, 'title', 'Chat Privado')
            id_grupo = event.chat_id

            alerta = (
                f"🚨 **PALAVRA ENCONTRADA**: {', '.join(palavras_encontradas)}\n"
                f"📍 **Origem**: {nome_grupo} (ID: `{id_grupo}`)\n"
                f"💬 **Mensagem**: {event.raw_text}"
            )

            print(f"\n🚨 Notificação enviada para {GRUPO_ALERTA}")
            print(f"📍 Origem: {nome_grupo}")
            print("-" * 40)

            # Envia a mensagem para o grupo de alerta
            await client.send_message(GRUPO_ALERTA, alerta)

    # 4. Iniciar o cliente
    await client.start()
    print("✅ Monitor iniciado! Aguardando mensagens...")
    await client.run_until_disconnected()

if __name__ == "__main__":
    # Este comando inicia o loop de eventos corretamente
    asyncio.run(main())