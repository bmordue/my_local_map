# Testing Best Practices

## Writing New Tests

1. **Unit tests** for new utility functions
2. **Integration tests** for new workflows
3. **Mock external dependencies** appropriately
4. **Use descriptive test names** and docstrings
5. **Test both success and failure paths**

## Example Test Template

```python
import pytest
from unittest.mock import patch, MagicMock

class TestNewFeature:
    """Test new feature functionality"""
    
    @pytest.mark.unit
    def test_new_function_success(self):
        """Test successful execution of new function"""
        # Arrange
        # Act  
        # Assert
        
    @pytest.mark.unit
    def test_new_function_error_handling(self):
        """Test error handling in new function"""
        # Test error conditions
```