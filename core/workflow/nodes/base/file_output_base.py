import sys
from pathlib import Path
sys.path.append(str(Path(__file__).absolute().parent.parent.parent.parent))

from copy import deepcopy
from typing import Optional

from markitdown import MarkItDown

from . import Node
from ...variables import Variable, ObjectVariable
from core.database.models import UploadFiles

md = MarkItDown(enable_plugins=False)

project_root = Path(__file__).absolute().parent.parent.parent.parent.parent


class FileOutputBaseNode(Node):
    '''
    Base class for all File Output Base nodes.
    '''

    def replace_documents_with_strvars_in_context(self, outputs_var: Optional[ObjectVariable]) -> ObjectVariable:
        outputs_in_context = deepcopy(outputs_var)
        if outputs_var:
            for var_name, variable in outputs_var.properties.items():
                if variable.type == 'file':
                    if var_value := variable.value:
                        file_path = None
                        if not variable.sub_type or variable.sub_type == 'document':
                            # Get file path
                            if isinstance(var_value, int):
                                # Upload file ID
                                file_data = UploadFiles().get_file_by_id(var_value)
                                file_path = project_root.joinpath(file_data['path'])
                            elif isinstance(var_value, str):
                                if var_value[0] == '/':
                                    var_value = var_value[1:]
                                file_path = project_root.joinpath('storage').joinpath(var_value)
                            else:
                                # This should never happen
                                raise Exception('Unsupported value type!')
                        if not variable.sub_type:
                            # Tag file type
                            if file_path.suffix in ['.jpg', 'jpeg', '.png', '.gif', '.webp']:
                                variable.sub_type = 'image'
                                outputs_in_context.properties[var_name].sub_type = 'image'
                            else:
                                variable.sub_type = 'document'
                                string_var = Variable(name=var_name, type='string', value=md.convert(file_path).text_content)
                                outputs_in_context.add_property(var_name, string_var)
                        elif variable.sub_type == 'document':
                            string_var = Variable(name=var_name, type='string', value=md.convert(file_path).text_content)
                            outputs_in_context.add_property(var_name, string_var)
                    else:
                        # No file
                        string_var = Variable(name=var_name, type='string', value='')
                        outputs_in_context.add_property(var_name, string_var)

        return outputs_in_context
    