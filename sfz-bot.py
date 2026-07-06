import discord
from discord.ext import commands
import os
import asyncio
from collections import deque

intents = discord.Intents.default()
intents.members = True
intents.voice_states = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

# ==================== CONFIGURAÇÕES ====================
SUPORTE_ENTRADA_ID = None      # Canal onde o usuário entra para pedir suporte
SUPORTE_CANAIS = []           # Lista de IDs dos canais de suporte (01, 02, 03...)
CANAL_ESPERA_ID = None        # Canal de espera (opcional)

fila_espera = deque()         # Fila de espera

@bot.event
async def on_ready():
    print(f'✅ Bot de Suporte Automático ONLINE como {bot.user}')
    print(f'Canais de suporte configurados: {len(SUPORTE_CANAIS)}')

@bot.event
async def on_voice_state_update(member, before, after):
    if after.channel is None:
        return

    # Usuário entrou no canal de suporte
    if SUPORTE_ENTRADA_ID and after.channel.id == SUPORTE_ENTRADA_ID:
        await asyncio.sleep(2)  # Delay para evitar erro

        moved = False
        
        # Tenta mover para o primeiro canal de suporte vazio
        for canal_id in SUPORTE_CANAIS:
            canal = member.guild.get_channel(canal_id)
            if canal and len(canal.members) == 0:  # Canal vazio
                try:
                    await member.move_to(canal)
                    await member.send(f"✅ Você foi movido para **{canal.name}**.\nUm atendente irá te ajudar em breve!")
                    moved = True
                    break
                except:
                    continue

        # Se todos os canais estiverem ocupados
        if not moved:
            if CANAL_ESPERA_ID:
                espera = member.guild.get_channel(CANAL_ESPERA_ID)
                if espera:
                    await member.move_to(espera)
                    fila_espera.append(member.id)
                    await member.send("⏳ Todos os atendentes estão ocupados.\nVocê foi colocado na **fila de espera**.")
            else:
                await member.send("⏳ Todos os atendentes estão ocupados. Aguarde um momento por favor.")

# ==================== COMANDOS ====================

@bot.command(name='setup')
@commands.has_permissions(administrator=True)
async def setup_suporte(ctx, entrada: discord.VoiceChannel, espera: discord.VoiceChannel = None):
    """Configura o sistema"""
    global SUPORTE_ENTRADA_ID, CANAL_ESPERA_ID
    SUPORTE_ENTRADA_ID = entrada.id
    CANAL_ESPERA_ID = espera.id if espera else None
    
    await ctx.send(f"✅ **Sistema de Suporte Configurado!**\n"
                  f"• Entrada: {entrada.mention}\n"
                  f"• Espera: {espera.mention if espera else 'Nenhum'}")

@bot.command(name='addsuporte')
@commands.has_permissions(administrator=True)
async def add_suporte_channel(ctx, canal: discord.VoiceChannel):
    """Adiciona canal de suporte"""
    global SUPORTE_CANAIS
    if canal.id not in SUPORTE_CANAIS:
        SUPORTE_CANAIS.append(canal.id)
        await ctx.send(f"✅ **{canal.name}** adicionado como canal de suporte!")
    else:
        await ctx.send("❌ Esse canal já está configurado.")

@bot.command(name='listsuporte')
async def list_suporte(ctx):
    """Lista todos os canais de suporte"""
    if not SUPORTE_CANAIS:
        return await ctx.send("Nenhum canal de suporte configurado.")
    
    msg = "**Canais de Suporte:**\n"
    for i, cid in enumerate(SUPORTE_CANAIS, 1):
        canal = ctx.guild.get_channel(cid)
        status = f"({len(canal.members)}/1)" if canal else "(erro)"
        msg += f"{i}. {canal.mention if canal else f'ID: {cid}'} {status}\n"
    await ctx.send(msg)

@bot.command(name='clearfila')
@commands.has_permissions(administrator=True)
async def clear_fila(ctx):
    """Limpa a fila de espera"""
    global fila_espera
    fila_espera.clear()
    await ctx.send("✅ Fila de espera limpa!")

# ==================== RODAR O BOT ====================
if __name__ == "__main__":
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        print("❌ Defina a variável DISCORD_TOKEN")
    else:
        bot.run(MTUyMzU1ODY1NDgwMzE4NTczNg.GHiGjK.PqWiRLiIDubwiZxrbaYQkIoXXUtgUJEuQRjzAg)