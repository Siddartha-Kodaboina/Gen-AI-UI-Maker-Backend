from django.views.decorators.clickjacking import xframe_options_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .services.llm import LLMService
from .services.file_generator import FileGenerator
import os
import logging
import traceback
from django.http import HttpResponse 

logger = logging.getLogger('llm_service')

llm_service = LLMService()
file_generator = FileGenerator()

@api_view(['POST'])
def generate_code(request):
    logger.info("Received generate_code request")
    try:
        # Log request data
        logger.debug(f"Request data: {request.data}")
        
        prompt = request.data.get('prompt')
        if not prompt:
            logger.warning("No prompt provided in request")
            return Response({'error': 'Prompt is required'}, status=400)

        logger.info(f"Processing prompt: {prompt[:50]}...")

        # Generate code using LLM
        logger.debug("Calling LLM service")
        llm_response = llm_service.generate_code(prompt)
        logger.debug(f"LLM Response received: {llm_response[:100]}...")

        # Parse and save files
        logger.debug("Parsing LLM response")
        files = file_generator.parse_llm_response(llm_response)
        logger.debug(f"Parsed files: {list(files.keys())}")

        logger.debug("Saving files")
        saved_files = file_generator.save_files(files)
        logger.info(f"Successfully saved files: {saved_files}")

        # Return response
        response_data = {
            'message': 'Files generated successfully',
            'files': saved_files,
            'contents': files,
            'previewUrl': f'http://localhost:8000/api/preview/{saved_files[0]}' if saved_files else None
        }
        logger.debug(f"Sending response: {response_data}")
        return Response(response_data)

    except Exception as e:
        logger.error(f"Error in generate_code: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return Response({
            'error': str(e),
            'detail': traceback.format_exc()
        }, status=500)

@api_view(['GET', 'PUT'])
def manage_files(request):
    logger.info(f"Received {request.method} request to manage_files")
    try:
        base_dir = 'generated_files'
        
        if request.method == 'GET':
            file_name = request.query_params.get('file')
            logger.debug(f"Requested file: {file_name}")
            
            if file_name:
                file_path = os.path.join(base_dir, file_name)
                logger.debug(f"Looking for file at: {file_path}")
                
                if os.path.exists(file_path):
                    with open(file_path, 'r') as f:
                        content = f.read()
                    logger.info(f"Successfully read file: {file_name}")
                    return Response({'content': content})
                
                logger.warning(f"File not found: {file_name}")
                return Response({'error': 'File not found'}, status=404)
            
            if os.path.exists(base_dir):
                files = os.listdir(base_dir)
                logger.info(f"Found files: {files}")
                return Response({'files': files})
            
            return Response({'files': []})
            
        elif request.method == 'PUT':
            file_name = request.data.get('file')
            content = request.data.get('content')
            
            if not file_name or content is None:
                logger.warning("Missing file name or content in PUT request")
                return Response({'error': 'File name and content are required'}, status=400)
            
            file_path = os.path.join(base_dir, file_name)
            logger.debug(f"Updating file: {file_path}")
            
            with open(file_path, 'w') as f:
                f.write(content)
            
            logger.info(f"Successfully updated file: {file_name}")
            return Response({'message': f'File {file_name} updated successfully'})
            
    except Exception as e:
        logger.error(f"Error in manage_files: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return Response({
            'error': str(e),
            'detail': traceback.format_exc()
        }, status=500)

@api_view(['GET'])
@xframe_options_exempt
def preview_file(request, filename):
    """Serve the generated file with proper headers for iframe embedding"""
    try:
        file_path = os.path.join('generated_files', filename)
        if not os.path.exists(file_path):
            return Response({'error': 'File not found'}, status=404)
        
        with open(file_path, 'r') as f:
            content = f.read()
        
        response = HttpResponse(content, content_type='text/html')
        # Use correct X-Frame-Options value
        response['Content-Security-Policy'] = "frame-ancestors 'self' http://localhost:3000"
        return response
        
    except Exception as e:
        logger.error(f"Error serving preview: {str(e)}")
        return Response({'error': str(e)}, status=500)