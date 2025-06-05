import json
from django import forms
from django.utils.safestring import mark_safe
from django.utils.html import escape


class JSONEditorWidget(forms.Widget):
    template_name = 'jsoneditor/jsoneditor.html'

    class Media:
        css = {
            'all': (
                'https://cdn.jsdelivr.net/npm/jsoneditor@9.5.6/dist/jsoneditor.min.css',
            )
        }
        js = (
            'https://cdn.jsdelivr.net/npm/jsoneditor@9.5.6/dist/jsoneditor.min.js',
        )

    def __init__(self, schema=None, collapsed=False, mode='tree', modes=None, *args, **kwargs):
        self.schema = schema
        self.collapsed = collapsed
        self.mode = mode
        self.modes = modes or ['tree', 'code']
        super().__init__(*args, **kwargs)

    def render(self, name, value, attrs=None, renderer=None):
        if isinstance(value, dict):
            value = json.dumps(value)
        elif value is None:
            value = ''

        escaped_value = escape(value)
        html = f'''
            <div id="jsoneditor_{name}" style="height: 400px;"></div>
            <textarea name="{name}" id="id_{name}" hidden>{escaped_value}</textarea>
            <script>
                const container = document.getElementById("jsoneditor_{name}");
                const textarea = document.getElementById("id_{name}");
                const options = {{
                    mode: "{self.mode}",
                    modes: {json.dumps(self.modes)},
                    onChangeText: function (jsonString) {{
                        textarea.value = jsonString;
                    }},
                    {"schema: " + json.dumps(self.schema) + "," if self.schema else ""}
                    collapse: {str(self.collapsed).lower()}
                }};
                const editor = new JSONEditor(container, options);
                if (textarea.value) {{
                    try {{
                        const initialJson = JSON.parse(textarea.value);
                        editor.set(initialJson);
                    }} catch (e) {{
                        console.warn("Invalid JSON:", e);
                    }}
                }}
            </script>
        '''
        return mark_safe(html)
