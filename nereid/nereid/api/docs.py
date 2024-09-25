from fastapi.openapi.docs import get_swagger_ui_html
from starlette.responses import HTMLResponse


# Swagger UI includes a supermassive curl div that is not height constrained.
# Not sure how this hasn't been fixed, but this patches it for this project.
def get_better_swagger_ui_html(*args, **kwargs) -> HTMLResponse:
    body = get_swagger_ui_html(**kwargs).body
    if isinstance(body, memoryview):
        body = body.tobytes()
    body_lines = body.decode().split("\n")
    ix = 4
    for i, line in enumerate(body_lines):
        if 'type="text/css" rel="stylesheet"' in line:
            ix = i

    new_css = "<style>#swagger-ui .curl-command .curl {max-height: 20em;}</style>"

    body_lines.insert(ix + 1, new_css)

    html = "\n".join(body_lines)

    return HTMLResponse(html)
