import os
import hashlib
from datetime import datetime
from werkzeug.utils import secure_filename
from app.services.media_compression_service import MediaCompressionService

class FileHandler:
    """Handle file uploads dan compression"""
    
    @staticmethod
    def generate_unique_filename(original_filename):
        """Generate unique filename dengan timestamp + hash"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        hash_suffix = hashlib.md5(original_filename.encode()).hexdigest()[:8]
        name, ext = os.path.splitext(original_filename)
        return f"{timestamp}_{hash_suffix}{ext}"
    
    @staticmethod
    def save_video_file(file, upload_folder, compressed_folder, quality='medium'):
        """
        Save dan compress video file
        Returns: {success, path, versions, metadata, message}
        """
        if not file or file.filename == '':
            return {'success': False, 'message': 'No file selected'}
        
        # Validate file type
        valid, msg = MediaCompressionService.validate_file_type(file.filename, 'video')
        if not valid:
            return {'success': False, 'message': msg}
        
        try:
            # Create directories
            os.makedirs(upload_folder, exist_ok=True)
            os.makedirs(compressed_folder, exist_ok=True)
            
            # Save original file
            filename = secure_filename(file.filename)
            filename = FileHandler.generate_unique_filename(filename)
            original_path = os.path.join(upload_folder, filename)
            file.save(original_path)
            
            # Get video metadata
            metadata = MediaCompressionService.get_video_metadata(original_path)
            
            # Compress video
            compress_result = MediaCompressionService.compress_video(
                original_path, 
                compressed_folder, 
                quality=quality
            )
            
            if not compress_result['success']:
                return compress_result
            
            # Return successful result
            return {
                'success': True,
                'original_filename': filename,
                'original_path': original_path,
                'original_size': compress_result['original_size'],
                'versions': compress_result['versions'],
                'compression_ratio': compress_result['compression_ratio'],
                'metadata': metadata,
                'message': compress_result['message']
            }
        except Exception as e:
            return {'success': False, 'message': f'Upload error: {str(e)}'}
    
    @staticmethod
    def save_image_file(file, upload_folder, compressed_folder, quality=85):
        """
        Save dan compress image file
        Returns: {success, jpeg_path, webp_path, compression_ratio, message}
        """
        if not file or file.filename == '':
            return {'success': False, 'message': 'No file selected'}
        
        # Validate file type
        valid, msg = MediaCompressionService.validate_file_type(file.filename, 'image')
        if not valid:
            return {'success': False, 'message': msg}
        
        try:
            # Create directories
            os.makedirs(upload_folder, exist_ok=True)
            os.makedirs(compressed_folder, exist_ok=True)
            
            # Save original file temporarily
            filename = secure_filename(file.filename)
            temp_path = os.path.join(upload_folder, FileHandler.generate_unique_filename(filename))
            file.save(temp_path)
            
            # Compress image
            compress_result = MediaCompressionService.compress_image(
                temp_path,
                compressed_folder,
                quality=quality
            )
            
            if not compress_result['success']:
                return compress_result
            
            # Remove original if compression successful
            if os.path.exists(temp_path):
                os.remove(temp_path)
            
            return compress_result
        except Exception as e:
            return {'success': False, 'message': f'Image upload error: {str(e)}'}
