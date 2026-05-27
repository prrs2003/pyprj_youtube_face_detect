import yt_dlp
import cv2
import os
import sys
from datetime import datetime

def log(message):
    """Exibe uma mensagem com timestamp para melhor rastreamento."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")
    sys.stdout.flush()

def download_youtube_video(url, output_path):
    """Baixa um vídeo do YouTube usando yt-dlp."""
    log("🔗 Conectando ao YouTube e obtendo informações do vídeo...")
    
    ydl_opts = {
        'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'restrictfilenames': True,
        'noplaylist': True,
        'quiet': False,
        'no_warnings': False,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            log("📥 Extraindo informações do vídeo...")
            info_dict = ydl.extract_info(url, download=False)
            filename = ydl.prepare_filename(info_dict)
            duration = info_dict.get('duration', 0)
            title = info_dict.get('title', 'Vídeo')
            
            log(f"📹 Título: {title}")
            log(f"⏱️  Duração: {duration // 60}:{duration % 60:02d} minutos")
            log(f"💾 Baixando para: {filename}")
            log("⏳ Iniciando download (isso pode levar alguns minutos)...")
            
            ydl.download([url])
            
            log(f"✅ Download concluído com sucesso: {filename}")
        return filename
    except Exception as e:
        log(f"❌ ERRO ao baixar vídeo: {str(e)}")
        raise


def detect_and_crop_faces(video_path, output_dir):
    """Detecta faces em um vídeo e as recorta para arquivos JPEG."""
    log("🔍 Carregando classificador de faces Haar Cascade...")
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    if face_cascade.empty():
        log("❌ ERRO: Impossível carregar o arquivo classificador Haar Cascade")
        raise IOError('Unable to load the face cascade classifier xml file')
    log("✅ Classificador de faces carregado com sucesso")

    log(f"🎬 Abrindo arquivo de vídeo: {video_path}")
    video_capture = cv2.VideoCapture(video_path)
    
    if not video_capture.isOpened():
        log("❌ ERRO: Impossível abrir o arquivo de vídeo")
        raise IOError(f"Unable to open video file: {video_path}")
    
    frame_width = int(video_capture.get(3))
    frame_height = int(video_capture.get(4))
    fps = video_capture.get(cv2.CAP_PROP_FPS)
    total_frames = int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
    
    log(f"📊 Informações do vídeo:")
    log(f"   - Resolução: {frame_width}x{frame_height}")
    log(f"   - FPS: {fps:.1f}")
    log(f"   - Total de frames: {total_frames}")
    log(f"   - Duração estimada: {total_frames/fps:.1f} segundos")
    
    scale_factor = 0.5  # The smaller the faster the face detection. But small faces might be missed
    log(f"🔧 Fator de escala para detecção: {scale_factor}")
    log("⏳ Iniciando processamento de frames...")
    
    count = 0
    frames_processed = 0
    faces_found_in_frame = 0
    last_progress_frames = 0
    progress_interval = max(1, total_frames // 20) if total_frames > 0 else 30  # Mostrar progresso 20 vezes
    
    while True:
        # Capture frame-by-frame
        ret, frame = video_capture.read()
        if not ret:
            log(f"✅ Fim do vídeo alcançado")
            break
        
        frames_processed += 1
        
        # Mostrar progresso a cada intervalo
        if frames_processed - last_progress_frames >= progress_interval:
            progress_percent = (frames_processed / total_frames * 100) if total_frames > 0 else 0
            log(f"📈 Progresso: {frames_processed}/{total_frames} frames ({progress_percent:.1f}%) - Faces encontradas: {count}")
            last_progress_frames = frames_processed
        ######
        # Resize the frame
        resized_frame = cv2.resize(frame, None, fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_AREA)

        gray = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2GRAY)

        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        
        faces_in_frame = len(faces)
        if faces_in_frame > 0:
            faces_found_in_frame += faces_in_frame

        # Draw a rectangle around the faces
        for (x, y, w, h) in faces:
            # Scale the coordinates back to the original image
            x, y, w, h = int(x / scale_factor), int(y / scale_factor), int(w / scale_factor), int(h / scale_factor)
            
            # Increase the size of the square
            padding_x = int(w * 0.10)
            padding_y = int(h * 0.10)
            x -= padding_x
            y -= padding_y
            w += 2 * padding_x
            h += 2 * padding_y
            
            # Prevent the square from going off screen
            x = max(0, x)
            y = max(0, y)
            w = min(frame_width - x, w)
            h = min(frame_height - y, h)

            face_image = frame[y:y+h, x:x+w]
            if face_image.size != 0:
                face_file = os.path.join(output_dir, f'face_{count}.jpg')
                cv2.imwrite(face_file, face_image)
                count += 1

    # When everything is done, release the capture
    video_capture.release()
    cv2.destroyAllWindows()
    
    log(f"🎉 Processamento de vídeo concluído!")
    log(f"📊 Estatísticas finais:")
    log(f"   - Total de frames processados: {frames_processed}")
    log(f"   - Total de faces detectadas: {count}")
    log(f"   - Frames com faces: {faces_found_in_frame if faces_found_in_frame > 0 else 'nenhum'}")

def main():
    """Função principal para executar a detecção de faces em um vídeo do YouTube."""
    log("=" * 70)
    log("🚀 INICIANDO DETECTOR DE FACES EM VÍDEO DO YOUTUBE")
    log("=" * 70)
    
    try:
        log("⌨️  Aguardando entrada do usuário...")
        youtube_url = input("Insira a URL do vídeo do YouTube: ").strip()
        
        if not youtube_url:
            log("❌ ERRO: URL vazia. Operação cancelada.")
            return
        
        log(f"✅ URL fornecida: {youtube_url}")
        
        output_dir = 'faces'  # Diretório para salvar as faces recortadas
        
        log(f"📁 Verificando diretório de saída: '{output_dir}'")
        if not os.path.exists(output_dir):
            log(f"   Criando diretório '{output_dir}'...")
            os.makedirs(output_dir)
            log(f"✅ Diretório criado: {output_dir}")
        else:
            log(f"✅ Diretório já existe: {output_dir}")
        
        log("\n" + "=" * 70)
        log("ETAPA 1: DOWNLOAD DO VÍDEO")
        log("=" * 70)
        video_path = download_youtube_video(youtube_url, '.')
        
        log("\n" + "=" * 70)
        log("ETAPA 2: DETECÇÃO E RECORTE DE FACES")
        log("=" * 70)
        detect_and_crop_faces(video_path, output_dir)
        
        log("\n" + "=" * 70)
        log("🎉 OPERAÇÃO CONCLUÍDA COM SUCESSO!")
        log("=" * 70)
        log(f"✅ Faces detectadas e salvas em '{output_dir}'")
        log(f"💾 Arquivo de vídeo local: {video_path}")
        log(f"📝 Para remover o vídeo manualmente, delete o arquivo: {video_path}")
        
    except KeyboardInterrupt:
        log("\n⚠️  OPERAÇÃO CANCELADA pelo usuário (Ctrl+C)")
    except Exception as e:
        log(f"\n❌ ERRO CRÍTICO: {str(e)}")
        log("Verifique os detalhes acima e tente novamente.")
        import traceback
        log(f"Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    main()