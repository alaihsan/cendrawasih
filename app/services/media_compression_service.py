import os
import subprocess
import threading
from datetime import datetime
from werkzeug.utils import secure_filename
from PIL import Image
import json
from flask import current_app

class MediaCompressionService:
    """Service untuk kompresi media (video/gambar) dengan HLS dan Background Processing"""
    
    ALLOWED_VIDEO = {'mp4', 'avi', 'mov', 'mkv', 'flv', 'wmv', 'webm'}
    ALLOWED_IMAGE = {'jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp'}
    
    @staticmethod
    def get_file_extension(filename):
        return filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    
    @staticmethod
    def validate_file_type(filename, file_type='video'):
        ext = MediaCompressionService.get_file_extension(filename)
        allowed = MediaCompressionService.ALLOWED_VIDEO if file_type == 'video' else MediaCompressionService.ALLOWED_IMAGE
        return ext in allowed, f"File type .{ext} not allowed. Allowed: {allowed}"
    
    @staticmethod
    def is_ffmpeg_available():
        """Check if ffmpeg and ffprobe are installed and accessible"""
        try:
            subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
            subprocess.run(['ffprobe', '-version'], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    @staticmethod
    def process_video_background(app, lesson_id, input_path, compressed_folder, hls_folder):
        """
        Background task untuk memproses video (Compression + HLS + Thumbnail)
        """
        with app.app_context():
            from app.models.lesson import Lesson
            from app import db
            
            lesson = Lesson.query.get(lesson_id)
            if not lesson:
                return

            try:
                lesson.compression_status = 'processing'
                db.session.commit()
                
                # 1. Generate Thumbnail
                thumb_result = MediaCompressionService.generate_video_thumbnail(input_path, compressed_folder, lesson_id)
                if thumb_result['success']:
                    lesson.compressed_image = thumb_result['thumbnail_path']
                    db.session.commit()
                
                # 2. Standard Compression (Multiple Qualities)
                compress_result = MediaCompressionService.compress_video(input_path, compressed_folder)
                
                if compress_result['success']:
                    lesson.compressed_video_versions = compress_result['versions']
                    lesson.compression_metadata = {
                        'original_size': compress_result['original_size'],
                        'total_compressed_size': compress_result['total_compressed_size'],
                        'compression_ratio': compress_result['compression_ratio']
                    }
                
                # 3. HLS Generation (Adaptive Streaming)
                hls_result = MediaCompressionService.generate_hls(input_path, hls_folder, lesson_id)
                if hls_result['success']:
                    lesson.hls_path = hls_result['playlist_path']
                
                lesson.compression_status = 'completed'
                db.session.commit()
                
            except Exception as e:
                lesson.compression_status = 'failed'
                lesson.compression_metadata = {'error': str(e)}
                db.session.commit()
                print(f"Background Video Processing Error: {str(e)}")

    @staticmethod
    def generate_video_thumbnail(input_path, output_folder, lesson_id):
        """Ambil 1 frame dari video sebagai thumbnail (poster)"""
        if not MediaCompressionService.is_ffmpeg_available():
            return {'success': False, 'message': 'FFmpeg not available'}
            
        try:
            os.makedirs(output_folder, exist_ok=True)
            thumb_name = f"thumb_lesson_{lesson_id}.jpg"
            output_path = os.path.join(output_folder, thumb_name)
            
            cmd = [
                'ffmpeg', '-i', input_path,
                '-ss', '00:00:01.000',
                '-vframes', '1',
                '-q:v', '2',
                '-y', output_path
            ]
            
            subprocess.run(cmd, capture_output=True, check=True)
            return {
                'success': True, 
                'thumbnail_path': f"uploads/compressed/{thumb_name}"
            }
        except Exception as e:
            return {'success': False, 'message': str(e)}

    @staticmethod
    def compress_video(input_path, output_folder):
        """Compress video ke berbagai kualitas (MP4)"""
        if not MediaCompressionService.is_ffmpeg_available():
            return {'success': False, 'message': 'FFmpeg tidak ditemukan.'}
        
        try:
            original_size = os.path.getsize(input_path)
            base_name = os.path.splitext(os.path.basename(input_path))[0]
            versions = {}
            
            # Quality presets
            presets = {
                'low': {'bitrate': '500k', 'scale': '480:270', 'crf': 28},
                'medium': {'bitrate': '1500k', 'scale': '1280:720', 'crf': 23},
                'high': {'bitrate': '3000k', 'scale': '1920:1080', 'crf': 20}
            }
            
            for quality_name, settings in presets.items():
                output_file = os.path.join(output_folder, f"{base_name}_{quality_name}.mp4")
                
                cmd = [
                    'ffmpeg', '-i', input_path,
                    '-vf', f"scale={settings['scale']}",
                    '-c:v', 'libx264', '-b:v', settings['bitrate'],
                    '-crf', str(settings['crf']), '-preset', 'veryfast',
                    '-c:a', 'aac', '-b:a', '128k', '-y', output_file
                ]
                
                subprocess.run(cmd, capture_output=True, check=True)
                
                if os.path.exists(output_file):
                    versions[quality_name] = f"uploads/compressed/{os.path.basename(output_file)}"
            
            total_compressed = sum(os.path.getsize(os.path.join(output_folder, os.path.basename(v))) for v in versions.values()) if versions else 0
            
            return {
                'success': True if versions else False,
                'original_size': original_size,
                'total_compressed_size': total_compressed,
                'compression_ratio': round((1 - total_compressed/original_size) * 100, 2) if original_size > 0 else 0,
                'versions': versions
            }
        except Exception as e:
            return {'success': False, 'message': str(e)}

    @staticmethod
    def generate_hls(input_path, output_root, lesson_id):
        """Generate HLS (m3u8) dengan adaptive bitrate"""
        if not MediaCompressionService.is_ffmpeg_available():
            return {'success': False, 'message': 'FFmpeg not available'}
            
        try:
            hls_dir = os.path.join(output_root, f"lesson_{lesson_id}")
            os.makedirs(hls_dir, exist_ok=True)
            
            playlist_name = "playlist.m3u8"
            output_path = os.path.join(hls_dir, playlist_name)
            
            cmd = [
                'ffmpeg', '-i', input_path,
                '-profile:v', 'baseline', '-level', '3.0',
                '-s', '1280x720', '-start_number', '0',
                '-hls_time', '10', '-hls_list_size', '0',
                '-f', 'hls', '-y', output_path
            ]
            
            subprocess.run(cmd, capture_output=True, check=True)
            
            relative_path = f"uploads/hls/lesson_{lesson_id}/{playlist_name}"
            return {'success': True, 'playlist_path': relative_path}
        except Exception as e:
            return {'success': False, 'message': str(e)}

    @staticmethod
    def compress_image(input_path, output_folder, quality=85):
        try:
            img = Image.open(input_path)
            original_size = os.path.getsize(input_path)
            
            base_name = os.path.splitext(os.path.basename(input_path))[0]
            jpeg_output = os.path.join(output_folder, f"{base_name}_comp.jpg")
            
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
                
            img.save(jpeg_output, 'JPEG', quality=quality, optimize=True)
            
            compressed_size = os.path.getsize(jpeg_output)
            return {
                'success': True,
                'jpeg_path': f"uploads/compressed/{os.path.basename(jpeg_output)}",
                'compression_ratio': round((1 - compressed_size / original_size) * 100, 2)
            }
        except Exception as e:
            return {'success': False, 'message': str(e)}

    @staticmethod
    def get_video_metadata(video_path):
        if not MediaCompressionService.is_ffmpeg_available():
            return {}
        try:
            cmd = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration : stream=width,height', '-of', 'json', video_path]
            result = subprocess.run(cmd, capture_output=True, text=True)
            return json.loads(result.stdout) if result.stdout else {}
        except:
            return {}
