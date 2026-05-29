import yt_dlp
import os
import sys
from datetime import datetime


def log(message):
    """Exibe uma mensagem com timestamp para melhor rastreamento."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")
    sys.stdout.flush()


def ensure_directory(path):
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
        log(f"✅ Diretório criado: {path}")
    else:
        log(f"✅ Diretório existente: {path}")


def download_youtube_video(url, output_dir):
    """Baixa o melhor vídeo disponível do YouTube como MP4."""
    ydl_opts = {
        'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'restrictfilenames': True,
        'noplaylist': True,
        'quiet': False,
        'no_warnings': False,
    }
###
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            log("📥 Extraindo informações do vídeo...")
            info = ydl.extract_info(url, download=False)
            title = info.get('title', 'video')
            duration = info.get('duration', 0)
            filename = ydl.prepare_filename(info)

            log(f"📹 Título: {title}")
            log(f"⏱️  Duração: {duration // 60}:{duration % 60:02d} minutos")
            log(f"💾 Iniciando download do vídeo: {filename}")
            ydl.download([url])

            log(f"✅ Download do vídeo concluído: {filename}")
            return filename
    except Exception as exc:
        log(f"❌ Falha ao baixar o vídeo: {exc}")
        raise


def download_youtube_audio(url, output_dir):
    """Baixa o melhor áudio disponível do YouTube como MP3."""
    ydl_opts = {
        'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
        'format': 'bestaudio/best',
        'restrictfilenames': True,
        'noplaylist': True,
        'quiet': False,
        'no_warnings': False,
        'postprocessors': [
            {
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }
        ],
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            log("📥 Extraindo informações do áudio...")
            info = ydl.extract_info(url, download=False)
            title = info.get('title', 'audio')
            filename = os.path.join(output_dir, f"{title}.mp3")

            log(f"🎧 Título: {title}")
            log(f"💾 Iniciando download do áudio: {filename}")
            ydl.download([url])

            log(f"✅ Download do áudio concluído: {filename}")
            return filename
    except Exception as exc:
        log(f"❌ Falha ao baixar o áudio: {exc}")
        raise


def main():
    log("=" * 70)
    log("🚀 DOWNLOAD DE VÍDEO E ÁUDIO DO YOUTUBE")
    log("=" * 70)

    try:
        youtube_url = input("Insira a URL do vídeo do YouTube: ").strip()
        if not youtube_url:
            log("❌ ERRO: URL vazia. Operação cancelada.")
            return

        output_dir = input("Insira o diretório de saída (padrão: downloads): ").strip() or 'downloads'
        ensure_directory(output_dir)

        log("\n" + "=" * 70)
        log("ETAPA 1: DOWNLOAD DO VÍDEO")
        log("=" * 70)
        video_file = download_youtube_video(youtube_url, output_dir)

        log("\n" + "=" * 70)
        log("ETAPA 2: DOWNLOAD DO ÁUDIO")
        log("=" * 70)
        audio_file = download_youtube_audio(youtube_url, output_dir)

        log("\n" + "🎉 Downloads concluídos com sucesso!")
        log(f"   - Arquivo de vídeo: {video_file}")
        log(f"   - Arquivo de áudio: {audio_file}")
    except Exception:
        log("❌ O processo foi interrompido devido a um erro.")


if __name__ == '__main__':
    main()
