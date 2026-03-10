import pytest
import json
from unittest.mock import Mock
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from handlers.health_handler import HealthHandler
from handlers.convert_handler import ConvertHandler


class TestHealthHandler:
    def test_health_response(self):
        mock_handler = Mock()
        mock_handler.wfile = Mock()
        
        HealthHandler.handle(mock_handler)
        
        assert mock_handler.send_response.called
        assert mock_handler.send_response.call_args[0][0] == 200
        
        response_data = json.loads(mock_handler.wfile.write.call_args[0][0].decode())
        assert response_data["status"] == "healthy"


class TestConvertHandler:
    def test_error_response(self):
        mock_handler = Mock()
        mock_handler.wfile = Mock()
        
        ConvertHandler._send_error(mock_handler, 400, "Test error")
        
        assert mock_handler.send_response.called
        assert mock_handler.send_response.call_args[0][0] == 400
        
        response_data = json.loads(mock_handler.wfile.write.call_args[0][0].decode())
        assert response_data["success"] is False
        assert response_data["error"] == "Test error"
    
    def test_success_response(self, tmp_path):
        mock_handler = Mock()
        mock_handler.wfile = Mock()
        
        output_path = str(tmp_path / "output.pdf")
        ConvertHandler._send_success(mock_handler, output_path)
        
        assert mock_handler.send_response.called
        assert mock_handler.send_response.call_args[0][0] == 200
        
        response_data = json.loads(mock_handler.wfile.write.call_args[0][0].decode())
        assert response_data["success"] is True
        assert response_data["output_path"] == output_path
