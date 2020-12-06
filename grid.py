import argparse
import asyncio
from pathlib import Path
from os import getenv

import discord
from PIL import Image

from dotenv import load_dotenv


def gerar_imagem(
    images_folder_path, width, height, thumb_width, thumb_height, output_file
):
    """
    @images_folder_path: Diretorio com fotos
    @thumb_width: Largura de cada foto no grid
    @thumb_height: Altura de cada foto no grid
    @width: Largura total da imagem (grid) final
    @height: Altura total da imagem (grid) final
    """

    # As imagens vieram do Discord com 1024 pixels de largura e altura.
    # Logo, o primeiro passo é redimensioná-las para 100 pixels de largura e altura.
    imagens = [
        Image.open(foto).resize((thumb_width, thumb_height), Image.ANTIALIAS)
        for foto in Path(images_folder_path).iterdir()
    ]

    # Aqui criamos a estrutura da imagem final, com 4800 pixels de largura e
    # 2800 pixels de altura.
    imagem_final = Image.new("RGB", (width, height))

    x_pace = int(width / thumb_width)
    y_pace = int(height / thumb_height)
    for x in range(0, x_pace):
        for y in range(0, y_pace):
            # A parte `% len(imagens)` faz com que o laço reuse imagens,
            # caso a proporção não seja perfeita.
            indice = (x_pace * y + x) % len(imagens)

            # Agora preenchemos a imagem final com cada uma das imagens de perfil
            # dos participamentes.
            imagem_final.paste(imagens[indice], (x * thumb_width, y * thumb_height))

    imagem_final.save(output_file)


async def grid_main(in_args):
    photos_folder = in_args.photos_folder
    output_file = in_args.output_file
    height = in_args.height
    width = in_args.width
    thumb_height = in_args.thumb_height
    thumb_width = in_args.thumb_width
    gerar_imagem(
        photos_folder,
        width=width,
        height=height,
        thumb_width=thumb_width,
        thumb_height=thumb_height,
        output_file=output_file,
    )


async def salvar_imagem(participante: discord.Member, output_folder):
    if participante.default_avatar_url == participante.avatar_url:
        # Se default_avatar_url é igual ao avatar_url, quer dizer que
        # a pessoa não alterou a foto de perfil
        return

    caminho = Path(output_folder) / "{participante.id}.webp"
    with open(caminho, "wb") as arquivo:
        await participante.avatar_url.save(arquivo)

    return caminho


async def download_discord_images(discord_token, discord_guild, output_folder):
    # Aqui criamos uma instância do client do Discord. Nós não precisávamos
    # usar o `discord.Intents.all()`, mas essa parte de autorização é mais
    # complexa, então fica para um próximo texto.
    cliente = discord.Client(intents=discord.Intents.all())
    await cliente.login(discord_token)

    # Nessa parte, buscamos o servidor da Python Brasil e listamos todos os
    # membros que estavam presentes.
    guild = await cliente.fetch_guild(discord_guild)
    membros = await guild.fetch_members().flatten()

    # Pronto, agora é só chamar a função salvar_imagem para cada um dos membros
    tarefas = [salvar_imagem(membro, output_folder=output_folder) for membro in membros]
    await asyncio.gather(*tarefas)

    await cliente.close()


async def download_main(input_args):
    discord_token = getenv("DISCORD_TOKEN")
    discord_guild = input_args.discord_guild
    output_folder = input_args.output_folder

    await download_discord_images(discord_token, discord_guild, output_folder)


def fetch(argv):
    parser = argparse.ArgumentParser()

    subp = parser.add_subparsers(required=True, dest="command")

    download_parser = subp.add_parser("download")
    download_parser.set_defaults(func=download_main)
    download_parser.add_argument(
        "-g", "--guild", dest="discord_guild", help="Discord Guild name"
    )
    download_parser.add_argument(
        "-d", "--dir", dest="output_folder", help="Help directory to save images"
    )

    grid_parser = subp.add_parser("grid")
    grid_parser.set_defaults(func=grid_main)
    grid_parser.add_argument(
        "-p",
        "--photos",
        dest="photos_folder",
        help="Input Photos folder",
        required=True,
    )
    grid_parser.add_argument(
        "-W", "--width", dest="width", type=int, help="Final image width", required=True
    )
    grid_parser.add_argument(
        "-H",
        "--height",
        dest="height",
        type=int,
        help="Final image height",
        required=True,
    )
    grid_parser.add_argument(
        "--tw",
        "--thumb_width",
        dest="thumb_width",
        type=int,
        help="Thumbnail (individual photo) width",
        default=100,
    )
    grid_parser.add_argument(
        "--th",
        "--thumb_height",
        dest="thumb_height",
        type=int,
        help="Thumbnail (individual height) ",
        default=100,
    )
    grid_parser.add_argument(
        "-o", "--output", dest="output_file", help="Final Output file", required=True
    )

    return parser.parse_args(argv)


async def main(argv):
    load_dotenv()

    in_args = fetch(argv)

    await in_args.func(in_args)


if __name__ == "__main__":
    import sys

    asyncio.run(main(sys.argv[1:]))
