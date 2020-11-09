import discord
from PIL import Image


def gerar_imagem():
    # As imagens vieram do Discord com 1024 pixels de largura e altura.
    # Logo, o primeiro passo é redimensioná-las para 100 pixels de largura e altura.
    imagens = [
        Image.open(foto).resize((100, 100), Image.ANTIALIAS)
        for foto in Path("fotos").iterdir()
    ]

    # Aqui criamos a estrutura da imagem final, com 4800 pixels de largura e
    # 2800 pixels de altura.
    imagem_final = Image.new('RGB', (4800, 2800))

    for x in range(0,48):
        for y in range(0,28):
            # A parte `% len(imagens)` faz com que o laço reuse imagens,
            # caso a proporção não seja perfeita.
            indice = (48 * y + x) % len(imagens)

            # Agora preenchemos a imagem final com cada uma das imagens de perfil
            # dos participamentes.
            imagem_final.paste(imagens[indice], (x * 100, y * 100))

    imagem_final.save("python-brasil-2020.jpg")



async def salvar_imagem(participante: discord.Member):
    if participante.default_avatar_url == participante.avatar_url:
        # Se default_avatar_url é igual ao avatar_url, quer dizer que
        # a pessoa não alterou a foto de perfil
        return

    caminho = f"fotos/{participante.id}.webp"
    with open(caminho, "wb") as arquivo:
        await participante.avatar_url.save(arquivo)

    return caminho


async def main():
    token = "Token do bot no Discord"
    guild = "ID do servidor da Python Brasil"

    # Aqui criamos uma instância do client do Discord. Nós não precisávamos
    # usar o `discord.Intents.all()`, mas essa parte de autorização é mais
    # complexa, então fica para um próximo texto.
    cliente = discord.Client(intents=discord.Intents.all())
    await cliente.login(token)

    # Nessa parte, buscamos o servidor da Python Brasil e listamos todos os
    # membros que estavam presentes.
    guild = await cliente.fetch_guild(guild)
    membros = await guild.fetch_members().flatten()

    # Pronto, agora é só chamar a função salvar_imagem para cada um dos membros
    tarefas = [salvar_imagem(membro) for membro in membros]
    await asyncio.gather(*tarefas)
    await client.close()
