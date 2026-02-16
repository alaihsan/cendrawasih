import os
import subprocess
from datetime import datetime
from werkzeug.utils import secure_filename
from PIL import Image
from io import BytesIO
import json

class MediaCompressionService:
    """Service untuk kompresi media (video/gambar) dengan multiple quality"""
    
    ALLOWED_VIDEO = {'mp4', 'avi', 'mov', 'mkv', 'flv', 'wmv', 'webm'}
    ALLOWED_IMAGE = {'jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp'}
    
    @staticmethod
    def get_file_extension(filename):
        """Get file extension"""
        return filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    
    @staticmethod
    def validate_file_type(filename, file_type='video'):
        """Validate file type"""
        ext = MediaCompressionService.get_file_extension(filename)
        allowed = MediaCompressionService.ALLOWED_VIDEO if file_type == 'video' else MediaCompressionService.ALLOWED_IMAGE
        return ext in allowed, f"File type .{ext} not allowed. Allowed: {allowed}"
    
    @staticmethod
    def compress_image(input_path, output_folder, quality=85, max_width=1920):
        """
        Compress gambar dengan berbagai ukuran
        Returns: {original_size, compressed_size, output_paths}
        """
        try:
            img = Image.open(input_path)
            original_size = os.path.getsize(input_path)
            
            # Resize jika lebih besar dari max_width
            if img.width > max_width:
                ratio = max_width / img.width
                new_height = int(img.height * ratio)
                img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
            
            # Convert RGBA ke RGB jika perlu
            if img.mode in ('RGBA', 'LA', 'P'):
                rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'RGBA':
                    rgb_img.paste(img, mask=img.split()[3])
                else:
                    rgb_img.paste(img)
                img = rgb_img
            
            # Save compressed JPEG
            base_name = os.path.splitext(os.path.basename(input_path))[0]
            jpeg_output = os.path.join(output_folder, f"{base_name}_compressed_{quality}.jpg")
            img.save(jpeg_output, 'JPEG', quality=quality, optimize=True)
            
            # Save WebP version (smaller)
            webp_output = os.path.join(output_folder, f"{base_name}_compressed.webp")
            img.save(webp_output, 'WEBP', quality=quality)
            
            compressed_size = os.path.getsize(jpeg_output)
            compression_ratio = (1 - compressed_size / original_size) * 100
            
            return {
                'success': True,
                'original_size': original_size,
                'compressed_size': compressed_size,
                'compression_ratio': round(compression_ratio, 2),
                'jpeg_path': jpeg_output,
                'webp_path': webp_output,
                'message': f'Compressed {compression_ratio:.1f}%'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Image compression error: {str(e)}'
            }
    
    @staticmethod
    def compress_video(input_path, output_folder, quality='medium'):
        """
        Compress video dengan multiple quality levels menggunakan FFmpeg
        Returns: {original_size, versions, metadata}
        
        Quality options: 'low' (480p), 'medium' (720p), 'high' (1080p)
        """
        try:
            # Check ffmpeg installed
            subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        except:
            return {
                'success': False,
                'message': 'FFmpeg not installed. Install: pip install ffmpeg-python atau download dari ffmpeg.org'
            }
        
        try:
            original_size = os.path.getsize(input_path)
            base_name = os.path.splitext(os.path.basename(input_path))[0]
            versions = {}
            
            # Quality presets
            presets = {
                'low': {'bitrate': '500k', 'scale': '480:270', 'crf': 28},
                'medium': {'bitrate': '1500k', 'scale': '1280:720', 'crf': 23},
                'high': {'bitrate': '3000k', 'scale': '1920:1080', 'crf': 20},
                'webm': {'bitrate': '1000k', 'scale': '1280:720', 'crf': 25}
            }
            
            for quality_name, settings in presets.items():
                ext = 'webm' if quality_name == 'webm' else 'mp4'
                output_file = os.path.join(output_folder, f"{base_name}_{quality_name}.{ext}")
                
                # Build ffmpeg command
                if ext == 'webm':
                    cmd = [
                        'ffmpeg', '-i', input_path,
                        '-vf', f"scale={settings['scale']}",
                        '-b:v', settings['bitrate'],
                        '-c:v', 'libvpx-vp9',
                        '-crf', str(settings['crf']),
                        '-c:a', 'libopus',
                        '-b:a', '128k',
                        '-y', output_file
                    ]
                else:
                    cmd = [
                        'ffmpeg', '-i', input_path,
                        '-vf', f"scale={settings['scale']}",
                        '-c:v', 'libx264',
                        '-b:v', settings['bitrate'],
                        '-crf', str(settings['crf']),
                        '-preset', 'medium',
                        '-c:a', 'aac',
                        '-b:a', '128k',
                        '-y', output_file
                    ]
                
                # Run ffmpeg
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode == 0 and os.path.exists(output_file):
                    compressed_size = os.path.getsize(output_file)
                    versions[quality_name] = {
                        'path': output_file,
                        'bitrate': settings['bitrate'],
                        'scale': settings['scale'],
                        'size': compressed_size,
                        'format': ext
                    }
            
            if not versions:
                return {
                    'success': False,
                    'message': 'Video compression failed. Check FFmpeg installation.'
                }
            
            # Calculate total compression
            total_compressed = sum(v['size'] for v in versions.values())
            
            return {
                'success': True,
                'original_size': original_size,
                'total_compressed_size': total_compressed,
                'compression_ratio': round((1 - total_compressed/original_size) * 100, 2),
                'versions': versions,
                'message': f'Video compressed successfully!'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Video compression error: {str(e)}'
            }
    
    @staticmethod
    def get_video_metadata(video_path):
        """Get video metadata using ffprobe"""
        try:
            cmd = [
                'ffprobe', '-v', 'error',
                '-show_entries', 'format=duration,size : stream=width,height,codec_type',
                '-of', 'json',
                video_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            return json.loads(result.stdout) if result.stdout else {}
        except:
            return {}
